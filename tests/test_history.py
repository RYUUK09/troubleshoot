"""Unit tests for Diagnosis History management."""

import pytest
from src.models import DiagnosisSessionResult
from config import STATUS_CONFIRMED


def test_log_and_retrieve_session(temp_history_manager):
    """Verifies that diagnostic sessions are recorded and can be queried."""
    session = DiagnosisSessionResult(
        domain="Network Troubleshooting",
        status=STATUS_CONFIRMED,
        primary_diagnosis="DNS Server Resolution Failure",
        primary_solution="Change DNS to 1.1.1.1",
        user_facts={"wifi_adapter_enabled": "YES", "dns_domain_resolves": "NO"}
    )

    record = temp_history_manager.log_session(session, user_notes="Customer Wi-Fi case")
    assert record["session_id"].startswith("SESS-")
    assert record["domain"] == "Network Troubleshooting"
    assert record["user_notes"] == "Customer Wi-Fi case"

    # Query
    records = temp_history_manager.get_records(domain_filter="Network Troubleshooting")
    assert len(records) == 1
    assert records[0]["primary_diagnosis"] == "DNS Server Resolution Failure"


def test_history_filtering_and_clear(temp_history_manager):
    """Tests domain filtering and history clearing."""
    session1 = DiagnosisSessionResult(domain="Software Troubleshooting", status=STATUS_CONFIRMED)
    session2 = DiagnosisSessionResult(domain="Vehicle Troubleshooting", status=STATUS_CONFIRMED)

    temp_history_manager.log_session(session1)
    temp_history_manager.log_session(session2)

    soft_records = temp_history_manager.get_records(domain_filter="Software Troubleshooting")
    assert len(soft_records) == 1

    temp_history_manager.clear_history()
    assert len(temp_history_manager.get_records()) == 0
