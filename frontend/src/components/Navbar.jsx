import React from 'react';
import { MessageSquare, Shield, CheckCircle2, AlertTriangle } from 'lucide-react';

export default function Navbar({
  activeTab,
  setActiveTab,
  healthStatus
}) {
  return (
    <header className="bg-white border-b border-slate-200 sticky top-0 z-30 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo and Title */}
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-lg bg-navy-800 flex items-center justify-center text-white font-bold text-lg shadow-sm">
              AI
            </div>
            <div>
              <span className="text-xs font-semibold uppercase tracking-wider text-navy-600 block">HCLTech Future Ready</span>
              <h1 className="text-base font-bold text-slate-900 leading-tight">University Student Services Assistant</h1>
            </div>
          </div>

          {/* Navigation Tabs */}
          <nav className="flex space-x-1 sm:space-x-2">
            <button
              onClick={() => setActiveTab('chat')}
              className={`flex items-center px-3 py-2 rounded-lg text-sm font-medium transition-colors cursor-pointer ${
                activeTab === 'chat'
                  ? 'bg-navy-800 text-white shadow-sm'
                  : 'text-slate-600 hover:text-navy-800 hover:bg-slate-100'
              }`}
            >
              <MessageSquare className="w-4 h-4 mr-2" />
              Chat Assistant
            </button>
            <button
              onClick={() => setActiveTab('admin')}
              className={`flex items-center px-3 py-2 rounded-lg text-sm font-medium transition-colors cursor-pointer ${
                activeTab === 'admin'
                  ? 'bg-navy-800 text-white shadow-sm'
                  : 'text-slate-600 hover:text-navy-800 hover:bg-slate-100'
              }`}
            >
              <Shield className="w-4 h-4 mr-2" />
              Admin & Ingestion
            </button>
          </nav>

          {/* Health Pill */}
          <div className="flex items-center space-x-3">
            <div
              className={`flex items-center px-2.5 py-1 rounded-full text-xs font-medium border ${
                healthStatus?.status === 'healthy'
                  ? 'bg-emerald-50 text-emerald-700 border-emerald-200'
                  : 'bg-amber-50 text-amber-700 border-amber-200'
              }`}
              title={`LLM Mode: ${healthStatus?.llm_mode || 'unknown'}`}
            >
              {healthStatus?.status === 'healthy' ? (
                <CheckCircle2 className="w-3.5 h-3.5 mr-1 text-emerald-600" />
              ) : (
                <AlertTriangle className="w-3.5 h-3.5 mr-1 text-amber-600" />
              )}
              {healthStatus?.status === 'healthy' ? 'System Online' : 'Checking Health...'}
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}
