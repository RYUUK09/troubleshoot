"""Unit tests for uncertainty handling, skip responses, and conflict detection."""

import pytest
from src.inference_engine import BackwardChainingEngine
from src.conflict_detector import ConflictDetector
from config import (
    STATUS_CONFIRMED,
    STATUS_POSSIBLE,
    STATUS_RULED_OUT,
    STATUS_INSUFFICIENT_EVIDENCE,
    STATUS_CONFLICTING_EVIDENCE,
    FACT_UNKNOWN,
)


def test_skip_does_not_falsely_prove_or_eliminate(sample_toy_kb):
    """
    Verifies that answering 'Not Sure / Skip' (UNKNOWN) does NOT eliminate the hypothesis,
    nor does it falsely confirm it.
    """
    engine = BackwardChainingEngine(sample_toy_kb)
    user_facts = {
        "fact_a": "YES",
        "fact_b": "UNKNOWN",  # Skipped
        "fact_d": "YES"
    }

    result = engine.diagnose_domain("Network Troubleshooting", user_facts)

    # Status should be POSSIBLE or INSUFFICIENT_EVIDENCE, NOT CONFIRMED and NOT RULED_OUT
    assert result.status in (STATUS_POSSIBLE, STATUS_INSUFFICIENT_EVIDENCE)
    assert len(result.confirmed_hypotheses) == 0

    # Fault Alpha should still be in possible hypotheses because it has not been contradicted
    possible_diagnoses = [h.diagnosis for h in result.possible_hypotheses]
    assert "Fault Alpha" in possible_diagnoses


def test_ruled_out_hypotheses_capture(sample_toy_kb):
    """Verifies that ruled-out hypotheses record exact condition contradicted and user's answer."""
    engine = BackwardChainingEngine(sample_toy_kb)
    user_facts = {
        "fact_a": "YES",
        "fact_b": "YES",
        "fact_d": "YES"  # R-TOY-02 requires fact_d=NO
    }

    result = engine.diagnose_domain("Network Troubleshooting", user_facts)
    summary = ConflictDetector.get_ruled_out_summary(result)

    assert len(summary) >= 1
    beta_elim = next((item for item in summary if item["rule_id"] == "R-TOY-02"), None)
    assert beta_elim is not None
    assert beta_elim["diagnosis"] == "Fault Beta"
    assert beta_elim["condition_fact"] == "fact_d"
    assert beta_elim["expected_value"] == "NO"
    assert beta_elim["actual_value"] == "YES"
    assert "narrative" in beta_elim


def test_domain_level_contradiction_detection():
    """Tests domain sanity contradiction checks (e.g. Wi-Fi adapter OFF yet Wi-Fi link connected)."""
    from src.models import DiagnosisSessionResult

    session = DiagnosisSessionResult(
        domain="Network Troubleshooting",
        status=STATUS_POSSIBLE,
        user_facts={
            "wifi_adapter_enabled": "NO",
            "local_network_connected": "YES"
        }
    )

    analysis = ConflictDetector.analyze_domain_conflicts(session)
    assert analysis["has_conflicts"] is True
    assert any("Wi-Fi adapter is reported DISABLED" in c for c in analysis["conflicts"])
