import React from 'react';
import { 
  FileText, 
  CheckCircle, 
  Clock, 
  ShieldAlert, 
  Plus, 
  Activity,
  ChevronRight
} from 'lucide-react';

export default function Dashboard() {
  // Mock data for the dashboard
  const recentClaims = [
    { id: 'CLM-8A9B2C', member: 'EMP001', category: 'CONSULTATION', amount: 1500, status: 'APPROVED', date: 'Oct 24, 2024' },
    { id: 'CLM-4C0A68', member: 'EMP042', category: 'HOSPITALIZATION', amount: 45000, status: 'MANUAL_REVIEW', date: 'Oct 23, 2024' },
    { id: 'CLM-9X2Y1Z', member: 'EMP018', category: 'PHARMACY', amount: 850, status: 'APPROVED', date: 'Oct 21, 2024' },
    { id: 'CLM-7L5M3N', member: 'EMP099', category: 'DENTAL', amount: 5000, status: 'REJECTED', date: 'Oct 20, 2024' },
  ];

  return (
    // Background Cream: #F8F4EE, Primary Text: #1F1F1F
    <div className="min-h-screen bg-[#F8F4EE] text-[#1F1F1F] font-sans p-6 md:p-10">
      
      {/* Header Section */}
      <div className="max-w-6xl mx-auto flex flex-col md:flex-row justify-between items-start md:items-center mb-10 gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Overview</h1>
          {/* Secondary Text: #555555 */}
          <p className="text-[#555555] mt-1">Welcome back. Here is your claims processing summary.</p>
        </div>
        
        {/* Primary Red CTA: #E5484D */}
        <button className="bg-[#E5484D] hover:bg-[#D43B40] text-white px-6 py-3 rounded-xl font-semibold flex items-center gap-2 shadow-sm transition-all transform hover:-translate-y-0.5">
          <Plus className="w-5 h-5" />
          New Claim
        </button>
      </div>

      <div className="max-w-6xl mx-auto space-y-8">
        
        {/* Top Metric Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          
          {/* Card 1: Blue Accent */}
          <div className="bg-[#FFFFFF] p-6 rounded-[16px] shadow-sm border border-gray-100 flex flex-col justify-between hover:shadow-md transition-shadow">
            <div className="flex justify-between items-start mb-4">
              <div className="p-3 bg-[#4F8FF7]/10 rounded-xl">
                <FileText className="w-6 h-6 text-[#4F8FF7]" />
              </div>
            </div>
            <div>
              <p className="text-[#555555] text-sm font-medium mb-1">Total Claims YTD</p>
              <h3 className="text-3xl font-bold text-[#1F1F1F]">1,284</h3>
            </div>
          </div>

          {/* Card 2: Pink Accent */}
          <div className="bg-[#FFFFFF] p-6 rounded-[16px] shadow-sm border border-gray-100 flex flex-col justify-between hover:shadow-md transition-shadow">
            <div className="flex justify-between items-start mb-4">
              <div className="p-3 bg-[#EC4899]/10 rounded-xl">
                <Activity className="w-6 h-6 text-[#EC4899]" />
              </div>
            </div>
            <div>
              <p className="text-[#555555] text-sm font-medium mb-1">AI Automation Rate</p>
              <h3 className="text-3xl font-bold text-[#1F1F1F]">94.2%</h3>
            </div>
          </div>

          {/* Card 3: Orange Accent */}
          <div className="bg-[#FFFFFF] p-6 rounded-[16px] shadow-sm border border-gray-100 flex flex-col justify-between hover:shadow-md transition-shadow">
            <div className="flex justify-between items-start mb-4">
              <div className="p-3 bg-[#F59E0B]/10 rounded-xl">
                <Clock className="w-6 h-6 text-[#F59E0B]" />
              </div>
            </div>
            <div>
              <p className="text-[#555555] text-sm font-medium mb-1">Avg. Processing Time</p>
              <h3 className="text-3xl font-bold text-[#1F1F1F]">1.4s</h3>
            </div>
          </div>

          {/* Card 4: Purple Accent */}
          <div className="bg-[#FFFFFF] p-6 rounded-[16px] shadow-sm border border-gray-100 flex flex-col justify-between hover:shadow-md transition-shadow">
            <div className="flex justify-between items-start mb-4">
              <div className="p-3 bg-[#6F42C1]/10 rounded-xl">
                <ShieldAlert className="w-6 h-6 text-[#6F42C1]" />
              </div>
            </div>
            <div>
              <p className="text-[#555555] text-sm font-medium mb-1">Pending Review</p>
              <h3 className="text-3xl font-bold text-[#1F1F1F]">28</h3>
            </div>
          </div>

        </div>

        {/* Main Data Section */}
        <div className="bg-[#FFFFFF] rounded-[16px] shadow-sm border border-gray-100 overflow-hidden">
          <div className="px-8 py-6 border-b border-gray-100 flex justify-between items-center bg-white">
            <h2 className="text-xl font-bold text-[#1F1F1F]">Recent Activity</h2>
            <button className="text-[#4F8FF7] text-sm font-semibold hover:underline">View All</button>
          </div>
          
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-[#F8F4EE]/50 border-b border-gray-100">
                  <th className="py-4 px-8 text-xs font-semibold text-[#555555] uppercase tracking-wider">Claim ID</th>
                  <th className="py-4 px-8 text-xs font-semibold text-[#555555] uppercase tracking-wider">Category</th>
                  <th className="py-4 px-8 text-xs font-semibold text-[#555555] uppercase tracking-wider">Amount</th>
                  <th className="py-4 px-8 text-xs font-semibold text-[#555555] uppercase tracking-wider">Date</th>
                  <th className="py-4 px-8 text-xs font-semibold text-[#555555] uppercase tracking-wider">Status</th>
                  <th className="py-4 px-8 text-xs font-semibold text-[#555555] uppercase tracking-wider text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {recentClaims.map((claim) => (
                  <tr key={claim.id} className="hover:bg-[#F8F4EE]/30 transition-colors group cursor-pointer">
                    <td className="py-4 px-8">
                      <div className="font-mono text-sm text-[#1F1F1F] font-medium">{claim.id}</div>
                      <div className="text-xs text-[#555555] mt-0.5">{claim.member}</div>
                    </td>
                    <td className="py-4 px-8">
                      <span className="text-sm font-medium text-[#1F1F1F] capitalize">{claim.category.toLowerCase()}</span>
                    </td>
                    <td className="py-4 px-8">
                      <span className="text-sm font-mono text-[#1F1F1F]">₹{claim.amount.toLocaleString()}</span>
                    </td>
                    <td className="py-4 px-8 text-sm text-[#555555]">
                      {claim.date}
                    </td>
                    <td className="py-4 px-8">
                      {claim.status === 'APPROVED' && (
                        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-[#4F8FF7]/10 text-[#4F8FF7]">
                          <CheckCircle className="w-3.5 h-3.5" /> Approved
                        </span>
                      )}
                      {claim.status === 'MANUAL_REVIEW' && (
                        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-[#F59E0B]/10 text-[#F59E0B]">
                          <ShieldAlert className="w-3.5 h-3.5" /> Review Needed
                        </span>
                      )}
                      {claim.status === 'REJECTED' && (
                        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-[#E5484D]/10 text-[#E5484D]">
                          <Activity className="w-3.5 h-3.5" /> Rejected
                        </span>
                      )}
                    </td>
                    <td className="py-4 px-8 text-right">
                      <button className="text-[#555555] group-hover:text-[#E5484D] transition-colors p-2 rounded-lg hover:bg-[#F8F4EE]">
                        <ChevronRight className="w-5 h-5" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

      </div>
    </div>
  );
}