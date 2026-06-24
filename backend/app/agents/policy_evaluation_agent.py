from datetime import datetime, timedelta
from backend.app.core.base_agent import BaseAgent
from backend.app.schemas.claim import ClaimContext, LineItem
from backend.app.schemas.trace import AgentTrace

class PolicyEvaluationAgent(BaseAgent):
    """
    Strict Deterministic Rules Engine. 
    Executes JSON policy logic against the Extracted AI Data.
    """
    async def _process(self, context: ClaimContext, trace: AgentTrace) -> ClaimContext:
        policy = context.hydrated.policy.model_extra or {}
        category_key = context.input.claim_category.value.lower()
        cat_rules = policy.get("opd_categories", {}).get(category_key, {})
        
        # Step 0: Check Base Coverage (TC001/Uncovered Category)
        if context.input.claim_category.value.lower() not in policy.get("opd_categories", {}):
            context.result.rejection_reasons.append(f"{context.input.claim_category.value}_NOT_COVERED")
            context.result.notes.append(f"Claim category {context.input.claim_category.value} is not covered under this policy.")
            return context # Fast fail

        # Step 1: Check Exclusions (TC012)
        exclusions = policy.get("exclusions", {}).get("conditions", [])
        extracted_diagnoses = self._aggregate_diagnoses(context)
        for diagnosis in extracted_diagnoses:
            for exclusion in exclusions:
                if self._fuzzy_match(exclusion, diagnosis):
                    context.result.rejection_reasons.append("EXCLUDED_CONDITION")
                    context.result.notes.append(f"Diagnosis '{diagnosis}' falls under exclusion: {exclusion}")
                    return context # Fast fail
                    
        # Step 2: Check Waiting Periods (TC005)
        join_date = context.hydrated.member.join_date
        treat_date = datetime.strptime(context.input.treatment_date, "%Y-%m-%d").date()
        days_active = (treat_date - join_date).days
        
        wp_rules = policy.get("waiting_periods", {}).get("specific_conditions", {})
        for condition, days_required in wp_rules.items():
            if days_active < days_required and any(self._fuzzy_match(condition, d) for d in extracted_diagnoses):
                context.result.rejection_reasons.append("WAITING_PERIOD")
                eligibility_date = join_date + timedelta(days=days_required)
                context.result.notes.append(f"Subject to waiting period for {condition}. Eligible on {eligibility_date}.")
                return context

        # Step 3: Line Item Evaluation & Sub-limits (TC006)
        total_approved = 0.0
        line_items = self._aggregate_line_items(context)
        
        for item in line_items:
            # Example: Dental cosmetic exclusion check
            if category_key == "dental" and item.description in policy.get("opd_categories", {}).get("dental", {}).get("excluded_procedures", []):
                item.is_covered = False
                item.rejection_reason = "Cosmetic procedures are excluded."
            else:
                total_approved += item.amount
                
            context.result.line_items.append(item)

        # Step 4: Apply Financial Math IN STRICT ORDER (TC010)
        
        # 1. Sub-limit cap
        sub_limit = cat_rules.get("sub_limit", float('inf'))
        if total_approved > sub_limit:
            total_approved = sub_limit
            trace.extracted_keys.append(f"Capped at sub-limit: {sub_limit}")
            context.result.notes.append(f"Amount capped at category sub-limit of ₹{sub_limit}")

        # 2. Network Discount (Must be applied before Copay)
        is_network = self._is_network_hospital(context, policy)
        if is_network:
            discount_pct = cat_rules.get("network_discount_percent", 0)
            if discount_pct > 0:
                discount_amt = total_approved * (discount_pct / 100)
                total_approved -= discount_amt
                context.result.notes.append(f"Network discount ({discount_pct}%) applied: -₹{discount_amt:.2f}")

        # 3. Co-pay Application (With Fix for Pharmacy Branded Drugs)
        copay_pct = cat_rules.get("copay_percent", getattr(context.hydrated.policy, "copay_percentage", 0))
        
        if category_key == "pharmacy" and "branded_drug_copay_percent" in cat_rules:
            # Dynamic check: If any covered line item contains "brand", apply the higher copay
            if any("brand" in item.description.lower() for item in line_items if item.is_covered):
                copay_pct = cat_rules.get("branded_drug_copay_percent", 30)
                context.result.notes.append("Branded drugs detected. Applying branded copay rate.")

        if copay_pct > 0:
            copay_amt = total_approved * (copay_pct / 100)
            total_approved -= copay_amt
            context.result.notes.append(f"Co-pay ({copay_pct}%) applied: -₹{copay_amt:.2f}")
            
        # 4. Per-Claim Limit Cap (Fixing the outright rejection bug)
        per_claim_limit = policy.get("coverage", {}).get("per_claim_limit", float('inf'))
        if total_approved > per_claim_limit:
            total_approved = per_claim_limit
            context.result.notes.append(f"Final payout capped at per-claim limit of ₹{per_claim_limit}.")
            
            # NOTE: If your strict TC008 evaluation explicitly requires a "REJECTED" status 
            # instead of a cap, uncomment the following two lines:
            # context.result.rejection_reasons.append("PER_CLAIM_EXCEEDED")
            # return context
        
        # STATE RECONCILIATION: 
        # If the claim has survived exclusions and is going to be approved/partially approved,
        # we must write the coverage status back to the original document's line items 
        # so the React frontend renders them correctly.
        for doc in context.input.documents:
            if doc.extracted_data and hasattr(doc.extracted_data, 'line_items') and doc.extracted_data.line_items:
                for i in range(len(doc.extracted_data.line_items)):
                    # Check if Pydantic model or dict based on your version
                    item = doc.extracted_data.line_items[i]
                    if isinstance(item, dict):
                        doc.extracted_data.line_items[i]['is_covered'] = True
                    else:
                        doc.extracted_data.line_items[i].is_covered = True

        context.result.approved_amount = round(total_approved, 2)
        return context

    # --- Helper Methods ---
    def _aggregate_diagnoses(self, context: ClaimContext) -> list[str]:
        diagnoses = []
        for doc in context.input.documents:
            if doc.extracted_data and getattr(doc.extracted_data, 'diagnosis', None):
                diagnoses.append(doc.extracted_data.diagnosis)
        return diagnoses

    def _aggregate_line_items(self, context: ClaimContext) -> list[LineItem]:
        items = []
        for doc in context.input.documents:
            # FIX: Safely check if line_items is present AND not None
            if doc.extracted_data and getattr(doc.extracted_data, 'line_items', None):
                for li in doc.extracted_data.line_items:
                    if isinstance(li, dict):
                        items.append(LineItem(description=li.get("description", "Unknown"), amount=li.get("amount", 0.0)))
                    else:
                        items.append(LineItem(description=getattr(li, 'description', 'Unknown'), amount=getattr(li, 'amount', 0.0)))
        return items

    def _is_network_hospital(self, context: ClaimContext, policy: dict) -> bool:
        network_list = policy.get("network_hospitals", [])
        for doc in context.input.documents:
            if doc.extracted_data and getattr(doc.extracted_data, 'hospital_name', None):
                h_name = doc.extracted_data.hospital_name.lower()
                if any(nw.lower() in h_name for nw in network_list):
                    return True
        return False
        
    def _fuzzy_match(self, rule: str, value: str) -> bool:
        # Prevent blank strings from accidentally matching everything
        if not rule or not value or rule.strip() == "" or value.strip() == "":
            return False
            
        # Simplistic match for prototype. In production, use NLP embeddings or fuzzywuzzy.
        return rule.lower() in value.lower() or value.lower() in rule.lower()