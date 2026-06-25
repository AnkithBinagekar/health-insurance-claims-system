export type DocumentType = 
  | 'PRESCRIPTION' 
  | 'HOSPITAL_BILL' 
  | 'PHARMACY_BILL' 
  | 'LAB_REPORT' 
  | 'DENTAL_REPORT' 
  | 'DISCHARGE_SUMMARY' 
  | 'DIAGNOSTIC_REPORT';

export interface CategoryRequirements {
  required: DocumentType[];
  optional: DocumentType[];
}

// Extracted exactly from policy_terms.json
export const DOCUMENT_REQUIREMENTS: Record<string, CategoryRequirements> = {
  CONSULTATION: {
    required: ["PRESCRIPTION", "HOSPITAL_BILL"],
    optional: ["LAB_REPORT", "DIAGNOSTIC_REPORT"]
  },
  DIAGNOSTIC: {
    required: ["PRESCRIPTION", "LAB_REPORT", "HOSPITAL_BILL"],
    optional: ["DISCHARGE_SUMMARY"]
  },
  PHARMACY: {
    required: ["PRESCRIPTION", "PHARMACY_BILL"],
    optional: []
  },
  DENTAL: {
    required: ["HOSPITAL_BILL"],
    optional: ["PRESCRIPTION", "DENTAL_REPORT"]
  },
  VISION: {
    required: ["PRESCRIPTION", "HOSPITAL_BILL"],
    optional: []
  },
  ALTERNATIVE_MEDICINE: {
    required: ["PRESCRIPTION", "HOSPITAL_BILL"],
    optional: []
  }
};

// Helper to neatly format "PHARMACY_BILL" -> "Pharmacy Bill"
export const formatDocName = (doc: string) => {
  return doc.split('_').map(word => word.charAt(0) + word.slice(1).toLowerCase()).join(' ');
};