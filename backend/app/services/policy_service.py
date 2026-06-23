from datetime import date
from typing import List, Dict, Optional, Tuple
from pydantic import BaseModel, Field

# ==========================================
# 1. Pydantic Models (JSON Schema Accurate)
# ==========================================

class TraceStep(BaseModel):
    rule_name: str
    passed: bool
    notes: str
    amount_adjusted: float = 0.0

class LineItem(BaseModel):
    description: str
    amount: float

class PolicyEvaluationResult(BaseModel):
    decision: str  # "APPROVED", "PARTIAL", "REJECTED"
    approved_amount: float
    rejection_reasons: List[str] = []
    trace: List[TraceStep] = []

class MemberData(BaseModel):
    member_id: str
    join_date: date
    ytd_claims_amount: float = 0.0

class Coverage(BaseModel):
    sum_insured_per_employee: float
    annual_opd_limit: float
    per_claim_limit: float

class CategoryRules(BaseModel):
    sub_limit: float
    copay_percent: float
    network_discount_percent: float = 0.0
    pre_auth_threshold: Optional[float] = None
    excluded_procedures: List[str] = []

class WaitingPeriods(BaseModel):
    initial_waiting_period_days: int
    pre_existing_conditions_days: int
    specific_conditions: Dict[str, int]

class Exclusions(BaseModel):
    conditions: List[str]
    dental_exclusions: Optional[List[str]] = []
    vision_exclusions: Optional[List[str]] = []

class PreAuthorization(BaseModel):
    required_for: List[str]
    validity_days: int

class PolicyData(BaseModel):
    policy_id: str
    coverage: Coverage
    opd_categories: Dict[str, CategoryRules]
    waiting_periods: WaitingPeriods
    exclusions: Exclusions
    pre_authorization: PreAuthorization
    network_hospitals: List[str]

class ClaimData(BaseModel):
    claim_id: str
    treatment_date: date
    hospital_name: str
    diagnosis: str
    procedure_name: Optional[str] = None
    pre_auth_id: Optional[str] = None
    line_items: List[LineItem]
    category_name: str


# ==========================================
# 2. Deterministic Rule Functions
# ==========================================

def check_waiting_periods(claim: ClaimData, member: MemberData, policy: PolicyData) -> Tuple[bool, TraceStep]:
    """Rule 5: Enrollment & Disease Waiting Periods"""
    active_days = (claim.treatment_date - member.join_date).days
    
    required_days = policy.waiting_periods.initial_waiting_period_days
    applied_condition = "standard initial enrollment"

    # Substring match to handle complex diagnosis strings (e.g., "Type 2 Diabetes Mellitus")
    for condition, days in policy.waiting_periods.specific_conditions.items():
        if condition.lower().replace("_", " ") in claim.diagnosis.lower():
            required_days = days
            applied_condition = condition
            break
    
    if active_days <= required_days:
        return False, TraceStep(
            rule_name="Waiting Period Check",
            passed=False,
            notes=f"Member active for {active_days} days. Condition '{applied_condition}' requires {required_days} days.",
            amount_adjusted=0.0
        )
        
    return True, TraceStep(
        rule_name="Waiting Period Check",
        passed=True,
        notes=f"Cleared. Member active for {active_days} days (Requires {required_days} for {applied_condition})."
    )

def check_pre_authorization(claim: ClaimData, category: CategoryRules, policy: PolicyData, total_amount: float) -> Tuple[bool, TraceStep]:
    """Rule 6: Pre-Authorization Threshold Verification"""
    requires_auth = False
    trigger_reason = ""

    if claim.procedure_name:
        for req in policy.pre_authorization.required_for:
            if req.lower() in claim.procedure_name.lower():
                requires_auth = True
                trigger_reason = f"Procedure explicitly matched pre-auth requirement: '{req}'."
                break
    
    if not requires_auth and category.pre_auth_threshold and total_amount > category.pre_auth_threshold:
        requires_auth = True
        trigger_reason = f"Amount ₹{total_amount} exceeds category pre-auth threshold of ₹{category.pre_auth_threshold}."

    if requires_auth and not claim.pre_auth_id:
        return False, TraceStep(
            rule_name="Pre-Authorization Check",
            passed=False,
            notes=f"Pre-auth missing. {trigger_reason}"
        )
        
    return True, TraceStep(
        rule_name="Pre-Authorization Check",
        passed=True,
        notes="No pre-auth required, or valid token provided."
    )

