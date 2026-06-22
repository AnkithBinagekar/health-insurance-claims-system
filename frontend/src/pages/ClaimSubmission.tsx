import React, { useState, useRef } from 'react';
import { UploadCloud, FileText, ChevronRight, X, File as FileIcon } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
// import { api } from '../services/api'; // <-- Uncomment this when ready to link to your backend!

export default function ClaimSubmission() {
  const navigate = useNavigate();
  
  // --- Form State ---
  const [memberId, setMemberId] = useState('EMP001');
  const [category, setCategory] = useState('CONSULTATION');
  const [amount, setAmount] = useState('1500');
  const [date, setDate] = useState('2024-11-01');
  
  // --- File Upload State ---
  const [files, setFiles] = useState<File[]>([]);
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // --- Drag & Drop Handlers ---
  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      // Append new files to existing files
      setFiles(prev => [...prev, ...Array.from(e.dataTransfer.files!)]);
    }
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setFiles(prev => [...prev, ...Array.from(e.target.files!)]);
    }
  };

  const removeFile = (indexToRemove: number) => {
    setFiles(files.filter((_, index) => index !== indexToRemove));
  };

  // --- Submission Handler ---
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (files.length === 0) {
      alert("Please upload at least one medical document.");
      return;
    }

    // TODO: Connect this to your actual API call
    console.log("Submitting claim for:", memberId, category, amount, date);
    console.log("Files attached:", files.map(f => f.name));
    
    /* Example API Integration:
    try {
      const formData = new FormData();
      formData.append('member_id', memberId);
      formData.append('category', category);
      formData.append('amount', amount);
      formData.append('date', date);
      files.forEach(file => formData.append('documents', file));
      
      const response = await api.submitClaim(formData);
      navigate(`/claim/${response.id}`);
    } catch (error) {
      console.error("Submission failed", error);
    }
    */
  };

  return (
    <div className="min-h-screen bg-gray-50 text-gray-900 py-12 px-4 sm:px-6 lg:px-8 font-sans">
      
      <div className="max-w-3xl mx-auto text-center mb-10">
        <div className="inline-flex items-center justify-center p-3 bg-indigo-100 rounded-full mb-4">
          <FileText className="w-8 h-8 text-indigo-600" />
        </div>
        <h1 className="text-4xl font-extrabold tracking-tight text-gray-900">
          Plum AI Pod
        </h1>
        <p className="mt-2 text-lg text-gray-600">
          Intelligent Claims Processing Engine
        </p>
      </div>

      <div className="max-w-2xl mx-auto bg-white rounded-2xl shadow-xl overflow-hidden border border-gray-100">
        <div className="px-8 py-6 bg-gray-50/50 border-b border-gray-100">
          <h2 className="text-xl font-semibold text-gray-800">Submit New Claim</h2>
          <p className="text-sm text-gray-500 mt-1">Upload your medical documents for automated verification.</p>
        </div>

        <form onSubmit={handleSubmit} className="p-8 space-y-6">
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-2">
              <label className="text-sm font-semibold text-gray-700">Member ID</label>
              <input 
                type="text" 
                value={memberId}
                onChange={(e) => setMemberId(e.target.value)}
                className="w-full px-4 py-2.5 bg-gray-50 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all"
                required
              />
            </div>

            <div className="space-y-2">
              <label className="text-sm font-semibold text-gray-700">Claim Category</label>
              <select 
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                className="w-full px-4 py-2.5 bg-gray-50 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all"
              >
                <option value="CONSULTATION">CONSULTATION</option>
                <option value="PHARMACY">PHARMACY</option>
                <option value="HOSPITALIZATION">HOSPITALIZATION</option>
                {/* Added missing backend categories! */}
                <option value="DENTAL">DENTAL</option>
                <option value="VISION">VISION</option>
              </select>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-semibold text-gray-700">Claimed Amount (₹)</label>
              <input 
                type="number" 
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
                className="w-full px-4 py-2.5 bg-gray-50 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all"
                required
              />
            </div>

            <div className="space-y-2">
              <label className="text-sm font-semibold text-gray-700">Treatment Date</label>
              <input 
                type="date" 
                value={date}
                onChange={(e) => setDate(e.target.value)}
                className="w-full px-4 py-2.5 bg-gray-50 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all"
                required
              />
            </div>
          </div>

          {/* Interactive Drag & Drop Upload Zone */}
          <div className="mt-8">
            <label className="text-sm font-semibold text-gray-700 block mb-2">Medical Documents</label>
            
            <div 
              onClick={() => fileInputRef.current?.click()}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              className={`border-2 border-dashed rounded-xl p-10 flex flex-col items-center justify-center text-center transition-colors cursor-pointer group
                ${isDragging ? 'bg-indigo-50 border-indigo-500' : 'border-gray-300 hover:bg-indigo-50/50 hover:border-indigo-400'}`}
            >
              <div className={`p-4 rounded-full transition-colors mb-4 ${isDragging ? 'bg-indigo-200' : 'bg-gray-100 group-hover:bg-indigo-100'}`}>
                <UploadCloud className={`w-8 h-8 ${isDragging ? 'text-indigo-700' : 'text-gray-500 group-hover:text-indigo-600'}`} />
              </div>
              <p className="text-gray-700 font-medium mb-1">
                <span className="text-indigo-600 hover:underline">Click to upload</span> or drag and drop
              </p>
              <p className="text-xs text-gray-500">Images or PDFs up to 10MB</p>
              
              <input 
                type="file" 
                ref={fileInputRef}
                onChange={handleFileInput}
                className="hidden" 
                multiple 
                accept="image/*,.pdf"
              /> 
            </div>

            {/* Render attached files list below the dropzone */}
            {files.length > 0 && (
              <div className="mt-4 space-y-2">
                {files.map((file, idx) => (
                  <div key={idx} className="flex items-center justify-between p-3 bg-gray-50 border border-gray-200 rounded-lg">
                    <div className="flex items-center gap-3 overflow-hidden">
                      <FileIcon className="w-5 h-5 text-indigo-500 flex-shrink-0" />
                      <span className="text-sm font-medium text-gray-700 truncate">{file.name}</span>
                    </div>
                    <button 
                      type="button" 
                      onClick={(e) => { e.stopPropagation(); removeFile(idx); }}
                      className="p-1 hover:bg-gray-200 rounded text-gray-500 hover:text-red-500 transition-colors"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="pt-4">
            <button 
              type="submit" 
              className="w-full flex items-center justify-center gap-2 bg-indigo-600 text-white font-bold text-lg py-3.5 rounded-xl hover:bg-indigo-700 hover:shadow-lg transform transition-all active:scale-[0.98]"
            >
              Process Claim Automatically
              <ChevronRight className="w-5 h-5" />
            </button>
          </div>
          
        </form>
      </div>
    </div>
  );
}