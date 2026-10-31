"""About View: Project documentation, BTech architecture walkthrough, and Viva Q&A guide."""

import streamlit as st

def render_about_view():
    st.markdown('<div class="main-header">🎓 Project Documentation & Viva Guide</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">BTech Final Year Project: AI-Based Intelligent Troubleshooting Expert System</div>', unsafe_allow_html=True)

    tab_overview, tab_arch, tab_viva = st.tabs([
        "📖 Project Overview",
        "🏗️ System Architecture & Logic",
        "🎯 Viva Questions & Model Answers"
    ])

    with tab_overview:
        st.subheader("1. Problem Statement")
        st.write("""
        Modern technical systems—spanning computer networks, enterprise software, automotive engineering, 
        and IoT devices—frequently experience failures that are difficult for non-specialists to diagnose. 
        Traditional online troubleshooting checklists are rigid and static, while large language model (LLM) 
        approaches are prone to hallucinating non-existent diagnostic steps, lack formal verification, and require 
        expensive external cloud APIs. 

        There is an urgent engineering need for a **deterministic, explainable, rule-based expert system** 
        that asks intelligent questions, derives intermediate facts, prevents cyclic reasoning, detects 
        contradictions, and operates 100% offline.
        """)

        st.subheader("2. Project Objectives")
        st.markdown("""
        1. **Multi-Domain Diagnostic Scope:** Provide expert-level troubleshooting across four major engineering fields: Network, Software, Vehicle, and IoT/Hardware.
        2. **Intelligent Backward Chaining:** Implement a multi-level recursive reasoning engine with intermediate fact derivation and cycle detection.
        3. **Information-Gain Question Selection:** Minimize user inquiry steps using the min-split heuristic $\\min(\\text{yes}, \\text{no})$.
        4. **Uncertainty & Conflict Detection:** Reliably support tri-state responses (*Yes*, *No*, *Not Sure / Skip*) and track ruled-out hypotheses with exact causal justifications.
        5. **Expert Knowledge Learning:** Implement a 7-step governance lifecycle for proposed rules with duplicate detection and active KB integration.
        6. **Empirical Evaluation Benchmark:** Evaluate authentic diagnostic test datasets without fabricated or hardcoded results.
        """)

        st.subheader("3. Technologies & Stack")
        st.markdown("""
        - **Language:** Python 3.12 (Strict typing, dataclasses, functional recursion)
        - **User Interface:** Streamlit (Dynamic session state, responsive layout)
        - **Knowledge Representation:** JSON-based declarative schema
        - **Data Analysis & Evaluation:** Pandas
        - **Visualizations:** Plotly Interactive Charts
        - **Automated Verification:** Pytest (34 passing test suites)
        """)

    with tab_arch:
        st.subheader("System Architecture")
        st.markdown("""
        The system follows a strict layered separation of concerns:
        ```
        +-------------------------------------------------------------------+
        |                       STREAMLIT UI LAYER                          |
        |  Dashboard | Diagnosis | KB Explorer | Expert Review | Evaluation |
        +---------------------------------+---------------------------------+
                                          |
        +---------------------------------v---------------------------------+
        |                    INFERENCE & REASONING ENGINE                   |
        |   - Multi-Level Backward Chaining   - Intermediate Fact Deriver   |
        |   - Cycle Detection (Call Stack)    - Conflict & Ruled-Out Tracker|
        +------------------+------------------------------+-----------------+
                           |                              |
        +------------------v--------------+ +-------------v-----------------+
        |   QUESTION SELECTION HEURISTIC  | |   EXPERT REVIEW & LEARNING    |
        |   Score = min(yes_count, no)    | |   Validation & Duplicate Check|
        +------------------+--------------+ +-------------+-----------------+
                           |                              |
        +------------------v------------------------------v-----------------+
        |                      KNOWLEDGE BASE (JSON)                        |
        |   Baseline KB (Protected)   <--->   Active KB (Expert Enriched)   |
        +-------------------------------------------------------------------+
        ```
        """)

        st.subheader("Multi-Level Backward Chaining Mechanism")
        st.write("""
        Unlike forward chaining (which starts from known facts and derives everything possible), **backward chaining 
        is goal-driven**. It starts with a candidate diagnostic hypothesis (e.g. *DNS Server Resolution Failure*) 
        and inspects its required conditions. If a condition is an **intermediate fact** (e.g. *WAN Connectivity Present*), 
        the engine pushes the goal onto a recursive evaluation stack, seeks intermediate rules that derive that fact, 
        and resolves the sub-conditions down to observable symptoms.
        """)

        st.subheader("Min-Split Question Selection Heuristic")
        st.write("""
        To avoid asking questions in an arbitrary or fixed sequence, the system computes for every candidate symptom $C$:
        $$\\text{Score}(C) = \\min(\\text{yes\\_count}(C), \\text{no\\_count}(C))$$
        Where $\\text{yes\\_count}$ is the number of viable hypotheses requiring $C=\\text{YES}$, and $\\text{no\\_count}$ 
        is the number requiring $C=\\text{NO}$. Maximizing this minimum count selects the question that partitions 
        competing hypotheses most evenly, similar to an optimal binary search tree.
        """)

    with tab_viva:
        st.subheader("Sample Viva Questions & Model Answers")

        with st.expander("Q1: What is the difference between Forward Chaining and Backward Chaining?"):
            st.write("""
            **Answer:**
            - **Forward Chaining (Data-Driven):** Starts from known facts and applies inference rules to extract all possible conclusions until no more rules can fire. Best suited for monitoring and planning.
            - **Backward Chaining (Goal-Driven):** Starts with a specific hypothesis or goal and works backward to find supporting facts or sub-goals. Best suited for diagnostic expert systems because it only queries symptoms relevant to current candidate hypotheses.
            """)

        with st.expander("Q2: How does your system handle circular dependencies in rules?"):
            st.write("""
            **Answer:**
            The engine maintains an active goal recursion set (`call_stack: Set[str]`). When an intermediate fact is requested, 
            the engine checks if that fact is already in the `call_stack`. If present, a circular dependency is detected; 
            the branch is immediately aborted, a cycle warning is appended to the reasoning trace, and infinite recursion (stack overflow) is prevented.
            """)

        with st.expander("Q3: Why is the match score NOT presented as a probability?"):
            st.write("""
            **Answer:**
            Presenting a rule match score as a probability is mathematically misleading unless rigorous Bayesian prior and posterior distributions have been empirically sampled. 
            Our expert system explicitly calculates and presents **Evidence Coverage** (e.g., *67% coverage: 2 of 3 conditions satisfied*), which transparently reflects the ratio of proven conditions without fabricating probabilistic certainty.
            """)

        with st.expander("Q4: How does the system handle 'Not Sure / Skip' answers without breaking reasoning?"):
            st.write("""
            **Answer:**
            When a user selects *Not Sure / Skip*, the fact's state is assigned `UNKNOWN`. The inference engine does not treat `UNKNOWN` as False, so the rule is not falsely ruled out. 
            However, it does not treat it as True, so the condition remains unverified. If sufficient differentiating facts remain, the engine continues asking other questions; otherwise, it reports `INSUFFICIENT_EVIDENCE`.
            """)

        with st.expander("Q5: How does Knowledge-Base Learning protect against malicious or corrupt rules?"):
            st.write("""
            **Answer:**
            The system employs a strict 7-step governance lifecycle:
            1. Rule Submission
            2. Structural Validation
            3. Duplicate & Overlap Detection
            4. Expert Peer Approval (unapproved rules remain inactive)
            5. Integration into the Active Knowledge Base
            6. Graph Consistency & Deadlock Verification
            7. Full Audit Logging with timestamps and reviewer identity.
            Furthermore, the baseline factory knowledge base is read-only and protected against modification.
            """)
