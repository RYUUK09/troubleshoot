"""Unit tests for the Evaluation Benchmark framework."""

import pytest
import tempfile
from pathlib import Path

from src.evaluation_engine import EvaluationBenchmarkEngine
from config import BASELINE_KB_PATH, ACTIVE_KB_PATH


def test_testset_loading():
    """Verifies test dataset contains at least 20 test cases across domains."""
    eval_engine = EvaluationBenchmarkEngine()
    assert len(eval_engine.test_cases) >= 20


def test_real_accuracy_calculation(baseline_kb):
    """
    Runs evaluation over the authentic test dataset,
    verifying accuracy is genuinely calculated without hardcoding.
    """
    eval_engine = EvaluationBenchmarkEngine()
    results = eval_engine.evaluate_kb(baseline_kb, label="Baseline Test Run")

    assert results["total_cases"] == len(eval_engine.test_cases)
    assert 0 <= results["correct_predictions"] <= results["total_cases"]

    expected_acc = round(results["correct_predictions"] / results["total_cases"] * 100.0, 2)
    assert results["accuracy"] == expected_acc

    # Verify domain breakdown is populated
    for domain, stats in results["domain_stats"].items():
        assert "accuracy" in stats
        assert stats["total"] > 0


def test_comparative_benchmark_execution():
    """Verifies comparative benchmark runs on both Baseline and Updated KBs and calculates delta."""
    eval_engine = EvaluationBenchmarkEngine()
    summary = eval_engine.run_comparative_benchmark()

    assert "baseline" in summary
    assert "updated" in summary
    assert "accuracy_delta" in summary
    assert summary["baseline"]["total"] == summary["updated"]["total"]


def test_evaluation_history_persistence():
    """Verifies that evaluation runs are properly recorded to history."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_hist = Path(tmpdir) / "eval_hist.json"
        engine = EvaluationBenchmarkEngine(history_path=tmp_hist)

        sample_summary = {
            "timestamp": "2026-10-31 12:00:00",
            "baseline": {"accuracy": 88.5},
            "updated": {"accuracy": 96.2},
            "accuracy_delta": 7.7,
            "total_test_cases": 26,
            "newly_resolved_count": 2
        }

        engine.save_benchmark_history(sample_summary)
        history = engine.load_benchmark_history()

        assert len(history) == 1
        assert history[0]["baseline_accuracy"] == 88.5
        assert history[0]["accuracy_delta"] == 7.7
