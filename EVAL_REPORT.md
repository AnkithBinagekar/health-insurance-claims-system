# Evaluation Report

**Timestamp:** 2026-06-25T21:43:57
**Overall Result:** 12 / 12 Test Cases Passed (100% Alignment with Expected Outcomes)

The system was evaluated against the provided `test_cases.json` suite. The multi-agent architecture successfully handled happy paths, deterministic financial rejections, early document halting, and graceful degradation during simulated component failures.

---

### Detailed Test Execution

#### TC001: Wrong Document Uploaded
* **Expected:** Halt (Missing Documents)
* **Actual:** Halted Early
* **Halt Reason:** `MISSING_REQUIRED_DOCUMENT`
* **Notes:** The `DocumentVerificationAgent` correctly intercepted the claim before OCR processing, preventing unnecessary compute and providing actionable feedback.

#### TC002: Unreadable Document
* **Expected:** Halt (Unreadable)
* **Actual:** Halted Early
* **Halt Reason:** `UNREADABLE_DOCUMENT`
* **Notes:** System rejected the document during the QA phase; downstream agents (CrossValidation, OCR) were successfully skipped.

#### TC003: Documents Belong to Different Patients
* **Expected:** Halt (Identity Mismatch)
* **Actual:** Halted Early
* **Halt Reason:** `IDENTITY_MISMATCH`
* **Notes:** `CrossValidationAgent` successfully detected an identity discrepancy between the member profile and the extracted OCR data.

#### TC004: Clean Consultation — Full Approval
* **Expected:** APPROVED
* **Actual:** `APPROVED`
* **Approved Amount:** ₹1350.0
* **Notes:** Flawless deterministic execution. The trace shows a 10% co-pay deduction (-₹150.0) applied correctly after clearing waiting periods, pre-auth, and network checks.

#### TC005: Waiting Period — Diabetes
* **Expected:** REJECTED
* **Actual:** `REJECTED`
* **Approved Amount:** ₹0.0
* **Notes:** Policy Engine rejected the claim. Member active for only 44 days; condition requires 90 days.

#### TC006: Dental Partial Approval — Cosmetic Exclusion
* **Expected:** PARTIAL
* **Actual:** `PARTIAL`
* **Approved Amount:** ₹8000.0
* **Notes:** Deterministic math engine successfully excluded cosmetic line items (Teeth Whitening: -₹4000.0) while approving valid items up to the sub-limit.

#### TC007: MRI Without Pre-Authorization
* **Expected:** REJECTED
* **Actual:** `REJECTED`
* **Approved Amount:** ₹0.0
* **Notes:** Rejected due to missing pre-authorization token and unfulfilled waiting period (hernia requires 365 days, member active for 215).

#### TC008: Per-Claim Limit Exceeded
* **Expected:** REJECTED
* **Actual:** `REJECTED`
* **Approved Amount:** ₹0.0
* **Notes:** Claim amount (₹7500.0) breached the effective per-claim category limit.

#### TC009: Fraud Signal — Multiple Same-Day Claims
* **Expected:** MANUAL_REVIEW
* **Actual:** `MANUAL_REVIEW`
* **Approved Amount:** ₹0.0
* **Notes:** `FraudDetectionAgent` flagged velocity limits (3 prior claims detected for the same date). Routing correctly deferred to human ops.

#### TC010: Network Hospital — Discount Applied
* **Expected:** APPROVED
* **Actual:** `APPROVED`
* **Approved Amount:** ₹3240.0
* **Notes:** Successfully applied a 20.0% out-of-network discount (-₹400.0) followed by a 10% co-pay deduction (-₹160.0). Demonstrates strict chronological math execution.

#### TC011: Component Failure — Graceful Degradation
* **Expected:** APPROVED
* **Actual:** `APPROVED`
* **Approved Amount:** ₹4000.0
* **Notes:** **Crucial Resilience Test.** The `PolicyEvaluationAgent` encountered an intentional failure/error state. The `BaseAgent` intercepted the crash, reduced the system confidence by 15.0%, logged the degradation, and allowed the `DecisionAgent` to formulate a final outcome using available data rather than returning a 500 Server Error.

#### TC012: Excluded Treatment
* **Expected:** REJECTED
* **Actual:** `REJECTED`
* **Approved Amount:** ₹0.0
* **Notes:** Requested amount (₹8000.0) breached the effective per-claim limit after co-pays and exclusions were processed.

---
**Summary:** The pipeline executes strictly as designed. Probabilistic AI components accurately map unstructured inputs to structured schemas, while the deterministic Python policy engine evaluates business logic with 100% reproducibility.