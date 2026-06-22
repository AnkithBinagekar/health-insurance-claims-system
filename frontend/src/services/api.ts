import axios from 'axios';
import { ClaimContextPayload } from '../types';

const API_BASE_URL = 'http://localhost:8000/api/claims';

export const api = {
  submitClaim: async (formData: FormData): Promise<string> => {
    const response = await axios.post(`${API_BASE_URL}/submit`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data.claim_id;
  },

  getClaimResult: async (claimId: string): Promise<ClaimContextPayload> => {
    const response = await axios.get(`${API_BASE_URL}/${claimId}`);
    return response.data;
  },
};