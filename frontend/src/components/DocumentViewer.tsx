import { useState } from 'react';

interface LineItem {
  description: string;
  amount: number;
  is_covered: boolean;
  rejection_reason?: string | null;
  bounding_box?: [number, number, number, number] | null;
}

interface ExtractedData {
  line_items?: LineItem[];
}

interface DocumentViewerProps {
  documentUrl: string;
  extractedData?: ExtractedData;
  isHalted?: boolean;
}

export default function DocumentViewer({ documentUrl, extractedData, isHalted }: DocumentViewerProps) {
  const [hoveredIndex, setHoveredIndex] = useState<number | null>(null);
  const lineItems = extractedData?.line_items || [];

  // FIX: Safely route local backend paths to the actual Azure/Backend URL
  const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
  const getFullImageUrl = (path: string) => {
    if (!path) return '';
    if (path.startsWith('http')) return path;
    const cleanPath = path.startsWith('/') ? path : `/${path}`;
    return `${API_BASE_URL}${cleanPath}`;
  };

  return (
    <div className="flex flex-col md:flex-row gap-6 w-full mt-6">
      
      {/* LEFT PANEL: The Image & Bounding Boxes */}
      <div className="relative w-full md:w-1/2 border rounded-lg overflow-hidden bg-gray-50">
        <img 
          src={getFullImageUrl(documentUrl)} 
          alt="Medical Document" 
          className="w-full h-auto block" 
        />
        
        {lineItems.map((item, index) => {
          if (!item.bounding_box) return null;
          
          const [ymin, xmin, ymax, xmax] = item.bounding_box;
          const top = `${(ymin / 1000) * 100}%`;
          const left = `${(xmin / 1000) * 100}%`;
          const height = `${((ymax - ymin) / 1000) * 100}%`;
          const width = `${((xmax - xmin) / 1000) * 100}%`;
          
          const isHovered = hoveredIndex === index;

          return (
            <div
              key={`bbox-${index}-${item.description}`} // FIX: Safer React Key
              style={{ top, left, height, width }}
              className={`absolute transition-all duration-200 pointer-events-none
                ${isHovered 
                  ? 'border-2 border-blue-500 bg-blue-500/20 shadow-[0_0_10px_rgba(59,130,246,0.5)]' 
                  : 'border border-blue-300/40 bg-transparent'
                }
              `}
            />
          );
        })}
      </div>

      {/* RIGHT PANEL: The Interactive Data Table or Halted Message */}
      <div className="w-full md:w-1/2">
        <h3 className="text-xl font-semibold mb-4 text-gray-800">
          Financial Breakdown
        </h3>
        
        {isHalted ? (
          <div className="bg-gray-50 border border-gray-200 border-dashed rounded-lg p-8 flex items-center justify-center text-center h-[calc(100%-3rem)]">
            <p className="text-gray-500 font-medium">
              Claim processing stopped before financial adjudication.
            </p>
          </div>
        ) : (
          <>
            <div className="bg-white rounded-lg shadow border overflow-hidden">
              <table className="w-full text-left text-sm">
                <thead className="bg-gray-100 border-b">
                  <tr>
                    <th className="p-3">Description</th>
                    <th className="p-3 text-right">Amount</th>
                    <th className="p-3 text-center">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y">
                  {lineItems.map((item, index) => (
                    <tr 
                      key={`row-${index}-${item.description}`}
                      onMouseEnter={() => setHoveredIndex(index)}
                      onMouseLeave={() => setHoveredIndex(null)}
                      className={`cursor-pointer transition-colors
                        ${hoveredIndex === index ? 'bg-blue-50' : 'hover:bg-gray-50'}
                      `}
                    >
                      <td className="p-3 text-gray-700">{item.description}</td>
                      <td className="p-3 text-right font-mono text-gray-900">₹{item.amount.toFixed(2)}</td>
                      <td className="p-3 text-center">
                        {item.is_covered ? (
                          <span className="text-green-600 bg-green-100 px-2 py-1 rounded text-xs font-medium">Covered</span>
                        ) : (
                          <span className="text-red-600 bg-red-100 px-2 py-1 rounded text-xs font-medium" title={item.rejection_reason || "Excluded"}>Excluded</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            
            <p className="text-xs text-gray-500 mt-3 flex items-center gap-1">
              💡 <span className="italic">Hover over a row to view its exact location on the source document.</span>
            </p>
          </>
        )}
      </div>
      
    </div>
  );
}