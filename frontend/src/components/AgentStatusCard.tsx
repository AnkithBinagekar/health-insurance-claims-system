import React, { useState } from 'react';
import { CheckCircle2, XCircle, SkipForward, AlertTriangle, Clock } from 'lucide-react';
import type { AgentTrace } from '../types';

export const AgentStatusCard: React.FC<{ trace: AgentTrace }> = ({ trace }) => {
  const [showErrorDetails, setShowErrorDetails] = useState(false);
  const getStatusColor = () => {
    switch (trace.status) {
      case "SUCCESS": return 'border-green-500 bg-green-50';
      case "FAILED":
      case "DEGRADED": return 'border-red-500 bg-red-50';
      case "SKIPPED": return 'border-gray-300 bg-gray-50';
      default: return 'border-blue-500 bg-blue-50';
    }
  };

  const getStatusIcon = () => {
    switch (trace.status) {
      case "SUCCESS": return <CheckCircle2 className="w-5 h-5 text-green-600" />;
      case "FAILED":
      case "DEGRADED": return <XCircle className="w-5 h-5 text-red-600" />;
      case "SKIPPED": return <SkipForward className="w-5 h-5 text-gray-500" />;
      default: return <Clock className="w-5 h-5 text-blue-600" />;
    }
  };

  return (
    <div className={`p-4 rounded-lg border-l-4 shadow-sm mb-4 ${getStatusColor()}`}>
      <div className="flex justify-between items-center mb-2">
        <div className="flex items-center space-x-2">
          {getStatusIcon()}
          <h4 className="font-semibold text-gray-800">{trace.agent_name}</h4>
        </div>
        <span className="text-xs font-mono text-gray-500 bg-white px-2 py-1 rounded border">
          {trace.execution_time_ms ? `${trace.execution_time_ms.toFixed(0)} ms` : '0 ms'}
        </span>
      </div>

      {trace.decision_impact && (
        <p className="text-sm font-medium text-indigo-700 bg-indigo-50 p-2 rounded mb-2 border border-indigo-100">
          ↳ {trace.decision_impact}
        </p>
      )}

      {trace.warnings.length > 0 && (
        <div className="mb-2">
          <p className="text-xs font-bold text-orange-600 flex items-center"><AlertTriangle className="w-3 h-3 mr-1"/> Warnings</p>
          <ul className="list-disc list-inside text-xs text-orange-700 ml-1">
            {trace.warnings.map((w, i) => <li key={i}>{w}</li>)}
          </ul>
        </div>
      )}

      {trace.errors.length > 0 && (
        <div className="mb-2 bg-red-50 p-3 rounded border border-red-100">
          <p className="text-xs font-bold text-red-700 flex items-center mb-2">
            <XCircle className="w-3 h-3 mr-1" /> Component Execution Failed
          </p>
          <div className="text-xs text-red-800 mb-2 space-y-1 ml-4">
            <p><span className="font-semibold">Reason:</span> {trace.errors[0]?.split('\n')[0] || "Internal agent error."}</p>
            <p><span className="font-semibold">Impact:</span> {trace.decision_impact || "Some fields may be unavailable."}</p>
            <p><span className="font-semibold">Recovery:</span> Pipeline continued using available data.</p>
          </div>
          <button 
            onClick={() => setShowErrorDetails(!showErrorDetails)}
            className="text-[10px] text-red-600 hover:text-red-800 underline ml-4 font-semibold transition-colors"
          >
            {showErrorDetails ? "Hide Technical Details" : "View Technical Details"}
          </button>
          
          {showErrorDetails && (
            <div className="mt-2 p-2 bg-red-950 text-red-100 rounded text-[10px] font-mono overflow-x-auto whitespace-pre-wrap max-h-40 overflow-y-auto">
              {trace.errors.map((e, i) => <div key={i} className="mb-2 pb-2 border-b border-red-800/50 last:border-0">{e}</div>)}
            </div>
          )}
        </div>
      )}

      {trace.extracted_keys.length > 0 && (
        <div className="mt-3 flex flex-wrap gap-1">
          {trace.extracted_keys.map((key, i) => (
            <span key={i} className="px-2 py-1 bg-white border text-gray-600 text-[10px] rounded-full">
              {key}
            </span>
          ))}
        </div>
      )}
    </div>
  );
};