def apply_network_discount(claim: ClaimData, category: CategoryRules, policy: PolicyData, base_amount: float) -> Tuple[float, TraceStep]:
    """Rule 7: Network Hospital Tariff Discounts"""
    if claim.hospital_name in policy.network_hospitals:
        discount_amount = base_amount * (category.network_discount_percent / 100)
        discounted_total = base_amount - discount_amount
        return discounted_total, TraceStep(
            rule_name="Network Discount",
            passed=True,
            notes=f"Applied {category.network_discount_percent}% discount for network hospital: {claim.hospital_name}.",
            amount_adjusted=-discount_amount
        )
        
    return base_amount, TraceStep(
        rule_name="Network Discount",
        passed=True,
        notes=f"Hospital '{claim.hospital_name}' is out-of-network. No base discount applied."
    )

def apply_exclusions(claim: ClaimData, category: CategoryRules, policy: PolicyData, current_amount: float) -> Tuple[float, TraceStep]:
    """Rule 8: Category & Procedural Exclusions"""
    excluded_sum = 0.0
    rejected_items = []
    
    # Aggregate global, category-specific, and JSON-nested exclusions
    raw_exclusions = policy.exclusions.conditions + category.excluded_procedures
    
    cat_key = claim.category_name.lower()
    if cat_key == "dental" and policy.exclusions.dental_exclusions:
        raw_exclusions.extend(policy.exclusions.dental_exclusions)
    elif cat_key == "vision" and policy.exclusions.vision_exclusions:
        raw_exclusions.extend(policy.exclusions.vision_exclusions)

    all_exclusions = [e.lower() for e in raw_exclusions]

    for item in claim.line_items:
        is_excluded = any(excl in item.description.lower() for excl in all_exclusions)
        if is_excluded:
            excluded_sum += item.amount
            rejected_items.append(item.description)

    new_amount = current_amount - excluded_sum
    
    if excluded_sum > 0:
        return new_amount, TraceStep(
            rule_name="Exclusions Application",
            passed=False, 
            notes=f"Excluded ₹{excluded_sum} for non-payable items: {', '.join(rejected_items)}.",
            amount_adjusted=-excluded_sum
        )

    return new_amount, TraceStep(
        rule_name="Exclusions Application",
        passed=True,
        notes="No excluded line items found."
    )

def apply_limits(claim: ClaimData, current_amount: float, category: CategoryRules, policy: PolicyData, member: MemberData) -> Tuple[float, TraceStep, Optional[str]]:
    """Rule 9: Multi-Level Policy Limits Check (Enforces Hard Rejections)"""
    
    # TC006 Fix: Specific category sub-limits override the general per-claim limit if they are higher.
    effective_per_claim_limit = max(policy.coverage.per_claim_limit, category.sub_limit)
    
    if current_amount > effective_per_claim_limit:
        return 0.0, TraceStep(
            rule_name="Per Claim Limit Check",
            passed=False,
            notes=f"Requested amount ₹{current_amount} breaches effective per-claim limit.",
            amount_adjusted=-current_amount
        ), "PER_CLAIM_EXCEEDED"

    # Soft Limit check: Sub-limits and annual limits cap the allowable payout.
    remaining_annual = policy.coverage.annual_opd_limit - member.ytd_claims_amount
    
    ceilings = {
        "Requested Amount": current_amount,
        "Remaining Annual Limit": remaining_annual
    }
    
    # TC010 Fix: Network hospitals bypass the category sub-limit
    if claim.hospital_name not in policy.network_hospitals:
        ceilings["Category Sub-Limit"] = category.sub_limit
        
    limiting_factor = min(ceilings, key=ceilings.get)
    capped_amount = ceilings[limiting_factor]
    reduction = current_amount - capped_amount

    if reduction > 0:
        return capped_amount, TraceStep(
            rule_name="Policy Limits Check",
            passed=False,
            notes=f"Amount capped at ₹{capped_amount} due to {limiting_factor}.",
            amount_adjusted=-reduction
        ), "LIMIT_EXCEEDED" # Returns string flag so orchestrator knows to mark PARTIAL

    return capped_amount, TraceStep(
        rule_name="Policy Limits Check",
        passed=True,
        notes="Amount is well within all sub-limits and annual caps."
    ), None

