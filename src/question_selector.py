"""Intelligent Question Selection Module implementing the Min-Split Information-Gain Heuristic.

Heuristic formula:
    score = min(yes_count, no_count)
Maximizes this minimum count to divide competing hypotheses as evenly as possible.
"""

from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass

from config import (
    FACT_YES,
    FACT_NO,
    FACT_UNKNOWN,
    STATUS_RULED_OUT,
    STATUS_CONFIRMED,
)
from src.models import Condition, Rule
from src.knowledge_base import KnowledgeBase
from src.inference_engine import BackwardChainingEngine


@dataclass
class CandidateQuestion:
    fact: str
    description: str
    yes_count: int
    no_count: int
    min_split_score: int
    total_rules_impacted: int
    targeted_rules: List[str]


class MinSplitQuestionSelector:
    """Selects the next most discriminative diagnostic question using the min-split heuristic."""

    def __init__(self, kb: KnowledgeBase, engine: BackwardChainingEngine):
        self.kb = kb
        self.engine = engine

    def _get_active_rules(self, domain: str, user_facts: Dict[str, str]) -> List[Rule]:
        """
        Returns rules that are still viable (not ruled out by contradictions).
        Includes both diagnostic and intermediate rules.
        """
        active_rules: List[Rule] = []
        derived_facts: Dict[str, str] = {}
        all_rules = self.kb.get_rules_for_domain(domain)

        for rule in all_rules:
            eval_res = self.engine.evaluate_rule(
                rule=rule,
                domain=domain,
                user_facts=user_facts,
                derived_facts=derived_facts,
                call_stack=set(),
                trace=[]
            )
            if eval_res.status != STATUS_RULED_OUT:
                active_rules.append(rule)

        return active_rules

    def _get_required_atomic_facts_for_rule(
        self,
        rule: Rule,
        domain: str,
        visited_stack: Set[str]
    ) -> Dict[str, str]:
        """
        Recursively unpacks all atomic facts required by a rule (including through intermediate facts).
        Returns a mapping: {atomic_fact: expected_value}
        """
        required: Dict[str, str] = {}
        target = rule.target_conclusion

        for cond in rule.conditions:
            if cond.is_intermediate or cond.fact in self.kb.get_all_intermediate_facts(domain):
                if cond.fact not in visited_stack:
                    # Intermediate condition: find rules that produce this intermediate fact
                    inter_rules = self.kb.get_rules_concluding(cond.fact, domain)
                    for ir in inter_rules:
                        sub_reqs = self._get_required_atomic_facts_for_rule(
                            ir, domain, visited_stack | {cond.fact}
                        )
                        for f, exp in sub_reqs.items():
                            required[f] = exp
            else:
                required[cond.fact] = cond.expected_value

        return required

    def get_candidate_questions(
        self,
        domain: str,
        user_facts: Dict[str, str]
    ) -> List[CandidateQuestion]:
        """
        Evaluates all unanswered atomic conditions across currently active rules,
        computing yes_count, no_count, and min_split_score.
        """
        active_rules = self._get_active_rules(domain, user_facts)
        intermediate_facts = self.kb.get_all_intermediate_facts(domain)
        all_observable = self.kb.get_all_observable_conditions(domain)

        # Map fact to description
        fact_descriptions: Dict[str, str] = {
            c.fact: c.description for c in all_observable if c.description
        }

        # Track fact expectations across active rules
        fact_yes_rules: Dict[str, List[str]] = {}
        fact_no_rules: Dict[str, List[str]] = {}

        for rule in active_rules:
            atomic_reqs = self._get_required_atomic_facts_for_rule(rule, domain, set())
            for fact, exp in atomic_reqs.items():
                if fact in user_facts:
                    continue  # Already answered
                if fact in intermediate_facts:
                    continue  # Intermediate, not directly observable

                if exp == FACT_YES:
                    fact_yes_rules.setdefault(fact, []).append(rule.rule_id)
                elif exp == FACT_NO:
                    fact_no_rules.setdefault(fact, []).append(rule.rule_id)

        all_candidate_facts = set(fact_yes_rules.keys()) | set(fact_no_rules.keys())
        candidates: List[CandidateQuestion] = []

        for fact in all_candidate_facts:
            yes_list = fact_yes_rules.get(fact, [])
            no_list = fact_no_rules.get(fact, [])
            yes_cnt = len(yes_list)
            no_cnt = len(no_list)
            min_score = min(yes_cnt, no_cnt)
            total_impact = yes_cnt + no_cnt
            all_targeted = list(set(yes_list + no_list))

            desc = fact_descriptions.get(fact, f"Is '{fact.replace('_', ' ')}' present?")

            candidates.append(
                CandidateQuestion(
                    fact=fact,
                    description=desc,
                    yes_count=yes_cnt,
                    no_count=no_cnt,
                    min_split_score=min_score,
                    total_rules_impacted=total_impact,
                    targeted_rules=all_targeted
                )
            )

        # Deterministic sorting:
        # Primary: min_split_score descending (maximizes min(yes, no))
        # Secondary: total_rules_impacted descending
        # Tertiary: fact name ascending (consistent tie-breaking)
        candidates.sort(
            key=lambda c: (c.min_split_score, c.total_rules_impacted, -ord(c.fact[0]) if c.fact else 0),
            reverse=True
        )

        return candidates

    def select_next_question(
        self,
        domain: str,
        user_facts: Dict[str, str]
    ) -> Optional[CandidateQuestion]:
        """
        Selects the single best next question to ask the user.
        Returns None if diagnosis is confirmed or no further questions exist.
        """
        # First check if diagnosis is already confirmed
        current_diag = self.engine.diagnose_domain(domain, user_facts)
        if current_diag.status == STATUS_CONFIRMED:
            return None

        candidates = self.get_candidate_questions(domain, user_facts)
        if not candidates:
            return None

        return candidates[0]
