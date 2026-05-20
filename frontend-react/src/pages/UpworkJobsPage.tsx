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
} from '@mui/material'

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

const columns = [
  'ID', 'Title', 'URL', 'Description',
  'Proposal', 'Cover Letter', 'Q1', 'Q2', 'Q3', 'Q4', 'Processed At',
]

export default function UpworkJobsPage() {
  const [jobs, setJobs] = useState<UpworkJob[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

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
      <Typography variant="h5" sx={{ fontWeight: 700, mb: 3 }}>
        Upwork Jobs
      </Typography>

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
                {columns.map(col => (
                  <TableCell
                    key={col}
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
                <TableRow key={job.id} hover>
                  <TableCell>{job.id}</TableCell>
                  <TableCell sx={{ maxWidth: 180, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                    {job.title}
                  </TableCell>
                  <TableCell>
                    <Link href={job.url} target="_blank" rel="noreferrer" underline="hover">
                      Link
                    </Link>
                  </TableCell>
                  <TableCell sx={{ maxWidth: 200, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                    {job.description ?? '—'}
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
                  <TableCell sx={{ maxWidth: 150, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                    {job.question1 ?? '—'}
                  </TableCell>
                  <TableCell sx={{ maxWidth: 150, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                    {job.question2 ?? '—'}
                  </TableCell>
                  <TableCell sx={{ maxWidth: 150, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                    {job.question3 ?? '—'}
                  </TableCell>
                  <TableCell sx={{ maxWidth: 150, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                    {job.question4 ?? '—'}
                  </TableCell>
                  <TableCell sx={{ whiteSpace: 'nowrap' }}>
                    {job.processedDatetime ?? '—'}
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
