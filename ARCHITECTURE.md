# Architecture & System Design

## Core Philosophy: The AI-Deterministic Split
The most critical architectural decision in this system is the strict separation between probabilistic extraction and deterministic financial calculation. Large Language Models (LLMs) are exceptional at reading messy, unstructured medical documents, but they hallucinate math and policy logic. 

To solve this, the architecture is split into two distinct phases:
1. **Multi-Agent Processing Layer (Probabilistic):** Uses LLMs strictly for OCR, quality assessment, and unstructured data extraction.
2. **Policy Engine (Deterministic):** A strict, zero-AI Python math engine (`policy_service.py`) that executes rule adjudication.

---

## Evaluation Outcome

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

---

## System Architecture Diagram

```text
       [React Frontend (Vercel)]
                  │ (REST API via HTTPS)
                  ▼
 [FastAPI Backend (Azure App Service)]
                  │
                  ▼
           [ClaimService]
   (Gateway & Context Hydration)
                  │
                  ▼
   [DocumentVerificationAgent] 
 (AI Vision: Legibility & QA Check)
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

       Component Breakdown & Pipeline Flow
The system processes claims sequentially through an orchestrated multi-agent workflow. Each component has a single, well-defined responsibility:

ClaimService (The Gateway): Accepts the REST API request, securely stores the uploaded files, hydrates the member's profile and policy terms from the data layer, and builds the initial ClaimContext.

DocumentVerificationAgent: Uses AI to assess image legibility. It cross-references the uploaded document types against the policy's required documents for the specific claim category, halting early with actionable feedback if required files are missing.

CrossValidationAgent: A deterministic validation step that verifies the patient identity on the extracted documents perfectly matches the primary policyholder or dependent's identity.

FraudDetectionAgent: Evaluates velocity heuristics (e.g., multiple claims on the same day) and claim value thresholds to flag suspicious claims for manual intervention.

PolicyEvaluationAgent: The core math engine. Maps the extracted JSON into strict Pydantic models and executes financial adjudication in exact chronological order: Waiting Periods -> Pre-Auth -> Network Discounts -> Exclusions -> Limits -> Co-pays.

DecisionAgent: Synthesizes the outputs of all previous steps, evaluates the system's ongoing confidence score, and formulates the final routing decision (APPROVED, PARTIAL, REJECTED, or MANUAL_REVIEW).

Key Architectural Decisions
Why AI Does Not Perform Financial Calculations
LLMs are utilized exclusively for document understanding and data extraction. All financial adjudication is deterministic. Using an LLM to calculate an insurance payout introduces unacceptable risks regarding reproducibility and hallucination. By shifting the calculation of Waiting Periods, Exclusions, Network Discounts, Co-pays, and Limits entirely into Python code (policy_service.py), we guarantee:

Auditability: Every math step is explicitly logged in the trace.

Reproducibility: The same input will yield the exact same financial output 100% of the time.

Safety: Zero risk of an AI hallucinating an unauthorized payout or misinterpreting a sub-limit.

Graceful Degradation & Fault Tolerance
In a production environment, individual components (like external LLM APIs) will inevitably time out or fail. The system is designed so that component failures do not crash the pipeline.

If a non-critical component fails, processing continues using the information that remains available. The system records the failure in the trace, reduces confidence, and can append a recommendation for manual review while still executing deterministic policy evaluation where possible. This behavior was explicitly validated through TC011.

Deployment Architecture
The system utilizes a decoupled frontend / backend architecture, optimizing for both edge delivery and heavy compute:

Frontend (Vercel): The React Single Page Application (SPA) is deployed on Vercel. This provides global edge-CDN distribution for static assets, ensuring rapid load times for users uploading heavy medical documents.

Backend (Azure App Service / Container Apps): The FastAPI orchestration engine and deterministic math services run on Azure. Azure provides robust, scalable Python compute environments ideal for managing asynchronous AI workloads and heavy network I/O with the Google APIs.

Scaling to Production Workloads
The current assignment prototype utilizes in-memory state (DB_CLAIMS_STORE) and local disk storage (temp_uploads) for speed of development. To scale this architecture to enterprise production volumes:

Persistent Object Storage (Azure Blob Storage): Local file uploads would be replaced by having the Vercel frontend request a presigned URL and stream the multipart forms directly to Azure Blob Storage. The FastAPI backend would only pass lightweight SAS URLs through the processing layer, freeing up RAM.

Stateless Compute & State Management (Azure Database for PostgreSQL): The global Python dictionary used for state would be replaced by PostgreSQL. This allows the FastAPI application to scale horizontally across multiple Azure worker nodes without state fragmentation.

Asynchronous Message Queues (Azure Service Bus): Heavy LLM extraction tasks would be decoupled from the synchronous HTTP request. The frontend would receive a task_id and poll (or use WebSockets) for the final decision.

Distributed Tracing: The trace array would be piped into an observability platform (like Datadog or Application Insights) to monitor AI confidence degradation and token usage across the fleet.

Component Contracts
1. DocumentVerificationAgent
Input: ClaimContext (contains List of Document objects with Storage URLs).

Output: Mutated ClaimContext. Flags doc.is_readable and sets context.state.is_halted = True if required docs are missing.

Errors Raised: Bypasses exceptions natively, catching AI timeouts and degrading system confidence gracefully.

2. FraudDetectionAgent
Input: ClaimContext (requires hydrated.claims_history and input.claimed_amount).

Output: Mutated ClaimContext. Appends Fraud Signal notes to context.result.notes if thresholds are breached.

Errors Raised: None (Deterministic execution).

3. PolicyEvaluationAgent (evaluate_claim)
Input: ClaimData, MemberData, PolicyData (Strict Pydantic Models).

Output: PolicyEvaluationResult (Contains final APPROVED/PARTIAL/REJECTED string, calculated float amount, and an array of TraceStep explanations).

Errors Raised: Raises validation errors if upstream AI models hallucinate malformed data types (caught safely by Pydantic before math execution).