# Architecture & System Design

## Core Philosophy: The AI-Deterministic Split
The most critical architectural decision in this system is the strict separation between probabilistic extraction and deterministic financial calculation. Large Language Models (LLMs) are exceptional at reading messy, unstructured medical documents, but they hallucinate math and policy logic. 

To solve this, the architecture is split into two phases:
1. **Agentic Pipeline (Probabilistic):** Uses LLMs strictly for OCR, quality assessment, and data extraction.
2. **Policy Engine (Deterministic):** A strict, zero-AI Python math engine (`policy_service.py`) that executes sub-limits, network discounts, and co-pays.

## Component Breakdown & Pipeline Flow
The system processes claims sequentially through an Orchestrator:

1. **ClaimService (The Gateway):** Accepts the REST API request, securely stores the uploaded files, hydrates the member's profile and policy terms from the data layer, and builds the `ClaimContext`.
2. **DocumentVerificationAgent:** Uses Gemini Flash to assess image legibility and checks if the uploaded document types match the policy's required documents for the specific claim category.
3. **CrossValidationAgent:** A deterministic agent that verifies the identity on the extracted documents matches the policyholder's identity. 
4. **FraudDetectionAgent:** Evaluates velocity heuristics (e.g., multiple claims on the same day) and claim value thresholds to route suspicious claims to `MANUAL_REVIEW`.
5. **DecisionAgent & Policy Engine:** Maps the extracted JSON into strict Pydantic models and executes the financial adjudication in exact chronological order (Waiting Periods -> Pre-Auth -> Network Discounts -> Exclusions -> Limits -> Co-pay).

## Scaling to 10x Load
The current prototype utilizes in-memory state (`DB_CLAIMS_STORE`) and local disk storage (`temp_uploads`) for speed of development. To scale this to process 75,000+ claims:

1. **Stateless Compute:** The FastAPI backend would be containerized and deployed across auto-scaling instances (e.g., AWS EC2 or ECS). 
2. **Persistent Blob Storage:** Local file uploads would be replaced by streaming the multipart forms directly to AWS S3, passing only the signed URLs through the AI pipeline.
3. **Asynchronous Message Queues:** Heavy LLM extraction tasks would be decoupled from the synchronous HTTP request using Celery and Redis/RabbitMQ. The frontend would receive a `task_id` and poll (or use WebSockets) for the final decision.
4. **Distributed Tracing:** The `AgentTrace` array would be piped into an observability platform like Datadog or ELK to monitor AI confidence degradation across the fleet.

---

## Component Contracts

### 1. DocumentVerificationAgent
* **Input:** `ClaimContext` (contains List of `Document` objects with Storage URLs).
* **Output:** Mutated `ClaimContext`. Flags `doc.is_readable` and sets `context.state.is_halted = True` if required docs are missing.
* **Errors Raised:** Bypasses exceptions natively, catching Gemini API timeouts and degrading system confidence gracefully.

### 2. FraudDetectionAgent
* **Input:** `ClaimContext` (requires `hydrated.claims_history` and `input.claimed_amount`).
* **Output:** Mutated `ClaimContext`. Appends `Fraud Signal` notes to `context.result.notes` if thresholds are breached.
* **Errors Raised:** None (Deterministic execution).

### 3. PolicyService (`evaluate_claim`)
* **Input:** `ClaimData`, `MemberData`, `PolicyData` (Strict Pydantic Models).
* **Output:** `PolicyEvaluationResult` (Contains final `APPROVED/PARTIAL/REJECTED` string, calculated float amount, and an array of `TraceStep` explanations).
* **Errors Raised:** Raises validation errors if upstream agents provide malformed data types (caught safely by Pydantic before math execution).