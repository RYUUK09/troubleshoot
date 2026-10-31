"""Conflict detection, ruled-out hypothesis explanation, and uncertainty analysis module."""

from typing import Dict, List, Any, Optional

from config import (
    FACT_YES,
    FACT_NO,
    FACT_UNKNOWN,
    STATUS_CONFIRMED,
    STATUS_POSSIBLE,
    STATUS_RULED_OUT,
    STATUS_CONFLICTING_EVIDENCE,
    STATUS_INSUFFICIENT_EVIDENCE,
)
from src.models import (
    RuleEvaluation,
    ContradictionDetail,
    DiagnosisSessionResult,
)


class ConflictDetector:
    """Analyzes diagnostic sessions for contradictions, ruled-out hypotheses, and uncertainty gaps."""

    @staticmethod
    def get_ruled_out_summary(session_result: DiagnosisSessionResult) -> List[Dict[str, Any]]:
        """
        Extracts structured explanations for every ruled-out hypothesis:
        - Diagnosis
        - Rule ID
        - Condition contradicted
        - Expected value vs User's actual answer
        - Detailed elimination rationale
        """
        summary: List[Dict[str, Any]] = []
        for c in session_result.ruled_out_hypotheses:
            summary.append({
                "diagnosis": c.diagnosis,
                "rule_id": c.rule_id,
                "condition_fact": c.condition_fact,
                "condition_description": c.condition_description,
                "expected_value": c.expected_value,
                "actual_value": c.actual_value,
                "elimination_reason": c.reason,
                "narrative": (
                    f"Hypothesis '{c.diagnosis}' (Rule {c.rule_id}) was eliminated because "
                    f"'{c.condition_description}' required {c.expected_value}, "
                    f"but observed answer was {c.actual_value}."
                )
            })
        return summary

    @staticmethod
    def get_possible_hypotheses_summary(session_result: DiagnosisSessionResult) -> List[Dict[str, Any]]:
        """
        Extracts structured details for remaining possible hypotheses:
        - Supporting evidence
        - Missing conditions
        - Match score / Evidence coverage
        - Uncertainty explanation
        """
        summary: List[Dict[str, Any]] = []
        for h in session_result.possible_hypotheses:
            supporting = [
                f"{c.description or c.fact} (Verified: {c.expected_value})"
                for c in h.satisfied_conditions
            ]
            missing = [
                f"{c.description or c.fact} (Required: {c.expected_value})"
                for c in h.missing_conditions
            ]

            summary.append({
                "rule_id": h.rule_id,
                "diagnosis": h.diagnosis,
                "evidence_coverage": h.evidence_coverage,
                "coverage_display": h.coverage_display,
                "satisfied_count": h.satisfied_count,
                "total_conditions": h.total_conditions,
                "supporting_evidence": supporting,
                "missing_conditions": missing,
                "uncertainty_explanation": (
                    f"Diagnosis requires {len(missing)} additional verified condition(s) "
                    f"to reach confirmation. Currently {h.coverage_display} verified."
                ),
                "solution_preview": h.solution
            })
        return summary

    @staticmethod
    def analyze_domain_conflicts(session_result: DiagnosisSessionResult) -> Dict[str, Any]:
        """
        Checks for high-level domain contradictions:
        - Multiple mutually exclusive confirmed diagnoses
        - Opposing symptom inputs
        - Skipped condition impacts
        """
        conflicts = []
        user_facts = session_result.user_facts

        # Domain specific sanity checks
        if user_facts.get("wifi_adapter_enabled") == FACT_NO and user_facts.get("local_network_connected") == FACT_YES:
            conflicts.append("Contradiction: Wi-Fi adapter is reported DISABLED, yet local Wi-Fi network connection was marked YES.")

        if user_facts.get("dashboard_lights_illuminate") == FACT_NO and user_facts.get("starter_motor_cranks_engine") == FACT_YES:
            conflicts.append("Contradiction: Vehicle dashboard has NO power, yet starter motor is reported cranking vigorously.")

        if user_facts.get("mcu_power_led_lit") == FACT_NO and user_facts.get("usb_port_recognized_in_os") == FACT_YES:
            conflicts.append("Contradiction: Microcontroller has NO power LED, yet host OS reported USB COM port active.")

        # Multiple confirmed hypotheses check
        if len(session_result.confirmed_hypotheses) > 1:
            diag_names = [h.diagnosis for h in session_result.confirmed_hypotheses]
            conflicts.append(f"Multiple competing diagnoses confirmed simultaneously: {', '.join(diag_names)}.")

        return {
            "has_conflicts": len(conflicts) > 0,
            "conflicts": conflicts,
            "is_insufficient_evidence": session_result.status == STATUS_INSUFFICIENT_EVIDENCE
        }
