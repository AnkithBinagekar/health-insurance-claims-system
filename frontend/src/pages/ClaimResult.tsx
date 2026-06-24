import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { ArrowLeft, Loader2 } from 'lucide-react';
import { api } from '../services/api';
import type { ClaimContextPayload } from '../types';
import { DecisionCard } from '../components/DecisionCard';
import { TraceTimeline } from '../components/TraceTimeline';
import DocumentViewer from '../components/DocumentViewer';

const ClaimResult: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [data, setData] = useState<ClaimContextPayload | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchResult = async () => {
      try {
        if (id) {
          const result = await api.getClaimResult(id);
          setData(result);
        }
      } catch (err) {
        setError('Failed to load claim data. It may not exist.');
      } finally {
        setLoading(false);
      }
    };
    fetchResult();
  }, [id]);

  if (loading) return <div className="flex justify-center items-center h-64"><Loader2 className="animate-spin w-10 h-10 text-indigo-600" /></div>;
  if (error || !data) return <div className="text-center text-red-600 mt-10 font-bold">{error}</div>;

  return (
    <div className="max-w-6xl mx-auto pb-12">
      <div className="mb-6 flex justify-between items-end">
        <div>
          <Link to="/" className="text-sm text-indigo-600 hover:text-indigo-800 flex items-center mb-2">
            <ArrowLeft className="w-4 h-4 mr-1" /> Submit another claim
          </Link>
          <h1 className="text-3xl font-bold text-gray-900">Claim Analysis</h1>
          <p className="text-gray-500 font-mono text-sm mt-1">ID: {data.trace.claim_id}</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-10">
        <div>
          <DecisionCard 
            result={data.result} 
            trace={data.trace} 
            haltedMsg={data.state.is_halted ? data.state.halt_message : undefined} 
          />
        </div>
        <div>
          <TraceTimeline traces={data.trace.agent_traces} />
        </div>
      </div>

     {/* --- NEW: The Interactive Bounding Box Viewer --- */}
      {/* Always render DocumentViewer if a document exists, handle halted state internally */}
      {data.input.documents && 
       data.input.documents.length > 0 && (
        <div className="mt-8 pt-8 border-t border-gray-200">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Document Verification</h2>
          <p className="text-gray-500 mb-6">Interactive view of the AI's spatial extraction.</p>
          
          <DocumentViewer 
            documentUrl={data.input.documents[0].storage_url} 
            extractedData={data.input.documents[0].extracted_data}
            isHalted={data.state.is_halted}
          />
        </div>
      )}
      
    </div>
  );
};

export default ClaimResult;