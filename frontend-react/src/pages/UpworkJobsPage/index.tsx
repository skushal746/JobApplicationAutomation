import { useEffect, useState } from 'react'
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Typography,
  CircularProgress,
  Alert,
  Box,
  Link,
  Chip,
  Button,
  IconButton,
  Tooltip,
} from '@mui/material'
import AddIcon from '@mui/icons-material/Add'
import PlayArrowIcon from '@mui/icons-material/PlayArrow'
import DeleteIcon from '@mui/icons-material/Delete'
import { useNavigate } from 'react-router-dom'

interface UpworkJob {
  id: number
  title: string
  url: string
  description: string | null
  proposalCreated: boolean
  coverLetterCreated: boolean
  question1: string | null
  question2: string | null
  question3: string | null
  question4: string | null
  processedDatetime: string | null
}

const columns = ['Title', 'URL', 'Proposal', 'Cover Letter', 'Processed At', '']

export default function UpworkJobsPage() {
  const [jobs, setJobs] = useState<UpworkJob[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [hoveredRow, setHoveredRow] = useState<number | null>(null)
  const navigate = useNavigate()

  useEffect(() => {
    const token = localStorage.getItem('token')
    fetch('/api/upwork-jobs', {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then(res => {
        if (!res.ok) throw new Error('Failed to load jobs')
        return res.json()
      })
      .then(setJobs)
      .catch(() => setError('Failed to load Upwork jobs'))
      .finally(() => setLoading(false))
  }, [])

  const handleProcess = (id: number) => {
    // TODO: wire up process endpoint
    console.log('Process job', id)
  }

  const handleDelete = (id: number) => {
    const token = localStorage.getItem('token')
    fetch(`/api/upwork-jobs/${id}`, {
      method: 'DELETE',
      headers: { Authorization: `Bearer ${token}` },
    }).then(res => {
      if (res.ok) setJobs(prev => prev.filter(j => j.id !== id))
    })
  }

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 6 }}>
        <CircularProgress />
      </Box>
    )
  }

  if (error) {
    return <Alert severity="error" sx={{ mt: 2 }}>{error}</Alert>
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 3 }}>
        <Typography variant="h5" sx={{ fontWeight: 700 }}>
          Upwork Jobs
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => navigate('/dashboard/upwork/add')}
          sx={{
            background: 'linear-gradient(195deg, #49a3f1, #1A73E8)',
            boxShadow: '0 3px 10px rgba(26,115,232,0.35)',
            textTransform: 'none',
            fontWeight: 600,
            '&:hover': { background: 'linear-gradient(195deg, #3d8fd4, #1557b0)' },
          }}
        >
          Add Job
        </Button>
      </Box>

      {jobs.length === 0 ? (
        <Alert severity="info">No jobs found.</Alert>
      ) : (
        <TableContainer
          component={Paper}
          sx={{ borderRadius: 2, boxShadow: '0 2px 12px rgba(0,0,0,0.08)' }}
        >
          <Table size="small" stickyHeader>
            <TableHead>
              <TableRow>
                {columns.map((col, i) => (
                  <TableCell
                    key={i}
                    sx={{
                      fontWeight: 700,
                      fontSize: '0.75rem',
                      textTransform: 'uppercase',
                      letterSpacing: '0.05em',
                      bgcolor: '#f5f5f8',
                      color: '#555',
                      whiteSpace: 'nowrap',
                    }}
                  >
                    {col}
                  </TableCell>
                ))}
              </TableRow>
            </TableHead>
            <TableBody>
              {jobs.map(job => (
                <TableRow
                  key={job.id}
                  hover
                  onMouseEnter={() => setHoveredRow(job.id)}
                  onMouseLeave={() => setHoveredRow(null)}
                >
                  <TableCell sx={{ maxWidth: 220, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                    {job.title}
                  </TableCell>
                  <TableCell>
                    <Link href={job.url} target="_blank" rel="noreferrer" underline="hover">
                      Link
                    </Link>
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={job.proposalCreated ? 'Yes' : 'No'}
                      size="small"
                      color={job.proposalCreated ? 'success' : 'default'}
                      variant="outlined"
                    />
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={job.coverLetterCreated ? 'Yes' : 'No'}
                      size="small"
                      color={job.coverLetterCreated ? 'success' : 'default'}
                      variant="outlined"
                    />
                  </TableCell>
                  <TableCell sx={{ whiteSpace: 'nowrap' }}>
                    {job.processedDatetime ?? '—'}
                  </TableCell>
                  <TableCell sx={{ whiteSpace: 'nowrap', textAlign: 'right' }}>
                    <Box sx={{ visibility: hoveredRow === job.id ? 'visible' : 'hidden', display: 'flex', gap: 0.5, justifyContent: 'flex-end' }}>
                      <Tooltip title="Start Processing">
                        <IconButton
                          size="small"
                          onClick={() => handleProcess(job.id)}
                          sx={{ color: '#1A73E8', '&:hover': { bgcolor: 'rgba(26,115,232,0.08)' } }}
                        >
                          <PlayArrowIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Delete">
                        <IconButton
                          size="small"
                          onClick={() => handleDelete(job.id)}
                          sx={{ color: '#e53935', '&:hover': { bgcolor: 'rgba(229,57,53,0.08)' } }}
                        >
                          <DeleteIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                    </Box>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}
    </Box>
  )
}
