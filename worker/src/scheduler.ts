import { log } from './log'

/**
 * Runs `task` now and then every `intervalMs`, measured from the start of each run.
 * Runs never overlap: if one takes longer than the interval (for example while waiting
 * for you to enter a code), the next starts right after it finishes.
 */
export function runEvery(intervalMs: number, task: () => Promise<void>): { stop: () => void } {
  let timer: NodeJS.Timeout | undefined
  let stopped = false

  const tick = async () => {
    const startedAt = Date.now()
    try {
      await task()
    } catch (err) {
      log.error('Run failed:', err instanceof Error ? err.message : err)
    }
    if (stopped) return
    const delay = Math.max(0, intervalMs - (Date.now() - startedAt))
    log.info(`Next check at ${new Date(Date.now() + delay).toLocaleTimeString()}`)
    timer = setTimeout(tick, delay)
  }

  void tick()
  return {
    stop: () => {
      stopped = true
      if (timer) clearTimeout(timer)
    },
  }
}
