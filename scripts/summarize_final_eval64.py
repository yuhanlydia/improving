#!/usr/bin/env python3
"""Build compact tables and paired comparisons for final 64-sample checkpoints."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from improving.metrics import compare_summaries


MODELS = ("base", "plain", "spd_hard", "spectral_soft")
KS = (1, 4, 8, 16, 64)
CORRECT_BUDGETS = (4, 8, 16, 64)


def _metric_cell(metric):
    if metric["mean"] is None:
        return "unavailable"
    ci = metric["ci95"]
    interval = "" if ci is None else f" [{ci[0]:.3f}, {ci[1]:.3f}]"
    return f"{metric['mean']:.3f}{interval}; {metric['eligible_tasks']}/{metric['total_tasks']} tasks"


def _expected_samples_match(expected_samples, sample_count):
    """Accept scalar protocols and per-task protocols with a uniform count."""
    if isinstance(expected_samples, dict):
        return bool(expected_samples) and all(value == sample_count for value in expected_samples.values())
    return expected_samples == sample_count


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("run_dir", type=Path)
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    source = args.run_dir / "supplemental_eval64"
    output = args.output_dir or source
    output.mkdir(parents=True, exist_ok=True)

    summaries = {}
    for model in MODELS:
        path = source / model / "evaluation.metrics.json"
        if not path.exists():
            raise FileNotFoundError(f"Missing completed metrics: {path}")
        summary = json.loads(path.read_text())
        protocol = summary["protocol"]
        if not _expected_samples_match(protocol["expected_samples"], 64) or protocol["ks"] != list(KS):
            raise ValueError(f"Unexpected 64-sample protocol for {model}: {protocol}")
        if protocol["correct_budgets"] != list(CORRECT_BUDGETS):
            raise ValueError(f"Unexpected correct budgets for {model}: {protocol['correct_budgets']}")
        summaries[model] = summary

    rows = []
    for model, summary in summaries.items():
        aggregate = summary["aggregate"]
        row = {"model": model, "tasks": aggregate["task_count"],
               "samples": aggregate["sample_count"], "correct": aggregate["correct_count"]}
        for k in KS:
            for prefix, metric in (
                ("pass", aggregate["pass_at_k"][str(k)]),
                ("implementation_coverage", aggregate["implementation_proxy"]["coverage_at_k"][str(k)]),
            ):
                row[f"{prefix}_at_{k}"] = metric["mean"]
                row[f"{prefix}_at_{k}_ci_low"] = metric["ci95"][0]
                row[f"{prefix}_at_{k}_ci_high"] = metric["ci95"][1]
        matched = aggregate["implementation_proxy"]["correct_matched_coverage_at_budgets"]
        for budget in CORRECT_BUDGETS:
            metric = matched[str(budget)]
            row[f"correct_matched_coverage_at_{budget}"] = metric["mean"]
            row[f"correct_matched_coverage_at_{budget}_eligible_tasks"] = metric["eligible_tasks"]
        rows.append(row)
    with (output / "summary.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    pairs = (("base", "plain"), ("base", "spd_hard"), ("base", "spectral_soft"),
             ("plain", "spectral_soft"), ("spd_hard", "spectral_soft"))
    comparisons = {
        f"{candidate}_minus_{reference}": compare_summaries(
            summaries[reference], summaries[candidate], correctness_margin=.01,
            bootstrap_samples=2000, seed=43)
        for reference, candidate in pairs
    }
    (output / "comparisons.json").write_text(json.dumps(comparisons, indent=2) + "\n")

    lines = ["# Final-checkpoint 64-sample MBPP evaluation", "",
             "All rows use 500 held-out MBPP tasks and 64 samples per task.", "",
             "## Pass@k", "",
             "| Model | " + " | ".join(f"pass@{k}" for k in KS) + " |",
             "| --- | " + " | ".join("---:" for _ in KS) + " |"]
    for model, summary in summaries.items():
        metrics = summary["aggregate"]["pass_at_k"]
        lines.append("| " + model + " | " + " | ".join(_metric_cell(metrics[str(k)]) for k in KS) + " |")
    lines += ["", "## Correct implementation coverage at total draw budget k", "",
              "Wrong samples remain in the draw population; all 500 tasks are included.", "",
              "| Model | " + " | ".join(f"coverage@{k}" for k in KS) + " |",
              "| --- | " + " | ".join("---:" for _ in KS) + " |"]
    for model, summary in summaries.items():
        metrics = summary["aggregate"]["implementation_proxy"]["coverage_at_k"]
        lines.append("| " + model + " | " + " | ".join(_metric_cell(metrics[str(k)]) for k in KS) + " |")
    lines += ["", "## Coverage at a fixed number of correct samples", "",
              "These estimates are conditional. Eligibility requires at least the displayed number of correct samples.", "",
              "| Model | " + " | ".join(f"correct coverage@{k}" for k in CORRECT_BUDGETS) + " |",
              "| --- | " + " | ".join("---:" for _ in CORRECT_BUDGETS) + " |"]
    for model, summary in summaries.items():
        metrics = summary["aggregate"]["implementation_proxy"]["correct_matched_coverage_at_budgets"]
        lines.append("| " + model + " | " + " | ".join(_metric_cell(metrics[str(k)]) for k in CORRECT_BUDGETS) + " |")
    lines += ["", "AST fingerprints are implementation proxies, not independently annotated algorithms.", ""]
    (output / "REPORT.md").write_text("\n".join(lines))
    print(json.dumps({"status": "complete", "models": list(MODELS), "output": str(output)}, indent=2))


if __name__ == "__main__":
    main()
