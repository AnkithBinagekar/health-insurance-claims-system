```markdown
# Plum AI Pod: Intelligent Claims Processing Engine

An intelligent, orchestrated health insurance claims processing system. This platform automates the ingestion, extraction, and deterministic financial adjudication of medical claims, producing highly explainable decisions.

## 🏆 Evaluation Results

The system was validated against the provided evaluation suite.

**Result: 12 / 12 Test Cases Passed**

The evaluation covered:
* Document validation
* Identity verification
* Waiting period enforcement
* Pre-authorization checks
* Fraud detection
* Partial approvals
* Network discounts
* Graceful degradation
* Explainable decision traces

> **Note:** The full evaluation report can be found in `eval_report.json`.

---

## 🏗️ Why This Architecture

This project implements an **Orchestrated Multi-Agent Architecture** designed specifically for high-compliance environments. 

* **Strict AI-Deterministic Separation:** Google Gemini models are used for document understanding, classification, legibility assessment, and structured information extraction. Deterministic policy evaluation is always executed by Python code. The AI **never** performs financial math. All policy rules, sub-limits, network discounts, and co-pays are evaluated by a pure Python rule-engine. This completely eliminates the risk of hallucinated payouts.
* **Explainability and Observability:** Black-box decisions are unacceptable in claims processing. Every agent logs its actions to an observability trace. The UI utilizes these traces to render human-readable operations logs and spatial bounding boxes (mapping normalized coordinates from the LLM directly onto the document), allowing human auditors to understand exactly *why* a decision was reached.
* **Production Scaling Path on Azure:** The FastAPI orchestration layer is designed to run statelessly on Azure App Services, ready to integrate with Azure Blob Storage (for document ingestion) and Azure Service Bus (to decouple long-running LLM extraction tasks from the synchronous HTTP request).

---

## 🤔 Design Decisions & Trade-offs (What I Rejected)

**Considered & Rejected: DeepSeek R1 for Semantic Policy Reasoning.**
I heavily considered using an advanced reasoning model (like DeepSeek R1's Chain-of-Thought) to reason through complex medical exclusions dynamically (e.g., *Is this rhinoplasty cosmetic or trauma-related?*). However, I made the conscious trade-off to cut this from the MVP. 
1. **Latency:** CoT models introduce a 15–30s latency block, which heavily degrades the synchronous UX for ops agents waiting for a result. 
2. **Compliance:** Hardcoding the core policy logic into a strictly typed Python engine offers significantly better predictability and auditability for an MVP than a probabilistic reasoning approach.

---