# Plum AI Pod: Intelligent Claims Processing Engine

## 🏗️ System Architecture
This project implements a **Multi-Agentic Pipeline** that strictly separates probabilistic AI extraction from deterministic financial execution.

1. **The Perception Layer (AI):** Uses Gemini 2.5 Vision to classify documents, verify missing files (Early Catch), and extract unstructured text into strictly typed JSON (Pydantic).
2. **The Logic Layer (Deterministic):** A pure Python rule-engine that applies policy rules, cascading sub-limits, network discounts, and co-pays. **The AI never does financial math.**

## 🔍 Observability & Auditing
To ensure the operations team trusts the AI, I implemented two major observability features:
* **The Confidence Ledger:** Every agent logs its base confidence and applies percentage penalties for errors or missing data. If confidence drops below a threshold, the claim is auto-routed to `MANUAL_REVIEW`.
* **Spatial Bounding Boxes:** The UI maps normalized `[ymin, xmin, ymax, xmax]` coordinates from the LLM directly onto the React frontend, allowing auditors to hover over data and see exactly where the AI extracted it from the medical bill.

## 🤔 Design Decisions & Trade-offs (What I Rejected)
**Considered & Rejected: DeepSeek R1 for Semantic Policy Reasoning.**
I heavily considered using DeepSeek R1's Chain-of-Thought to reason through complex medical exclusions (e.g., *Is this rhinoplasty cosmetic or trauma-related?*). However, I made the **conscious trade-off** to cut this from the MVP. 
1. **Latency:** CoT models introduce a 15–30s latency block, which heavily degrades the synchronous UX for ops agents waiting for a result. 
2. **Compliance:** Keeping the core logic strictly within a Python engine completely eliminates the risk of an LLM hallucinating an insurance payout. 

## 🚀 Scaling to 10x Load
If Plum deploys this to hundreds of concurrent hospitals/users, the current synchronous FastAPI architecture will hit immediate rate limits (as seen with Gemini's 429 errors during testing).
To solve this, I would pivot to an **Asynchronous Event-Driven Architecture**:
1. Move the API to an API Gateway that drops claims into a **Redis / Celery task queue**.
2. Background workers process the LLM calls safely using exponential backoff (`tenacity`).
3. The frontend subscribes to a **WebSocket** or Server-Sent Events (SSE) to update the UI progress bar in real-time as the agents complete their work.