"""Pytest configuration and shared fixtures for AI Troubleshooting Expert System tests."""

import pytest
import tempfile
import json
from pathlib import Path

from config import BASELINE_KB_PATH, TEST_DATASET_PATH, DOMAINS
from src.models import Rule, Condition
from src.knowledge_base import KnowledgeBase
from src.inference_engine import BackwardChainingEngine
from src.question_selector import MinSplitQuestionSelector
from src.expert_review import ExpertReviewManager
from src.evaluation_engine import EvaluationBenchmarkEngine
from src.history_manager import DiagnosisHistoryManager


@pytest.fixture
def baseline_kb():
    """Provides a fresh instance of KnowledgeBase loaded from baseline."""
    return KnowledgeBase(BASELINE_KB_PATH)


@pytest.fixture
def inference_engine(baseline_kb):
    """Provides an instance of BackwardChainingEngine."""
    return BackwardChainingEngine(baseline_kb)


@pytest.fixture
def question_selector(baseline_kb, inference_engine):
    """Provides an instance of MinSplitQuestionSelector."""
    return MinSplitQuestionSelector(baseline_kb, inference_engine)


@pytest.fixture
def temp_kb():
    """Creates an isolated temporary KnowledgeBase in a temporary directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir) / "kb.json"
        with open(BASELINE_KB_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        yield KnowledgeBase(tmp_path)


@pytest.fixture
def temp_expert_manager(temp_kb):
    """Creates an isolated ExpertReviewManager with a temp file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_proposals = Path(tmpdir) / "proposals.json"
        with open(tmp_proposals, "w", encoding="utf-8") as f:
            json.dump([], f)
        yield ExpertReviewManager(tmp_proposals)


@pytest.fixture
def temp_history_manager():
    """Creates an isolated DiagnosisHistoryManager with a temp file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_hist = Path(tmpdir) / "history.json"
        with open(tmp_hist, "w", encoding="utf-8") as f:
            json.dump([], f)
        yield DiagnosisHistoryManager(tmp_hist)


@pytest.fixture
def sample_toy_kb():
    """Creates a small toy KnowledgeBase for deterministic reasoning tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        kb_path = Path(tmpdir) / "toy_kb.json"
        rules = [
            # Intermediate rule: Fact C derives from A and B
            {
                "rule_id": "R-TOY-INT-1",
                "domain": "Network Troubleshooting",
                "intermediate_fact": "fact_c",
                "diagnosis": None,
                "conditions": [
                    {"fact": "fact_a", "expected_value": "YES", "description": "A is true", "is_intermediate": False},
                    {"fact": "fact_b", "expected_value": "YES", "description": "B is true", "is_intermediate": False}
                ],
                "explanation": "Fact C derived from A and B",
                "solution": "N/A",
                "approval_status": "APPROVED",
                "author": "Test Harness"
            },
            # Diagnosis 1: Requires fact_c (intermediate) and fact_d
            {
                "rule_id": "R-TOY-01",
                "domain": "Network Troubleshooting",
                "diagnosis": "Fault Alpha",
                "conditions": [
                    {"fact": "fact_c", "expected_value": "YES", "description": "C is true", "is_intermediate": True},
                    {"fact": "fact_d", "expected_value": "YES", "description": "D is true", "is_intermediate": False}
                ],
                "explanation": "Fault Alpha detected",
                "solution": "Fix Alpha",
                "approval_status": "APPROVED",
                "author": "Test Harness"
            },
            # Diagnosis 2: Competing hypothesis requiring fact_c and fact_d=NO
            {
                "rule_id": "R-TOY-02",
                "domain": "Network Troubleshooting",
                "diagnosis": "Fault Beta",
                "conditions": [
                    {"fact": "fact_c", "expected_value": "YES", "description": "C is true", "is_intermediate": True},
                    {"fact": "fact_d", "expected_value": "NO", "description": "D is false", "is_intermediate": False}
                ],
                "explanation": "Fault Beta detected",
                "solution": "Fix Beta",
                "approval_status": "APPROVED",
                "author": "Test Harness"
            }
        ]
        with open(kb_path, "w", encoding="utf-8") as f:
            json.dump({"version": "1.0.0", "rules": rules}, f, indent=2)
        yield KnowledgeBase(kb_path)
