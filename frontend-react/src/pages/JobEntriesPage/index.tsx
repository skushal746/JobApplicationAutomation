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
} from '@mui/material'
import AddIcon from '@mui/icons-material/Add'
import { useNavigate } from 'react-router-dom'

type JobType = 'WORKDAY' | 'DIGICERT'
type JobEntryStatus = 'PENDING' | 'IN_PROGRESS' | 'NEEDS_REVIEW' | 'SUBMITTED' | 'FAILED'

interface JobEntry {
  id: number
  userId: number
  url: string
  jobType: JobType
  status: JobEntryStatus
  createdAt: string
  updatedAt: string | null
}

const columns = ['URL', 'Job Type', 'Status', 'Created At', 'Updated At']

const statusColor: Record<JobEntryStatus, 'default' | 'info' | 'warning' | 'success' | 'error'> = {
  PENDING: 'default',
  IN_PROGRESS: 'info',
  NEEDS_REVIEW: 'warning',
  SUBMITTED: 'success',
  FAILED: 'error',
}

// The backend sends timestamps like "2026-10-15T11:43:49.990732"; show them as "2026-10-15 11:43".
function formatDateTime(value: string | null) {
  if (!value) return '—'
  return value.replace('T', ' ').slice(0, 16)
}

function formatLabel(value: string) {
  return value
    .toLowerCase()
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ')
}

export default function JobEntriesPage() {
  const [entries, setEntries] = useState<JobEntry[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const navigate = useNavigate()

  useEffect(() => {
    const token = localStorage.getItem('token')
    fetch('/api/job-entries', {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then(res => {
        if (!res.ok) throw new Error('Failed to load job entries')
        return res.json()
      })
      .then(setEntries)
      .catch(() => setError('Failed to load job entries'))
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
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 3 }}>
        <Typography variant="h5" sx={{ fontWeight: 700 }}>
          Job Entries
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => navigate('/dashboard/job-entries/add')}
          sx={{
            background: 'linear-gradient(195deg, #49a3f1, #1A73E8)',
            boxShadow: '0 3px 10px rgba(26,115,232,0.35)',
            textTransform: 'none',
            fontWeight: 600,
            '&:hover': { background: 'linear-gradient(195deg, #3d8fd4, #1557b0)' },
          }}
        >
          Add Job Entry
        </Button>
      </Box>

      {entries.length === 0 ? (
        <Alert severity="info">No job entries found.</Alert>
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
              {entries.map(entry => (
                <TableRow key={entry.id} hover>
                  <TableCell sx={{ maxWidth: 360, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                    <Link href={entry.url} target="_blank" rel="noreferrer" underline="hover" title={entry.url}>
                      {entry.url}
                    </Link>
                  </TableCell>
                  <TableCell>
                    <Chip label={formatLabel(entry.jobType)} size="small" variant="outlined" />
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={formatLabel(entry.status)}
                      size="small"
                      color={statusColor[entry.status] ?? 'default'}
                      variant="outlined"
                    />
                  </TableCell>
                  <TableCell sx={{ whiteSpace: 'nowrap' }}>{formatDateTime(entry.createdAt)}</TableCell>
                  <TableCell sx={{ whiteSpace: 'nowrap' }}>{formatDateTime(entry.updatedAt)}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}
    </Box>
  )
}
