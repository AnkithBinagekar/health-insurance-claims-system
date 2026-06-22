import React from 'react';
import { CheckCircle2, AlertCircle, XCircle, ShieldAlert, IndianRupee } from 'lucide-react';

// Define your props based on your existing types
interface DecisionCardProps {
  result: any;
  trace: any;
  haltedMsg?: string;
}

export const DecisionCard: React.FC<DecisionCardProps> = ({ result, trace, haltedMsg }) => {
  // Determine the primary status and color scheme dynamically
  const isHalted = !!haltedMsg;
  const status = isHalted ? 'HALTED' : (result?.decision?.value || 'MANUAL_REVIEW');
  
  // 1. Familiar Patterns: Traffic-light color mapping
  type ThemeConfig = {
    bg: string;
    border: string;
    text: string;
    icon: typeof CheckCircle2;
    title: string;
  };

  const themeMap: Record<string, ThemeConfig> = {
    APPROVED: { bg: 'bg-emerald-50', border: 'border-emerald-200', text: 'text-emerald-700', icon: CheckCircle2, title: 'Claim Approved' },
    PARTIAL: { bg: 'bg-blue-50', border: 'border-blue-200', text: 'text-blue-700', icon: AlertCircle, title: 'Partially Approved' },
    MANUAL_REVIEW: { bg: 'bg-amber-50', border: 'border-amber-200', text: 'text-amber-700', icon: ShieldAlert, title: 'Manual Review Required' },
    REJECTED: { bg: 'bg-rose-50', border: 'border-rose-200', text: 'text-rose-700', icon: XCircle, title: 'Claim Rejected' },
    HALTED: { bg: 'bg-gray-100', border: 'border-gray-300', text: 'text-gray-700', icon: AlertCircle, title: 'Processing Halted' }
  };

  const theme = themeMap[status] || themeMap.MANUAL_REVIEW;

  const Icon = theme.icon;
  // Calculate final confidence safely
  const finalConfidence = trace?.confidence_ledger?.length > 0 
    ? trace.confidence_ledger[trace.confidence_ledger.length - 1].new_confidence * 100 
    : (trace?.base_confidence || 1) * 100;

  return (
    // 4. Consistent Styling: Matching the form's rounded-xl and soft shadow
    <div className={`rounded-2xl border shadow-sm overflow-hidden transition-all duration-200 hover:shadow-md bg-white ${theme.border}`}>
      
      {/* Header section with dynamic color */}
      <div className={`px-6 py-5 border-b ${theme.bg} ${theme.border} flex items-start justify-between`}>
        <div className="flex items-center gap-3">
          <Icon className={`w-8 h-8 ${theme.text}`} />
          <div>
            <h2 className={`text-xl font-bold ${theme.text}`}>{theme.title}</h2>
            <p className="text-sm font-medium text-gray-600 mt-0.5">
              ID: <span className="font-mono text-gray-800">{trace?.claim_id}</span>
            </p>
          </div>
        </div>
        
        {/* 1. Clear Visual Hierarchy: The most important number is huge */}
        {!isHalted && (
          <div className="text-right">
            <p className="text-sm font-semibold text-gray-500 uppercase tracking-wide">Approved Amount</p>
            <div className={`flex items-center justify-end font-bold text-3xl ${status === 'REJECTED' ? 'text-gray-400 line-through' : 'text-gray-900'}`}>
              <IndianRupee className="w-6 h-6 mr-1" />
              {result?.approved_amount?.toFixed(2) || '0.00'}
            </div>
          </div>
        )}
      </div>

      <div className="p-6 space-y-6">
        
        {/* 5. Instant Feedback: Halted message stands out immediately if the pipeline stopped */}
        {isHalted ? (
          <div className="bg-rose-50 border-l-4 border-rose-500 p-4 rounded-r-lg">
            <p className="text-rose-800 font-medium">{haltedMsg}</p>
          </div>
        ) : (
          <>
            {/* 3. Simplicity & Focus: AI Confidence represented visually, not just as text */}
            <div>
              <div className="flex justify-between items-end mb-2">
                <span className="text-sm font-semibold text-gray-700">AI Confidence Score</span>
                <span className={`text-lg font-bold ${finalConfidence < 80 ? 'text-amber-600' : 'text-emerald-600'}`}>
                  {finalConfidence.toFixed(1)}%
                </span>
              </div>
              <div className="w-full bg-gray-100 rounded-full h-2.5 overflow-hidden">
                <div 
                  className={`h-2.5 rounded-full transition-all duration-1000 ease-out ${finalConfidence < 80 ? 'bg-amber-500' : 'bg-emerald-500'}`} 
                  style={{ width: `${finalConfidence}%` }}
                ></div>
              </div>
            </div>

            {/* Structured Reasons & Notes */}
            {((result?.rejection_reasons?.length > 0) || (result?.notes?.length > 0)) && (
              <div className="grid gap-4 mt-6 border-t pt-6">
                
                {result?.rejection_reasons?.length > 0 && (
                  <div>
                    <h3 className="text-sm font-bold text-gray-900 uppercase tracking-wider mb-2 flex items-center gap-2">
                      <ShieldAlert className="w-4 h-4 text-rose-500" />
                      Flags & Rejections
                    </h3>
                    <ul className="space-y-2">
                      {result.rejection_reasons.map((reason: string, idx: number) => (
                        <li key={idx} className="text-sm text-gray-700 bg-gray-50 px-3 py-2 rounded-md border border-gray-100">
                          {reason}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {result?.notes?.length > 0 && (
                  <div>
                    <h3 className="text-sm font-bold text-gray-900 uppercase tracking-wider mb-2 text-gray-500">
                      Deterministic Notes
                    </h3>
                    <ul className="space-y-1">
                      {result.notes.map((note: string, idx: number) => (
                        <li key={idx} className="text-sm text-gray-600 flex items-start gap-2">
                          <span className="text-indigo-400 mt-0.5">•</span>
                          {note}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};