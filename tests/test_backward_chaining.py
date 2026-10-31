"""Unit tests for multi-level backward chaining and intermediate fact derivation."""

import pytest
from src.inference_engine import BackwardChainingEngine
from config import (
    STATUS_CONFIRMED,
    STATUS_POSSIBLE,
    STATUS_RULED_OUT,
    STATUS_NO_MATCH,
    FACT_YES,
    FACT_NO,
)


def test_toy_backward_chaining_success(sample_toy_kb):
    """
    Tests derivation of Intermediate Fact C from A and B,
    which in turn allows backward chaining to confirm Fault Alpha.
    """
    engine = BackwardChainingEngine(sample_toy_kb)
    # Provide facts A=YES, B=YES, D=YES
    user_facts = {
        "fact_a": "YES",
        "fact_b": "YES",
        "fact_d": "YES"
    }

    result = engine.diagnose_domain("Network Troubleshooting", user_facts)

    assert result.status == STATUS_CONFIRMED
    assert result.primary_diagnosis == "Fault Alpha"
    assert len(result.confirmed_hypotheses) == 1
    assert result.confirmed_hypotheses[0].rule_id == "R-TOY-01"

    # Verify intermediate fact was derived
    assert "fact_c" in result.derived_facts
    assert result.derived_facts["fact_c"] == "YES"

    # Verify Fault Beta was ruled out because fact_d=YES, but R-TOY-02 requires fact_d=NO
    assert any(c.rule_id == "R-TOY-02" for c in result.ruled_out_hypotheses)


def test_toy_backward_chaining_intermediate_failure(sample_toy_kb):
    """Tests that if symptom B is NO, intermediate fact C is disproved, ruling out Fault Alpha."""
    engine = BackwardChainingEngine(sample_toy_kb)
    user_facts = {
        "fact_a": "YES",
        "fact_b": "NO",
        "fact_d": "YES"
    }

    result = engine.diagnose_domain("Network Troubleshooting", user_facts)

    # Both R-TOY-01 and R-TOY-02 depend on fact_c
    assert result.status == STATUS_NO_MATCH
    assert "fact_c" in result.derived_facts
    assert result.derived_facts["fact_c"] == "NO"


def test_evidence_coverage_calculation(sample_toy_kb):
    """
    Verifies that evidence coverage is calculated as satisfied_count / total_conditions,
    and is properly formatted as a percentage coverage rather than a probability.
    """
    engine = BackwardChainingEngine(sample_toy_kb)
    # Only supply fact_a=YES and fact_b=YES (deriving fact_c=YES), but fact_d is unknown
    user_facts = {
        "fact_a": "YES",
        "fact_b": "YES"
    }

    result = engine.diagnose_domain("Network Troubleshooting", user_facts)

    assert result.status == STATUS_POSSIBLE
    assert len(result.possible_hypotheses) == 2  # Both Alpha and Beta are possible

    for hyp in result.possible_hypotheses:
        assert hyp.satisfied_count == 1  # fact_c is satisfied
        assert hyp.total_conditions == 2
        assert hyp.evidence_coverage == 0.5
        assert "50% (1 of 2 conditions verified)" in hyp.coverage_display


def test_multi_level_network_dns_chain(baseline_kb):
    """
    Tests real multi-level backward chaining on Network Troubleshooting domain:
    local_link_established -> lan_communication_functional -> wan_connectivity_present -> DNS Failure.
    """
    engine = BackwardChainingEngine(baseline_kb)
    user_facts = {
        "wifi_adapter_enabled": "YES",
        "local_network_connected": "YES",
        "router_gateway_ping_success": "YES",
        "public_ip_ping_success": "YES",
        "dns_domain_resolves": "NO"
    }

    result = engine.diagnose_domain("Network Troubleshooting", user_facts)

    assert result.status == STATUS_CONFIRMED
    assert result.primary_diagnosis == "DNS Server Resolution Failure"
    assert "local_link_established" in result.derived_facts
    assert result.derived_facts["local_link_established"] == "YES"
    assert "lan_communication_functional" in result.derived_facts
    assert result.derived_facts["lan_communication_functional"] == "YES"
    assert "wan_connectivity_present" in result.derived_facts
    assert result.derived_facts["wan_connectivity_present"] == "YES"


def test_multi_level_vehicle_cranking_chain(baseline_kb):
    """
    Tests multi-level backward chaining on Vehicle domain:
    dashboard_lights_illuminate -> electrical_system_powered -> cranking_subsystem_functional -> Fuel Starvation.
    """
    engine = BackwardChainingEngine(baseline_kb)
    user_facts = {
        "dashboard_lights_illuminate": "YES",
        "starter_rapid_clicking_sound": "NO",
        "starter_motor_cranks_engine": "YES",
        "fuel_level_sufficient": "NO"
    }

    result = engine.diagnose_domain("Vehicle Troubleshooting", user_facts)

    assert result.status == STATUS_CONFIRMED
    assert result.primary_diagnosis == "Fuel Starvation or Depleted Fuel Tank"
    assert result.derived_facts.get("electrical_system_powered") == "YES"
    assert result.derived_facts.get("cranking_subsystem_functional") == "YES"
