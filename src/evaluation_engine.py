"""Evaluation and benchmark module to run authentic diagnostic test suites,
measure true accuracy, compare baseline vs updated knowledge bases, and log history.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

from config import (
    BASELINE_KB_PATH,
    ACTIVE_KB_PATH,
    TEST_DATASET_PATH,
    EVALUATION_HISTORY_PATH,
    DOMAINS,
    STATUS_CONFIRMED,
    STATUS_POSSIBLE,
)
from src.knowledge_base import KnowledgeBase
from src.inference_engine import BackwardChainingEngine


class EvaluationBenchmarkEngine:
    """Runs rigorous diagnostic evaluation against a designated test dataset."""

    def __init__(
        self,
        testset_path: Optional[Path] = None,
        history_path: Optional[Path] = None
    ):
        self.testset_path = testset_path or TEST_DATASET_PATH
        self.history_path = history_path or EVALUATION_HISTORY_PATH
        self.test_cases: List[Dict[str, Any]] = []
        self.load_testset()

    def load_testset(self) -> None:
        """Loads test cases from JSON test dataset file."""
        if not self.testset_path.exists():
            self.test_cases = []
            return
        with open(self.testset_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            self.test_cases = data.get("test_cases", [])

    def evaluate_kb(
        self,
        kb: KnowledgeBase,
        label: str = "Evaluation Run",
        domain_filter: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Executes all test cases against the provided KnowledgeBase.
        Calculates true accuracy without hardcoding or simulation.
        """
        engine = BackwardChainingEngine(kb)
        cases_to_run = self.test_cases
        if domain_filter and domain_filter != "All Domains":
            cases_to_run = [c for c in cases_to_run if c["domain"] == domain_filter]

        detailed_results = []
        domain_stats = {
            d: {"total": 0, "correct": 0, "accuracy": 0.0}
            for d in DOMAINS
        }
        category_stats: Dict[str, Dict[str, Any]] = {}

        total_correct = 0

        for case in cases_to_run:
            case_id = case["test_id"]
            domain = case["domain"]
            case_name = case["name"]
            facts = case["facts"]
            expected = case["expected_diagnosis"]
            category = case.get("category", "General")

            # Run backward chaining diagnosis
            res = engine.diagnose_domain(domain, facts)

            # Determine predicted diagnosis
            predicted = "NO_MATCH"
            if res.confirmed_hypotheses:
                predicted = res.confirmed_hypotheses[0].diagnosis
            elif res.possible_hypotheses:
                predicted = res.possible_hypotheses[0].diagnosis
            else:
                predicted = res.primary_diagnosis or "NO_MATCH"

            # Check match
            is_match = (predicted == expected)
            if is_match:
                total_correct += 1

            # Update stats
            if domain in domain_stats:
                domain_stats[domain]["total"] += 1
                if is_match:
                    domain_stats[domain]["correct"] += 1

            cat_entry = category_stats.setdefault(category, {"total": 0, "correct": 0})
            cat_entry["total"] += 1
            if is_match:
                cat_entry["correct"] += 1

            detailed_results.append({
                "test_id": case_id,
                "name": case_name,
                "domain": domain,
                "category": category,
                "expected": expected,
                "predicted": predicted,
                "status": res.status,
                "is_match": is_match,
                "coverage": (
                    res.confirmed_hypotheses[0].coverage_display
                    if res.confirmed_hypotheses
                    else (res.possible_hypotheses[0].coverage_display if res.possible_hypotheses else "0%")
                )
            })

        total_count = len(cases_to_run)
        overall_accuracy = (total_correct / total_count * 100.0) if total_count > 0 else 0.0

        # Compute domain percentages
        for d, s in domain_stats.items():
            s["accuracy"] = (s["correct"] / s["total"] * 100.0) if s["total"] > 0 else 0.0

        # Compute category percentages
        for cat, s in category_stats.items():
            s["accuracy"] = (s["correct"] / s["total"] * 100.0) if s["total"] > 0 else 0.0

        return {
            "label": label,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_cases": total_count,
            "correct_predictions": total_correct,
            "accuracy": round(overall_accuracy, 2),
            "domain_stats": domain_stats,
            "category_stats": category_stats,
            "detailed_results": detailed_results
        }

    def run_comparative_benchmark(self) -> Dict[str, Any]:
        """
        Runs identical evaluation across:
        1. Baseline Knowledge Base
        2. Updated Active Knowledge Base
        Produces side-by-side comparison, accuracy delta, and identified improvements.
        """
        # Load baseline KB
        baseline_kb = KnowledgeBase(BASELINE_KB_PATH)
        baseline_results = self.evaluate_kb(baseline_kb, label="Baseline KB")

        # Load updated active KB
        active_kb = KnowledgeBase(ACTIVE_KB_PATH)
        active_results = self.evaluate_kb(active_kb, label="Updated KB")

        # Compute newly resolved test cases
        baseline_map = {r["test_id"]: r["is_match"] for r in baseline_results["detailed_results"]}
        active_map = {r["test_id"]: r["is_match"] for r in active_results["detailed_results"]}

        newly_resolved_cases = []
        for case in active_results["detailed_results"]:
            cid = case["test_id"]
            if not baseline_map.get(cid, False) and active_map.get(cid, False):
                newly_resolved_cases.append(case)

        accuracy_delta = round(active_results["accuracy"] - baseline_results["accuracy"], 2)

        benchmark_summary = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_test_cases": len(self.test_cases),
            "baseline": {
                "accuracy": baseline_results["accuracy"],
                "correct": baseline_results["correct_predictions"],
                "total": baseline_results["total_cases"],
                "domain_stats": baseline_results["domain_stats"]
            },
            "updated": {
                "accuracy": active_results["accuracy"],
                "correct": active_results["correct_predictions"],
                "total": active_results["total_cases"],
                "domain_stats": active_results["domain_stats"]
            },
            "accuracy_delta": accuracy_delta,
            "newly_resolved_count": len(newly_resolved_cases),
            "newly_resolved_cases": newly_resolved_cases,
            "baseline_detailed": baseline_results["detailed_results"],
            "updated_detailed": active_results["detailed_results"]
        }

        # Save to history
        self.save_benchmark_history(benchmark_summary)

        return benchmark_summary

    def save_benchmark_history(self, summary: Dict[str, Any]) -> None:
        """Appends evaluation run summary to history JSON file."""
        history = self.load_benchmark_history()
        history_entry = {
            "timestamp": summary["timestamp"],
            "baseline_accuracy": summary["baseline"]["accuracy"],
            "updated_accuracy": summary["updated"]["accuracy"],
            "accuracy_delta": summary["accuracy_delta"],
            "total_test_cases": summary["total_test_cases"],
            "newly_resolved_count": summary["newly_resolved_count"]
        }
        history.append(history_entry)
        with open(self.history_path, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2)

    def load_benchmark_history(self) -> List[Dict[str, Any]]:
        """Reads historical evaluation runs from file."""
        if not self.history_path.exists():
            return []
        try:
            with open(self.history_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
