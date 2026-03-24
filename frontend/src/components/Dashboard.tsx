import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Check, Clipboard, Edit2, RotateCcw, Send } from 'lucide-react';
import { useWebSocket } from '../hooks/useWebSocket';

const API_BASE = 'http://localhost:8000';
const WS_URL = 'ws://localhost:8000/ws';

interface Job {
  id: number;
  title: string;
  description: string;
  proposal: {
    id: number;
    content: string;
    status: string;
  };
}

export const Dashboard: React.FC = () => {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [selectedJob, setSelectedJob] = useState<Job | null>(null);
  const [editedProposal, setEditedProposal] = useState('');
  const [copying, setCopying] = useState(false);
  const { lastMessage } = useWebSocket(WS_URL);

  useEffect(() => {
    fetchPendingJobs();
  }, []);

  useEffect(() => {
    if (lastMessage?.type === 'new_job') {
      fetchPendingJobs();
    }
  }, [lastMessage]);

  const fetchPendingJobs = async () => {
    try {
      const res = await axios.get(`${API_BASE}/jobs/pending`);
      setJobs(res.data);
    } catch (err) {
      console.error('Failed to fetch jobs', err);
    }
  };

  const handleApprove = async () => {
    if (!selectedJob) return;
    try {
      await axios.post(`${API_BASE}/proposals/${selectedJob.proposal.id}/approve`, {
        content: editedProposal
      });
      
      // Copy to clipboard
      await navigator.clipboard.writeText(editedProposal);
      setCopying(true);
      setTimeout(() => setCopying(false), 2000);
      
      setSelectedJob(null);
      fetchPendingJobs();
    } catch (err) {
      console.error('Approval failed', err);
    }
  };

  return (
    <div className="min-h-screen bg-neutral-950 text-neutral-100 p-8 flex flex-col md:flex-row gap-8">
      {/* Sidebar - Jobs List */}
      <div className="w-full md:w-1/3 flex flex-col gap-4">
        <h1 className="text-2xl font-bold mb-4 flex items-center gap-2">
          <Send className="text-blue-500" /> HITL Pipeline
        </h1>
        <div className="flex flex-col gap-3 overflow-y-auto max-h-[calc(100vh-12rem)]">
          {jobs.length === 0 ? (
            <p className="text-neutral-500 text-center py-8 bg-neutral-900 rounded-lg border border-neutral-800">
              No pending jobs to review.
            </p>
          ) : (
            jobs.map((job) => (
              <button
                key={job.id}
                onClick={() => {
                  setSelectedJob(job);
                  setEditedProposal(job.proposal.content);
                }}
                className={`p-4 rounded-lg border transition-all text-left ${
                  selectedJob?.id === job.id
                    ? 'bg-neutral-800 border-blue-500 shadow-[0_0_15px_rgba(59,130,246,0.2)]'
                    : 'bg-neutral-900 border-neutral-800 hover:border-neutral-700'
                }`}
              >
                <h3 className="font-semibold text-lg">{job.title}</h3>
                <p className="text-sm text-neutral-400 mt-1 line-clamp-2">
                  {job.description}
                </p>
              </button>
            ))
          )}
        </div>
      </div>

      {/* Main Content - Proposal Editor */}
      <div className="flex-1 flex flex-col gap-6">
        {selectedJob ? (
          <>
            <div className="bg-neutral-900 p-6 rounded-xl border border-neutral-800">
              <h2 className="text-xl font-bold mb-2">{selectedJob.title}</h2>
              <div className="text-sm text-neutral-400 space-y-2">
                <p>{selectedJob.description}</p>
              </div>
            </div>

            <div className="flex-1 flex flex-col gap-4">
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-semibold flex items-center gap-2">
                  <Edit2 size={18} className="text-blue-500" /> Draft Proposal
                </h2>
                <button
                  onClick={() => setEditedProposal(selectedJob.proposal.content)}
                  className="text-xs text-neutral-500 hover:text-neutral-300 flex items-center gap-1"
                >
                  <RotateCcw size={12} /> Reset to Original
                </button>
              </div>
              <textarea
                value={editedProposal}
                onChange={(e) => setEditedProposal(e.target.value)}
                className="flex-1 bg-neutral-900 border border-neutral-800 rounded-xl p-6 font-mono text-sm leading-relaxed focus:outline-none focus:ring-2 focus:ring-blue-500/50 resize-none"
              />
              <button
                onClick={handleApprove}
                disabled={copying}
                className="w-full py-4 bg-blue-600 hover:bg-blue-500 disabled:bg-neutral-800 text-white rounded-xl font-bold transition-all flex items-center justify-center gap-2 group"
              >
                {copying ? (
                  <>
                    <Check size={20} /> Approved & Copied!
                  </>
                ) : (
                  <>
                    <Clipboard size={20} className="group-hover:scale-110 transition-transform" /> 
                    Approve & Copy to Clipboard
                  </>
                )}
              </button>
            </div>
          </>
        ) : (
          <div className="flex-1 flex items-center justify-center text-neutral-500 border-2 border-dashed border-neutral-800 rounded-3xl">
            Select a job from the sidebar to review the proposal
          </div>
        )}
      </div>
    </div>
  );
};
