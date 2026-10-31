# University Project Demonstration & Viva Walkthrough Guide

## AI-Based Intelligent Troubleshooting Expert System

Use this guide during your live project presentation and viva examination. It contains exact, step-by-step click paths, expected system outputs, and key talking points for examiners.

---

## ⚡ Quick Launch Instructions

1. Open PowerShell or Command Prompt in the project folder:
   ```powershell
   cd "c:\Users\hp\OneDrive\Documents\ai new pro"
   ```
2. Run the application:
   ```powershell
   streamlit run app.py
   ```
   *(Or double-click `run_app.bat`)*
3. The application will open at `http://localhost:8501`.

---

## 🎬 6-Step Demonstration Script for Examiners

### Step 1: Dashboard Overview (2 Minutes)
- **Action:** Start on the **📊 Dashboard** view.
- **Show:**
  - Active Rules: `46` rules across `4` domains.
  - The 4 domain cards: Network, Software, Vehicle, and IoT/Hardware.
  - The interactive Plotly rule distribution donut chart.
- **Talking Point:**
  > *"Examiners, our system separates knowledge representation from reasoning. It covers four major engineering domains and operates 100% offline without external LLMs or cloud APIs."*

---

### Step 2: Multi-Level Backward Chaining Demo (3 Minutes)
- **Action:** Click **🔍 Diagnosis** in the sidebar.
- **Domain:** Select **Network Troubleshooting**.
- **Interactive Question Flow:**
  1. *Is your device's Wi-Fi / network adapter enabled?* $\longrightarrow$ Click **✅ Yes**
  2. *Is your device connected to local Wi-Fi?* $\longrightarrow$ Click **✅ Yes**
  3. *Can your device ping default gateway IP (192.168.1.1)?* $\longrightarrow$ Click **✅ Yes**
  4. *Can your device ping public IP (8.8.8.8)?* $\longrightarrow$ Click **✅ Yes**
  5. *Can your device open websites by name?* $\longrightarrow$ Click **❌ No**
- **Outcome:**
  - Banner: **Diagnostic Fault Confirmed**
  - Diagnosis: **DNS Server Resolution Failure**
  - Recommended Solution: *"Flush local DNS resolver cache: run ipconfig /flushdns..."*
- **Crucial Feature to Highlight:**
  - Open the **🔬 Backward Chaining Trace** tab.
  - Show how the engine recursively proved:
    1. `local_link_established = YES` (via Rule `R-NET-INT-001`)
    2. `lan_communication_functional = YES` (via Rule `R-NET-INT-002`)
    3. `wan_connectivity_present = YES` (via Rule `R-NET-INT-003`)
    4. Concluded terminal diagnosis via Rule `R-NET-006`.
  - Open the **🚫 Ruled-Out Diagnoses** tab and show that other hypotheses (like Wi-Fi Signal Degradation or Captive Portal) were eliminated with exact contradiction reasons.
- **Talking Point:**
  > *"This proves that our engine does not use hardcoded if-else trees. It uses formal backward-chaining goal recursion down to observable symptoms."*

---

### Step 3: Min-Split Question Selection Heuristic Demo (2 Minutes)
- **Action:** Reset the session in **🔍 Diagnosis**.
- **Show:**
  - Look at the top question box.
  - Point out the **Min-Split Score** and **Active Rules Impacted** counters.
  - Open the expandable box: *"Why this question was chosen (Min-Split Heuristic)"*.
- **Talking Point:**
  > *"Notice that questions are not asked in a fixed sequence. The engine calculates $\min(\text{yes\_count}, \text{no\_count})$ for all candidate symptoms and dynamically selects the question that partitions remaining competing hypotheses most evenly."*

---

### Step 4: Uncertainty & Skip Handling Demo (2 Minutes)
- **Action:** Select **Vehicle Troubleshooting**.
- **Interactive Flow:**
  - On the first question: Click **❓ Not Sure / Skip**.
  - Show that the candidate hypotheses are **not** falsely ruled out.
  - Show that the leading hypothesis remains listed under **Candidate Hypotheses** with unverified condition status.
- **Talking Point:**
  > *"Traditional expert systems crash or produce false negatives when a user skips a question. Our system maintains tri-state logic: True, False, and Unknown. Hypotheses remain active as 'Possible' until definitively proved or contradicted."*

---

### Step 5: Expert Review & Knowledge-Base Learning Demo (3 Minutes)
- **Action:** Click **🛡️ Expert Review** in the sidebar.
- **Demonstration:**
  1. Open the **📝 Submit New Diagnostic Rule** tab.
  2. Attempt to submit a rule with an existing Rule ID (`R-NET-001`).
     - **Result:** System immediately blocks it with **Duplicate Detected**.
  3. Open the **⏳ Pending Review** tab.
     - Show proposal `EXP-PROP-003` (SPI Bus Clock Inversion).
     - Enter your name as Reviewer (`Examiner / Chief Architect`).
     - Click **✅ Approve & Integrate into KB**.
     - **Result:** Live integration into the active knowledge base with an audit trail!
- **Talking Point:**
  > *"This demonstrates our 7-step governance lifecycle. New rules cannot self-activate. They must undergo input validation, duplicate detection, and peer approval before being merged into the active knowledge base."*

---

### Step 6: Empirical Benchmark & Evaluation Demo (2 Minutes)
- **Action:** Click **📈 Evaluation Benchmark** in the sidebar.
- **Action:** Click **🚀 Run Comparative Benchmark Now**.
- **Show:**
  - Metric cards: **Baseline Accuracy: 92.86%**, **Updated KB Accuracy: 100.00%**, **Delta: +7.14%**.
  - Side-by-side Plotly bar chart comparing domain performance.
  - Select radio button: *"Newly Resolved Cases by Expert Learning"*.
  - Show test cases `TC-NET-08` and `TC-SOFT-07`, which failed on Baseline but passed on Updated KB!
- **Talking Point:**
  > *"Examiners, these numbers are not hardcoded. The system runs all 28 authentic test cases live through the backward chaining engine across both knowledge bases, proving genuine diagnostic accuracy improvement."*

---

## 🏆 Summary Checklist for High Viva Scores

- [x] Tested all 4 domains live.
- [x] Demonstrated multi-level backward chaining trace.
- [x] Explained $\min(\text{yes}, \text{no})$ information gain heuristic.
- [x] Demonstrated tri-state skip handling (*Yes*, *No*, *Not Sure*).
- [x] Demonstrated ruled-out contradiction explanations.
- [x] Demonstrated expert review and active KB integration.
- [x] Presented live benchmark results and Plotly visualization.
- [x] Ran 34 passing Pytest automated test suites.