def apply_copay(current_amount: float, category: CategoryRules) -> Tuple[float, TraceStep]:
    """Rule 10: Final Category Co-Pay"""
    if category.copay_percent > 0:
        patient_share = current_amount * (category.copay_percent / 100)
        final_payout = current_amount - patient_share
        return final_payout, TraceStep(
            rule_name="Co-Pay Deduction",
            passed=True,
            notes=f"Deducted {category.copay_percent}% co-pay (₹{patient_share}).",
            amount_adjusted=-patient_share
        )
        
    return current_amount, TraceStep(
        rule_name="Co-Pay Deduction",
        passed=True,
        notes="No co-pay required for this category."
    )


# ==========================================
# 3. Main Adjudication Orchestrator
# ==========================================

def evaluate_claim(claim: ClaimData, member: MemberData, policy: PolicyData) -> PolicyEvaluationResult:
    trace_log = []
    reasons = []
    
    category = policy.opd_categories.get(claim.category_name.lower())
    if not category:
         return PolicyEvaluationResult(decision="REJECTED", approved_amount=0.0, rejection_reasons=["INVALID_CATEGORY"], trace=[])

    raw_total = sum(item.amount for item in claim.line_items)

    # --- Phase 1: Gatekeeping Rules ---
    passed_waiting, trace_step = check_waiting_periods(claim, member, policy)
    trace_log.append(trace_step)
    if not passed_waiting:
        reasons.append("WAITING_PERIOD")
        return PolicyEvaluationResult(decision="REJECTED", approved_amount=0.0, rejection_reasons=reasons, trace=trace_log)

    passed_auth, trace_step = check_pre_authorization(claim, category, policy, raw_total)
    trace_log.append(trace_step)
    if not passed_auth:
        reasons.append("PRE_AUTH_MISSING")
        return PolicyEvaluationResult(decision="REJECTED", approved_amount=0.0, rejection_reasons=reasons, trace=trace_log)


    # --- Phase 2: Mathematical Adjudication ---
    current_amount = raw_total

    current_amount, trace_step = apply_network_discount(claim, category, policy, current_amount)
    trace_log.append(trace_step)

    current_amount, trace_step = apply_exclusions(claim, category, policy, current_amount)
    trace_log.append(trace_step)
    if trace_step.passed is False:
        reasons.append("PARTIAL_EXCLUSIONS")

    if current_amount <= 0:
        reasons.append("EXCLUDED_CONDITION")
        return PolicyEvaluationResult(decision="REJECTED", approved_amount=0.0, rejection_reasons=reasons, trace=trace_log)

    # Multi-Level Limits (Handles Hard Rejections vs Soft Caps)
    current_amount, trace_step, limit_flag = apply_limits(claim, current_amount, category, policy, member)
    trace_log.append(trace_step)
    
    if limit_flag == "PER_CLAIM_EXCEEDED":
        reasons = ["PER_CLAIM_EXCEEDED"] # Override other partial reasons
        return PolicyEvaluationResult(decision="REJECTED", approved_amount=0.0, rejection_reasons=reasons, trace=trace_log)
    elif limit_flag == "LIMIT_EXCEEDED":
        reasons.append("LIMIT_EXCEEDED")

    final_amount, trace_step = apply_copay(current_amount, category)
    trace_log.append(trace_step)

    # --- Final Decision Formulation ---
    decision = "APPROVED"
    if reasons:  
        decision = "PARTIAL"
        
    return PolicyEvaluationResult(
        decision=decision,
        approved_amount=round(final_amount, 2),
        rejection_reasons=reasons,
        trace=trace_log
    )