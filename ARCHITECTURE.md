Here is the complete, final Markdown for your **`ARCHITECTURE.md`** file. You can copy everything inside this block, from the first `#` to the very end, and paste it directly into your project to replace the old version.

```markdown
# Architecture & System Design

## Core Philosophy: The AI-Deterministic Split
The most critical architectural decision in this system is the strict separation between probabilistic extraction and deterministic financial calculation. Large Language Models (LLMs) are exceptional at reading messy, unstructured medical documents, but they hallucinate math and policy logic. 

To solve this, the architecture is split into two distinct phases:
1. **Multi-Agent Processing Layer (Probabilistic):** Uses specialized LLM agents strictly for document classification, OCR, and unstructured data extraction.
2. **Policy Engine (Deterministic):** A strict, zero-AI Python math engine that executes rule adjudication and financial calculations based on JSON policy definitions.

---

## System Architecture Diagram

```text
       [React Frontend (Vercel)]
                  │ (REST API via HTTPS)
                  ▼
 [FastAPI Backend (Azure Container Apps)]
                  │
                  ▼
           [ClaimService]
   (Gateway & Context Hydration)
                  │
                  ▼
   [DocumentClassifierAgent] 
 (AI Vision: Identifies Document Types)
                  │
                  ▼
   [DocumentVerificationAgent] 
 (AI Vision: Validates Required Docs)
                  │
                  ▼
     [OCRExtractionAgent] 
(AI Vision: Extracts Structured JSON)
                  │
                  ▼
     [CrossValidationAgent] 
(Deterministic: Identity Matching)
                  │
                  ▼
      [FraudDetectionAgent] 
(Deterministic: Velocity & Limits)
                  │
                  ▼
    [PolicyEvaluationAgent] 
 (Deterministic: Financial Math)
                  │
                  ▼
          [DecisionAgent] 
  (Final Routing & Verdict Logic)
                  │
                  ▼
       [Response + Trace Payload]

```

## Component Breakdown & Pipeline Flow

The system processes claims sequentially through an orchestrated multi-agent workflow. Each component has a single, well-defined responsibility:

* **ClaimService (The Gateway):** Accepts the REST API request, securely stores uploaded files, hydrates the member's profile and policy terms, and builds the initial `ClaimContext`.
* **DocumentClassifierAgent:** Analyzes the uploaded images to classify them into standard enums (e.g., HOSPITAL_BILL, PRESCRIPTION).
* **DocumentVerificationAgent:** Cross-references the uploaded document types against the policy's required documents for the specific claim category. It acts as a "Shift-Left" validation gate, halting early with actionable feedback if mandatory files are missing.
* **OCRExtractionAgent:** The heaviest AI component. Uses Gemini 2.5 Flash to extract medical and financial data into strict Pydantic schemas.
* **CrossValidationAgent:** A deterministic validation step that verifies the patient identity on the extracted documents perfectly matches the primary policyholder or dependent's identity.
* **FraudDetectionAgent:** Evaluates velocity heuristics and claim value thresholds to flag suspicious claims for manual intervention.
* **PolicyEvaluationAgent:** The core math engine. Maps the extracted JSON into strict models and executes financial adjudication in exact chronological order: *Waiting Periods -> Pre-Auth -> Network Discounts -> Exclusions -> Limits -> Co-pays.*
* **DecisionAgent:** Synthesizes the outputs of all previous steps, evaluates the system's ongoing confidence score, and formulates the final routing decision (`APPROVED`, `PARTIAL`, `REJECTED`, or `MANUAL_REVIEW`).

---

## Key Architectural Decisions

### 1. Why AI Does Not Perform Financial Calculations

LLMs are utilized exclusively for perception tasks (document understanding). All financial adjudication is deterministic. Using an LLM to calculate an insurance payout introduces unacceptable risks regarding reproducibility. By shifting math entirely into pure Python code, we guarantee:

* **Auditability:** Every math step is explicitly logged in the trace.
* **Reproducibility:** The same input will yield the exact same financial output 100% of the time.
* **Safety:** Zero risk of an AI hallucinating an unauthorized payout or misinterpreting a sub-limit.

### 2. Resilience, Caching & Graceful Degradation

External AI services are prone to transient errors (503s) and rate limits (429s). This system implements a multi-layered defense mechanism to ensure high availability:

* **Exponential Backoff Retries:** All Gemini API calls are wrapped in a `@retry` decorator to automatically handle transient network hiccups without failing the claim.
* **MD5 Hashing Cache:** To reduce latency and API costs, identical document and prompt combinations are hashed and cached locally.
* **BaseAgent Fallbacks:** If an LLM completely exhausts its retries, the `BaseAgent` traps the exception. Instead of returning a 500 Server Error, it logs the failure to the trace, applies a confidence penalty, and allows the deterministic pipeline to finish using available data.

---

## Scaling to Production Workloads (10x Load)

The current prototype utilizes local storage and sequential execution for development speed. To scale this architecture to enterprise production volumes:

1. **Parallel Execution:** The `DocumentClassifierAgent` and `DocumentVerificationAgent` are currently sequential. I would utilize `asyncio.gather` to run independent AI agents concurrently, significantly reducing TTFB (Time to First Byte).
2. **Stateless Compute & Caching:** Replace the local file cache with a distributed Redis cluster, and replace the in-memory/SQLite state with Azure Database for PostgreSQL.
3. **Configurable Rules Engine:** Move the deterministic policy evaluation from hardcoded Python into a dedicated rules engine (like Drools or a custom AST parser) to support thousands of different employer policies without requiring code deployments.

---

## Component Contracts

### 1. DocumentVerificationAgent

* **Input:** `ClaimContext` (contains List of Document objects with Storage URLs).
* **Output:** Mutated `ClaimContext`. Sets `context.state.is_halted = True` and populates the rejection reason if required docs are missing.
* **Errors Raised:** Bypasses exceptions natively via `BaseAgent`, catching AI timeouts and degrading system confidence gracefully.

### 2. OCRExtractionAgent

* **Input:** `ClaimContext` (specifically validated Document objects).
* **Output:** Mutated `ClaimContext`. Populates `doc.extracted_data` with a structured `OcrOutputSchema` (line items, totals, dates).
* **Errors Raised:** Fails gracefully on 429/503 limits; Pydantic handles schema validation errors natively.

### 3. PolicyEvaluationAgent

* **Input:** Hydrated `ClaimContext` (containing OCR data, Member data, and Policy JSON rules).
* **Output:** `PolicyEvaluationResult` (Contains final decision string, calculated float amount, and an array of deterministic `TraceStep` explanations).
* **Errors Raised:** Raises validation errors if upstream AI models hallucinate malformed data types that bypass Pydantic coercions.

```

```