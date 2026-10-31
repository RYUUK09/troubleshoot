"""Unit tests for the Min-Split Question Selection heuristic."""

import pytest
from src.question_selector import MinSplitQuestionSelector
from src.inference_engine import BackwardChainingEngine


def test_min_split_heuristic_discrimination(sample_toy_kb):
    """
    In sample_toy_kb:
    Rule 1 (Fault Alpha): needs fact_c (from A and B) and fact_d=YES
    Rule 2 (Fault Beta): needs fact_c (from A and B) and fact_d=NO
    If A and B are answered YES:
    Active rules are Rule 1 and Rule 2.
    For fact_d:
      yes_count = 1 (Rule 1)
      no_count = 1 (Rule 2)
      min(yes_count, no_count) = 1!
    Fact D perfectly divides the 2 hypotheses and should be the top selected question!
    """
    engine = BackwardChainingEngine(sample_toy_kb)
    selector = MinSplitQuestionSelector(sample_toy_kb, engine)

    user_facts = {
        "fact_a": "YES",
        "fact_b": "YES"
    }

    candidates = selector.get_candidate_questions("Network Troubleshooting", user_facts)
    assert len(candidates) > 0

    top_q = candidates[0]
    assert top_q.fact == "fact_d"
    assert top_q.yes_count == 1
    assert top_q.no_count == 1
    assert top_q.min_split_score == 1


def test_no_repeated_questions(baseline_kb):
    """Ensures that once a question is answered (YES, NO, or UNKNOWN), it is never repeated."""
    engine = BackwardChainingEngine(baseline_kb)
    selector = MinSplitQuestionSelector(baseline_kb, engine)

    user_facts = {
        "wifi_adapter_enabled": "YES",
        "local_network_connected": "NO"
    }

    candidates = selector.get_candidate_questions("Network Troubleshooting", user_facts)
    candidate_facts = [c.fact for c in candidates]

    assert "wifi_adapter_enabled" not in candidate_facts
    assert "local_network_connected" not in candidate_facts


def test_selection_terminates_when_confirmed(sample_toy_kb):
    """Ensures selector returns None when a diagnosis has been definitively confirmed."""
    engine = BackwardChainingEngine(sample_toy_kb)
    selector = MinSplitQuestionSelector(sample_toy_kb, engine)

    user_facts = {
        "fact_a": "YES",
        "fact_b": "YES",
        "fact_d": "YES"  # Confirms Fault Alpha
    }

    next_q = selector.select_next_question("Network Troubleshooting", user_facts)
    assert next_q is None
