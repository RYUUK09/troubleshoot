"""Intelligent Inference Engine implementing multi-level backward chaining,
intermediate fact derivation, cycle detection, and explainable reasoning.
"""

from typing import Dict, List, Set, Optional, Tuple, Any
from copy import deepcopy

from config import (
    FACT_YES,
    FACT_NO,
    FACT_UNKNOWN,
    STATUS_CONFIRMED,
    STATUS_POSSIBLE,
    STATUS_RULED_OUT,
    STATUS_INSUFFICIENT_EVIDENCE,
    STATUS_CONFLICTING_EVIDENCE,
    STATUS_NO_MATCH,
)
from src.models import (
    Rule,
    Condition,
    ContradictionDetail,
    RuleEvaluation,
    DiagnosisSessionResult,
)
from src.knowledge_base import KnowledgeBase


class BackwardChainingEngine:
    """Multi-level backward chaining inference engine with cycle detection and explanation."""

    def __init__(self, kb: KnowledgeBase):
        self.kb = kb

    def evaluate_condition(
        self,
        condition: Condition,
        domain: str,
        user_facts: Dict[str, str],
        derived_facts: Dict[str, str],
        call_stack: Set[str],
        trace: List[str]
    ) -> Tuple[str, Optional[str]]:
        """
        Evaluates a single condition using backward chaining if intermediate,
        or direct fact lookup if atomic.
        Returns: (state, reason_or_detail)
        Where state is 'SATISFIED', 'CONTRADICTED', or 'MISSING'
        """
        fact_name = condition.fact
        expected = condition.expected_value

        # Case 1: Fact already derived
        if fact_name in derived_facts:
            actual = derived_facts[fact_name]
            trace.append(f"  [Cached Fact] '{fact_name}' = {actual} (expected {expected})")
            if actual == expected:
                return "SATISFIED", f"Derived fact '{fact_name}' matches expected '{expected}'"
            elif actual in (FACT_YES, FACT_NO):
                return "CONTRADICTED", f"Derived fact '{fact_name}' is '{actual}', but rule requires '{expected}'"
            else:
                return "MISSING", f"Derived fact '{fact_name}' remains unresolved"

        # Case 2: Intermediate condition -> Backward chain through intermediate rules
        if condition.is_intermediate or fact_name in self.kb.get_all_intermediate_facts(domain):
            trace.append(f"  [Goal Recursion] Evaluating intermediate goal '{fact_name}'...")

            # Cycle detection
            if fact_name in call_stack:
                cycle_path = " -> ".join(list(call_stack) + [fact_name])
                trace.append(f"  [CYCLE DETECTED] Circular dependency encountered: {cycle_path}. Aborting branch.")
                return "MISSING", f"Circular dependency on '{fact_name}'"

            # Backward-chain on rules that derive this intermediate fact
            candidate_rules = self.kb.get_rules_concluding(fact_name, domain)
            if not candidate_rules:
                trace.append(f"  [Missing Derivation] No rules found to derive intermediate fact '{fact_name}'.")
                return "MISSING", f"No rule derives intermediate fact '{fact_name}'"

            new_stack = call_stack | {fact_name}
            derived_success = False
            all_ruled_out = True

            for sub_rule in candidate_rules:
                trace.append(f"    [Sub-Rule Evaluation] Checking {sub_rule.rule_id} for '{fact_name}'...")
                sub_eval = self.evaluate_rule(
                    sub_rule, domain, user_facts, derived_facts, new_stack, trace
                )

                if sub_eval.status == STATUS_CONFIRMED:
                    derived_facts[fact_name] = FACT_YES
                    derived_success = True
                    all_ruled_out = False
                    trace.append(f"    [Sub-Goal Proved] Intermediate fact '{fact_name}' = YES via {sub_rule.rule_id}.")
                    break
                elif sub_eval.status == STATUS_POSSIBLE:
                    all_ruled_out = False

            if derived_success:
                actual = FACT_YES
            elif all_ruled_out and candidate_rules:
                actual = FACT_NO
                derived_facts[fact_name] = FACT_NO
                trace.append(f"    [Sub-Goal Disproved] Intermediate fact '{fact_name}' = NO (all sub-rules ruled out).")
            else:
                actual = FACT_UNKNOWN
                derived_facts[fact_name] = FACT_UNKNOWN
                trace.append(f"    [Sub-Goal Inconclusive] Intermediate fact '{fact_name}' = UNKNOWN (insufficient facts).")

            if actual == expected:
                return "SATISFIED", f"Intermediate goal '{fact_name}' proved {actual}"
            elif actual in (FACT_YES, FACT_NO):
                return "CONTRADICTED", f"Intermediate goal '{fact_name}' resolved to {actual}, expected {expected}"
            else:
                return "MISSING", f"Intermediate goal '{fact_name}' is unresolved"

        # Case 3: Atomic fact lookup in user facts
        if fact_name in user_facts:
            actual = user_facts[fact_name]
            trace.append(f"  [Observed Fact] '{fact_name}' = {actual} (expected {expected})")
            if actual == expected:
                return "SATISFIED", f"Observed symptom '{fact_name}' matches expected {expected}"
            elif actual in (FACT_YES, FACT_NO):
                return "CONTRADICTED", f"User answered '{actual}', but rule requires '{expected}'"
            else:
                # User selected "UNKNOWN" (Not Sure / Skip)
                return "MISSING", f"User selected 'Not Sure / Skip' for '{fact_name}'"
        else:
            trace.append(f"  [Unobserved Fact] '{fact_name}' not yet answered.")
            return "MISSING", f"Condition '{fact_name}' has not been answered yet"

    def evaluate_rule(
        self,
        rule: Rule,
        domain: str,
        user_facts: Dict[str, str],
        derived_facts: Dict[str, str],
        call_stack: Set[str],
        trace: List[str]
    ) -> RuleEvaluation:
        """
        Evaluates a complete rule against facts by inspecting all conditions.
        """
        satisfied_conditions: List[Condition] = []
        missing_conditions: List[Condition] = []
        contradictions: List[ContradictionDetail] = []
        rule_trace: List[str] = [f"Evaluating Rule {rule.rule_id} for target '{rule.target_conclusion}':"]

        for cond in rule.conditions:
            cond_trace: List[str] = []
            state, reason = self.evaluate_condition(
                cond, domain, user_facts, derived_facts, call_stack, cond_trace
            )
            rule_trace.extend(cond_trace)

            if state == "SATISFIED":
                satisfied_conditions.append(cond)
            elif state == "CONTRADICTED":
                actual_val = user_facts.get(cond.fact, derived_facts.get(cond.fact, "UNKNOWN"))
                contradictions.append(
                    ContradictionDetail(
                        rule_id=rule.rule_id,
                        diagnosis=rule.target_conclusion,
                        condition_fact=cond.fact,
                        condition_description=cond.description or cond.fact,
                        expected_value=cond.expected_value,
                        actual_value=actual_val,
                        reason=reason or "Condition contradicted"
                    )
                )
            else:
                missing_conditions.append(cond)

        total_conds = len(rule.conditions)
        satisfied_cnt = len(satisfied_conditions)
        coverage = (satisfied_cnt / total_conds) if total_conds > 0 else 0.0

        if contradictions:
            status = STATUS_RULED_OUT
            rule_trace.append(f"-> Result: RULED_OUT ({len(contradictions)} contradiction(s))")
        elif satisfied_cnt == total_conds:
            status = STATUS_CONFIRMED
            rule_trace.append(f"-> Result: CONFIRMED (All {total_conds} conditions satisfied)")
        else:
            status = STATUS_POSSIBLE
            rule_trace.append(f"-> Result: POSSIBLE ({satisfied_cnt}/{total_conds} satisfied, {len(missing_conditions)} missing)")

        trace.extend(rule_trace)

        return RuleEvaluation(
            rule_id=rule.rule_id,
            domain=domain,
            diagnosis=rule.target_conclusion,
            status=status,
            satisfied_conditions=satisfied_conditions,
            missing_conditions=missing_conditions,
            contradictions=contradictions,
            evidence_coverage=coverage,
            total_conditions=total_conds,
            satisfied_count=satisfied_cnt,
            reasoning_trace=rule_trace,
            explanation=rule.explanation,
            solution=rule.solution
        )

    def diagnose_domain(
        self,
        domain: str,
        user_facts: Dict[str, str],
        timestamp: str = ""
    ) -> DiagnosisSessionResult:
        """
        Runs complete backward chaining diagnosis across all diagnostic rules for a domain.
        Categorizes hypotheses into Confirmed, Possible, and Ruled-Out.
        Detects conflicts and uncertainty.
        """
        derived_facts: Dict[str, str] = {}
        full_trace: List[str] = [f"=== Backward-Chaining Diagnosis Session: Domain '{domain}' ==="]
        diagnostic_rules = self.kb.get_diagnostic_rules(domain)

        confirmed_evals: List[RuleEvaluation] = []
        possible_evals: List[RuleEvaluation] = []
        ruled_out_details: List[ContradictionDetail] = []

        for rule in diagnostic_rules:
            eval_res = self.evaluate_rule(
                rule=rule,
                domain=domain,
                user_facts=user_facts,
                derived_facts=derived_facts,
                call_stack=set(),
                trace=full_trace
            )

            if eval_res.status == STATUS_CONFIRMED:
                confirmed_evals.append(eval_res)
            elif eval_res.status == STATUS_POSSIBLE:
                possible_evals.append(eval_res)
            elif eval_res.status == STATUS_RULED_OUT:
                ruled_out_details.extend(eval_res.contradictions)

        # Sort possible hypotheses by evidence coverage descending, then satisfied count descending
        possible_evals.sort(key=lambda x: (x.evidence_coverage, x.satisfied_count), reverse=True)

        # Detect conflicts among confirmed diagnoses
        unique_confirmed_diagnoses = {e.diagnosis for e in confirmed_evals}
        status = STATUS_NO_MATCH
        primary_diag: Optional[str] = None
        primary_sol: Optional[str] = None

        if len(unique_confirmed_diagnoses) > 1:
            # Multiple conflicting diagnoses simultaneously confirmed
            status = STATUS_CONFLICTING_EVIDENCE
            primary_diag = f"Conflicting Diagnoses: {' vs '.join(unique_confirmed_diagnoses)}"
            primary_sol = "Inconsistent or conflicting symptoms observed across multiple distinct fault models. Re-verify symptoms."
            full_trace.append(f"[CONFLICT DETECTED] Multiple distinct hypotheses confirmed: {unique_confirmed_diagnoses}")

        elif len(confirmed_evals) >= 1:
            status = STATUS_CONFIRMED
            top = confirmed_evals[0]
            primary_diag = top.diagnosis
            primary_sol = top.solution
            full_trace.append(f"[DIAGNOSIS CONFIRMED] Primary Diagnosis: '{primary_diag}' via rule {top.rule_id}.")

        elif possible_evals:
            # Check if user has answered any questions with UNKNOWN
            has_unknown_answers = any(v == FACT_UNKNOWN for v in user_facts.values())
            has_any_yes_or_no = any(v in (FACT_YES, FACT_NO) for v in user_facts.values())

            # If user answered facts but skipped key ones, or if all active hypotheses have missing conditions
            if has_unknown_answers and has_any_yes_or_no:
                status = STATUS_INSUFFICIENT_EVIDENCE
            else:
                status = STATUS_POSSIBLE

            top_possible = possible_evals[0]
            primary_diag = f"Possible: {top_possible.diagnosis}"
            primary_sol = top_possible.solution
            full_trace.append(f"[HYPOTHESIS REMAINING] Top possible diagnosis: '{top_possible.diagnosis}' ({top_possible.coverage_display}).")

        else:
            status = STATUS_NO_MATCH
            primary_diag = "No Matching Fault Model Found"
            primary_sol = "None of the standard known diagnostic rules matched the provided symptom pattern. Consult advanced technical documentation."
            full_trace.append("[NO MATCH] All known diagnostic rules were ruled out by contradiction.")

        return DiagnosisSessionResult(
            domain=domain,
            status=status,
            primary_diagnosis=primary_diag,
            primary_solution=primary_sol,
            confirmed_hypotheses=confirmed_evals,
            possible_hypotheses=possible_evals,
            ruled_out_hypotheses=ruled_out_details,
            user_facts=user_facts,
            derived_facts=derived_facts,
            full_trace=full_trace,
            unresolved_questions_count=len(possible_evals[0].missing_conditions) if possible_evals else 0,
            timestamp=timestamp
        )
