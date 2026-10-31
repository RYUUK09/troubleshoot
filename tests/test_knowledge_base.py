"""Unit tests for the Knowledge Base manager."""

import pytest
from config import DOMAINS, STATUS_APPROVED
from src.knowledge_base import KnowledgeBase
from src.models import Rule, Condition


def test_baseline_kb_loading(baseline_kb):
    """Verifies baseline knowledge base loads properly and contains expected rules."""
    assert len(baseline_kb.rules) > 0
    assert baseline_kb.version == "1.0.0"


def test_all_four_domains_present(baseline_kb):
    """Verifies that all 4 required troubleshooting domains have rules in the KB."""
    for domain in DOMAINS:
        rules = baseline_kb.get_rules_for_domain(domain)
        assert len(rules) >= 5, f"Domain '{domain}' has insufficient rules ({len(rules)} found)."


def test_diagnostic_and_intermediate_separation(baseline_kb):
    """Verifies rules are correctly segregated into intermediate and final diagnostic rules."""
    for domain in DOMAINS:
        intermediate_rules = baseline_kb.get_intermediate_rules(domain)
        diagnostic_rules = baseline_kb.get_diagnostic_rules(domain)

        assert len(intermediate_rules) >= 1, f"Domain '{domain}' must have intermediate rules."
        assert len(diagnostic_rules) >= 5, f"Domain '{domain}' must have final diagnostic rules."

        # Verify intermediate rules have intermediate_fact and no diagnosis
        for ir in intermediate_rules:
            assert ir.is_intermediate_rule is True
            assert ir.intermediate_fact is not None
            assert ir.diagnosis is None

        # Verify diagnostic rules have diagnosis and no intermediate_fact
        for dr in diagnostic_rules:
            assert dr.is_intermediate_rule is False
            assert dr.diagnosis is not None


def test_kb_integrity_validation(baseline_kb):
    """Verifies baseline KB passes consistency validation without any broken links or duplicate IDs."""
    result = baseline_kb.validate_integrity()
    assert result["valid"] is True, f"Integrity issues found in baseline KB: {result['issues']}"
    assert len(result["issues"]) == 0


def test_observable_conditions_exclusion(baseline_kb):
    """Ensures get_all_observable_conditions does not return intermediate derived facts."""
    for domain in DOMAINS:
        observable = baseline_kb.get_all_observable_conditions(domain)
        intermediate_facts = baseline_kb.get_all_intermediate_facts(domain)

        for c in observable:
            assert c.fact not in intermediate_facts, (
                f"Observable conditions list included intermediate fact '{c.fact}' in domain '{domain}'"
            )


def test_get_rule_by_id(baseline_kb):
    """Tests retrieving specific rules by ID."""
    rule = baseline_kb.get_rule_by_id("R-NET-001")
    assert rule is not None
    assert rule.domain == "Network Troubleshooting"
    assert rule.diagnosis == "Wi-Fi Adapter Disabled or Hardware Faulty"

    non_existent = baseline_kb.get_rule_by_id("NON-EXISTENT-ID")
    assert non_existent is None


def test_add_rule_and_save(temp_kb):
    """Tests adding a rule to the active knowledge base."""
    new_rule = Rule(
        rule_id="R-TEST-CUSTOM-01",
        domain="Network Troubleshooting",
        conditions=[
            Condition(fact="test_symptom_x", expected_value="YES", description="Test symptom")
        ],
        diagnosis="Custom Test Fault",
        explanation="Testing addition",
        solution="Test solution",
        approval_status=STATUS_APPROVED
    )

    initial_count = len(temp_kb.rules)
    success = temp_kb.add_rule(new_rule)
    assert success is True
    assert len(temp_kb.rules) == initial_count + 1

    # Overwrite check
    success_dup = temp_kb.add_rule(new_rule, overwrite=False)
    assert success_dup is False
