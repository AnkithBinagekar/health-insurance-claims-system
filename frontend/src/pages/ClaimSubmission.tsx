import React, { useState, useRef } from 'react';
import { UploadCloud, FileText, ChevronRight, X, File as FileIcon, ArrowLeft, Loader2 } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { api } from '../services/api'; // <-- The crucial API import restored

export default function ClaimSubmission() {
  const navigate = useNavigate();
  
  // Form State
  const [memberId, setMemberId] = useState('EMP001');
  const [category, setCategory] = useState('CONSULTATION');
  const [amount, setAmount] = useState('1500');
  const [date, setDate] = useState('2024-11-01');
  
  // File & Upload State
  const [files, setFiles] = useState<File[]>([]);
  const [isDragging, setIsDragging] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Drag & Drop Handlers
  const handleDragOver = (e: React.DragEvent) => { e.preventDefault(); setIsDragging(true); };
  const handleDragLeave = (e: React.DragEvent) => { e.preventDefault(); setIsDragging(false); };
  
  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault(); 
    setIsDragging(false);
    if (e.dataTransfer.files?.length) {
      setFiles(prev => [...prev, ...Array.from(e.dataTransfer.files!)]);
    }
  };
  
  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files?.length) {
      setFiles(prev => [...prev, ...Array.from(e.target.files!)]);
    }
  };
  
  const removeFile = (indexToRemove: number) => {
    setFiles(files.filter((_, index) => index !== indexToRemove));
  };

  // The REAL API Submission Handler
  const handleSubmit = async (e: React.SyntheticEvent) => {
    e.preventDefault();
    
    if (files.length === 0) {
      alert("Please upload at least one medical document.");
      return;
    }

    setIsSubmitting(true);

    try {
      const formData = new FormData();
      formData.append('member_id', memberId);
      formData.append('claim_category', category);
      formData.append('claimed_amount', amount);
      formData.append('treatment_date', date);
      files.forEach(file => formData.append('files', file));

      // 2. Send to Python Backend
      const response: any = await api.submitClaim(formData); 
      
      // Print the exact response to the browser console for debugging
      console.log("SUCCESS! Backend returned:", response);
      
      // 3. Smartly extract the Claim ID whether you use Fetch or Axios
      const realClaimId = response?.claim_id || response?.data?.claim_id; 
      
      if (realClaimId) {
        navigate(`/claim/${realClaimId}`);
      } else {
        // If it still fails, the console.log above will show us exactly why
        throw new Error("Could not find claim_id in the response object.");
      }
      
    } catch (error) {
      console.error("Submission failed:", error);
      alert("Failed to process claim. Check the browser console (F12) for the exact error.");
      setIsSubmitting(false); 
    }
  };

  return (
    <div className="min-h-screen py-12 px-4 sm:px-6 lg:px-8">
      
      {/* Header & Navigation */}
      <div className="max-w-3xl mx-auto mb-8">
        <button 
          onClick={() => navigate('/dashboard')} 
          className="text-plum-muted hover:text-plum-primary flex items-center text-sm font-medium transition-colors mb-6"
        >
          <ArrowLeft className="w-4 h-4 mr-1" /> Back to Dashboard
        </button>
        
        <div className="text-center">
          <div className="inline-flex items-center justify-center p-3 bg-white shadow-sm border border-gray-100 rounded-2xl mb-4">
            <FileText className="w-8 h-8 text-plum-primary" />
          </div>
          <h1 className="text-4xl font-extrabold tracking-tight">Submit New Claim</h1>
          <p className="mt-2 text-lg text-plum-muted">Upload your medical documents for automated verification.</p>
        </div>
      </div>

      {/* Main Form Card */}
      <div className="max-w-2xl mx-auto bg-white rounded-[16px] shadow-sm border border-gray-100 overflow-hidden">
        <form onSubmit={handleSubmit} className="p-8 space-y-6">
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-2">
              <label className="text-sm font-semibold text-plum-text">Member ID</label>
              <input 
                type="text" value={memberId} onChange={(e) => setMemberId(e.target.value)}
                className="w-full px-4 py-2.5 bg-plum-bg/50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-plum-primary/20 focus:border-plum-primary transition-all outline-none" 
                required 
              />
            </div>

            <div className="space-y-2">
              <label className="text-sm font-semibold text-plum-text">Claim Category</label>
              <select 
                value={category} onChange={(e) => setCategory(e.target.value)}
                className="w-full px-4 py-2.5 bg-plum-bg/50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-plum-primary/20 focus:border-plum-primary transition-all outline-none"
              >
                <option value="CONSULTATION">CONSULTATION</option>
                <option value="PHARMACY">PHARMACY</option>
                <option value="HOSPITALIZATION">HOSPITALIZATION</option>
                <option value="DENTAL">DENTAL</option>
                <option value="VISION">VISION</option>
              </select>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-semibold text-plum-text">Claimed Amount (₹)</label>
              <input 
                type="number" value={amount} onChange={(e) => setAmount(e.target.value)}
                className="w-full px-4 py-2.5 bg-plum-bg/50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-plum-primary/20 focus:border-plum-primary transition-all outline-none" 
                required 
              />
            </div>

            <div className="space-y-2">
              <label className="text-sm font-semibold text-plum-text">Treatment Date</label>
              <input 
                type="date" value={date} onChange={(e) => setDate(e.target.value)}
                className="w-full px-4 py-2.5 bg-plum-bg/50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-plum-primary/20 focus:border-plum-primary transition-all outline-none" 
                required 
              />
            </div>
          </div>

          {/* Interactive Drag & Drop Zone */}
          <div className="mt-8">
            <label className="text-sm font-semibold text-plum-text block mb-2">Medical Documents</label>
            <div 
              onClick={() => fileInputRef.current?.click()}
              onDragOver={handleDragOver} 
              onDragLeave={handleDragLeave} 
              onDrop={handleDrop}
              className={`border-2 border-dashed rounded-xl p-10 flex flex-col items-center justify-center text-center transition-all cursor-pointer group
                ${isDragging ? 'bg-plum-primary/5 border-plum-primary' : 'border-gray-200 hover:bg-plum-bg hover:border-plum-primary/50'}`}
            >
              <div className={`p-4 rounded-full transition-colors mb-4 ${isDragging ? 'bg-plum-primary/10' : 'bg-plum-bg group-hover:bg-white shadow-sm'}`}>
                <UploadCloud className={`w-8 h-8 ${isDragging ? 'text-plum-primary' : 'text-plum-muted group-hover:text-plum-primary'}`} />
              </div>
              <p className="font-medium mb-1 text-plum-text">
                <span className="text-plum-primary hover:underline">Click to upload</span> or drag and drop
              </p>
              <p className="text-xs text-plum-muted">Images or PDFs up to 10MB</p>
              
              <input 
                type="file" ref={fileInputRef} onChange={handleFileInput} 
                className="hidden" multiple accept="image/*,.pdf" 
              /> 
            </div>

            {/* Attached Files List */}
            {files.length > 0 && (
              <div className="mt-4 space-y-2">
                {files.map((file, idx) => (
                  <div key={idx} className="flex items-center justify-between p-3 bg-plum-bg/50 border border-gray-200 rounded-xl">
                    <div className="flex items-center gap-3 overflow-hidden">
                      <FileIcon className="w-5 h-5 text-plum-purple flex-shrink-0" />
                      <span className="text-sm font-medium text-plum-text truncate">{file.name}</span>
                    </div>
                    <button 
                      type="button" 
                      onClick={(e) => { e.stopPropagation(); removeFile(idx); }} 
                      className="p-1.5 hover:bg-white rounded-md text-plum-muted hover:text-plum-primary transition-colors shadow-sm"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Submit Button (Changes to a spinner when loading!) */}
          <div className="pt-4">
            <button 
              type="submit" 
              disabled={isSubmitting}
              className={`w-full flex items-center justify-center gap-2 bg-plum-primary text-white font-bold text-lg py-3.5 rounded-xl transition-all ${
                isSubmitting ? 'opacity-70 cursor-not-allowed' : 'hover:bg-plum-hover hover:shadow-lg transform active:scale-[0.98]'
              }`}
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Processing via AI Agents...
                </>
              ) : (
                <>
                  Process Claim Automatically
                  <ChevronRight className="w-5 h-5" />
                </>
              )}
            </button>
          </div>
          
        </form>
      </div>
    </div>
  );
}