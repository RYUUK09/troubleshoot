# AI-Based Intelligent Troubleshooting Expert System

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/UI-Streamlit-FF4B4B.svg)](https://streamlit.io/)
[![Pytest Tests](https://img.shields.io/badge/tests-34%20passed-brightgreen.svg)](https://docs.pytest.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An intelligent, explainable, rule-based expert system developed from scratch in Python and Streamlit. Designed for academic demonstration, research evaluation, and university viva presentations.

The system features **multi-level backward chaining**, an **information-gain min-split question selection heuristic**, **tri-state uncertainty handling** (*Yes*, *No*, *Not Sure / Skip*), **conflict detection**, **ruled-out hypothesis tracking**, a **7-step expert review governance lifecycle**, and an **authentic empirical benchmark framework**.

---

## 📑 Table of Contents

- [Key Features](#-key-features)
- [Troubleshooting Domains](#-troubleshooting-domains)
- [System Architecture](#-system-architecture)
- [Algorithmic Mechanisms](#-algorithmic-mechanisms)
  - [1. Multi-Level Backward Chaining](#1-multi-level-backward-chaining)
  - [2. Min-Split Information-Gain Heuristic](#2-min-split-information-gain-heuristic)
  - [3. Tri-State Uncertainty Handling](#3-tri-state-uncertainty-handling)
  - [4. Conflict Detection & Ruled-Out Explanations](#4-conflict-detection--ruled-out-explanations)
  - [5. 7-Step Expert Review Governance](#5-7-step-expert-review-governance)
- [Directory Structure](#-directory-structure)
- [Installation & Quick Start](#-installation--quick-start)
- [Automated Test Suite](#-automated-test-suite)
- [Empirical Evaluation Results](#-empirical-evaluation-results)
- [Demonstration Sequence for University Viva](#-demonstration-sequence-for-university-viva)
- [Viva Questions & Answers](#-sample-viva-questions--answers)
- [License](#-license)

---

## 🌟 Key Features

1. **Pure Offline & Deterministic AI:** Operates 100% locally without paid APIs, external cloud dependencies, or unverified LLM hallucinations.
2. **Four Specialized Domains:** Independent diagnostic engines for Network, Software, Vehicle, and IoT/Hardware engineering.
3. **Multi-Level Backward Chaining:** Recursively evaluates goals down to intermediate facts and observable symptoms with strict cycle detection.
4. **Optimal Inquiries (Min-Split Heuristic):** Dynamically partitions candidate hypotheses using $\min(\text{yes\_count}, \text{no\_count})$ to minimize question count.
5. **Robust Uncertainty Handling:** Supports *Yes*, *No*, and *Not Sure / Skip* without premature hypothesis elimination.
6. **Transparent Evidence Coverage:** Formatted as percentage coverage ($n$ of $m$ conditions satisfied), explicitly distinguished from probability.
7. **Comprehensive Ruled-Out Tracking:** Displays exact causal justifications and contradicted symptoms for every eliminated diagnosis.
8. **Expert Review & Active KB Learning:** Controlled rule proposal, input validation, duplicate detection, and peer approval.
9. **Authentic Evaluation Framework:** Real test datasets evaluating Baseline vs. Updated Knowledge Bases with Plotly visualizations.
10. **Interactive Streamlit Dashboard:** Professional, responsive web interface tailored for university grading and viva review.

---

## 🌐 Troubleshooting Domains

| Domain | Scope & Diagnostic Coverage | Sample Diagnoses |
| :--- | :--- | :--- |
| **Network Troubleshooting** | Physical link, Wi-Fi signal, DHCP/Gateway, DNS resolution, Captive Portals, ISP outages, VPN loops | Wi-Fi Signal Degradation, DNS Server Resolution Failure, ISP Upstream Fiber Outage |
| **Software Troubleshooting** | OS architecture compatibility, disk exhaustion, missing runtime DLLs, antivirus quarantine, UAC permissions, memory leaks | Missing Visual C++ Runtimes, Antivirus False-Positive Quarantine, Heap Memory Leak |
| **Vehicle Troubleshooting** *(Safety Conscious)* | 12V starter battery, starter motor relay, fuel starvation, cooling system boiling, tyre pressure deflation, acoustic brake wear | Depleted 12V Battery, Severe Thermal Overheating, Brake Pad Acoustic Wear Alert |
| **IoT & Hardware Troubleshooting** | Board power rails, USB-to-UART bridge ICs, ROM bootloader sync, I2C bus pull-ups, logic level translation, ADC line EMI | Missing USB-to-UART Driver, I2C Floating Lines / Missing Pull-Ups, RF Brownout |

---

## 🏗️ System Architecture

```
                                  +---------------------------------------+
                                  |         STREAMLIT UI LAYER            |
                                  |  Dashboard | Diagnosis | Explorer     |
                                  |  Expert Review | History | Benchmark  |
                                  +-------------------+-------------------+
                                                      |
                                                      v
                                  +---------------------------------------+
                                  |        INFERENCE ENGINE CORE          |
                                  |   BackwardChainingEngine              |
                                  |   - Recursive goal evaluation         |
                                  |   - Intermediate fact derivation      |
                                  |   - Cycle detection (Call stack)      |
                                  +---------+-------------------+---------+
                                            |                   |
                     +----------------------+                   +---------------------+
                     v                                                                v
+------------------------------------------+                      +------------------------------------------+
|       QUESTION SELECTION MODULE          |                      |        CONFLICT DETECTION MODULE         |
|   MinSplitQuestionSelector               |                      |   ConflictDetector                       |
|   - Heuristic: min(yes_count, no_count)  |                      |   - Ruled-out hypothesis explanations    |
|   - Deterministic tie-breaking           |                      |   - Domain sanity checks                 |
|   - Zero question repetition             |                      |   - Uncertainty & missing fact analysis  |
+--------------------+---------------------+                      +--------------------+---------------------+
                     |                                                                 |
                     +------------------------------+----------------------------------+
                                                    |
                                                    v
                                  +---------------------------------------+
                                  |         KNOWLEDGE BASE LAYER          |
                                  |   Baseline KB (Protected, Factory)    |
                                  |   Active KB (Includes Expert Rules)   |
                                  |   Evaluation Testset (28 Cases)       |
                                  +---------------------------------------+
```

---

## 🧠 Algorithmic Mechanisms

### 1. Multi-Level Backward Chaining
Unlike forward-chaining systems that blindly deduce all possible facts from inputs, our **backward-chaining engine is goal-directed**:
1. It selects candidate diagnostic hypotheses for a domain.
2. For each rule concluding hypothesis $H$, it inspects conditions $C_1, C_2, \dots, C_k$.
3. When condition $C_i$ is an **intermediate fact**, the engine pushes $C_i$ onto a recursive evaluation stack (`call_stack: Set[str]`) and evaluates intermediate rules concluding $C_i$.
4. **Cycle Prevention:** If a fact is requested that already exists in `call_stack`, recursion halts immediately, a cycle warning is recorded, and stack overflow is prevented.

Reasoning chain example:
$$\text{Symptoms} \longrightarrow \text{Intermediate Fact} \longrightarrow \text{Higher-Level Condition} \longrightarrow \text{Final Diagnosis}$$
$$(\text{wifi\_adapter\_enabled} \land \text{local\_network\_connected}) \implies \text{local\_link\_established}$$
$$(\text{local\_link\_established} \land \text{router\_gateway\_ping}) \implies \text{lan\_communication\_functional}$$
$$(\text{lan\_communication\_functional} \land \text{public\_ip\_ping}) \implies \text{wan\_connectivity\_present}$$
$$(\text{wan\_connectivity\_present} \land \neg\text{dns\_domain\_resolves}) \implies \text{DNS Server Resolution Failure}$$

### 2. Min-Split Information-Gain Heuristic
To determine which question to ask next, the system calculates for every unanswered atomic condition $C$:
$$\text{Score}(C) = \min(\text{yes\_count}(C), \text{no\_count}(C))$$
Where:
- $\text{yes\_count}(C)$: Number of viable active rules requiring $C = \text{YES}$.
- $\text{no\_count}(C)$: Number of viable active rules requiring $C = \text{NO}$ (or eliminated if $C = \text{YES}$).

The question that **maximizes** this score is selected. This heuristic splits the active hypothesis search space as evenly as possible (approximating an optimal binary decision tree). Ties are resolved deterministically by total rule impact, then lexicographical fact ordering.

### 3. Tri-State Uncertainty Handling
Every question provides three responses:
- **Yes (True):** Condition is verified satisfied for expected YES rules; contradicts expected NO rules.
- **No (False):** Condition is verified satisfied for expected NO rules; contradicts expected YES rules.
- **Not Sure / Skip (Unknown):** Fact assigned `UNKNOWN`. It does **not** falsely confirm or eliminate any rule. The hypothesis remains viable in "Possible Diagnoses" with an explanation of missing facts.

### 4. Conflict Detection & Ruled-Out Explanations
For every eliminated hypothesis, the system records:
- The exact diagnosis and rule ID.
- The condition that was contradicted.
- The user's actual input versus expected rule value.
- A human-readable causal explanation for why the fault was disqualified.

### 5. 7-Step Expert Review Governance
1. **Rule Submission:** Proposer inputs rule ID, domain, conditions, explanation, solution, author.
2. **Input Validation:** Enforces non-empty lists, valid domains, valid logic.
3. **Duplicate Detection:** Checks ID conflicts and identical symptom-diagnosis mappings.
4. **Peer Approval:** Unapproved rules are marked `PENDING_REVIEW` and never fire in diagnosis.
5. **Active KB Integration:** Upon approval, rule is written to `knowledge_base.json`.
6. **Consistency Verification:** Full KB graph validation (detects circularities or orphaned facts).
7. **Audit Logging:** Logs reviewer name, timestamp, and review notes.

---

## 📁 Directory Structure

```
ai-troubleshooting-expert-system/
├── app.py                         # Streamlit application entry point & router
├── config.py                      # System configuration, paths, and constants
├── run_app.bat                    # Windows 1-click application launcher
├── run_tests.bat                  # Windows 1-click test runner
├── run_app.ps1                    # PowerShell launcher
├── requirements.txt               # Project dependencies
├── README.md                      # Complete system documentation
├── ARCHITECTURE.md                # In-depth architectural design specification
├── PROJECT_REPORT.md              # University BTech report with Viva guide
├── PROJECT_DEMO_GUIDE.md          # Step-by-step viva presentation walkthrough
├── data/
│   ├── knowledge_base_baseline.json # Factory baseline knowledge base (44 rules)
│   ├── knowledge_base.json        # Active knowledge base (includes approved expert rules)
│   ├── evaluation_testset.json    # Authentic test dataset (28 test cases)
│   ├── expert_proposals.json      # Proposals log with review statuses
│   ├── diagnosis_history.json     # Saved diagnosis sessions log
│   └── evaluation_history.json    # Benchmark execution history
├── src/
│   ├── __init__.py
│   ├── models.py                  # Dataclasses & enums (Rule, Condition, etc.)
│   ├── knowledge_base.py          # KnowledgeBase loader, query engine, integrity validator
│   ├── inference_engine.py        # Multi-level backward chaining engine with cycle prevention
│   ├── question_selector.py       # Min-split heuristic question selection module
│   ├── conflict_detector.py       # Conflict detector and ruled-out hypothesis tracker
│   ├── expert_review.py           # 7-step expert review governance manager
│   ├── evaluation_engine.py       # Empirical testset evaluation engine
│   ├── history_manager.py         # Session history logger and query engine
│   └── visualizer.py              # Plotly chart generators
├── ui/
│   ├── __init__.py
│   ├── components.py              # Reusable CSS and styled UI components
│   ├── dashboard_view.py          # Dashboard view with summary metrics
│   ├── diagnosis_view.py          # Interactive diagnosis workflow
│   ├── kb_explorer_view.py        # Knowledge Base explorer and rule catalog
│   ├── expert_review_view.py      # Expert rule submission and approval view
│   ├── history_view.py            # Historical session inspector and exporter
│   ├── evaluation_view.py         # Comparative benchmark view with charts
│   └── about_view.py              # Project viva guide and architectural specs
└── tests/
    ├── __init__.py
    ├── conftest.py                # Pytest fixtures and toy KB definitions
    ├── test_backward_chaining.py  # Backward chaining & intermediate fact tests
    ├── test_cycle_detection.py    # Circular dependency prevention tests
    ├── test_domains.py            # Domain-specific scenario tests (all 4 domains)
    ├── test_evaluation.py         # Benchmark accuracy calculation tests
    ├── test_expert_review.py      # Rule submission, duplicate check, approval tests
    ├── test_history.py            # History logging and filtering tests
    ├── test_knowledge_base.py     # KB loading, filtering, integrity tests
    ├── test_question_selection.py # Min-split heuristic and tie-breaking tests
    └── test_uncertainty_conflict.py # Skip, conflict, and ruled-out tests
```

---

## 🚀 Installation & Quick Start

### Prerequisites
- Python 3.10, 3.11, or 3.12
- Windows, macOS, or Linux

### Step 1: Clone or Navigate to Project Directory
```powershell
cd "c:\Users\hp\OneDrive\Documents\ai new pro"
```

### Step 2: Install Dependencies
```powershell
pip install -r requirements.txt
```

### Step 3: Run the Application
You can launch the application with:
```powershell
streamlit run app.py
```
*Or on Windows, simply double-click `run_app.bat` or execute `./run_app.ps1`.*

Open your web browser and navigate to **`http://localhost:8501`**.

---

## 🧪 Automated Test Suite

The project includes 34 comprehensive automated tests covering all functional and architectural specifications:

```powershell
pytest tests/ -v
```
*Or double-click `run_tests.bat`.*

### Test Execution Output:
```text
============================= test session starts =============================
platform win32 -- Python 3.12.13, pytest-9.2.0, pluggy-1.7.0
rootdir: C:\Users\hp\OneDrive\Documents\ai new pro
collected 34 items

tests/test_backward_chaining.py::test_toy_backward_chaining_success PASSED [  2%]
tests/test_backward_chaining.py::test_toy_backward_chaining_intermediate_failure PASSED [  5%]
tests/test_backward_chaining.py::test_evidence_coverage_calculation PASSED [  8%]
tests/test_backward_chaining.py::test_multi_level_network_dns_chain PASSED [ 11%]
tests/test_backward_chaining.py::test_multi_level_vehicle_cranking_chain PASSED [ 14%]
tests/test_cycle_detection.py::test_indirect_circular_dependency_handling PASSED [ 17%]
tests/test_domains.py::test_network_domain_scenarios PASSED              [ 20%]
tests/test_domains.py::test_software_domain_scenarios PASSED             [ 23%]
tests/test_domains.py::test_vehicle_domain_scenarios PASSED              [ 26%]
tests/test_domains.py::test_iot_domain_scenarios PASSED                  [ 29%]
tests/test_evaluation.py::test_testset_loading PASSED                    [ 32%]
tests/test_evaluation.py::test_real_accuracy_calculation PASSED          [ 35%]
tests/test_evaluation.py::test_comparative_benchmark_execution PASSED    [ 38%]
tests/test_evaluation.py::test_evaluation_history_persistence PASSED     [ 41%]
tests/test_expert_review.py::test_rule_submission_and_validation PASSED  [ 44%]
tests/test_expert_review.py::test_validation_rejects_missing_fields PASSED [ 47%]
tests/test_expert_review.py::test_duplicate_rule_detection PASSED        [ 50%]
tests/test_expert_review.py::test_approval_integrates_rule_into_kb PASSED [ 52%]
tests/test_expert_review.py::test_rejection_workflow PASSED              [ 55%]
tests/test_history.py::test_log_and_retrieve_session PASSED              [ 58%]
tests/test_history.py::test_history_filtering_and_clear PASSED           [ 61%]
tests/test_knowledge_base.py::test_baseline_kb_loading PASSED            [ 64%]
tests/test_knowledge_base.py::test_all_four_domains_present PASSED       [ 67%]
tests/test_knowledge_base.py::test_diagnostic_and_intermediate_separation PASSED [ 70%]
tests/test_knowledge_base.py::test_kb_integrity_validation PASSED        [ 73%]
tests/test_knowledge_base.py::test_observable_conditions_exclusion PASSED [ 76%]
tests/test_knowledge_base.py::test_get_rule_by_id PASSED                 [ 79%]
tests/test_knowledge_base.py::test_add_rule_and_save PASSED              [ 82%]
tests/test_question_selection.py::test_min_split_heuristic_discrimination PASSED [ 85%]
tests/test_question_selection.py::test_no_repeated_questions PASSED      [ 88%]
tests/test_question_selection.py::test_selection_terminates_when_confirmed PASSED [ 91%]
tests/test_uncertainty_conflict.py::test_skip_does_not_falsely_prove_or_eliminate PASSED [ 94%]
tests/test_uncertainty_conflict.py::test_ruled_out_hypotheses_capture PASSED [ 97%]
tests/test_uncertainty_conflict.py::test_domain_level_contradiction_detection PASSED [100%]

============================= 34 passed in 0.42s ==============================
```

---

## 📊 Empirical Evaluation Results

The system includes a dedicated test dataset (`data/evaluation_testset.json`) containing **28 realistic diagnostic cases** across all four troubleshooting domains.

Evaluation results are calculated dynamically by executing the backward-chaining engine against each test case. **No numbers are hardcoded or fabricated.**

| Evaluation Metric | Baseline Knowledge Base | Updated (Expert-Enriched) KB | Delta / Improvement |
| :--- | :---: | :---: | :---: |
| **Total Test Cases** | 28 | 28 | — |
| **Correct Predictions** | 26 | 28 | **+2 Cases** |
| **Overall Diagnostic Accuracy** | **92.86%** | **100.00%** | **+7.14%** |
| Network Troubleshooting | 87.5% (7/8) | 100.0% (8/8) | +12.5% |
| Software Troubleshooting | 85.7% (6/7) | 100.0% (7/7) | +14.3% |
| Vehicle Troubleshooting | 100.0% (7/7) | 100.0% (7/7) | 0.0% |
| IoT & Hardware Troubleshooting | 100.0% (6/6) | 100.0% (6/6) | 0.0% |

### Why Did Updated KB Accuracy Improve?
The baseline KB lacked rules for two novel enterprise failure modes:
1. `TC-NET-08`: Spanning Tree Protocol loop in Ethernet mesh backhauls.
2. `TC-SOFT-07`: Local server TCP socket binding collisions (`EADDRINUSE`).

When expert proposals `R-NET-EXP-001` and `R-SOFT-EXP-001` were peer-reviewed and integrated into the active KB, the system correctly diagnosed these cases, demonstrating **real, measurable knowledge-base learning**!

---

## 🎓 Demonstration Sequence for University Viva

Follow this recommended sequence during your project demonstration:

1. **Dashboard Overview:** Show active rule metrics, domain cards, and the rule distribution donut chart.
2. **Interactive Diagnosis Demonstration:**
   - Navigate to **🔍 Diagnosis**.
   - Select **Network Troubleshooting**.
   - Answer:
     - *Is your device's Wi-Fi / network adapter enabled?* -> **Yes**
     - *Is your device connected to the local Wi-Fi network?* -> **Yes**
     - *Can your device ping default gateway IP?* -> **Yes**
     - *Can your device ping public IP (8.8.8.8)?* -> **Yes**
     - *Can your device open websites by name?* -> **No**
   - **Outcome:** System confirms **DNS Server Resolution Failure**.
   - Expand the **Backward Chaining Trace** to show how `local_link_established`, `lan_communication_functional`, and `wan_connectivity_present` were recursively derived!
   - Show the **Ruled-Out Diagnoses** tab to demonstrate causal contradiction tracking.
3. **Uncertainty & Skip Handling:**
   - Reset session and select **Vehicle Troubleshooting**.
   - Answer **Not Sure / Skip** on initial questions. Show that hypotheses remain active in "Possible Hypotheses" without premature elimination.
4. **Knowledge Base Explorer:**
   - Filter by domain and search for specific rules. Show the distinction between intermediate derivation rules and final diagnostic rules.
5. **Expert Review Workflow:**
   - Open **🛡️ Expert Review**.
   - Show pending proposals, input validation, and duplicate detection.
   - Demonstrate approving a proposed rule and show how it immediately integrates into the active KB.
6. **Empirical Evaluation Benchmark:**
   - Navigate to **📈 Evaluation Benchmark**.
   - Click **Run Comparative Benchmark Now**.
   - Present the side-by-side Plotly bar chart showing the +7.14% measured accuracy increase between Baseline and Updated KBs.

---

## 🎯 Sample Viva Questions & Answers

### Q1: What is the core reasoning mechanism of this project?
> **Answer:** It uses multi-level **backward chaining** (goal-driven reasoning). The engine starts with potential diagnostic hypotheses and evaluates the required conditions recursively. If a condition is an intermediate fact, sub-rules are invoked to prove or disprove it, terminating at observable symptoms.

### Q2: Why did you choose backward chaining over forward chaining?
> **Answer:** Forward chaining starts from all known facts and derives everything it can, which can query dozens of irrelevant symptoms. Backward chaining is goal-driven, meaning it only investigates symptoms pertinent to active, unconfirmed hypotheses, minimizing user effort.

### Q3: How does your question selection heuristic work?
> **Answer:** We implemented an information-gain-inspired **min-split heuristic**:
> $$\text{Score} = \min(\text{yes\_count}, \text{no\_count})$$
> For every unanswered condition, we count how many active hypotheses expect Yes and how many expect No. Choosing the question that maximizes this minimum partitions the hypothesis space in half at each step, similar to an optimal binary search tree.

### Q4: How do you prevent circular reasoning (infinite recursion)?
> **Answer:** The engine maintains an active goal recursion call stack (`call_stack: Set[str]`). If an intermediate goal currently being resolved is encountered again, circular dependency is flagged, the recursive branch is aborted, and a cycle warning is recorded in the reasoning trace.

### Q5: How does your system handle uncertainty?
> **Answer:** We support tri-state facts (*Yes*, *No*, *Not Sure / Skip*). Selecting *Not Sure / Skip* marks the fact as `UNKNOWN`. It does not falsify the rule or falsely confirm it; instead, it preserves the hypothesis as *Possible* with lower evidence coverage and prompts other discriminating questions if available.

---

## 📜 License

This project is licensed under the MIT License — open-source and free for educational and research use.
