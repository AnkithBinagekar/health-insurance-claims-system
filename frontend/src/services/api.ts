import axios from 'axios';
import type { ClaimContextPayload } from '../types';

const API_BASE_URL = 'http://localhost:8000/api/claims';

export const api = {
 submitClaim: async (formData: FormData) => {
    
    const response = await axios.post('http://localhost:8000/api/claims/submit', formData);
    return response.data; // You must return .data for Axios
  },
  getClaimResult: async (claimId: string): Promise<ClaimContextPayload> => {
    const response = await axios.get(`${API_BASE_URL}/${claimId}`);
    return response.data;
  },
};