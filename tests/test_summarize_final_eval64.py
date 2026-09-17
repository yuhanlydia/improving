import importlib.util
from pathlib import Path


def _load_script():
    path = Path(__file__).parents[1] / "scripts" / "summarize_final_eval64.py"
    spec = importlib.util.spec_from_file_location("summarize_final_eval64", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_expected_samples_accepts_uniform_per_task_mapping():
    module = _load_script()
    matches = getattr(module, "_expected_samples_match", lambda *_: False)

    assert matches({"Mbpp/11": 64, "Mbpp/12": 64}, 64)


def test_expected_samples_rejects_nonuniform_per_task_mapping():
    module = _load_script()
    matches = getattr(module, "_expected_samples_match", lambda *_: True)

    assert not matches({"Mbpp/11": 64, "Mbpp/12": 63}, 64)
