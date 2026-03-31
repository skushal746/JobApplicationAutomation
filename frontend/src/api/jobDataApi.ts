import axios from 'axios';

const API_BASE = 'http://localhost:8000';

export interface JobData {
  id: number;
  job_portal_type: string;
  job_url: string;
  job_status: 'active' | 'applied' | 'not_active';
}

export interface JobDataCreate {
  job_portal_type: string;
  job_url: string;
  job_status?: 'active' | 'applied' | 'not_active';
}

const apiClient = axios.create({
  baseURL: API_BASE,
});

export const jobDataApi = {
  getAll: async (): Promise<JobData[]> => {
    const { data } = await apiClient.get('/jobdata');
    return data;
  },
  getOne: async (id: number): Promise<JobData> => {
    const { data } = await apiClient.get(`/jobdata/${id}`);
    return data;
  },
  create: async (jobData: JobDataCreate): Promise<JobData> => {
    const { data } = await apiClient.post('/jobdata', jobData);
    return data;
  },
  update: async (id: number, jobData: JobDataCreate): Promise<JobData> => {
    const { data } = await apiClient.put(`/jobdata/${id}`, jobData);
    return data;
  },
  delete: async (id: number): Promise<void> => {
    await apiClient.delete(`/jobdata/${id}`);
  },
  automateLinkedIn: async (id: number): Promise<void> => {
    await apiClient.post(`/jobdata/${id}/automate/linkedin`);
  },
  automateAllLinkedIn: async (): Promise<void> => {
    await apiClient.post('/jobdata/automate/linkedin');
  },
};
