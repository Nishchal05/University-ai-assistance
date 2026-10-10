import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import ChatPage from './pages/ChatPage';
import AdminPage from './pages/AdminPage';
import { checkHealth } from './lib/api';
import { AlertTriangle } from 'lucide-react';

export default function App() {
  const [activeTab, setActiveTab] = useState('chat');
  const [healthStatus, setHealthStatus] = useState(null);
  const [healthError, setHealthError] = useState(null);

  useEffect(() => {
    // Health check on startup
    checkHealth()
      .then((data) => {
        setHealthStatus(data);
        setHealthError(null);
      })
      .catch((err) => {
        console.error('Initial health check failed:', err);
        setHealthError(err.message);
      });
  }, []);

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col font-sans">
      {/* Startup Health Warning Banner if Down or Degraded */}
      {healthError && (
        <div className="bg-rose-600 text-white px-4 py-2.5 text-xs font-semibold flex items-center justify-center space-x-2 shadow-sm">
          <AlertTriangle className="w-4 h-4 flex-shrink-0" />
          <span>Backend Unavailable: {healthError}. Verify FastAPI is running on port 8000.</span>
        </div>
      )}

      {/* Navigation Bar */}
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        healthStatus={healthStatus}
      />

      {/* Main Content Area */}
      <main className="flex-1">
        {activeTab === 'chat' && (
          <ChatPage />
        )}

        {activeTab === 'admin' && (
          <AdminPage />
        )}
      </main>
    </div>
  );
}
