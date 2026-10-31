"""Knowledge Base management module for loading, validating, and querying diagnostic rules."""

import json
from pathlib import Path
from typing import List, Dict, Optional, Set, Any
import copy

from config import (
    BASELINE_KB_PATH,
    ACTIVE_KB_PATH,
    DOMAINS,
    STATUS_APPROVED,
)
from src.models import Rule, Condition


class KnowledgeBase:
    """Manages diagnostic rules, intermediate facts, and domain knowledge."""

    def __init__(self, kb_path: Optional[Path] = None):
        self.kb_path = kb_path or ACTIVE_KB_PATH
        self.rules: List[Rule] = []
        self.version: str = "1.0.0"
        self.load()

    def load(self, path: Optional[Path] = None) -> None:
        """Loads rules from JSON file."""
        target_path = path or self.kb_path
        if not target_path.exists():
            if BASELINE_KB_PATH.exists():
                target_path = BASELINE_KB_PATH
            else:
                raise FileNotFoundError(f"Knowledge base file not found: {target_path}")

        with open(target_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.version = data.get("version", "1.0.0")
        raw_rules = data.get("rules", [])
        self.rules = [Rule.from_dict(r) for r in raw_rules]

    def save(self, path: Optional[Path] = None) -> None:
        """Saves active knowledge base to JSON file."""
        target_path = path or self.kb_path
        data = {
            "version": self.version,
            "rules": [r.to_dict() for r in self.rules]
        }
        with open(target_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def reset_to_baseline(self) -> None:
        """Resets active knowledge base back to factory baseline rules."""
        if not BASELINE_KB_PATH.exists():
            raise FileNotFoundError("Baseline knowledge base not found.")
        with open(BASELINE_KB_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.rules = [Rule.from_dict(r) for r in data.get("rules", [])]
        self.version = data.get("version", "1.0.0")
        self.save(ACTIVE_KB_PATH)

    def get_rules_for_domain(self, domain: str, only_approved: bool = True) -> List[Rule]:
        """Returns all rules for a given domain."""
        return [
            r for r in self.rules
            if r.domain == domain and (not only_approved or r.approval_status == STATUS_APPROVED)
        ]

    def get_diagnostic_rules(self, domain: str, only_approved: bool = True) -> List[Rule]:
        """Returns rules concluding a final diagnosis."""
        return [
            r for r in self.get_rules_for_domain(domain, only_approved)
            if not r.is_intermediate_rule and r.diagnosis
        ]

    def get_intermediate_rules(self, domain: str, only_approved: bool = True) -> List[Rule]:
        """Returns rules concluding an intermediate fact."""
        return [
            r for r in self.get_rules_for_domain(domain, only_approved)
            if r.is_intermediate_rule and r.intermediate_fact
        ]

    def get_rules_concluding(self, fact_or_diagnosis: str, domain: str, only_approved: bool = True) -> List[Rule]:
        """Returns all rules that conclude the specified diagnosis or intermediate fact."""
        domain_rules = self.get_rules_for_domain(domain, only_approved)
        results = []
        for r in domain_rules:
            if r.is_intermediate_rule and r.intermediate_fact == fact_or_diagnosis:
                results.append(r)
            elif not r.is_intermediate_rule and r.diagnosis == fact_or_diagnosis:
                results.append(r)
        return results

    def get_rule_by_id(self, rule_id: str) -> Optional[Rule]:
        """Finds a rule by its unique identifier."""
        for r in self.rules:
            if r.rule_id == rule_id:
                return r
        return None

    def get_all_intermediate_facts(self, domain: str) -> Set[str]:
        """Returns the set of all intermediate fact names for a domain."""
        return {
            r.intermediate_fact for r in self.get_intermediate_rules(domain)
            if r.intermediate_fact
        }

    def get_all_observable_conditions(self, domain: str) -> List[Condition]:
        """Returns all atomic (non-intermediate) conditions for a domain, deduplicated by fact name."""
        seen_facts: Set[str] = set()
        intermediate_facts = self.get_all_intermediate_facts(domain)
        conditions: List[Condition] = []

        for r in self.get_rules_for_domain(domain):
            for c in r.conditions:
                if c.fact not in seen_facts and c.fact not in intermediate_facts and not c.is_intermediate:
                    seen_facts.add(c.fact)
                    conditions.append(c)

        return conditions

    def validate_integrity(self) -> Dict[str, Any]:
        """
        Validates KB consistency:
        - Checks for duplicate rule IDs
        - Checks that all intermediate conditions have at least one producing rule
        - Checks for direct self-referencing cycles
        """
        issues = []
        rule_ids = set()
        duplicates = []

        for r in self.rules:
            if r.rule_id in rule_ids:
                duplicates.append(r.rule_id)
            rule_ids.add(r.rule_id)

        if duplicates:
            issues.append(f"Duplicate Rule IDs detected: {duplicates}")

        # Check domain intermediate completeness
        for d in DOMAINS:
            inter_facts = self.get_all_intermediate_facts(d)
            for r in self.get_rules_for_domain(d):
                for c in r.conditions:
                    if c.is_intermediate and c.fact not in inter_facts:
                        issues.append(
                            f"Rule {r.rule_id} requires intermediate fact '{c.fact}', "
                            f"but no intermediate rule derives it in domain '{d}'."
                        )

        # Check self-cycles
        for r in self.rules:
            target = r.target_conclusion
            for c in r.conditions:
                if c.fact == target:
                    issues.append(f"Direct circular dependency in rule {r.rule_id}: condition references its own conclusion '{target}'")

        return {
            "valid": len(issues) == 0,
            "total_rules": len(self.rules),
            "domains": {d: len(self.get_rules_for_domain(d)) for d in DOMAINS},
            "issues": issues
        }

    def add_rule(self, rule: Rule, overwrite: bool = False) -> bool:
        """Adds a new rule to the knowledge base."""
        existing = self.get_rule_by_id(rule.rule_id)
        if existing and not overwrite:
            return False
        if existing and overwrite:
            self.rules = [r for r in self.rules if r.rule_id != rule.rule_id]

        self.rules.append(rule)
        return True
