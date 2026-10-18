import { log } from './log'

export interface Schedule {
  /** Start a run right away and restart the countdown. Ignored while a run is in progress. */
  runNow: () => boolean
  isRunning: () => boolean
  stop: () => void
}

/**
 * Runs `task` now and then every `intervalMs`, measured from the start of each run.
 * Runs never overlap: if one takes longer than the interval (for example while waiting
 * for you to enter a code), the next starts right after it finishes.
 */
export function runEvery(intervalMs: number, task: () => Promise<void>): Schedule {
  let timer: NodeJS.Timeout | undefined
  let stopped = false
  let running = false

  const tick = async () => {
    if (running || stopped) return
    if (timer) clearTimeout(timer)
    running = true
    const startedAt = Date.now()
    try {
      await task()
    } catch (err) {
      log.error('Run failed:', err instanceof Error ? err.message : err)
    } finally {
      running = false
    }
    if (stopped) return
    const delay = Math.max(0, intervalMs - (Date.now() - startedAt))
    log.info(`Next scheduled check at ${new Date(Date.now() + delay).toLocaleTimeString()}`)
    timer = setTimeout(tick, delay)
  }

  void tick()
  return {
    runNow: () => {
      if (running || stopped) return false
      void tick()
      return true
    },
    isRunning: () => running,
    stop: () => {
      stopped = true
      if (timer) clearTimeout(timer)
    },
  }
}
