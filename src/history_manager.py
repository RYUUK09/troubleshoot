"""Diagnosis History Manager for recording, querying, and exporting diagnosis sessions."""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

from config import DIAGNOSIS_HISTORY_PATH
from src.models import DiagnosisSessionResult


class DiagnosisHistoryManager:
    """Manages persistent logging of user diagnostic sessions."""

    def __init__(self, history_path: Optional[Path] = None):
        self.history_path = history_path or DIAGNOSIS_HISTORY_PATH
        self.records: List[Dict[str, Any]] = []
        self.load_history()

    def load_history(self) -> List[Dict[str, Any]]:
        """Loads historical diagnosis sessions."""
        if not self.history_path.exists():
            self.records = []
            return []
        try:
            with open(self.history_path, "r", encoding="utf-8") as f:
                self.records = json.load(f)
                return self.records
        except Exception:
            self.records = []
            return []

    def save_history(self) -> None:
        """Saves historical records to file."""
        with open(self.history_path, "w", encoding="utf-8") as f:
            json.dump(self.records, f, indent=2)

    def log_session(
        self,
        result: DiagnosisSessionResult,
        user_notes: str = ""
    ) -> Dict[str, Any]:
        """Logs a completed diagnostic session."""
        session_id = f"SESS-{datetime.now().strftime('%Y%m%d%H%M%S')}-{len(self.records) + 1}"
        record = {
            "session_id": session_id,
            "timestamp": result.timestamp or datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "domain": result.domain,
            "status": result.status,
            "primary_diagnosis": result.primary_diagnosis,
            "primary_solution": result.primary_solution,
            "facts_answered_count": len(result.user_facts),
            "user_facts": result.user_facts,
            "derived_facts": result.derived_facts,
            "confirmed_count": len(result.confirmed_hypotheses),
            "possible_count": len(result.possible_hypotheses),
            "ruled_out_count": len(result.ruled_out_hypotheses),
            "confirmed_diagnoses": [h.diagnosis for h in result.confirmed_hypotheses],
            "user_notes": user_notes
        }
        self.records.insert(0, record)  # Most recent first
        self.save_history()
        return record

    def get_records(
        self,
        domain_filter: Optional[str] = None,
        status_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Filters diagnosis history."""
        results = self.records
        if domain_filter and domain_filter != "All Domains":
            results = [r for r in results if r.get("domain") == domain_filter]
        if status_filter and status_filter != "All Statuses":
            results = [r for r in results if r.get("status") == status_filter]
        return results

    def clear_history(self) -> None:
        """Clears diagnostic history records."""
        self.records = []
        self.save_history()
