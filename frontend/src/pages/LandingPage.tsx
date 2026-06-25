import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Bot, ShieldCheck, Zap, ArrowRight, Activity, Server } from 'lucide-react';

export default function LandingPage() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen flex flex-col font-sans overflow-hidden">
      
      {/* Navigation Bar */}
      <nav className="w-full max-w-7xl mx-auto px-6 py-6 flex justify-between items-center z-10">
        <div className="flex items-center gap-2">
          <div className="bg-plum-primary p-2 rounded-lg">
            <Activity className="w-6 h-6 text-white" />
          </div>
          <span className="text-xl font-bold tracking-tight text-plum-text">Plum AI Pod</span>
        </div>
        <div className="hidden md:flex items-center gap-8 text-sm font-medium text-plum-muted">
          <a href="https://github.com/AnkithBinagekar/health-insurance-claims-system/blob/main/ARCHITECTURE.md" className="hover:text-plum-primary transition-colors">Architecture</a>
          <a href="#observability" className="hover:text-plum-primary transition-colors">Observability</a>
          <a href="https://github.com/AnkithBinagekar/health-insurance-claims-system" target="_blank" rel="noreferrer" className="hover:text-plum-primary transition-colors">GitHub Repo</a>
        </div>
        <button 
          onClick={() => navigate('/dashboard')}
          className="text-sm font-bold text-plum-text hover:text-plum-primary transition-colors"
        >
          Launch Demo &rarr;
        </button>
      </nav>

      {/* Hero Section */}
      <main className="flex-grow flex items-center justify-center relative px-6 py-12 md:py-24">
        
        {/* Background Decorative Blur */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[600px] bg-plum-purple/10 blur-[120px] rounded-full pointer-events-none"></div>

        <div className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-16 items-center relative z-10">
          
          {/* Left Column: Copy & CTA */}
          <div className="max-w-2xl">
            <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-plum-blue/10 text-plum-blue text-sm font-semibold mb-6 border border-plum-blue/20">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-plum-blue opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-plum-blue"></span>
              </span>
              Built for Plum AI Engineer Assignment
            </div>
            
            <h1 className="text-5xl md:text-6xl font-extrabold tracking-tight text-plum-text leading-[1.1] mb-6">
              Health Insurance <br/>
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-plum-primary to-plum-purple">
              Claims Engine
Built with AI
              </span>
            </h1>
            
            <p className="text-lg md:text-xl text-plum-muted mb-8 leading-relaxed">
              Upload claim documents, validate policy eligibility, extract medical information using Gemini Vision, detect inconsistencies, and generate deterministic claim decisions through a multi-agent pipeline.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4">
              <button 
                onClick={() => navigate('/dashboard')}
                className="bg-plum-primary hover:bg-plum-hover text-white px-8 py-4 rounded-xl font-bold text-lg flex items-center justify-center gap-2 shadow-sm transition-all transform hover:-translate-y-0.5"
              >
                Start Claim Analysis
                <ArrowRight className="w-5 h-5" />
              </button>
            </div>
          </div>

          {/* Right Column: Abstract Abstract UI/Code Graphic */}
          <div className="hidden lg:block relative">
            <div className="absolute inset-0 bg-gradient-to-tr from-plum-orange/20 to-plum-pink/20 blur-2xl rounded-3xl transform rotate-3"></div>
            <div className="relative bg-white border border-gray-100 p-8 rounded-3xl shadow-xl transform -rotate-2 hover:rotate-0 transition-transform duration-500">
              <div className="flex items-center justify-between mb-8 border-b border-gray-50 pb-4">
                <div className="flex gap-2">
                  <div className="w-3 h-3 rounded-full bg-red-400"></div>
                  <div className="w-3 h-3 rounded-full bg-amber-400"></div>
                  <div className="w-3 h-3 rounded-full bg-emerald-400"></div>
                </div>
                <div className="text-xs font-mono text-gray-400">agent_pipeline.py</div>
              </div>
              
              <div className="space-y-4 font-mono text-sm">
                <div className="flex items-center gap-3 text-plum-muted">
                  <Server className="w-4 h-4 text-plum-blue" />
                  <span><span className="text-plum-purple">await</span> DocumentClassifierAgent.run()</span>
                </div>
                 <div className="flex items-center gap-3 text-plum-muted">
                  <Server className="w-4 h-4 text-plum-pink" />
                  <span><span className="text-plum-purple">await</span> DocumentVerificationAgent.run()</span>
                </div>
                <div className="flex items-center gap-3 text-plum-muted">
                  <Server className="w-4 h-4 text-plum-pink" />
                  <span><span className="text-plum-purple">await</span> OCRExtractionAgent.run()</span>
                </div>
                <div className="pl-7 text-emerald-500 font-semibold text-xs border-l-2 border-gray-100 ml-1.5 py-2">
                  &rarr; 200 OK: Extracted 14 line items.
                </div>
                <div className="flex items-center gap-3 text-plum-muted">
                  <Server className="w-4 h-4 text-plum-orange" />
                  <span><span className="text-plum-purple">await</span> CrossValidationAgent.run()</span>
                </div>
                <div className="flex items-center gap-3 text-plum-muted">
                  <Server className="w-4 h-4 text-plum-orange" />
                  <span><span className="text-plum-purple">await</span> FraudDetectionAgent.run()</span>
                </div>
                <div className="flex items-center gap-3 text-plum-muted">
                  <Server className="w-4 h-4 text-plum-orange" />
                  <span><span className="text-plum-purple">await</span> PolicyEvaluationAgent.run()</span>
                </div>
                <div className="flex items-center gap-3 text-plum-muted">
                  <Server className="w-4 h-4 text-plum-orange" />
                  <span><span className="text-plum-purple">await</span> DecisionAgent.run()</span>
                </div>
                <div className="pl-7 text-plum-primary font-bold mt-4 pt-4 border-t border-gray-50">
                  <span className="text-gray-400">Result:</span> APPROVED
                </div>
                <div className="pl-7 text-plum-primary font-bold mt-4 pt-4 border-t border-gray-50">
                  <span className="text-gray-400">Confidence:</span> 96%
                  
                </div>
              </div>
            </div>
          </div>

        </div>
      </main>

      {/* Value Props Footer */}
      <footer className="w-full bg-white border-t border-gray-100 py-12 px-6">
        <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="flex flex-col items-center md:items-start text-center md:text-left">
            <div className="bg-plum-bg p-3 rounded-xl mb-4">
              <Bot className="w-6 h-6 text-plum-purple" />
            </div>
            <h3 className="font-bold text-plum-text mb-2">Multi-Agent Pipeline</h3>
            <p className="text-sm text-plum-muted">Independent AI agents perform classification,
verification, OCR, fraud detection and policy
evaluation before deterministic adjudication.</p>
          </div>
          <div className="flex flex-col items-center md:items-start text-center md:text-left">
            <div className="bg-plum-bg p-3 rounded-xl mb-4">
              <ShieldCheck className="w-6 h-6 text-emerald-600" />
            </div>
            <h3 className="font-bold text-plum-text mb-2">Deterministic Decision Engine</h3>
            <p className="text-sm text-plum-muted">AI extracts information while Python policy
rules calculate payouts using explainable,
rule-based decisions.</p>
          </div>
          <div className="flex flex-col items-center md:items-start text-center md:text-left">
            <div className="bg-plum-bg p-3 rounded-xl mb-4">
              <Zap className="w-6 h-6 text-plum-orange" />
            </div>
            <h3 className="font-bold text-plum-text mb-2">Spatial Observability</h3>
            <p className="text-sm text-plum-muted">Every extracted field links back to its
document location with confidence scores
and execution traces.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}