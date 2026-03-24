import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Plus, Edit2, Save, X } from 'lucide-react';

const API_BASE = 'http://localhost:8000';

interface JobData {
  id: number;
  job_portal_type: string;
  job_url: string;
}

export default function JobDataManagement() {
  const [jobs, setJobs] = useState<JobData[]>([]);
  const [isAdding, setIsAdding] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [jobPortalType, setJobPortalType] = useState('workday');
  const [jobUrl, setJobUrl] = useState('');

  useEffect(() => {
    fetchJobs();
  }, []);

  const fetchJobs = async () => {
    try {
      const resp = await axios.get(`${API_BASE}/jobdata`);
      setJobs(resp.data);
    } catch (err) {
      console.error('Failed to fetch jobs', err);
    }
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await axios.post(`${API_BASE}/jobdata`, { job_portal_type: jobPortalType, job_url: jobUrl });
      setJobPortalType('workday');
      setJobUrl('');
      setIsAdding(false);
      fetchJobs();
    } catch (err) {
      console.error('Failed to create job', err);
    }
  };

  const handleUpdate = async (id: number) => {
    try {
      await axios.put(`${API_BASE}/jobdata/${id}`, { job_portal_type: jobPortalType, job_url: jobUrl });
      setEditingId(null);
      fetchJobs();
    } catch (err) {
      console.error('Failed to update job', err);
    }
  };

  const startEditing = (job: JobData) => {
    setEditingId(job.id);
    setJobPortalType(job.job_portal_type);
    setJobUrl(job.job_url);
  };

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-slate-800">Job Portal Data</h2>
        <button
          onClick={() => setIsAdding(true)}
          className="flex items-center gap-2 bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 transition"
        >
          <Plus size={20} /> Add Job
        </button>
      </div>

      {isAdding && (
        <form onSubmit={handleCreate} className="mb-8 p-4 bg-white rounded-xl shadow-sm border border-slate-200">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Job Portal Type</label>
              <select
                value={jobPortalType}
                onChange={(e) => setJobPortalType(e.target.value)}
                className="w-full rounded-lg border-slate-300 focus:border-indigo-500 focus:ring-indigo-500"
              >
                <option value="workday">Workday</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Job URL</label>
              <input
                type="url"
                required
                value={jobUrl}
                onChange={(e) => setJobUrl(e.target.value)}
                placeholder="https://..."
                className="w-full rounded-lg border-slate-300 focus:border-indigo-500 focus:ring-indigo-500"
              />
            </div>
          </div>
          <div className="flex justify-end gap-2 mt-4">
            <button
              type="button"
              onClick={() => setIsAdding(false)}
              className="px-4 py-2 text-slate-600 hover:bg-slate-100 rounded-lg"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
            >
              Save Job
            </button>
          </div>
        </form>
      )}

      <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
        <table className="w-full text-left">
          <thead className="bg-slate-50 border-b border-slate-200">
            <tr>
              <th className="px-6 py-3 text-sm font-semibold text-slate-900">Portal Type</th>
              <th className="px-6 py-3 text-sm font-semibold text-slate-900">URL</th>
              <th className="px-6 py-3 text-sm font-semibold text-slate-900 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {jobs.map((job) => (
              <tr key={job.id} className="hover:bg-slate-50 transition">
                <td className="px-6 py-4">
                  {editingId === job.id ? (
                    <select
                      value={jobPortalType}
                      onChange={(e) => setJobPortalType(e.target.value)}
                      className="rounded-lg border-slate-300 text-sm"
                    >
                      <option value="workday">Workday</option>
                    </select>
                  ) : (
                    <span className="capitalize px-2 py-1 bg-slate-100 rounded text-xs font-semibold text-slate-600">
                      {job.job_portal_type}
                    </span>
                  )}
                </td>
                <td className="px-6 py-4">
                  {editingId === job.id ? (
                    <input
                      type="url"
                      value={jobUrl}
                      onChange={(e) => setJobUrl(e.target.value)}
                      className="w-full rounded-lg border-slate-300 text-sm"
                    />
                  ) : (
                    <a href={job.job_url} target="_blank" rel="noopener noreferrer" className="text-sm text-indigo-600 hover:underline truncate block max-w-xs">
                      {job.job_url}
                    </a>
                  )}
                </td>
                <td className="px-6 py-4 text-right">
                  {editingId === job.id ? (
                    <div className="flex justify-end gap-2">
                      <button onClick={() => handleUpdate(job.id)} className="p-1 text-emerald-600 hover:bg-emerald-50 rounded">
                        <Save size={18} />
                      </button>
                      <button onClick={() => setEditingId(null)} className="p-1 text-slate-400 hover:bg-slate-100 rounded">
                        <X size={18} />
                      </button>
                    </div>
                  ) : (
                    <button onClick={() => startEditing(job)} className="p-1 text-slate-400 hover:bg-slate-100 rounded">
                      <Edit2 size={18} />
                    </button>
                  )}
                </td>
              </tr>
            ))}
            {jobs.length === 0 && !isAdding && (
              <tr>
                <td colSpan={3} className="px-6 py-12 text-center text-slate-500 italic">
                  No jobs added yet. Use the "Add Job" button above to get started.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
