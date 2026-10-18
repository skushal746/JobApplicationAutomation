import { BackendClient } from './api'
import { closeBrowser } from './browser'
import { config } from './config'
import { log } from './log'
import { processPendingEntries, requestStop } from './processor'
import { runEvery, type Schedule } from './scheduler'

const api = new BackendClient()
const once = process.argv.includes('--once')

// How often to report in and check for "Run now". Cheap: no job entries are fetched.
const HEARTBEAT_MS = 10_000

let schedule: Schedule | null = null
let heartbeatTimer: NodeJS.Timeout | undefined

/**
 * One run, whether scheduled or from "Run now". It reports RUNNING and IDLE the moment
 * they happen, so the UI is never up to a heartbeat behind. It also takes any waiting
 * "Run now" request at the start, since this run covers it; a click made during the
 * run stays pending and causes exactly one follow-up run.
 */
async function runOnce() {
  await api.heartbeat('RUNNING').catch(() => {})
  await api.claimRun().catch(() => false)
  try {
    await processPendingEntries(api)
  } finally {
    await api.heartbeat('IDLE').catch(() => {})
  }
}

let heartbeatInFlight = false

/** Reports IDLE or RUNNING, and starts a run when "Run now" was clicked in the UI. */
async function heartbeat() {
  if (heartbeatInFlight) return // a slow backend must not stack up overlapping heartbeats
  heartbeatInFlight = true
  try {
    const running = schedule?.isRunning() ?? false
    const status = await api.heartbeat(running ? 'RUNNING' : 'IDLE')

    // A click during a run stays pending in the backend and is picked up here once the
    // run ends, so it is never lost. The new run claims the request as it starts (runOnce).
    if (status.runRequested && schedule && !schedule.isRunning()) {
      log.info('"Run now" requested from the UI')
      schedule.runNow()
    }
  } catch (err) {
    log.warn('Heartbeat failed:', err instanceof Error ? err.message : err)
  } finally {
    heartbeatInFlight = false
  }
}

async function shutdown() {
  log.info('Stopping…')
  requestStop()
  schedule?.stop()
  if (heartbeatTimer) clearInterval(heartbeatTimer)
  await closeBrowser()
  // Tell the UI straight away rather than waiting for the heartbeat to go stale.
  await api.heartbeat('STOPPED').catch(() => {})
  process.exit(0)
}
process.on('SIGINT', shutdown)
process.on('SIGTERM', shutdown)

if (once) {
  processPendingEntries(api)
    .then(() => process.exit(0))
    .catch(err => {
      log.error(err instanceof Error ? err.message : err)
      process.exit(1)
    })
} else {
  log.info(
    `Worker started. Checking ${config.apiUrl} every ${config.pollIntervalMs / 60_000} minutes, ` +
      `and for "Run now" every ${HEARTBEAT_MS / 1000} seconds. Ctrl+C to stop.`,
  )
  // The same code runs on the 30-minute schedule and on "Run now".
  schedule = runEvery(config.pollIntervalMs, runOnce)
  void heartbeat()
  heartbeatTimer = setInterval(heartbeat, HEARTBEAT_MS)
}
