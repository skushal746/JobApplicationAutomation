import { useCallback, useEffect, useRef, useState } from 'react'
import { Box, Button, Chip, CircularProgress, Tooltip } from '@mui/material'
import PlayArrowIcon from '@mui/icons-material/PlayArrow'
import { apiFetch } from '../auth'

interface WorkerStatus {
  runRequested: boolean
  runRequestedAt: string | null
  state: 'IDLE' | 'RUNNING' | 'STOPPED' | null
  lastSeenAt: string | null
  online: boolean
}

const POLL_MS = 5_000

interface Props {
  /** Called when the worker goes from running to idle, so the page can reload its entries. */
  onRunFinished?: () => void
}

/**
 * "Run now" for the worker on the user's machine. The click is stored by the backend;
 * the worker picks it up on its next check (every 10 seconds), so the button works
 * even if the worker is started later.
 */
export default function WorkerRunButton({ onRunFinished }: Props) {
  const [status, setStatus] = useState<WorkerStatus | null>(null)
  const [requesting, setRequesting] = useState(false)
  const [error, setError] = useState('')
  const wasRunning = useRef(false)
  const onRunFinishedRef = useRef(onRunFinished)
  onRunFinishedRef.current = onRunFinished

  const applyStatus = useCallback((next: WorkerStatus) => {
    const running = next.online && next.state === 'RUNNING'
    if (wasRunning.current && !running) onRunFinishedRef.current?.()
    wasRunning.current = running
    setStatus(next)
  }, [])

  useEffect(() => {
    let cancelled = false
    const load = () =>
      apiFetch('/api/worker/status')
        .then(res => (res.ok ? res.json() : Promise.reject(new Error(String(res.status)))))
        .then(next => {
          if (!cancelled) applyStatus(next)
        })
        .catch(() => {})
    load()
    const timer = setInterval(load, POLL_MS)
    return () => {
      cancelled = true
      clearInterval(timer)
    }
  }, [applyStatus])

  const handleRunNow = async () => {
    setRequesting(true)
    setError('')
    try {
      const res = await apiFetch('/api/worker/run', { method: 'POST' })
      if (!res.ok) throw new Error('Failed to request a run')
      applyStatus(await res.json())
    } catch {
      setError('Could not request a run. Please try again.')
    } finally {
      setRequesting(false)
    }
  }

  const online = status?.online ?? false
  const running = online && status?.state === 'RUNNING'
  const queued = status?.runRequested ?? false

  const chip = !status
    ? { label: 'Worker: checking…', color: 'default' as const }
    : !online
      ? { label: 'Worker offline', color: 'default' as const }
      : running
        ? { label: 'Worker running', color: 'info' as const }
        : { label: 'Worker idle', color: 'success' as const }

  const buttonLabel = running ? 'Running…' : queued ? 'Run requested' : 'Run now'
  const tooltip = error
    ? error
    : !online
      ? 'The worker is not running. Start it with "npm start" in the worker folder; a requested run starts as soon as it comes online.'
      : running
        ? 'The worker is processing pending entries. Check the Chrome window on your computer.'
        : queued
          ? 'Waiting for the worker to pick up the request (up to 10 seconds).'
          : 'Process all pending job entries now instead of waiting for the next 30-minute check.'

  return (
    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
      <Chip label={chip.label} color={chip.color} size="small" variant="outlined" />
      <Tooltip title={tooltip}>
        {/* span keeps the tooltip working while the button is disabled */}
        <span>
          <Button
            variant="outlined"
            startIcon={requesting || queued || running ? <CircularProgress size={16} /> : <PlayArrowIcon />}
            onClick={handleRunNow}
            disabled={requesting || queued || running}
            color={error ? 'error' : 'primary'}
            sx={{ textTransform: 'none', fontWeight: 600 }}
          >
            {buttonLabel}
          </Button>
        </span>
      </Tooltip>
    </Box>
  )
}
