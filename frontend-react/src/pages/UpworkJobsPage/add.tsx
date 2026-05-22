import { useState } from 'react'
import {
  Box,
  Typography,
  TextField,
  FormControlLabel,
  Switch,
  Button,
  Paper,
  Alert,
  CircularProgress,
} from '@mui/material'
import ArrowBackIcon from '@mui/icons-material/ArrowBack'
import { useNavigate } from 'react-router-dom'

interface UpworkJobForm {
  title: string
  url: string
  description: string
  proposalCreated: boolean
  coverLetterCreated: boolean
  question1: string
  question2: string
  question3: string
  question4: string
}

const initialForm: UpworkJobForm = {
  title: '',
  url: '',
  description: '',
  proposalCreated: false,
  coverLetterCreated: false,
  question1: '',
  question2: '',
  question3: '',
  question4: '',
}

export default function AddUpworkJob() {
  const [form, setForm] = useState<UpworkJobForm>(initialForm)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')
  const navigate = useNavigate()

  const handleChange = (field: keyof UpworkJobForm) => (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => {
    setForm(prev => ({ ...prev, [field]: e.target.value }))
  }

  const handleToggle = (field: keyof UpworkJobForm) => (
    e: React.ChangeEvent<HTMLInputElement>
  ) => {
    setForm(prev => ({ ...prev, [field]: e.target.checked }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSubmitting(true)
    setError('')

    const token = localStorage.getItem('token')
    const payload = {
      ...form,
      description: form.description || null,
      question1: form.question1 || null,
      question2: form.question2 || null,
      question3: form.question3 || null,
      question4: form.question4 || null,
    }

    try {
      const res = await fetch('/api/upwork-jobs', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(payload),
      })

      if (!res.ok) throw new Error('Failed to create job')
      navigate('/dashboard/upwork')
    } catch {
      setError('Failed to create job. Please try again.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 3 }}>
        <Button
          startIcon={<ArrowBackIcon />}
          onClick={() => navigate('/dashboard/upwork')}
          sx={{ textTransform: 'none', color: '#7b809a' }}
        >
          Back
        </Button>
        <Typography variant="h5" sx={{ fontWeight: 700 }}>
          Add Upwork Job
        </Typography>
      </Box>

      <Paper sx={{ p: 3, borderRadius: 2, boxShadow: '0 2px 12px rgba(0,0,0,0.08)', maxWidth: 720 }}>
        {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

        <Box component="form" onSubmit={handleSubmit} sx={{ display: 'flex', flexDirection: 'column', gap: 2.5 }}>
          <TextField
            label="Title"
            value={form.title}
            onChange={handleChange('title')}
            required
            fullWidth
            size="small"
          />

          <TextField
            label="URL"
            value={form.url}
            onChange={handleChange('url')}
            required
            fullWidth
            size="small"
            type="url"
          />

          <TextField
            label="Description"
            value={form.description}
            onChange={handleChange('description')}
            fullWidth
            size="small"
            multiline
            rows={3}
          />

          <Box sx={{ display: 'flex', gap: 3 }}>
            <FormControlLabel
              control={
                <Switch
                  checked={form.proposalCreated}
                  onChange={handleToggle('proposalCreated')}
                  color="primary"
                />
              }
              label="Proposal Created"
            />
            <FormControlLabel
              control={
                <Switch
                  checked={form.coverLetterCreated}
                  onChange={handleToggle('coverLetterCreated')}
                  color="primary"
                />
              }
              label="Cover Letter Created"
            />
          </Box>

          <TextField
            label="Question 1"
            value={form.question1}
            onChange={handleChange('question1')}
            fullWidth
            size="small"
          />
          <TextField
            label="Question 2"
            value={form.question2}
            onChange={handleChange('question2')}
            fullWidth
            size="small"
          />
          <TextField
            label="Question 3"
            value={form.question3}
            onChange={handleChange('question3')}
            fullWidth
            size="small"
          />
          <TextField
            label="Question 4"
            value={form.question4}
            onChange={handleChange('question4')}
            fullWidth
            size="small"
          />

          <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end', pt: 1 }}>
            <Button
              variant="outlined"
              onClick={() => navigate('/dashboard/upwork')}
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
              {submitting ? <CircularProgress size={20} color="inherit" /> : 'Save Job'}
            </Button>
          </Box>
        </Box>
      </Paper>
    </Box>
  )
}
