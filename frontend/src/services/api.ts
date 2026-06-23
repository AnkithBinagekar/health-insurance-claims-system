import axios from 'axios';
import type { ClaimContextPayload } from '../types';

// Fallback to localhost for local dev, but use Vercel env var in production
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const api = {
  submitClaim: async (formData: FormData) => {
    // 1. Remove hardcoded localhost. 
    // 2. Use the base URL dynamically.
    const response = await axios.post(`${API_BASE_URL}/api/claims/submit`, formData, {
      headers: { 'Accept': 'application/json' }
    });
    return response.data;
  },
  
  getClaimResult: async (claimId: string): Promise<ClaimContextPayload> => {
    const response = await axios.get(`${API_BASE_URL}/api/claims/${claimId}`);
    return response.data;
  },
};