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
  TextField,
  MenuItem,
} from '@mui/material'
import AddIcon from '@mui/icons-material/Add'
import FilterAltOffIcon from '@mui/icons-material/FilterAltOff'
import { useLocation, useNavigate, useSearchParams } from 'react-router-dom'
import { apiFetch } from '../../auth'

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

const JOB_TYPES: JobType[] = ['WORKDAY', 'DIGICERT']
const STATUSES: JobEntryStatus[] = ['PENDING', 'IN_PROGRESS', 'NEEDS_REVIEW', 'SUBMITTED', 'FAILED']

// Filter names double as URL query keys, both on this page and in the API call.
const FILTER_KEYS = ['from', 'to', 'status', 'jobType'] as const
type FilterKey = (typeof FILTER_KEYS)[number]

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
  const [searchParams, setSearchParams] = useSearchParams()
  const navigate = useNavigate()
  const location = useLocation()

  const filters: Record<FilterKey, string> = {
    from: searchParams.get('from') ?? '',
    to: searchParams.get('to') ?? '',
    status: searchParams.get('status') ?? '',
    jobType: searchParams.get('jobType') ?? '',
  }
  const hasFilters = FILTER_KEYS.some(key => filters[key])
  // ISO yyyy-MM-dd strings compare correctly as plain strings.
  const invalidRange = Boolean(filters.from && filters.to && filters.from > filters.to)

  const query = new URLSearchParams()
  FILTER_KEYS.forEach(key => {
    if (filters[key]) query.set(key, filters[key])
  })
  const queryString = query.toString()

  useEffect(() => {
    if (invalidRange) {
      setLoading(false)
      return
    }

    // Abort the previous request when filters change quickly, so an older
    // response can never overwrite a newer one.
    const controller = new AbortController()
    setLoading(true)
    setError('')

    apiFetch(`/api/job-entries${queryString ? `?${queryString}` : ''}`, {
      signal: controller.signal,
    })
      .then(res => {
        if (!res.ok) throw new Error('Failed to load job entries')
        return res.json()
      })
      .then(setEntries)
      .catch(err => {
        if (err.name !== 'AbortError') setError('Failed to load job entries')
      })
      .finally(() => {
        if (!controller.signal.aborted) setLoading(false)
      })

    return () => controller.abort()
  }, [queryString, invalidRange])

  const setFilter = (key: FilterKey) => (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const next = new URLSearchParams(searchParams)
    if (e.target.value) next.set(key, e.target.value)
    else next.delete(key)
    setSearchParams(next, { replace: true })
  }

  const clearFilters = () => setSearchParams({}, { replace: true })

  const filterFieldSx = { minWidth: 170, bgcolor: '#fff' }

  const renderResults = () => {
    if (invalidRange) {
      return <Alert severity="warning">The From date must be on or before the To date.</Alert>
    }
    if (loading) {
      return (
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 6 }}>
          <CircularProgress />
        </Box>
      )
    }
    if (error) {
      return <Alert severity="error">{error}</Alert>
    }
    if (entries.length === 0) {
      return (
        <Alert severity="info">
          {hasFilters ? 'No job entries match these filters.' : 'No job entries found.'}
        </Alert>
      )
    }

    return (
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
    )
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
          // Pass the active filters along so the Add page can return to the same filtered list.
          onClick={() => navigate('/dashboard/job-entries/add', { state: { listSearch: location.search } })}
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

      <Box sx={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center', gap: 2, mb: 2.5 }}>
        <TextField
          label="Created From"
          type="date"
          size="small"
          value={filters.from}
          onChange={setFilter('from')}
          error={invalidRange}
          sx={filterFieldSx}
          slotProps={{ inputLabel: { shrink: true }, htmlInput: { max: filters.to || undefined } }}
        />
        <TextField
          label="Created To"
          type="date"
          size="small"
          value={filters.to}
          onChange={setFilter('to')}
          error={invalidRange}
          sx={filterFieldSx}
          slotProps={{ inputLabel: { shrink: true }, htmlInput: { min: filters.from || undefined } }}
        />
        <TextField
          select
          label="Status"
          size="small"
          value={filters.status}
          onChange={setFilter('status')}
          sx={filterFieldSx}
          slotProps={{ inputLabel: { shrink: true }, select: { displayEmpty: true } }}
        >
          <MenuItem value="">All</MenuItem>
          {STATUSES.map(status => (
            <MenuItem key={status} value={status}>{formatLabel(status)}</MenuItem>
          ))}
        </TextField>
        <TextField
          select
          label="Job Type"
          size="small"
          value={filters.jobType}
          onChange={setFilter('jobType')}
          sx={filterFieldSx}
          slotProps={{ inputLabel: { shrink: true }, select: { displayEmpty: true } }}
        >
          <MenuItem value="">All</MenuItem>
          {JOB_TYPES.map(type => (
            <MenuItem key={type} value={type}>{formatLabel(type)}</MenuItem>
          ))}
        </TextField>
        <Button
          startIcon={<FilterAltOffIcon />}
          onClick={clearFilters}
          disabled={!hasFilters}
          sx={{ textTransform: 'none', color: '#7b809a' }}
        >
          Clear filters
        </Button>
      </Box>

      {renderResults()}
    </Box>
  )
}
