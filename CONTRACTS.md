# Component Contracts

This document defines the strict interfaces for the primary agents in the Health Insurance Claims Processing System. Each agent inherits from a `BaseAgent` class, ensuring standard error handling, confidence tracking, and trace logging.

---

### 1. DocumentClassifierAgent
**Responsibility:** Identifies the type of uploaded medical documents (e.g., Hospital Bill, Prescription) using vision models.
* **Input:** `ClaimContext` (Contains a list of `Document` objects with raw file bytes or storage URLs).
* **Output:** Mutated `ClaimContext`. For each document, sets the `detected_type` attribute (Enum: `HOSPITAL_BILL`, `PRESCRIPTION`, `LAB_REPORT`, `UNKNOWN`).
* **Errors Raised:** * `google.genai.errors.APIError` (Caught by `BaseAgent` -> triggers graceful degradation).

### 2. DocumentVerificationAgent
**Responsibility:** Cross-references the uploaded document types against the mandatory requirements for the given `ClaimCategory` in the policy terms.
* **Input:** `ClaimContext` (Requires documents to have a `detected_type` and the claim to have a `claim_category`).
* **Output:** Mutated `ClaimContext`. 
  * If valid: Proceeds normally.
  * If invalid: Sets `context.state.is_halted = True`, populates `context.state.halt_reason = "MISSING_REQUIRED_DOCUMENT"`, and appends an actionable error string to the trace.
* **Errors Raised:** Bypasses exceptions natively, acting as a strict gating mechanism before expensive OCR steps.

### 3. OCRExtractionAgent
**Responsibility:** Extracts structured medical and financial data from the verified documents.
* **Input:** `ClaimContext` (Only processes documents that passed verification).
* **Output:** Mutated `ClaimContext`. Populates `doc.extracted_data` with a strict Pydantic `OcrOutputSchema` (includes `patient_name`, `date`, `hospital_name`, `line_items`, `total_amount`).
* **Errors Raised:** * `pydantic.ValidationError` (If the LLM hallucinates malformed types).
  * `RateLimitError` / `429 Quota Exceeded` (Caught by `BaseAgent`, reduces system confidence by 15%, allows pipeline to continue).

### 4. CrossValidationAgent
**Responsibility:** Deterministically verifies that the patient identity extracted from the documents matches the member's profile.
* **Input:** `ClaimContext` (Requires hydrated `MemberData` and `doc.extracted_data`).
* **Output:** Mutated `ClaimContext`. Halts pipeline with `IDENTITY_MISMATCH` if fuzzy string matching falls below the acceptable threshold.
* **Errors Raised:** None (Deterministic execution).

### 5. FraudDetectionAgent
**Responsibility:** Evaluates velocity heuristics and claim value thresholds to flag suspicious activity.
* **Input:** `ClaimContext` (Requires hydrated `claims_history` for the member).
* **Output:** Mutated `ClaimContext`. If thresholds are breached (e.g., >2 claims in 24 hours), appends a flag to `context.result.notes` and sets a recommendation for `MANUAL_REVIEW`.
* **Errors Raised:** None (Deterministic execution).

### 6. PolicyEvaluationAgent
**Responsibility:** The core deterministic math engine. Executes financial adjudication based strictly on the JSON policy rules.
* **Input:** `ClaimContext` (Contains fully extracted OCR data, member enrollment dates, and policy terms).
* **Output:** Mutated `ClaimContext`. Calculates the exact financial payout by sequentially applying: *Waiting Periods -> Pre-Auth -> Network Discounts -> Exclusions -> Sub-limits -> Co-pays*. Updates `context.result.approved_amount`.
* **Errors Raised:** `TypeError`, `ValueError` (If corrupted data bypasses upstream validation).

### 7. DecisionAgent
**Responsibility:** Synthesizes the outputs of all previous steps to formulate the final routing decision.
* **Input:** `ClaimContext` (All prior agent outputs and trace logs).
* **Output:** Final `ClaimResponse` payload containing:
  * `status`: `APPROVED`, `PARTIAL`, `REJECTED`, or `MANUAL_REVIEW`
  * `approved_amount`: Float
  * `confidence_score`: Float (0.0 to 1.0)
  * `execution_trace`: Array of step-by-step audit logs.
* **Errors Raised:** None (Terminal node).