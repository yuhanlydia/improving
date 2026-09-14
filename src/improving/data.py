"""Validated JSONL records and opt-in preparation of real coding datasets.

Dataset packages and network downloads are used only inside preparation calls.
The MBPP calibration and validation subsets come exclusively from its official
``full/train`` split; its official test split is reserved for evaluation.
"""

from __future__ import annotations

import ast
import copy
import hashlib
import json
import os
from pathlib import Path
import random
import tempfile
import unicodedata
from collections.abc import Iterable, Mapping
from typing import Any


def read_jsonl(path: str | Path) -> list[dict[str, Any]]:
    """Read JSON objects, rejecting malformed/nonobject lines with locations."""
    records = []
    with Path(path).open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            try:
                record = json.loads(line, parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)))
            except (json.JSONDecodeError, ValueError) as error:
                raise ValueError(f"{path}: line {line_number}: invalid JSON: {error}") from error
            if not isinstance(record, dict):
                raise ValueError(f"{path}: line {line_number}: expected a JSON object")
            records.append(record)
    return records


def write_jsonl(path: str | Path, records: Iterable[Mapping[str, Any]]) -> None:
    """Atomically replace a file only after all records serialize successfully."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent, prefix=f".{path.name}.", suffix=".tmp", delete=False) as handle:
            temporary = Path(handle.name)
            for record in records:
                if not isinstance(record, Mapping):
                    raise ValueError("JSONL records must be mappings")
                handle.write(json.dumps(dict(record), ensure_ascii=False, allow_nan=False) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def _nonempty_string(record: Mapping[str, Any], key: str) -> None:
    if not isinstance(record.get(key), str) or not record[key].strip():
        raise ValueError(f"{key} must be a nonempty string")


def validate_tasks(records: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Return copied records after schema, IDs, and span integrity checks."""
    output, seen = [], set()
    for raw in records:
        if not isinstance(raw, Mapping):
            raise ValueError("Task records must be mappings")
        record = dict(raw)
        for key in ("task_id", "prompt", "source", "split"):
            _nonempty_string(record, key)
        task_id = record["task_id"]
        if "/" not in task_id or task_id.startswith("/") or task_id.endswith("/"):
            raise ValueError("task_id must be namespaced, for example Mbpp/601")
        if task_id in seen:
            raise ValueError(f"Duplicate task_id: {task_id}")
        seen.add(task_id)
        for key in ("reference", "tests", "entry_point", "code_prefix", "original_prompt"):
            if key in record and not isinstance(record[key], str):
                raise ValueError(f"{task_id}: {key} must be a string")
        if "entry_point" in record and record["entry_point"] and not record["entry_point"].isidentifier():
            raise ValueError(f"{task_id}: entry_point must be a Python identifier")
        if "calibration_spans" in record:
            spans, reference = record["calibration_spans"], record.get("reference", "")
            if not isinstance(spans, list) or not spans:
                raise ValueError(f"{task_id}: calibration_spans must be nonempty intervals")
            previous_end = 0
            for span in spans:
                if (not isinstance(span, (list, tuple)) or len(span) != 2 or
                    any(type(value) is not int for value in span) or
                    not 0 <= previous_end <= span[0] < span[1] <= len(reference)):
                    raise ValueError(f"{task_id}: invalid or overlapping calibration_spans")
                previous_end = span[1]
        output.append(record)
    return output


def validate_completions(records: Iterable[Mapping[str, Any]], tasks: Iterable[Mapping[str, Any]] | None = None) -> list[dict[str, Any]]:
    """Reject duplicate/unknown keys without discarding empty or invalid code."""
    task_ids = None if tasks is None else {task["task_id"] for task in validate_tasks(tasks)}
    output, seen = [], set()
    for raw in records:
        if not isinstance(raw, Mapping):
            raise ValueError("Completion records must be mappings")
        record = dict(raw)
        _nonempty_string(record, "task_id")
        if type(record.get("sample_id")) is not int or record["sample_id"] < 0:
            raise ValueError("sample_id must be a nonnegative integer")
        if not isinstance(record.get("completion"), str):
            raise ValueError("completion must be a string (empty is allowed)")
        key = (record["task_id"], record["sample_id"])
        if key in seen:
            raise ValueError(f"Duplicate completion key: {key}")
        if task_ids is not None and record["task_id"] not in task_ids:
            raise ValueError(f"Unknown task_id: {record['task_id']}")
        seen.add(key)
        for field in ("prompt_tokens", "generation_tokens", "round"):
            if field in record and (type(record[field]) is not int or record[field] < 0):
                raise ValueError(f"{field} must be a nonnegative integer")
        output.append(record)
    return output


