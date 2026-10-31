"""Configuration constants and path definitions for AI Troubleshooting Expert System."""

import os
import sys
from pathlib import Path

# Base Paths
PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / "data"
SRC_DIR = PROJECT_ROOT / "src"
TESTS_DIR = PROJECT_ROOT / "tests"
UI_DIR = PROJECT_ROOT / "ui"

# Data file paths
BASELINE_KB_PATH = DATA_DIR / "knowledge_base_baseline.json"
ACTIVE_KB_PATH = DATA_DIR / "knowledge_base.json"
TEST_DATASET_PATH = DATA_DIR / "evaluation_testset.json"
EXPERT_PROPOSALS_PATH = DATA_DIR / "expert_proposals.json"
DIAGNOSIS_HISTORY_PATH = DATA_DIR / "diagnosis_history.json"
EVALUATION_HISTORY_PATH = DATA_DIR / "evaluation_history.json"

# Supported Domains
DOMAINS = [
    "Network Troubleshooting",
    "Software Troubleshooting",
    "Vehicle Troubleshooting",
    "IoT & Hardware Troubleshooting",
]

DOMAIN_ICONS = {
    "Network Troubleshooting": "🌐",
    "Software Troubleshooting": "💻",
    "Vehicle Troubleshooting": "🚗",
    "IoT & Hardware Troubleshooting": "🔌",
}

DOMAIN_SHORT_CODES = {
    "Network Troubleshooting": "NET",
    "Software Troubleshooting": "SOFT",
    "Vehicle Troubleshooting": "VEH",
    "IoT & Hardware Troubleshooting": "IOT",
}

# Tri-state fact values
FACT_YES = "YES"
FACT_NO = "NO"
FACT_UNKNOWN = "UNKNOWN"

VALID_FACT_VALUES = {FACT_YES, FACT_NO, FACT_UNKNOWN}

# Diagnostic Outcomes
STATUS_CONFIRMED = "CONFIRMED"
STATUS_POSSIBLE = "POSSIBLE"
STATUS_RULED_OUT = "RULED_OUT"
STATUS_INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"
STATUS_CONFLICTING_EVIDENCE = "CONFLICTING_EVIDENCE"
STATUS_NO_MATCH = "NO_MATCH"

# Rule Review Status
STATUS_APPROVED = "APPROVED"
STATUS_PENDING = "PENDING_REVIEW"
STATUS_REJECTED = "REJECTED"

# UI Settings
APP_TITLE = "AI-Based Intelligent Troubleshooting Expert System"
APP_SUBTITLE = "Explainable Multi-Domain Diagnostic Expert System with Backward Chaining & Heuristic Optimization"
VERSION = "1.0.0"
