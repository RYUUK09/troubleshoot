"""Unit tests verifying circular dependency prevention and cycle detection."""

import pytest
import tempfile
import json
from pathlib import Path

from src.knowledge_base import KnowledgeBase
from src.inference_engine import BackwardChainingEngine
from config import STATUS_NO_MATCH, STATUS_POSSIBLE


def test_indirect_circular_dependency_handling():
    """
    Creates an indirect cycle:
    Intermediate Rule 1: A -> B
    Intermediate Rule 2: B -> C
    Intermediate Rule 3: C -> A
    Diagnostic Rule: requires C -> Diagnosis 'Infinite Cycle Fault'
    Verifies that the inference engine catches the cycle, aborts recursion, and logs cycle warning.
    """
    cyclic_rules = [
        {
            "rule_id": "R-CYCLE-01",
            "domain": "Network Troubleshooting",
            "intermediate_fact": "fact_b",
            "diagnosis": None,
            "conditions": [
                {"fact": "fact_a", "expected_value": "YES", "description": "A", "is_intermediate": True}
            ],
            "explanation": "Derives B from A",
            "solution": "N/A",
            "approval_status": "APPROVED",
            "author": "Cycle Test"
        },
        {
            "rule_id": "R-CYCLE-02",
            "domain": "Network Troubleshooting",
            "intermediate_fact": "fact_c",
            "diagnosis": None,
            "conditions": [
                {"fact": "fact_b", "expected_value": "YES", "description": "B", "is_intermediate": True}
            ],
            "explanation": "Derives C from B",
            "solution": "N/A",
            "approval_status": "APPROVED",
            "author": "Cycle Test"
        },
        {
            "rule_id": "R-CYCLE-03",
            "domain": "Network Troubleshooting",
            "intermediate_fact": "fact_a",
            "diagnosis": None,
            "conditions": [
                {"fact": "fact_c", "expected_value": "YES", "description": "C", "is_intermediate": True}
            ],
            "explanation": "Derives A from C (Closes Cycle)",
            "solution": "N/A",
            "approval_status": "APPROVED",
            "author": "Cycle Test"
        },
        {
            "rule_id": "R-CYCLE-DIAG",
            "domain": "Network Troubleshooting",
            "intermediate_fact": None,
            "diagnosis": "Infinite Cycle Fault",
            "conditions": [
                {"fact": "fact_c", "expected_value": "YES", "description": "C", "is_intermediate": True}
            ],
            "explanation": "Diagnostic rule needing cyclic fact C",
            "solution": "Fix loop",
            "approval_status": "APPROVED",
            "author": "Cycle Test"
        }
    ]

    with tempfile.TemporaryDirectory() as tmpdir:
        kb_path = Path(tmpdir) / "cycle_kb.json"
        with open(kb_path, "w", encoding="utf-8") as f:
            json.dump({"version": "1.0.0", "rules": cyclic_rules}, f, indent=2)

        kb = KnowledgeBase(kb_path)
        engine = BackwardChainingEngine(kb)

        # Trigger diagnosis: should NOT throw RecursionError
        result = engine.diagnose_domain("Network Troubleshooting", {})

        assert result is not None
        # Check that CYCLE DETECTED was recorded in the reasoning trace
        trace_str = " ".join(result.full_trace)
        assert "CYCLE DETECTED" in trace_str
        assert "Circular dependency encountered" in trace_str