def prompt_fingerprint(prompt: str) -> str:
    """Hash Unicode-normalized text with runs of whitespace collapsed."""
    normalized = " ".join(unicodedata.normalize("NFKC", prompt).split())
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def assert_disjoint_splits(splits: Mapping[str, Iterable[Mapping[str, Any]]]) -> None:
    """Reject a task ID or normalized prompt present in different splits."""
    ids: dict[str, str] = {}
    prompts: dict[str, str] = {}
    for split, raw_tasks in splits.items():
        for task in validate_tasks(raw_tasks):
            if task["split"] != split:
                raise ValueError(f"{task['task_id']}: declared split {task['split']} differs from {split}")
            for value, seen, kind in ((task["task_id"], ids, "task_id"),
                (prompt_fingerprint(task["prompt"]), prompts, "prompt fingerprint"),
                (prompt_fingerprint(task.get("original_prompt", task["prompt"])), prompts, "original prompt fingerprint")):
                if value in seen and seen[value] != split:
                    raise ValueError(f"Cross-split {kind} leakage: {seen[value]} and {split} ({task['task_id']})")
                seen[value] = split


def _mbpp_entry_point(row: Mapping[str, Any]) -> str:
    try:
        names = {node.name for node in ast.parse(row["code"]).body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))}
        for test in row["test_list"]:
            for node in ast.walk(ast.parse(test)):
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in names:
                    return node.func.id
    except SyntaxError:
        pass
    return ""


def _mbpp_interface(row: Mapping[str, Any]) -> dict[str, str]:
    """Expose only the required callable interface, never reference behavior."""
    entry_point = _mbpp_entry_point(row)
    definitions = ast.parse(row["code"]).body
    function = next((node for node in definitions if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == entry_point), None)
    if function is None:
        raise ValueError(f"Mbpp/{row['task_id']}: cannot determine required function interface")
    arguments = copy.deepcopy(function.args)
    all_arguments = [*arguments.posonlyargs, *arguments.args, *arguments.kwonlyargs]
    all_arguments += [arg for arg in (arguments.vararg, arguments.kwarg) if arg is not None]
    for argument in all_arguments:
        argument.annotation = None
        argument.type_comment = None
    arguments.defaults = [ast.Constant(value=Ellipsis) for _ in arguments.defaults]
    arguments.kw_defaults = [None if value is None else ast.Constant(value=Ellipsis) for value in arguments.kw_defaults]
    prefix = "async def" if isinstance(function, ast.AsyncFunctionDef) else "def"
    stub = f"{prefix} {entry_point}({ast.unparse(arguments)}):\n    pass"
    prompt = f"{row['text']}\n\nImplement this Python function. Return only the complete implementation.\n{stub}"
    return {"entry_point": entry_point, "prompt": prompt, "original_prompt": row["text"],
        "prompt_protocol": "mbpp-function-interface-v1", "interface_source": "reference-ast-signature-only"}


