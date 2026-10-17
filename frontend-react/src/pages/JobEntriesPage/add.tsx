import { useState } from 'react'
import {
  Box,
  Typography,
  TextField,
  MenuItem,
  Button,
  Paper,
  Alert,
  CircularProgress,
} from '@mui/material'
import ArrowBackIcon from '@mui/icons-material/ArrowBack'
import { useLocation, useNavigate } from 'react-router-dom'
import { apiFetch } from '../../auth'

const jobTypes = [
  { value: 'WORKDAY', label: 'Workday' },
  { value: 'DIGICERT', label: 'Digicert' },
  { value: 'ORACLE', label: 'Oracle (e.g. JPMorgan Chase)' },
] as const

type JobType = (typeof jobTypes)[number]['value']

interface JobEntryForm {
  url: string
  jobType: JobType | ''
}

const initialForm: JobEntryForm = { url: '', jobType: '' }

export default function AddJobEntry() {
  const [form, setForm] = useState<JobEntryForm>(initialForm)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')
  const navigate = useNavigate()
  const location = useLocation()

  // Return to the list with whatever filters it had when the user clicked Add.
  const listSearch = (location.state as { listSearch?: string } | null)?.listSearch ?? ''
  const LIST_PATH = `/dashboard/job-entries${listSearch}`

  const handleChange = (field: keyof JobEntryForm) => (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => {
    setForm(prev => ({ ...prev, [field]: e.target.value }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSubmitting(true)
    setError('')

    // Only url and jobType are sent. The backend sets the user from the token,
    // the status to PENDING and the created time.
    try {
      const res = await apiFetch('/api/job-entries', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: form.url.trim(), jobType: form.jobType }),
      })

      if (res.status === 409) {
        setError('You have already added a job entry with this URL.')
        return
      }
      if (res.status === 400) {
        setError('Please enter a valid http or https URL of up to 700 characters.')
        return
      }
      if (!res.ok) throw new Error('Failed to create job entry')

      navigate(LIST_PATH)
    } catch {
      setError('Failed to create job entry. Please try again.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 3 }}>
        <Button
          startIcon={<ArrowBackIcon />}
          onClick={() => navigate(LIST_PATH)}
          sx={{ textTransform: 'none', color: '#7b809a' }}
        >
          Back
        </Button>
        <Typography variant="h5" sx={{ fontWeight: 700 }}>
          Add Job Entry
        </Typography>
      </Box>

      <Paper sx={{ p: 3, borderRadius: 2, boxShadow: '0 2px 12px rgba(0,0,0,0.08)', maxWidth: 720 }}>
        {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

        <Box component="form" onSubmit={handleSubmit} sx={{ display: 'flex', flexDirection: 'column', gap: 2.5 }}>
          <TextField
            label="URL"
            value={form.url}
            onChange={handleChange('url')}
            required
            fullWidth
            size="small"
            type="url"
            placeholder="https://company.wd1.myworkdayjobs.com/..."
            slotProps={{ htmlInput: { maxLength: 700 } }}
          />

          <TextField
            select
            label="Job Type"
            value={form.jobType}
            onChange={handleChange('jobType')}
            required
            fullWidth
            size="small"
          >
            {jobTypes.map(type => (
              <MenuItem key={type.value} value={type.value}>
                {type.label}
              </MenuItem>
            ))}
          </TextField>

          <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end', pt: 1 }}>
            <Button
              variant="outlined"
              onClick={() => navigate(LIST_PATH)}
              sx={{ textTransform: 'none' }}
              disabled={submitting}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              variant="contained"
              disabled={submitting}
              sx={{
                background: 'linear-gradient(195deg, #49a3f1, #1A73E8)',
                boxShadow: '0 3px 10px rgba(26,115,232,0.35)',
                textTransform: 'none',
                fontWeight: 600,
                '&:hover': { background: 'linear-gradient(195deg, #3d8fd4, #1557b0)' },
              }}
            >
              {submitting ? <CircularProgress size={20} color="inherit" /> : 'Save Job Entry'}
            </Button>
          </Box>
        </Box>
      </Paper>
    </Box>
  )
}
