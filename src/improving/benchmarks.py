"""Pinned, evaluation-only transfer benchmarks for the SPECTRUM ICLR suite.

Only MBPP supplies training/calibration/validation data. APPS, CodeContests,
and LiveCodeBench are explicitly adapted verification protocols; their scores
must not be labelled official leaderboard scores. HumanEval+ is delegated to
the existing official EvalPlus bridge and deliberately has no builtin tests.
Preparation never executes a candidate or reference program.
"""
from __future__ import annotations

import ast
import base64
from collections import Counter
from collections.abc import Mapping, Sequence
import hashlib
import io
from importlib.metadata import version as package_version
import json
import os
from pathlib import Path
import pickle
import random
import re
from typing import Any
import zlib

from .data import (assert_disjoint_splits, prepare_mbpp, prompt_fingerprint,
                   read_jsonl, validate_tasks, write_jsonl)
from .utils import atomic_json, stable_hash


BENCHMARKS = ("mbpp", "humanevalplus", "apps_intro", "codecontests", "livecodebench")
HF_REPOSITORIES = {
    "mbpp": "google-research-datasets/mbpp",
    "apps_intro": "codeparrot/apps",
    "codecontests": "deepmind/code_contests",
    "livecodebench": "livecodebench/code_generation_lite",
}
HUMANEVAL_RELEASE = "v0.1.10"
EVALPLUS_VERSION = "0.3.1"
PREPARATION_PROTOCOL = "spectrum-five-benchmarks-v1"