def prepare_mbpp(output_dir: str | Path, seed: int = 42, calibration_size: int = 50, validation_size: int = 30, revision: str | None = None) -> dict[str, list[dict[str, Any]]]:
    """Download official MBPP full, partition train deterministically, save JSONL.

    A revision should be pinned for reproducible experiments. If omitted, the
    records explicitly retain ``revision=None`` and HF split fingerprints so
    an unpinned download is never misrepresented as a known source revision.

    Preserve official test rows. Remove original-prompt overlaps from the train
    pool, then deduplicate that pool by lowest numeric task ID before assigning
    train/calibration/validation. This is dataset hygiene, not response filtering.
    """
    if any(type(size) is not int or size < 0 for size in (calibration_size, validation_size)):
        raise ValueError("Split sizes must be nonnegative integers")
    try:
        from datasets import load_dataset
    except ImportError as error:
        raise ImportError("MBPP preparation requires installing improving-code[train]") from error
    dataset = load_dataset("google-research-datasets/mbpp", "full", revision=revision)
    source_rows = {name: list(dataset[name]) for name in ("train", "test")}
    source_fingerprints = {}
    for name, rows in source_rows.items():
        snapshot = [{"task_id": f"Mbpp/{row['task_id']}",
                     "prompt_fingerprint": prompt_fingerprint(row.get("original_prompt", row["text"]))}
                    for row in sorted(rows, key=lambda item: int(item["task_id"]))]
        source_fingerprints[name] = {
            "dataset_fingerprint": getattr(dataset[name], "_fingerprint", None),
            "prompt_snapshot_sha256": hashlib.sha256(
                json.dumps(snapshot, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()}
    eval_prompts: dict[str, list[str]] = {}
    for row in sorted(source_rows["test"], key=lambda item: int(item["task_id"])):
        fingerprint = prompt_fingerprint(row.get("original_prompt", row["text"]))
        eval_prompts.setdefault(fingerprint, []).append(f"Mbpp/{row['task_id']}")
    pool, exclusions, retained_prompts = [], [], {}
    for row in sorted(source_rows["train"], key=lambda item: int(item["task_id"])):
        fingerprint = prompt_fingerprint(row.get("original_prompt", row["text"]))
        if fingerprint in eval_prompts:
            reason = "original_prompt_overlaps_official_test"
            matches = eval_prompts[fingerprint]
        elif fingerprint in retained_prompts:
            reason = "duplicate_original_prompt_in_train_pool"
            matches = [retained_prompts[fingerprint]]
        else:
            retained_prompts[fingerprint] = f"Mbpp/{row['task_id']}"
            pool.append(row)
            continue
        exclusions.append({"task_id": f"Mbpp/{row['task_id']}",
                           "original_task_id": row["task_id"], "original_split": "train",
                           "reason": reason, "prompt_fingerprint": fingerprint,
                           "matching_task_ids": matches})
    if calibration_size + validation_size >= len(pool):
        raise ValueError("Calibration and validation must leave a nonempty decontaminated official train pool")
    random.Random(seed).shuffle(pool)
    raw_splits = {"train": pool[calibration_size + validation_size:], "calibration": pool[:calibration_size],
                  "validation": pool[calibration_size:calibration_size + validation_size], "eval": source_rows["test"]}
    prepared = {}
    for split, rows in raw_splits.items():
        original_split = "test" if split == "eval" else "train"
        prepared[split] = [dict(task_id=f"Mbpp/{row['task_id']}", original_task_id=row["task_id"],
            **_mbpp_interface(row), reference=row["code"],
            tests="\n".join(filter(None, [row.get("test_setup_code", ""), *row["test_list"]])),
            source="google-research-datasets/mbpp", split=split,
            original_split=original_split, dataset_config="full", revision=revision, split_seed=seed,
            dataset_fingerprint=getattr(dataset[original_split], "_fingerprint", None)) for row in rows]
    assert_disjoint_splits(prepared)
    for split, rows in prepared.items():
        write_jsonl(Path(output_dir) / f"{split}.jsonl", rows)
    manifest = {
        "source": "google-research-datasets/mbpp", "dataset_config": "full",
        "revision": revision, "split_seed": seed,
        "preparation_protocol": "mbpp-official-test-preserving-decontamination-v1",
        "fingerprint_protocol": "sha256-nfkc-whitespace-collapsed-v1",
        "source_counts": {name: len(rows) for name, rows in source_rows.items()},
        "source_fingerprints": source_fingerprints,
        "clean_train_pool_count": len(pool), "excluded_count": len(exclusions),
        "exclusions": exclusions,
        "output_counts": {split: len(rows) for split, rows in prepared.items()},
        "output_task_ids": {split: [row["task_id"] for row in rows] for split, rows in prepared.items()},
    }
    write_jsonl(Path(output_dir) / "preparation_manifest.jsonl", [manifest])
    return prepared


def prepare_humaneval(output_dir: str | Path) -> dict[str, list[dict[str, Any]]]:
    """Fetch official HumanEval through optional EvalPlus, for evaluation only.

    This prepares original HumanEval checks; extended HumanEval+ correctness
    must come from the external EvalPlus bridge. The upstream helper downloads
    OpenAI's master snapshot, so its content hash is recorded and revision is
    explicitly unpinned.
    """
    try:
        from evalplus.data.humaneval import get_human_eval
    except ImportError as error:
        raise ImportError("HumanEval preparation requires improving-code[evalplus]") from error
    problems = get_human_eval()
    dataset_hash = hashlib.sha256(json.dumps(problems, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()
    rows = [dict(task_id=task_id, prompt=row["prompt"], reference=row["canonical_solution"],
        tests=row["test"], entry_point=row["entry_point"], source="openai/human-eval", split="eval",
        original_split="test", revision=None, dataset_sha256=dataset_hash,
        code_prefix=row["prompt"], completion_mode="continuation", test_mode="check")
        for task_id, row in sorted(problems.items())]
    rows = validate_tasks(rows)
    write_jsonl(Path(output_dir) / "eval.jsonl", rows)
    return {"eval": rows}
