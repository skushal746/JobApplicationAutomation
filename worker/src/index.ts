import { BackendClient } from './api'
import { closeBrowser } from './browser'
import { config } from './config'
import { log } from './log'
import { processPendingEntries, requestStop } from './processor'
import { runEvery } from './scheduler'

const api = new BackendClient()
const once = process.argv.includes('--once')

async function shutdown() {
  log.info('Stopping…')
  requestStop()
  await closeBrowser()
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
  log.info(`Worker started. Checking ${config.apiUrl} every ${config.pollIntervalMs / 60_000} minutes. Ctrl+C to stop.`)
  runEvery(config.pollIntervalMs, () => processPendingEntries(api))
}
