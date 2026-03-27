import React, { useState } from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Button,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Typography,
  Box,
  MenuItem,
  Select,
  FormControl,
  InputLabel,
  Chip,
} from '@mui/material';
import {
  Edit as EditIcon,
  Delete as DeleteIcon,
  Add as AddIcon,
} from '@mui/icons-material';
import { 
  useJobDataList, 
  useCreateJobData, 
  useUpdateJobData, 
  useDeleteJobData 
} from '../hooks/useJobDataQueries';
import { JobData } from '../api/jobDataApi';

const getStatusColor = (status: string) => {
  switch (status) {
    case 'active': return 'success';
    case 'applied': return 'info';
    case 'not_active': return 'default';
    default: return 'default';
  }
};

export default function JobDataManagement() {
  // Queries & Mutations
  const { data: jobs } = useJobDataList();
  const createMutation = useCreateJobData();
  const updateMutation = useUpdateJobData();
  const deleteMutation = useDeleteJobData();

  const [open, setOpen] = useState(false);
  const [editingJob, setEditingJob] = useState<JobData | null>(null);
  
  // Form State
  const [jobPortalType, setJobPortalType] = useState('workday');
  const [jobUrl, setJobUrl] = useState('');
  const [jobStatus, setJobStatus] = useState<'active' | 'applied' | 'not_active'>('active');

  const handleOpen = (job?: JobData) => {
    if (job) {
      setEditingJob(job);
      setJobPortalType(job.job_portal_type);
      setJobUrl(job.job_url);
      setJobStatus(job.job_status);
    } else {
      setEditingJob(null);
      setJobPortalType('workday');
      setJobUrl('');
      setJobStatus('active');
    }
    setOpen(true);
  };

  const handleClose = () => {
    setOpen(false);
    setEditingJob(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const payload = { 
      job_portal_type: jobPortalType, 
      job_url: jobUrl,
      job_status: jobStatus
    };
    
    if (editingJob) {
      updateMutation.mutate({ id: editingJob.id, data: payload }, {
        onSuccess: handleClose
      });
    } else {
      createMutation.mutate(payload, {
        onSuccess: handleClose
      });
    }
  };

  const handleDelete = async (id: number) => {
    if (window.confirm('Are you sure you want to delete this job portal entry?')) {
      deleteMutation.mutate(id);
    }
  };

  return (
    <Box className="p-6 max-w-6xl mx-auto">
      <Box className="flex justify-between items-center mb-6">
        <Typography variant="h4" component="h2" className="font-bold text-slate-800">
          Job Data
        </Typography>
        <Button
          variant="contained"
          color="primary"
          startIcon={<AddIcon />}
          onClick={() => handleOpen()}
          className="bg-indigo-600 hover:bg-indigo-700 normal-case shadow-none"
        >
          Add Job
        </Button>
      </Box>

      <TableContainer component={Paper} className="shadow-sm border border-slate-200 rounded-xl overflow-hidden">
        <Table sx={{ minWidth: 650 }} aria-label="job data table">
          <TableHead className="bg-slate-50">
            <TableRow>
              <TableCell className="font-semibold text-slate-900">Portal Type</TableCell>
              <TableCell className="font-semibold text-slate-900">URL</TableCell>
              <TableCell className="font-semibold text-slate-900">Status</TableCell>
              <TableCell align="right" className="font-semibold text-slate-900">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody className="divide-y divide-slate-100">
            {jobs.map((job) => (
              <TableRow key={job.id} className="hover:bg-slate-50 transition">
                <TableCell>
                  <span className="capitalize px-2 py-1 bg-slate-100 rounded text-xs font-semibold text-slate-600">
                    {job.job_portal_type}
                  </span>
                </TableCell>
                <TableCell>
                  <a 
                    href={job.job_url} 
                    target="_blank" 
                    rel="noopener noreferrer" 
                    className="text-sm text-indigo-600 hover:underline truncate block max-w-sm"
                  >
                    {job.job_url}
                  </a>
                </TableCell>
                <TableCell>
                  <Chip 
                    label={job.job_status.replace('_', ' ')} 
                    size="small" 
                    color={getStatusColor(job.job_status) as any} 
                    variant="outlined"
                    className="capitalize font-medium"
                  />
                </TableCell>
                <TableCell align="right">
                  <Box className="flex justify-end gap-1">
                    <IconButton size="small" onClick={() => handleOpen(job)} className="text-slate-400 hover:text-indigo-600">
                      <EditIcon fontSize="small" />
                    </IconButton>
                    <IconButton size="small" onClick={() => handleDelete(job.id)} className="text-slate-400 hover:text-red-500">
                      <DeleteIcon fontSize="small" />
                    </IconButton>
                  </Box>
                </TableCell>
              </TableRow>
            ))}
            {jobs.length === 0 && (
              <TableRow>
                <TableCell colSpan={4} align="center" className="py-12 text-slate-500 italic">
                  No job data entries found.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Add/Edit Dialog */}
      <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
        <form onSubmit={handleSubmit}>
          <DialogTitle className="font-bold">
            {editingJob ? 'Edit Job Portal Entry' : 'Add New Job Portal Entry'}
          </DialogTitle>
          <DialogContent>
            <Box className="flex flex-col gap-5 mt-2">
              <FormControl fullWidth>
                <InputLabel id="portal-type-label">Job Portal Type</InputLabel>
                <Select
                  labelId="portal-type-label"
                  value={jobPortalType}
                  label="Job Portal Type"
                  onChange={(e) => setJobPortalType(e.target.value as string)}
                >
                  <MenuItem value="workday">Workday</MenuItem>
                  <MenuItem value="linkedin">LinkedIn</MenuItem>
                  <MenuItem value="indeed">Indeed</MenuItem>
                  <MenuItem value="upwork">Upwork</MenuItem>
                  <MenuItem value="wellfound">Wellfound</MenuItem>
                  <MenuItem value="other">Other</MenuItem>
                </Select>
              </FormControl>

              <TextField
                required
                fullWidth
                label="Job URL"
                type="url"
                value={jobUrl}
                onChange={(e) => setJobUrl(e.target.value)}
                placeholder="https://..."
                variant="outlined"
              />

              <FormControl fullWidth>
                <InputLabel id="job-status-label">Status</InputLabel>
                <Select
                  labelId="job-status-label"
                  value={jobStatus}
                  label="Status"
                  onChange={(e) => setJobStatus(e.target.value as any)}
                >
                  <MenuItem value="active">Active</MenuItem>
                  <MenuItem value="applied">Applied</MenuItem>
                  <MenuItem value="not_active">Not Active</MenuItem>
                </Select>
              </FormControl>
            </Box>
          </DialogContent>
          <DialogActions className="p-4">
            <Button onClick={handleClose} className="text-slate-500 lowercase">
              Cancel
            </Button>
            <Button 
              type="submit" 
              variant="contained" 
              className="bg-indigo-600 hover:bg-indigo-700 font-semibold"
              disabled={createMutation.isPending || updateMutation.isPending}
            >
              {createMutation.isPending || updateMutation.isPending ? 'Saving...' : (editingJob ? 'Update Entry' : 'Add Entry')}
            </Button>
          </DialogActions>
        </form>
      </Dialog>
    </Box>
  );
}
