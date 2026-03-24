import React, { useState } from 'react';
import { Dashboard } from './components/Dashboard';
import JobDataManagement from './components/JobDataManagement';
import './index.css';

function App() {
  const [activeTab, setActiveTab] = useState<'drafts' | 'manage'>('drafts');

  return (
    <div className="min-h-screen bg-slate-50">
      <nav className="bg-white border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex">
              <div className="flex-shrink-0 flex items-center">
                <span className="text-xl font-bold text-indigo-600">HITL Pipeline</span>
              </div>
              <div className="ml-8 flex space-x-8">
                <button
                  onClick={() => setActiveTab('drafts')}
                  className={`inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium ${
                    activeTab === 'drafts'
                      ? 'border-indigo-500 text-slate-900'
                      : 'border-transparent text-slate-500 hover:text-slate-700 hover:border-slate-300'
                  }`}
                >
                  Proposal Drafts
                </button>
                <button
                  onClick={() => setActiveTab('manage')}
                  className={`inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium ${
                    activeTab === 'manage'
                      ? 'border-indigo-500 text-slate-900'
                      : 'border-transparent text-slate-500 hover:text-slate-700 hover:border-slate-300'
                  }`}
                >
                  Manage Job Data
                </button>
              </div>
            </div>
          </div>
        </div>
      </nav>

      <main>
        {activeTab === 'drafts' ? <Dashboard /> : <JobDataManagement />}
      </main>
    </div>
  );
}

export default App;
