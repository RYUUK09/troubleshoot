"""Data models and schemas for the AI Troubleshooting Expert System."""

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Any
from enum import Enum

class FactState(str, Enum):
    YES = "YES"
    NO = "NO"
    UNKNOWN = "UNKNOWN"

    @classmethod
    def from_bool(cls, val: Optional[bool]) -> "FactState":
        if val is True:
            return cls.YES
        elif val is False:
            return cls.NO
        return cls.UNKNOWN

    def to_bool(self) -> Optional[bool]:
        if self == FactState.YES:
            return True
        elif self == FactState.NO:
            return False
        return None


@dataclass
class Condition:
    fact: str
    expected_value: str = "YES"  # "YES" or "NO"
    description: str = ""
    is_intermediate: bool = False

    def matches(self, actual_value: str) -> bool:
        return actual_value == self.expected_value

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Condition":
        return cls(
            fact=data["fact"],
            expected_value=data.get("expected_value", "YES"),
            description=data.get("description", ""),
            is_intermediate=data.get("is_intermediate", False)
        )


@dataclass
class Rule:
    rule_id: str
    domain: str
    conditions: List[Condition]
    diagnosis: Optional[str] = None
    intermediate_fact: Optional[str] = None
    explanation: str = ""
    solution: str = ""
    approval_status: str = "APPROVED"
    author: str = "System Baseline"
    created_at: str = "2026-10-31"

    @property
    def is_intermediate_rule(self) -> bool:
        return bool(self.intermediate_fact and not self.diagnosis)

    @property
    def target_conclusion(self) -> str:
        return self.intermediate_fact if self.is_intermediate_rule else (self.diagnosis or "")

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["conditions"] = [c.to_dict() if isinstance(c, Condition) else c for c in self.conditions]
        return d

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Rule":
        conditions = [
            Condition.from_dict(c) if isinstance(c, dict) else c
            for c in data.get("conditions", [])
        ]
        return cls(
            rule_id=data["rule_id"],
            domain=data["domain"],
            conditions=conditions,
            diagnosis=data.get("diagnosis"),
            intermediate_fact=data.get("intermediate_fact"),
            explanation=data.get("explanation", ""),
            solution=data.get("solution", ""),
            approval_status=data.get("approval_status", "APPROVED"),
            author=data.get("author", "System Baseline"),
            created_at=data.get("created_at", "2026-10-31")
        )


@dataclass
class ContradictionDetail:
    rule_id: str
    diagnosis: str
    condition_fact: str
    condition_description: str
    expected_value: str
    actual_value: str
    reason: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class RuleEvaluation:
    rule_id: str
    domain: str
    diagnosis: str
    status: str  # CONFIRMED, POSSIBLE, RULED_OUT
    satisfied_conditions: List[Condition] = field(default_factory=list)
    missing_conditions: List[Condition] = field(default_factory=list)
    contradictions: List[ContradictionDetail] = field(default_factory=list)
    evidence_coverage: float = 0.0  # 0.0 to 1.0 (satisfied / total)
    total_conditions: int = 0
    satisfied_count: int = 0
    reasoning_trace: List[str] = field(default_factory=list)
    explanation: str = ""
    solution: str = ""

    @property
    def coverage_display(self) -> str:
        pct = int(round(self.evidence_coverage * 100))
        return f"{pct}% ({self.satisfied_count} of {self.total_conditions} conditions verified)"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "domain": self.domain,
            "diagnosis": self.diagnosis,
            "status": self.status,
            "satisfied_conditions": [c.to_dict() for c in self.satisfied_conditions],
            "missing_conditions": [c.to_dict() for c in self.missing_conditions],
            "contradictions": [c.to_dict() for c in self.contradictions],
            "evidence_coverage": self.evidence_coverage,
            "coverage_display": self.coverage_display,
            "total_conditions": self.total_conditions,
            "satisfied_count": self.satisfied_count,
            "reasoning_trace": self.reasoning_trace,
            "explanation": self.explanation,
            "solution": self.solution,
        }


@dataclass
class DiagnosisSessionResult:
    domain: str
    status: str  # CONFIRMED, POSSIBLE, INSUFFICIENT_EVIDENCE, CONFLICTING_EVIDENCE, NO_MATCH
    primary_diagnosis: Optional[str] = None
    primary_solution: Optional[str] = None
    confirmed_hypotheses: List[RuleEvaluation] = field(default_factory=list)
    possible_hypotheses: List[RuleEvaluation] = field(default_factory=list)
    ruled_out_hypotheses: List[ContradictionDetail] = field(default_factory=list)
    user_facts: Dict[str, str] = field(default_factory=dict)
    derived_facts: Dict[str, str] = field(default_factory=dict)
    full_trace: List[str] = field(default_factory=list)
    unresolved_questions_count: int = 0
    timestamp: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "domain": self.domain,
            "status": self.status,
            "primary_diagnosis": self.primary_diagnosis,
            "primary_solution": self.primary_solution,
            "confirmed_hypotheses": [h.to_dict() for h in self.confirmed_hypotheses],
            "possible_hypotheses": [h.to_dict() for h in self.possible_hypotheses],
            "ruled_out_hypotheses": [r.to_dict() for r in self.ruled_out_hypotheses],
            "user_facts": self.user_facts,
            "derived_facts": self.derived_facts,
            "full_trace": self.full_trace,
            "unresolved_questions_count": self.unresolved_questions_count,
            "timestamp": self.timestamp,
        }
