"""Unit tests for Expert Review, Duplicate Detection, and Knowledge Base Learning."""

import pytest
from src.expert_review import ExpertReviewManager
from config import STATUS_PENDING, STATUS_APPROVED, STATUS_REJECTED


def test_rule_submission_and_validation(temp_expert_manager, temp_kb):
    """Tests successful submission of a valid rule proposal."""
    valid_data = {
        "rule_id": "R-TEST-EXP-99",
        "domain": "Network Troubleshooting",
        "diagnosis": "New Custom Diagnosis",
        "conditions": [
            {"fact": "custom_symptom_a", "expected_value": "YES", "description": "Custom A"}
        ],
        "explanation": "Custom explanation",
        "solution": "Custom solution",
        "author": "Dr. Test"
    }

    success, msg, prop_id = temp_expert_manager.submit_proposal(valid_data, temp_kb)
    assert success is True
    assert prop_id is not None

    proposals = temp_expert_manager.get_proposals(status=STATUS_PENDING)
    assert len(proposals) == 1
    assert proposals[0]["rule_id"] == "R-TEST-EXP-99"


def test_validation_rejects_missing_fields(temp_expert_manager, temp_kb):
    """Tests that submission fails if required fields or conditions are missing."""
    invalid_data = {
        "rule_id": "R-INVALID",
        "domain": "Network Troubleshooting",
        # Missing diagnosis, explanation, solution, conditions
    }

    success, msg, prop_id = temp_expert_manager.submit_proposal(invalid_data, temp_kb)
    assert success is False
    assert "Missing required field" in msg or "Validation Failed" in msg


def test_duplicate_rule_detection(temp_expert_manager, temp_kb):
    """Ensures duplicate rule IDs or duplicate condition logic are rejected."""
    # Attempt to submit a rule with an existing rule ID (e.g. R-NET-001)
    dup_id_data = {
        "rule_id": "R-NET-001",
        "domain": "Network Troubleshooting",
        "diagnosis": "Some Different Name",
        "conditions": [{"fact": "sample_fact", "expected_value": "YES", "description": "desc"}],
        "explanation": "exp",
        "solution": "sol",
        "author": "author"
    }

    success, msg, _ = temp_expert_manager.submit_proposal(dup_id_data, temp_kb)
    assert success is False
    assert "already exists" in msg


def test_approval_integrates_rule_into_kb(temp_expert_manager, temp_kb):
    """
    Verifies that:
    1. A pending rule is NOT active in the KB.
    2. Upon expert approval, the rule is integrated into the active KB.
    """
    data = {
        "rule_id": "R-TEST-EXP-101",
        "domain": "Software Troubleshooting",
        "diagnosis": "Novel Kernel Memory Leak",
        "conditions": [
            {"fact": "system_meets_minimum_os_version", "expected_value": "YES", "description": "OS OK"},
            {"fact": "kernel_page_fault_rate_high", "expected_value": "YES", "description": "Page fault high"}
        ],
        "explanation": "Kernel memory leak explanation",
        "solution": "Kernel patch",
        "author": "Kernel Specialist"
    }

    success, msg, prop_id = temp_expert_manager.submit_proposal(data, temp_kb)
    assert success is True

    # Rule must NOT be in KB yet
    assert temp_kb.get_rule_by_id("R-TEST-EXP-101") is None

    # Approve proposal
    appr_success, appr_msg = temp_expert_manager.approve_proposal(
        prop_id, approver_name="Chief Architect", review_notes="Approved for integration", kb=temp_kb
    )
    assert appr_success is True

    # Rule MUST now exist in active KB
    integrated = temp_kb.get_rule_by_id("R-TEST-EXP-101")
    assert integrated is not None
    assert integrated.diagnosis == "Novel Kernel Memory Leak"
    assert integrated.approval_status == STATUS_APPROVED


def test_rejection_workflow(temp_expert_manager, temp_kb):
    """Tests rejecting a proposal with review notes."""
    data = {
        "rule_id": "R-TEST-EXP-REJECT",
        "domain": "Vehicle Troubleshooting",
        "diagnosis": "Unsubstantiated Diagnosis",
        "conditions": [{"fact": "symptom_x", "expected_value": "YES", "description": "desc"}],
        "explanation": "exp",
        "solution": "sol",
        "author": "Tester"
    }

    _, _, prop_id = temp_expert_manager.submit_proposal(data, temp_kb)
    rej_success, rej_msg = temp_expert_manager.reject_proposal(
        prop_id, reviewer_name="Safety Officer", rejection_reason="Violates safety protocols"
    )

    assert rej_success is True
    proposals = temp_expert_manager.get_proposals(status=STATUS_REJECTED)
    assert len(proposals) == 1
    assert proposals[0]["review_notes"] == "Violates safety protocols"