def _sha(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _json(value: Any, *, where: str) -> Any:
    if isinstance(value, str):
        try:
            return json.loads(value)
        except json.JSONDecodeError as error:
            raise ValueError(f"{where}: malformed JSON") from error
    return value


def _text(value: Any, *, where: str, allow_empty: bool = False) -> str:
    if not isinstance(value, str) or (not allow_empty and not value.strip()):
        raise ValueError(f"{where}: expected {'possibly empty ' if allow_empty else 'nonempty '}text")
    return value


def _hf_revision(repository: str, requested: str | None) -> str:
    """Resolve once, then use only the returned immutable commit for downloads."""
    from huggingface_hub import HfApi
    revision = HfApi().dataset_info(repository, revision=requested or "main").sha
    if not isinstance(revision, str) or not re.fullmatch(r"[0-9a-f]{40}", revision):
        raise ValueError(f"{repository}: cannot resolve an immutable dataset revision")
    return revision


def _download_jsonl(repository: str, revision: str, filenames: Sequence[str]):
    from huggingface_hub import hf_hub_download
    rows, files = [], {}
    for filename in filenames:
        local = Path(hf_hub_download(repository, filename, repo_type="dataset", revision=revision))
        rows.extend(read_jsonl(local))
        files[filename] = {"sha256": _sha(local), "bytes": local.stat().st_size}
    return rows, files


def _stdin_task(task_id: str, question: str, cases: Sequence[tuple[str, str]], *,
                source: str, metadata: dict[str, Any]) -> dict[str, Any]:
    if not cases:
        raise ValueError(f"{task_id}: no verification tests")
    checked = [(_text(x, where=f"{task_id} input", allow_empty=True),
                _text(y, where=f"{task_id} output", allow_empty=True)) for x, y in cases]
    prompt = (_text(question, where=f"{task_id} question") +
              "\n\nImplement a Python function solve(stdin: str) -> str. The argument contains "
              "the complete standard input for one execution of the problem. Return the complete "
              "standard output as a string. Do not read from standard input or print the answer. "
              "Return only Python code, including any imports and the complete solve function.")
    tests = (f"_spectrum_cases = {checked!r}\n"
             "for _spectrum_stdin, _spectrum_expected in _spectrum_cases:\n"
             "    _spectrum_actual = solve(_spectrum_stdin)\n"
             "    assert isinstance(_spectrum_actual, str), 'solve must return str'\n"
             "    assert _spectrum_actual.split() == _spectrum_expected.split()\n")
    return {"task_id": task_id, "prompt": prompt, "original_prompt": question,
            "tests": tests, "entry_point": "solve", "source": source, "split": "eval",
            "original_split": "test", "evaluation_backend": "builtin",
            "prompt_protocol": "stdin-string-function-v1",
            "evaluation_protocol": "adapted-all-tests-whitespace-token-exact-v1",
            "test_count": len(checked), **metadata}


def _function_task(task_id: str, question: str, starter: str, function: str,
                   cases: Sequence[tuple[list[Any], Any]], *, source: str,
                   metadata: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(function, str) or not function.isidentifier():
        raise ValueError(f"{task_id}: invalid callable name {function!r}")
    if not cases:
        raise ValueError(f"{task_id}: no verification tests")
    if any(not isinstance(args, list) for args, _ in cases):
        raise ValueError(f"{task_id}: function test input must be an argument list")
    # The interface comes from the published starter, never from solutions.
    class_style = bool(re.search(r"(?m)^\s*class\s+Solution\b", starter))
    interface = f"Solution().{function}" if class_style else function
    instruction = (f"Implement the Python callable {interface}. Preserve the published interface. "
                   "Return only the complete Python implementation and any required imports.")
    prompt = _text(question, where=f"{task_id} question") + "\n\n" + instruction
    if starter.strip():
        prompt += "\n\nPublished starter code:\n" + starter
    # JSON structural equality deliberately permits tuple/list representation
    # equivalence, but does not sort sequences or coerce values to strings.
    serialized = json.dumps(list(cases), ensure_ascii=False, allow_nan=False)
    tests = ("import json as _spectrum_json\n"
             f"_spectrum_cases = _spectrum_json.loads({serialized!r})\n"
             "for _spectrum_args, _spectrum_expected in _spectrum_cases:\n"
             f"    _spectrum_actual = {interface}(*_spectrum_args)\n"
             "    _spectrum_actual = _spectrum_json.loads(_spectrum_json.dumps(_spectrum_actual, allow_nan=False))\n"
             "    assert _spectrum_actual == _spectrum_expected\n")
    return {"task_id": task_id, "prompt": prompt, "original_prompt": question,
            "tests": tests, "entry_point": function, "source": source, "split": "eval",
            "original_split": "test", "evaluation_backend": "builtin",
            "prompt_protocol": "published-callable-interface-v1",
            "evaluation_protocol": "adapted-all-tests-json-structural-equality-v1",
            "test_count": len(cases), "callable_style": "Solution" if class_style else "function",
            **metadata}


def convert_apps(row: Mapping[str, Any], revision: str) -> dict[str, Any]:
    """Convert a selected APPS test row; preserve its callable/standard-I/O style."""
    identifier = row.get("problem_id", row.get("id"))
    if identifier is None:
        raise ValueError("APPS row lacks problem_id/id")
    task_id = f"AppsIntro/{identifier}"
    io_tests = _json(row.get("input_output"), where=f"{task_id} input_output")
    if not isinstance(io_tests, dict):
        raise ValueError(f"{task_id}: missing input_output tests")
    inputs, outputs = io_tests.get("inputs"), io_tests.get("outputs")
    if not isinstance(inputs, list) or not isinstance(outputs, list) or not inputs or len(inputs) != len(outputs):
        raise ValueError(f"{task_id}: missing or unmatched input/output tests")
    metadata = {"revision": revision, "difficulty": row.get("difficulty"),
                "source_url": row.get("url", ""), "original_task_id": identifier}
    function = io_tests.get("fn_name")
    cases = list(zip(inputs, outputs))
    if function:
        return _function_task(task_id, row["question"], row.get("starter_code", ""),
                              function, cases, source=HF_REPOSITORIES["apps_intro"], metadata=metadata)
    return _stdin_task(task_id, row["question"], cases,
                       source=HF_REPOSITORIES["apps_intro"], metadata=metadata)


def _contest_cases(value: Any, task_id: str, name: str) -> list[tuple[str, str]]:
    """Support HF's struct-of-lists and list-of-structs representations."""
    if isinstance(value, Mapping):
        inputs, outputs = value.get("input"), value.get("output")
        if not isinstance(inputs, list) or not isinstance(outputs, list) or len(inputs) != len(outputs):
            raise ValueError(f"{task_id}: malformed {name}")
        return list(zip(inputs, outputs))
    if isinstance(value, list):
        if any(not isinstance(case, Mapping) or not {"input", "output"}.issubset(case) for case in value):
            raise ValueError(f"{task_id}: malformed {name}")
        return [(case["input"], case["output"]) for case in value]
    raise ValueError(f"{task_id}: missing {name}")


def convert_codecontests(row: Mapping[str, Any], revision: str) -> dict[str, Any]:
    name = _text(row.get("name"), where="CodeContests name")
    task_id = "CodeContests/" + hashlib.sha256(name.encode()).hexdigest()[:20]
    cases, counts = [], {}
    for field in ("public_tests", "private_tests", "generated_tests"):
        group = _contest_cases(row.get(field), task_id, field)
        cases.extend(group)
        counts[field] = len(group)
    return _stdin_task(task_id, row["description"], cases,
        source=HF_REPOSITORIES["codecontests"], metadata={
            "revision": revision, "original_task_id": name, "difficulty": row.get("difficulty"),
            "source_problem": row.get("source"), "test_group_counts": counts,
            "original_input_file": row.get("input_file", ""),
            "original_output_file": row.get("output_file", "")})


class _PrimitiveUnpickler(pickle.Unpickler):
    """LCB serializes JSON strings; no class resolution or code execution needed."""
    def find_class(self, module, name):
        raise ValueError("LiveCodeBench fixture contains a forbidden pickle global")

    def persistent_load(self, pid):
        raise ValueError("LiveCodeBench fixture contains a forbidden persistent object")


def _private_lcb_tests(value: Any, task_id: str) -> list[dict[str, Any]]:
    if isinstance(value, list):
        return value
    try:
        decoded = _json(value, where=f"{task_id} private tests")
    except ValueError:
        if not isinstance(value, str):
            raise
        try:
            compressed = base64.b64decode(value, validate=True)
            decompressor = zlib.decompressobj()
            packed = decompressor.decompress(compressed, 64 * 1024 * 1024)
            if not decompressor.eof or decompressor.unconsumed_tail:
                raise ValueError("Decoded test fixture exceeds 64 MiB or is truncated")
            unpacked = _PrimitiveUnpickler(io.BytesIO(packed)).load()
            if not isinstance(unpacked, (str, bytes)):
                raise ValueError("Expected a serialized JSON string")
            decoded = json.loads(unpacked)
        except Exception as error:
            raise ValueError(f"{task_id}: cannot decode official private-test fixture") from error
    if not isinstance(decoded, list):
        raise ValueError(f"{task_id}: private tests must decode to a list")
    return decoded


def convert_livecodebench(row: Mapping[str, Any], revision: str, release: str) -> dict[str, Any]:
    question_id = _text(row.get("question_id"), where="LiveCodeBench question_id")
    platform = _text(row.get("platform"), where="LiveCodeBench platform")
    task_id = f"LiveCodeBench/{platform}/{question_id}"
    public = _json(row.get("public_test_cases"), where=f"{task_id} public tests")
    private = _private_lcb_tests(row.get("private_test_cases"), task_id)
    metadata = _json(row.get("metadata"), where=f"{task_id} metadata")
    if not isinstance(public, list) or not isinstance(metadata, dict):
        raise ValueError(f"{task_id}: malformed test/metadata structure")
    tests = public + private
    if not tests or any(not isinstance(t, dict) or not {"input", "output", "testtype"}.issubset(t) for t in tests):
        raise ValueError(f"{task_id}: missing or malformed tests")
    styles = {t["testtype"] for t in tests}
    if len(styles) != 1 or not styles.issubset({"stdin", "functional"}):
        raise ValueError(f"{task_id}: unsupported mixed test types {styles}")
    info = {"revision": revision, "release": release, "original_task_id": question_id,
            "platform": platform, "contest_date": row.get("contest_date"),
            "difficulty": row.get("difficulty"),
            "test_group_counts": {"public": len(public), "private": len(private)}}
    if styles == {"stdin"}:
        return _stdin_task(task_id, row["question_content"], [(t["input"], t["output"]) for t in tests],
                           source=HF_REPOSITORIES["livecodebench"], metadata=info)
    # Official functional fixture format: one JSON argument per input line.
    cases = []
    for test in tests:
        if not isinstance(test["input"], str) or not isinstance(test["output"], str):
            raise ValueError(f"{task_id}: functional fixtures must contain JSON text")
        args = [json.loads(line) for line in test["input"].splitlines() if line.strip()]
        cases.append((args, json.loads(test["output"])))
    return _function_task(task_id, row["question_content"], row.get("starter_code", ""),
        metadata.get("func_name"), cases, source=HF_REPOSITORIES["livecodebench"], metadata=info)


def _humanevalplus() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    if os.environ.get("HUMANEVAL_OVERRIDE_PATH"):
        raise ValueError("Unset HUMANEVAL_OVERRIDE_PATH for the official pinned HumanEval+ benchmark")
    if package_version("evalplus") != EVALPLUS_VERSION:
        raise ValueError(f"HumanEval+ preparation requires evalplus=={EVALPLUS_VERSION}")
    from evalplus.data import get_human_eval_plus
    from evalplus.data.humaneval import HUMANEVAL_PLUS_VERSION
    from evalplus.data.utils import get_dataset_metadata
    if HUMANEVAL_PLUS_VERSION != HUMANEVAL_RELEASE:
        raise ValueError("Installed EvalPlus has a different HumanEval+ fixture release")
    problems = get_human_eval_plus()
    if len(problems) != 164:
        raise ValueError(f"Expected all 164 HumanEval+ tasks, found {len(problems)}")
    _, fixture = get_dataset_metadata("HumanEvalPlus", HUMANEVAL_RELEASE, False, False)
    digest = _sha(fixture)
    rows = []
    for task_id, task in sorted(problems.items()):
        rows.append({"task_id": task_id, "prompt": task["prompt"],
            "original_prompt": task["prompt"], "entry_point": task["entry_point"],
            "source": "evalplus/HumanEvalPlus", "split": "eval", "original_split": "test",
            "completion_mode": "continuation", "code_prefix": task["prompt"],
            "revision": HUMANEVAL_RELEASE, "dataset_sha256": digest,
            "prompt_protocol": "evalplus-original-0.3.1", "evaluation_backend": "evalplus",
            "evaluation_protocol": "official-base-and-plus-tests-no-sanitization"})
    return rows, {"evalplus_version": EVALPLUS_VERSION, "release": HUMANEVAL_RELEASE,
                  "dataset_sha256": digest, "task_count": len(rows)}


def _exclusion_index(paths: Sequence[str | Path]) -> tuple[dict[str, list[str]], list[dict[str, str]]]:
    fingerprints: dict[str, list[str]] = {}
    files = []
    for raw_path in paths:
        path = Path(raw_path)
        files.append({"path": str(path.resolve()), "sha256": _sha(path)})
        for task in read_jsonl(path):
            if task.get("split") not in {"train", "calibration", "validation"}:
                raise ValueError(f"Exclusions must be training/calibration/validation data: {path}")
            for field in ("prompt", "original_prompt"):
                if task.get(field):
                    fingerprint = prompt_fingerprint(task[field])
                    fingerprints.setdefault(fingerprint, []).append(task["task_id"])
    return fingerprints, files


def prepare_benchmark(name: str, output_dir: str | Path, *, revision: str | None = None,
                      seed: int = 42, calibration_size: int = 50, validation_size: int = 30,
                      limit: int | None = None, lcb_release: str = "release_v5",
                      exclusions_from: Sequence[str | Path] = ()) -> dict[str, Any]:
    """Prepare and pin one benchmark, writing eval.jsonl and manifest.json.

    Existing directories are reused only when the complete configuration and
    checksums match. To refresh an upstream source, choose a new output directory.
    ``limit`` selects a seeded, model-independent subset of transfer benchmarks;
    it is intentionally prohibited for the two original MBPP/HumanEval+ test sets.
    """
    if name not in BENCHMARKS:
        raise ValueError(f"Unknown benchmark {name!r}; choose from {BENCHMARKS}")
    if type(seed) is not int or (limit is not None and (type(limit) is not int or limit < 1)):
        raise ValueError("seed must be an integer; limit must be a positive integer or None")
    if name in {"mbpp", "humanevalplus"} and limit is not None:
        raise ValueError(f"{name}: preserve the complete official test split; do not pass limit")
    output = Path(output_dir)
    fingerprint_index, excluded_files = _exclusion_index(exclusions_from)
    request = {"name": name, "requested_revision": revision, "seed": seed,
        "calibration_size": calibration_size, "validation_size": validation_size,
        "limit": limit, "lcb_release": lcb_release, "exclusions_from": excluded_files,
        "preparation_protocol": PREPARATION_PROTOCOL}
    previous = output / "manifest.json"
    if previous.is_file():
        manifest = json.loads(previous.read_text())
        if manifest.get("request") != request:
            raise ValueError(f"Preparation settings changed: use a new directory instead of {output}")
        for file, info in manifest["output_files"].items():
            if not (output / file).is_file() or _sha(output / file) != info["sha256"]:
                raise ValueError(f"Prepared benchmark changed or incomplete: {output / file}")
        return manifest
    if output.exists() and any(output.iterdir()):
        raise ValueError(f"Unmanifested files exist in {output}; use a new preparation directory")
    resolved = None if name == "humanevalplus" else _hf_revision(HF_REPOSITORIES[name], revision)
    exclusions: list[dict[str, Any]] = []
    source_metadata: dict[str, Any] = {}
    if name == "mbpp":
        splits = prepare_mbpp(output, seed, calibration_size, validation_size, resolved)
        source_count = sum(len(value) for value in splits.values())
        source_metadata = read_jsonl(output / "preparation_manifest.jsonl")[0]
    elif name == "humanevalplus":
        if revision not in (None, HUMANEVAL_RELEASE):
            raise ValueError(f"HumanEval+ uses the fixed release {HUMANEVAL_RELEASE}")
        rows, source_metadata = _humanevalplus()
        source_count = len(rows)
        splits = {"eval": rows}
    elif name == "apps_intro":
        raw, source_metadata = _download_jsonl(HF_REPOSITORIES[name], resolved, ["test.jsonl"])
        source_count = len(raw)
        rows = []
        for record in raw:
            if record.get("difficulty") != "introductory":
                exclusions.append({"original_task_id": record.get("problem_id", record.get("id")),
                                   "reason": "predeclared_introductory_difficulty_only"})
            else:
                rows.append(convert_apps(record, resolved))
        splits = {"eval": rows}
    elif name == "codecontests":
        from datasets import load_dataset
        raw = load_dataset(HF_REPOSITORIES[name], split="test", revision=resolved)
        source_count = len(raw)
        source_metadata = {"dataset_fingerprint": getattr(raw, "_fingerprint", None)}
        splits = {"eval": [convert_codecontests(row, resolved) for row in raw]}
    else:
        if not re.fullmatch(r"release_v[1-6]", lcb_release):
            raise ValueError("Pin an explicit supported LiveCodeBench release_v1 through release_v6")
        count = int(lcb_release.removeprefix("release_v"))
        filenames = ["test.jsonl"] + [f"test{i}.jsonl" for i in range(2, count + 1)]
        raw, source_metadata = _download_jsonl(HF_REPOSITORIES[name], resolved, filenames)
        source_count = len(raw)
        splits = {"eval": [convert_livecodebench(row, resolved, lcb_release) for row in raw]}
    # Never put target evaluation solutions in calibration/training records.
    eval_rows = sorted(validate_tasks(splits["eval"]), key=lambda row: row["task_id"])
    clean = []
    for row in eval_rows:
        matches = set()
        for field in ("prompt", "original_prompt"):
            if row.get(field):
                matches.update(fingerprint_index.get(prompt_fingerprint(row[field]), ()))
        if matches:
            if name in {"mbpp", "humanevalplus"}:
                raise ValueError(f"Official evaluation task overlaps training inputs: {row['task_id']}; "
                                 "decontaminate training before fitting models")
            exclusions.append({"task_id": row["task_id"], "reason": "exact_normalized_training_prompt_overlap",
                               "matching_task_ids": sorted(matches)})
        else:
            clean.append(row)
    eligible_count = len(clean)
    if limit is not None and len(clean) > limit:
        random.Random(seed).shuffle(clean)
        selected, remainder = clean[:limit], clean[limit:]
        exclusions.extend({"task_id": row["task_id"], "reason": "predeclared_seeded_task_limit"} for row in remainder)
        clean = sorted(selected, key=lambda row: row["task_id"])
    if not clean:
        raise ValueError(f"{name}: no eligible evaluation tasks; no empty benchmark will be written")
    splits["eval"] = clean
    assert_disjoint_splits(splits)
    output_files = {}
    for split, rows in splits.items():
        path = output / f"{split}.jsonl"
        write_jsonl(path, rows)
        output_files[path.name] = {"sha256": _sha(path), "count": len(rows), "bytes": path.stat().st_size}
    if (output / "preparation_manifest.jsonl").is_file():
        path = output / "preparation_manifest.jsonl"
        output_files[path.name] = {"sha256": _sha(path), "count": 1, "bytes": path.stat().st_size}
    if name == "humanevalplus":
        path = output / "dataset_metadata.json"
        atomic_json(path, {"evalplus_version": EVALPLUS_VERSION, "datasets": {"HumanEvalPlus": {
            "version": HUMANEVAL_RELEASE, "task_count": len(clean),
            "sha256": source_metadata["dataset_sha256"]}}})
        output_files[path.name] = {"sha256": _sha(path), "count": 1, "bytes": path.stat().st_size}
    manifest = {"name": name, "request": request, "revision": resolved,
        "source_metadata": source_metadata, "source_count": source_count,
        "eligible_count_before_limit": eligible_count, "exclusions": exclusions,
        "exclusion_counts": dict(Counter(row["reason"] for row in exclusions)),
        "output_files": output_files, "output_task_ids": {key: [r["task_id"] for r in val] for key, val in splits.items()},
        "evaluation_backend": "evalplus" if name == "humanevalplus" else "builtin",
        "evaluation_protocols": sorted({row.get("evaluation_protocol", "mbpp-original-tests") for row in clean}),
        "training_allowed": name == "mbpp", "data_only_preparation": True,
        "reference_program_execution": False, "request_sha256": stable_hash(request)}
    atomic_json(previous, manifest)
    return manifest


def make_humanevalplus_evaluator(tasks_path: str | Path, settings: Mapping[str, Any] | None = None):
    """Return the official EvalPlus callback and its immutable evaluator identity.

    The callback plugs directly into ``longitudinal.evaluate_checkpoints``.
    Defaults to the existing bounded Docker bridge. The explicitly enabled
    local fallback retains its ``local-unsafe`` label in all output provenance.
    """
    from .formal_transfer import (_attempt, _evaluate_output, _image_identity,
        _local_runtime_manifest, _validate_dataset, _wrapper)
    from .metrics import summarize_records
    from .verification import export_evalplus, import_evalplus_results

    path = Path(tasks_path)
    tasks = read_jsonl(path)
    metadata_path = path.parent / "dataset_metadata.json"
    metadata = json.loads(metadata_path.read_text())
    release = _validate_dataset(tasks, metadata)
    evaluator_settings = dict(settings or {})
    backend = evaluator_settings.get("backend", "docker")
    if backend == "docker":
        evaluator_settings["image_identity"] = _image_identity(
            evaluator_settings.get("image", "improving-evalplus:0.3.1"))
    elif backend == "local":
        if not evaluator_settings.get("allow_unsafe_local", False):
            raise ValueError("Local EvalPlus requires explicit allow_unsafe_local=True")
        evaluator_settings["runtime_identity"] = _local_runtime_manifest()
        evaluator_settings["image_identity"] = "local-unsafe:" + stable_hash(evaluator_settings["runtime_identity"])
    else:
        raise ValueError("Official EvalPlus backend must be docker or explicitly enabled local")
    prepared_tasks_hash = stable_hash(tasks)
    repo = Path(__file__).resolve().parents[2]
    identity = {"backend": "official-evalplus", "package_version": EVALPLUS_VERSION,
        "release": release, "tasks_sha256": _sha(path), "metadata_sha256": _sha(metadata_path),
        "settings": evaluator_settings,
        "wrapper_sha256": _sha(repo / "scripts" / "evalplus_docker.sh"),
        "bridge_sha256": _sha(Path(__file__).with_name("formal_transfer.py"))}

    def evaluate(task_rows, records, output_path, evaluation_settings, *, expected_samples, seed=42):
        task_rows, records = list(task_rows), list(records)
        if stable_hash(task_rows) != prepared_tasks_hash:
            raise ValueError("HumanEval+ evaluation tasks differ from the prepared official snapshot")
        counts = Counter(row["task_id"] for row in records)
        if counts != Counter({task["task_id"]: expected_samples for task in task_rows}):
            raise ValueError("HumanEval+ requires every prepared task and every requested sample")
        output_path = Path(output_path)
        export_path = output_path.with_suffix(".evalplus.jsonl")
        manifest_path = export_evalplus(task_rows, records, export_path,
            code_extraction=evaluation_settings.get("code_extraction", "first_fence"))
        official_output = _attempt(output_path.with_suffix(".evalplus"))
        try:
            _wrapper("evaluate", official_output, evaluator_settings, export_path)
            official = _evaluate_output(official_output, export_path, {"release": release},
                                       len(task_rows), len(records), backend=backend)
            verified = import_evalplus_results(records, official_output / "samples_eval_results.json",
                tasks=task_rows, require_plus=True, manifest_path=manifest_path)
            write_jsonl(output_path.with_suffix(".verified.jsonl"), verified)
            summary = summarize_records(verified,
                ks=evaluation_settings.get("ks", [1, 4, 8, 16, 32, 64]),
                correct_budget=evaluation_settings.get("correct_budget", 4),
                correct_budgets=evaluation_settings.get("correct_budgets", [2, 4, 8, 16]),
                bootstrap_samples=evaluation_settings.get("bootstrap_samples", 2000), seed=seed,
                expected_samples={task["task_id"]: expected_samples for task in task_rows})
            summary["evaluation"] = {**official, "evaluator_identity": identity,
                "code_extraction": evaluation_settings.get("code_extraction", "first_fence"),
                "official_output": str(official_output.resolve())}
            atomic_json(output_path.with_suffix(".metrics.json"), summary)
            return summary
        except BaseException as error:
            atomic_json(official_output / "failed.json", {"type": type(error).__name__,
                "message": str(error), "evaluator_identity": identity})
            raise
    return evaluate, identity
