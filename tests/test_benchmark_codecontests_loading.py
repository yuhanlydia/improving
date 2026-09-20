from improving import benchmarks
from improving.data import read_jsonl


def test_codecontests_streams_only_pinned_test_split(tmp_path, monkeypatch):
    import datasets

    revision = "a" * 40
    record = {
        "name": "test-problem", "description": "Return the input.",
        "public_tests": {"input": ["one\n"], "output": ["one\n"]},
        "private_tests": {"input": ["two\n"], "output": ["two\n"]},
        "generated_tests": {"input": ["three\n"], "output": ["three\n"]},
    }

    def load_dataset(repository, *, split, revision, streaming=False):
        assert streaming, "Nonstreaming loading prepares unwanted train/validation shards"
        assert repository == "deepmind/code_contests"
        assert split == "test"
        assert revision == "a" * 40
        return iter([record])

    monkeypatch.setattr(datasets, "load_dataset", load_dataset)
    monkeypatch.setattr(benchmarks, "_hf_revision", lambda *args: revision)
    manifest = benchmarks.prepare_benchmark("codecontests", tmp_path)
    assert manifest["source_count"] == 1
    assert manifest["revision"] == revision
    assert manifest["source_metadata"]["split"] == "test"
    assert manifest["source_metadata"]["loading_mode"] == "streaming"
    assert read_jsonl(tmp_path / "eval.jsonl") == [benchmarks.convert_codecontests(record, revision)]
