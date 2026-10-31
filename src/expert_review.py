"""Expert Review and Knowledge-Base Learning Module.

Enforces a 7-step governance lifecycle:
1. Rule Submission
2. Input Validation
3. Duplicate Detection
4. Expert Approval
5. Active Knowledge-Base Integration
6. Knowledge-Base Consistency Verification
7. Audit Trail Logging
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime

from config import (
    EXPERT_PROPOSALS_PATH,
    DOMAINS,
    STATUS_APPROVED,
    STATUS_PENDING,
    STATUS_REJECTED,
)
from src.models import Rule, Condition
from src.knowledge_base import KnowledgeBase


class ExpertReviewManager:
    """Manages rule submissions, duplicate validation, approval workflow, and active KB integration."""

    def __init__(self, proposals_path: Optional[Path] = None):
        self.proposals_path = proposals_path or EXPERT_PROPOSALS_PATH
        self.proposals: List[Dict[str, Any]] = []
        self.load_proposals()

    def load_proposals(self) -> None:
        """Loads proposals from storage."""
        if not self.proposals_path.exists():
            self.proposals = []
            return
        with open(self.proposals_path, "r", encoding="utf-8") as f:
            self.proposals = json.load(f)

    def save_proposals(self) -> None:
        """Persists proposals to storage."""
        with open(self.proposals_path, "w", encoding="utf-8") as f:
            json.dump(self.proposals, f, indent=2)

    def validate_rule_input(self, data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Step 2: Input Validation
        Validates structure and completeness of a submitted rule.
        """
        required_fields = ["rule_id", "domain", "conditions", "explanation", "solution", "author"]
        for field in required_fields:
            if not data.get(field):
                return False, f"Missing required field: '{field}'"

        if data["domain"] not in DOMAINS:
            return False, f"Invalid domain: '{data['domain']}'. Must be one of {DOMAINS}"

        if not data.get("diagnosis") and not data.get("intermediate_fact"):
            return False, "Rule must have either a 'diagnosis' or an 'intermediate_fact'"

        conditions = data.get("conditions", [])
        if not isinstance(conditions, list) or len(conditions) == 0:
            return False, "Conditions must be a non-empty list of condition objects"

        for idx, cond in enumerate(conditions):
            if not isinstance(cond, dict) or not cond.get("fact"):
                return False, f"Condition #{idx+1} is missing a valid 'fact' identifier"
            if cond.get("expected_value") not in ("YES", "NO"):
                return False, f"Condition #{idx+1} expected_value must be 'YES' or 'NO'"

        return True, None

    def check_duplicate(
        self,
        candidate_data: Dict[str, Any],
        kb: KnowledgeBase
    ) -> Tuple[bool, Optional[str]]:
        """
        Step 3: Duplicate Rule Detection
        Checks whether the proposed rule duplicates an existing active rule or proposal.
        """
        rule_id = candidate_data["rule_id"].strip().upper()
        domain = candidate_data["domain"]
        diagnosis = candidate_data.get("diagnosis")
        candidate_facts = {c["fact"]: c.get("expected_value", "YES") for c in candidate_data["conditions"]}

        # Check existing KB rules
        for existing_rule in kb.get_rules_for_domain(domain):
            if existing_rule.rule_id.upper() == rule_id:
                return True, f"A rule with ID '{rule_id}' already exists in domain '{domain}'"

            if diagnosis and existing_rule.diagnosis == diagnosis:
                existing_facts = {c.fact: c.expected_value for c in existing_rule.conditions}
                if existing_facts == candidate_facts:
                    return True, (
                        f"Duplicate logic: Rule {existing_rule.rule_id} already covers "
                        f"diagnosis '{diagnosis}' with identical condition set."
                    )

        # Check pending/approved proposals
        for prop in self.proposals:
            if prop.get("proposal_id") != candidate_data.get("proposal_id"):
                if prop["rule_id"].upper() == rule_id:
                    return True, f"A proposal with Rule ID '{rule_id}' already exists in proposals log"

        return False, None

    def submit_proposal(
        self,
        rule_dict: Dict[str, Any],
        kb: KnowledgeBase
    ) -> Tuple[bool, str, Optional[str]]:
        """
        Step 1 & 2 & 3: Rule Submission, Validation, and Duplicate Check.
        Returns: (success, message, proposal_id)
        """
        # Step 2: Validate
        valid, val_err = self.validate_rule_input(rule_dict)
        if not valid:
            return False, f"Validation Failed: {val_err}", None

        # Step 3: Check Duplicate
        is_dup, dup_err = self.check_duplicate(rule_dict, kb)
        if is_dup:
            return False, f"Duplicate Rejected: {dup_err}", None

        proposal_id = f"PROP-{datetime.now().strftime('%Y%m%d%H%M%S')}-{len(self.proposals) + 1}"
        proposal = {
            "proposal_id": proposal_id,
            "rule_id": rule_dict["rule_id"].strip().upper(),
            "domain": rule_dict["domain"],
            "diagnosis": rule_dict.get("diagnosis"),
            "intermediate_fact": rule_dict.get("intermediate_fact"),
            "conditions": rule_dict["conditions"],
            "explanation": rule_dict["explanation"],
            "solution": rule_dict["solution"],
            "approval_status": STATUS_PENDING,
            "author": rule_dict["author"],
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "reviewed_by": None,
            "review_notes": ""
        }

        self.proposals.append(proposal)
        self.save_proposals()
        return True, f"Rule proposed successfully with Proposal ID: {proposal_id}. Awaiting expert review.", proposal_id

    def approve_proposal(
        self,
        proposal_id: str,
        approver_name: str,
        review_notes: str,
        kb: KnowledgeBase
    ) -> Tuple[bool, str]:
        """
        Steps 4, 5, 6, 7: Expert Approval, Integration, Consistency Verification, and Audit Logging.
        """
        target_prop = None
        for p in self.proposals:
            if p["proposal_id"] == proposal_id:
                target_prop = p
                break

        if not target_prop:
            return False, f"Proposal '{proposal_id}' not found."

        if target_prop["approval_status"] == STATUS_APPROVED:
            return False, f"Proposal '{proposal_id}' has already been approved."

        # Convert to Rule model
        rule_obj = Rule(
            rule_id=target_prop["rule_id"],
            domain=target_prop["domain"],
            conditions=[Condition.from_dict(c) for c in target_prop["conditions"]],
            diagnosis=target_prop.get("diagnosis"),
            intermediate_fact=target_prop.get("intermediate_fact"),
            explanation=target_prop["explanation"],
            solution=target_prop["solution"],
            approval_status=STATUS_APPROVED,
            author=target_prop["author"],
            created_at=target_prop.get("created_at", datetime.now().strftime("%Y-%m-%d"))
        )

        # Step 5: Add rule to KnowledgeBase
        kb.add_rule(rule_obj, overwrite=True)

        # Step 6: Verify Knowledge-Base Consistency
        integrity = kb.validate_integrity()
        if not integrity["valid"]:
            # Roll back rule from KB
            kb.rules = [r for r in kb.rules if r.rule_id != rule_obj.rule_id]
            return False, f"Consistency Verification Failed: {'; '.join(integrity['issues'])}"

        # Save integrated active knowledge base
        kb.save()

        # Step 7: Audit Information
        target_prop["approval_status"] = STATUS_APPROVED
        target_prop["reviewed_by"] = approver_name
        target_prop["review_notes"] = review_notes
        target_prop["approved_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.save_proposals()

        return True, f"Rule '{rule_obj.rule_id}' successfully approved and integrated into active Knowledge Base."

    def reject_proposal(
        self,
        proposal_id: str,
        reviewer_name: str,
        rejection_reason: str
    ) -> Tuple[bool, str]:
        """Rejects a proposed rule with audit notes."""
        target_prop = None
        for p in self.proposals:
            if p["proposal_id"] == proposal_id:
                target_prop = p
                break

        if not target_prop:
            return False, f"Proposal '{proposal_id}' not found."

        target_prop["approval_status"] = STATUS_REJECTED
        target_prop["reviewed_by"] = reviewer_name
        target_prop["review_notes"] = rejection_reason
        target_prop["rejected_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.save_proposals()

        return True, f"Proposal '{proposal_id}' rejected."

    def get_proposals(
        self,
        status: Optional[str] = None,
        domain: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Queries proposals with optional filtering."""
        results = self.proposals
        if status:
            results = [p for p in results if p.get("approval_status") == status]
        if domain:
            results = [p for p in results if p.get("domain") == domain]
        return results
