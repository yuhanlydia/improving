"""Same-problem geometry reports and reproducible intervention banks.

Subspaces describe response-loss sensitivity in one frozen model coordinate
system. They are not algorithm labels. Every geometric comparison below stays
inside the same module, and descriptive reports compare only the same problem.
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Mapping, Sequence
from copy import deepcopy
import math
from numbers import Integral
import random

import torch
from torch import Tensor

from .geometry import (compare_subspaces, concatenate_span,
                       grassmann_interpolate, normalized_operator)


def _positive_integer(value, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, Integral) or value < 1:
        raise ValueError(f"{name} must be a positive integer")
    return int(value)


def _validate_artifacts(artifacts: Sequence[Mapping]) -> list[Mapping]:
    records = list(artifacts)
    dimensions: dict[str, int] = {}
    identities = set()
    for artifact in records:
        if not isinstance(artifact, Mapping):
            raise ValueError("artifacts must be mappings")
        identity = (str(artifact.get("task_id", "")), str(artifact.get("sample_id", "")))
        if not all(identity) or identity in identities:
            raise ValueError("each artifact needs a unique (task_id, sample_id)")
        identities.add(identity)
        modules = artifact.get("modules")
        if not isinstance(modules, Mapping) or not modules:
            raise ValueError("each artifact must contain nonempty modules")
        for name, entry in modules.items():
            if not isinstance(name, str) or not name or not isinstance(entry, Mapping):
                raise ValueError("modules must map nonempty names to records")
            basis = entry.get("basis")
            eigenvalues = entry.get("eigenvalues")
            if (not isinstance(basis, Tensor) or basis.ndim != 2 or basis.is_complex()
                    or basis.shape[0] < 1 or not torch.isfinite(basis).all()):
                raise ValueError(f"invalid basis for {name}")
            d, r = basis.shape
            if r > d or dimensions.setdefault(name, d) != d:
                raise ValueError(f"inconsistent ambient dimension for module {name}")
            if (not isinstance(eigenvalues, Tensor) or eigenvalues.ndim != 1
                    or eigenvalues.is_complex() or eigenvalues.numel() != r
                    or not torch.isfinite(eigenvalues).all()
                    or bool((eigenvalues <= 0).any())):
                raise ValueError(f"{name}: eigenvalues must match actual positive-rank basis")
            values = eigenvalues.detach().double().cpu()
            if values.numel() > 1 and bool((values[1:] > values[:-1] * (1 + 1e-7)).any()):
                raise ValueError(f"{name}: eigenvalues and basis must be in descending order")
            b = basis.detach().double().cpu()
            if not torch.allclose(b.T @ b, torch.eye(r, dtype=torch.float64),
                                  atol=1e-5, rtol=1e-5):
                raise ValueError(f"{name}: basis must be orthonormal; do not pad its rank")
    return records


def _identity(artifact: Mapping) -> tuple[str, str]:
    return str(artifact["task_id"]), str(artifact["sample_id"])


def _pair_from_index(index: int, n: int) -> tuple[int, int]:
    """Invert lexicographic combinations(range(n), 2), without materializing it."""
    low, high = 0, n - 2
    while low < high:
        middle = (low + high + 1) // 2
        if middle * (2 * n - middle - 1) // 2 <= index:
            low = middle
        else:
            high = middle - 1
    offset = low * (2 * n - low - 1) // 2
    return low, low + 1 + index - offset


def _spectrum_summary(entry: Mapping) -> dict:
    values = entry["eigenvalues"].detach().double().cpu()
    if not values.numel():
        return {"stored_rank": 0, "effective_rank": 0.0, "participation_rank": 0.0,
                "rank_80": 0, "rank_90": 0, "rank_95": 0}
    # Normalize before summing so large finite eigenvalues cannot overflow.
    scaled = values / values[0]
    probabilities = scaled / scaled.sum()
    cumulative = probabilities.cumsum(0)
    result = {
        "stored_rank": int(values.numel()),
        "effective_rank": float(torch.exp(-torch.special.xlogy(probabilities, probabilities).sum())),
        "participation_rank": float(1 / probabilities.square().sum()),
    }
    for percentage in (80, 90, 95):
        result[f"rank_{percentage}"] = min(
            len(values), int(torch.searchsorted(cumulative, percentage / 100)) + 1)
    # Keep extraction's energy-threshold rank separate from entropy effective
    # rank; the former may refer to total observed energy including omitted tail.
    for source, target in (("effective_rank", "extracted_energy_rank"),
                           ("captured_energy", "captured_energy"),
                           ("energy_target", "extracted_energy_target"),
                           ("rank_capped", "rank_capped"),
                           ("energy_target_reached", "energy_target_reached")):
        if isinstance(entry.get(source), (int, float, bool)):
            result[target] = entry[source]
    return result


def _macro_aggregate(rows: list[dict]) -> list[dict]:
    grouped = defaultdict(lambda: defaultdict(list))
    for row in rows:
        key = (row["module"], row["comparison"], row["rank_a"], row["rank_b"])
        grouped[key][row["task_id"]].append(row["metrics"])
    aggregates = []
    for (module, comparison, rank_a, rank_b), tasks in sorted(grouped.items()):
        metric_names = sorted({key for task_rows in tasks.values() for metrics in task_rows
                               for key, value in metrics.items()
                               if isinstance(value, (int, float)) and not isinstance(value, bool)})
        means = {}
        for metric in metric_names:
            task_means = []
            for task_rows in tasks.values():
                values = [float(row[metric]) for row in task_rows
                          if metric in row and isinstance(row[metric], (int, float))
                          and math.isfinite(float(row[metric]))]
                if values:
                    task_means.append(sum(values) / len(values))
            if task_means:
                means[metric] = sum(task_means) / len(task_means)
        aggregates.append({"module": module, "comparison": comparison,
                           "rank_a": rank_a, "rank_b": rank_b,
                           "task_count": len(tasks),
                           "pair_count": sum(map(len, tasks.values())),
                           "task_macro_mean": means})
    return aggregates


def summarize_geometry(
    artifacts: Sequence[Mapping], ranks: Sequence[int] = (4, 8, 16, 32),
    max_pairs_per_task: int = 45, seed: int = 42,
) -> dict:
    """Return a JSON-safe report, with fixed-rank and unequal-rank comparisons.

    Pair subsampling is uniform within each problem, before rank eligibility.
    Both the full eligibility denominator and actually sampled eligible count
    are reported. Adjacent requested ranks are compared in both directions for
    containment; absence of a rank is never repaired with random/zero padding.
    Macro means first average pairs inside each task, then average tasks equally.
    Effective-rank statistics refer to the *stored* spectrum, which may be capped
    during extraction; they are not estimates of unrecorded spectral tails.
    """
    records = sorted(_validate_artifacts(artifacts), key=_identity)
    grid = sorted({_positive_integer(rank, "rank") for rank in ranks})
    if not grid:
        raise ValueError("at least one rank is required")
    limit = _positive_integer(max_pairs_per_task, "max_pairs_per_task")
    rng = random.Random(seed)
    tasks = defaultdict(list)
    for artifact in records:
        tasks[str(artifact["task_id"])].append(artifact)
    rows, individual, sampling = [], [], []
    selected_counts = defaultdict(int)
    module_names = sorted({name for record in records for name in record["modules"]})
    for record in records:
        for module, entry in sorted(record["modules"].items()):
            individual.append({"task_id": str(record["task_id"]),
                               "sample_id": str(record["sample_id"]), "module": module,
                               **_spectrum_summary(entry)})

    for task_id, candidates in sorted(tasks.items()):
        possible = len(candidates) * (len(candidates) - 1) // 2
        indices = sorted(rng.sample(range(possible), min(possible, limit)))
        sampling.append({"task_id": task_id, "artifact_count": len(candidates),
                         "possible_pairs": possible, "sampled_pairs": len(indices)})
        for index in indices:
            i, j = _pair_from_index(index, len(candidates))
            left, right = candidates[i], candidates[j]
            common = sorted(set(left["modules"]) & set(right["modules"]))
            for module in common:
                a, b = left["modules"][module]["basis"], right["modules"][module]["basis"]
                comparisons = [(rank, rank, "fixed_rank") for rank in grid]
                comparisons += [(ra, rb, "unequal_rank")
                                for small, large in zip(grid, grid[1:])
                                for ra, rb in ((small, large), (large, small))]
                for rank_a, rank_b, kind in comparisons:
                    if a.shape[1] < rank_a or b.shape[1] < rank_b:
                        continue
                    metrics = compare_subspaces(a[:, :rank_a], b[:, :rank_b])
                    angles = metrics.get("principal_angles_degrees", [])
                    if angles:
                        metrics.update(principal_angle_mean_degrees=sum(angles) / len(angles),
                                       principal_angle_max_degrees=max(angles),
                                       principal_angle_min_degrees=min(angles))
                    row = {"task_id": task_id, "sample_a": str(left["sample_id"]),
                           "sample_b": str(right["sample_id"]), "module": module,
                           "comparison": kind, "rank_a": rank_a, "rank_b": rank_b,
                           "metrics": metrics}
                    label_a = left.get("metadata", {}).get("strategy_label")
                    label_b = right.get("metadata", {}).get("strategy_label")
                    if isinstance(label_a, (str, int)) and isinstance(label_b, (str, int)):
                        row.update(strategy_label_a=label_a, strategy_label_b=label_b,
                                   same_supplied_strategy_label=label_a == label_b)
                    rows.append(row)
                    if kind == "fixed_rank":
                        selected_counts[(module, rank_a)] += 1

    eligibility = []
    for module in module_names:
        for rank in grid:
            available = [record for record in records if module in record["modules"]]
            eligible = [record for record in available
                        if record["modules"][module]["basis"].shape[1] >= rank]
            by_task = defaultdict(int)
            for record in eligible:
                by_task[str(record["task_id"])] += 1
            eligibility.append({
                "module": module, "rank": rank, "artifact_count": len(available),
                "eligible_artifact_count": len(eligible),
                "ineligible_artifact_count": len(available) - len(eligible),
                "tasks_with_eligible_artifacts": len(by_task),
                "tasks_with_two_eligible_artifacts": sum(n >= 2 for n in by_task.values()),
                "possible_eligible_pairs": sum(n * (n - 1) // 2 for n in by_task.values()),
                "evaluated_eligible_pairs": selected_counts[(module, rank)],
            })
    spectrum_macros = []
    for module in module_names:
        by_task = defaultdict(list)
        for item in individual:
            if item["module"] == module:
                by_task[item["task_id"]].append(item)
        numeric_keys = ("stored_rank", "effective_rank", "participation_rank",
                        "rank_80", "rank_90", "rank_95")
        means = {key: sum(sum(item[key] for item in task_rows) / len(task_rows)
                          for task_rows in by_task.values()) / len(by_task)
                 for key in numeric_keys}
        spectrum_macros.append({"module": module, "task_count": len(by_task),
                                "artifact_count": sum(map(len, by_task.values())),
                                "task_macro_mean": means})
    return {"schema_version": 1, "scope": "same_task_same_module",
            "requested_ranks": grid, "seed": seed, "max_pairs_per_task": limit,
            "artifact_count": len(records), "task_count": len(tasks),
            "effective_rank_scope": "stored_eigenvalue_spectrum_only",
            "effective_rank_definition": "exp(entropy(normalized_stored_eigenvalues))",
            "pair_sampling": sampling, "eligibility": eligibility,
            "individual": individual, "pairs": rows,
            "spectrum_macro_aggregates": spectrum_macros,
            "macro_aggregates": _macro_aggregate(rows)}


def _distance(left: Mapping, right: Mapping, rank: int) -> float:
    common = sorted(set(left["modules"]) & set(right["modules"]))
    if not common:
        raise ValueError("bank candidates must share at least one named module")
    distances = []
    for module in common:
        a = left["modules"][module]["basis"][:, :rank].detach().double().cpu()
        b = right["modules"][module]["basis"][:, :rank].detach().double().cpu()
        overlap = float((a.T @ b).square().sum())
        distances.append(math.sqrt(max(0.0, min(1.0, 1 - overlap / rank))))
    return sum(distances) / len(distances)


def build_bank(artifacts: Sequence[Mapping], rank: int, count: int, seed: int = 42) -> list[dict]:
    """Select existing samples by deterministic farthest-first chordal distance.

    Each retained sample has the requested actual rank in *every* recorded module.
    Distances use small cross-Gram matrices and O(N) storage, not an N-by-N table.
    Caller must supply training artifacts from the same frozen model only.
    """
    rank, count = _positive_integer(rank, "rank"), _positive_integer(count, "count")
    records = sorted(_validate_artifacts(artifacts), key=_identity)
    candidates = [record for record in records
                  if all(entry["basis"].shape[1] >= rank for entry in record["modules"].values())]
    if len(candidates) < count:
        raise ValueError(f"need {count} rank-{rank} candidates, found {len(candidates)} "
                         f"of {len(records)}; rank padding is not permitted")
    generator = random.Random(seed)
    chosen = [generator.randrange(len(candidates))]
    selection_distances = [None]
    minimum_distances = [float("inf")] * len(candidates)
    while len(chosen) < count:
        latest = candidates[chosen[-1]]
        for i, candidate in enumerate(candidates):
            minimum_distances[i] = min(minimum_distances[i], _distance(latest, candidate, rank))
        for index in chosen:
            minimum_distances[index] = -1.0
        next_index = max(range(len(candidates)), key=lambda i: minimum_distances[i])
        chosen.append(next_index)
        selection_distances.append(minimum_distances[next_index])
    bank = []
    for position, (index, distance) in enumerate(zip(chosen, selection_distances)):
        record = candidates[index]
        selected = {key: deepcopy(value) for key, value in record.items() if key != "modules"}
        selected["modules"] = {}
        for module, entry in record["modules"].items():
            selected["modules"][module] = {
                **{key: deepcopy(value) for key, value in entry.items()
                   if key not in {"basis", "eigenvalues"}},
                "basis": entry["basis"][:, :rank].detach().double().cpu().clone(),
                "eigenvalues": entry["eigenvalues"][:rank].detach().double().cpu().clone(),
            }
        selected["bank_selection"] = {"index": position, "rank": rank, "seed": seed,
                                      "input_count": len(records),
                                      "eligible_count": len(candidates),
                                      "excluded_count": len(records) - len(candidates),
                                      "distance_to_selected": distance,
                                      "method": "farthest_first_mean_normalized_chordal"}
        bank.append(selected)
    return bank


def operator_family(
    bank: Sequence[Mapping], strength: float = 1.0,
    interpolation: Sequence[float] = (0.25, 0.5, 0.75), seed: int = 42,
) -> dict[str, dict[str, Tensor]]:
    """Return pre-RoPE residual operators with matched ||T-I||_F per module.

    Arms are response 0/1, their span, a span-rank-matched random control,
    Grassmann interpolants, a single-rank random control, and an equal-weight
    pooled top-r subspace. They are geometry probes, not SPD reproductions.
    The span can have higher rank, but its total perturbation norm is matched.
    """
    records = _validate_artifacts(bank)
    if not records:
        raise ValueError("operator_family requires a nonempty bank")
    if not math.isfinite(strength) or strength < 0:
        raise ValueError("strength must be finite and nonnegative")
    fractions = [float(value) for value in interpolation]
    if any(not math.isfinite(value) or not 0 < value < 1 for value in fractions):
        raise ValueError("interpolation fractions must lie strictly between zero and one")
    names = [f"interpolate_{value:.6g}" for value in fractions]
    if len(names) != len(set(names)):
        raise ValueError("interpolation fractions must be distinct")
    modules = set(records[0]["modules"])
    if any(set(record["modules"]) != modules for record in records):
        raise ValueError("operator bank entries must use the same module set")
    generator = torch.Generator(device="cpu").manual_seed(seed)
    result: dict[str, dict[str, Tensor]] = defaultdict(dict)
    for module in sorted(modules):
        bases = [record["modules"][module]["basis"].detach().double().cpu() for record in records]
        rank = bases[0].shape[1]
        if rank < 1 or any(basis.shape[1] != rank for basis in bases):
            raise ValueError("operator bank must have one common positive actual rank")
        dimension = bases[0].shape[0]

        def add(name: str, basis: Tensor) -> None:
            result[name][module] = normalized_operator(basis, strength=strength)

        def random_basis(r: int) -> Tensor:
            matrix = torch.randn(dimension, r, dtype=torch.float64, generator=generator)
            return torch.linalg.qr(matrix, mode="reduced").Q

        add("single0", bases[0])
        add("random_single", random_basis(rank))
        # SVD of the thin concatenation avoids constructing a dense covariance.
        pooled = torch.linalg.svd(torch.cat(bases, dim=1), full_matrices=False).U[:, :rank]
        add("pooled", pooled)
        if len(bases) >= 2:
            add("single1", bases[1])
            span = concatenate_span(bases[:2])
            add("span", span)
            add("matched_random_span", random_basis(span.shape[1]))
            for fraction, name in zip(fractions, names):
                add(name, grassmann_interpolate(bases[0], bases[1], fraction))
    return dict(result)
