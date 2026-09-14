from improving.cli import _parser


def test_verify_cli_accepts_explicit_code_extraction_protocol():
    args = _parser().parse_args([
        "verify", "--tasks", "tasks.jsonl", "--samples", "samples.jsonl",
        "--output", "verified.jsonl", "--code-extraction", "first_fence",
    ])
    assert args.code_extraction == "first_fence"


def test_metrics_cli_accepts_multiple_correct_sample_budgets():
    args = _parser().parse_args([
        "metrics", "--tasks", "tasks.jsonl", "--samples", "verified.jsonl",
        "--output", "metrics.json", "--expected-samples", "64",
        "--correct-budgets", "2,4,8",
    ])
    assert args.correct_budgets == "2,4,8"
