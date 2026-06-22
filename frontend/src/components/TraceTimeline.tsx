import React from 'react';
import type { AgentTrace } from '../types';
import { AgentStatusCard } from './AgentStatusCard';

export const TraceTimeline: React.FC<{ traces: AgentTrace[] }> = ({ traces }) => {
  return (
    <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
      <h3 className="text-lg font-bold text-gray-800 mb-4 border-b pb-2">Execution Trace</h3>
      <div className="space-y-2 relative before:absolute before:inset-0 before:ml-5 before:-translate-x-px md:before:mx-auto md:before:translate-x-0 before:h-full before:w-0.5 before:bg-gradient-to-b before:from-transparent before:via-gray-200 before:to-transparent">
        {traces.map((trace, index) => (
          <div key={index} className="relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group is-active">
            <div className="w-full">
              <AgentStatusCard trace={trace} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};