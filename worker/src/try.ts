/**
 * Sample run of one job URL, without the backend or a job entry:
 *
 *   npm run try -- <job url> [JOB_TYPE]        (JOB_TYPE defaults to AKAMAI_ORACLECLOUD)
 *
 * Opens Chrome with Playwright and runs the adapter for that job type exactly as a
 * scheduled run would: Apply, your email, waits for you to enter the code, fills the
 * form and stops before Submit. Nothing is read from or saved to the database.
 */
import { adapters } from './adapters'
import { closeBrowser, openBrowser } from './browser'
import { config } from './config'
import { log } from './log'
import { loadProfile } from './profile'
import type { JobEntry, JobType } from './types'

const [url, jobType = 'AKAMAI_ORACLECLOUD'] = process.argv.slice(2)

if (!url) {
  console.error('Usage: npm run try -- <job url> [JOB_TYPE]')
  process.exit(1)
}

const adapter = adapters[jobType as JobType]
if (!adapter) {
  console.error(`No script for job type "${jobType}". Supported: ${Object.keys(adapters).join(', ')}`)
  process.exit(1)
}

// The adapter only needs the URL; the rest stands in for a backend job entry.
const entry: JobEntry = {
  id: 0,
  userId: 0,
  url,
  jobType: jobType as JobType,
  status: 'PENDING',
  createdAt: new Date().toISOString(),
  updatedAt: null,
}

async function main() {
  const profile = loadProfile()
  const context = await openBrowser()
  const page = await context.newPage()
  // A persistent context opens with a blank tab; keep only the job's tab.
  for (const other of context.pages()) if (other !== page) await other.close().catch(() => {})

  log.info(`Trying ${adapter!.name} → ${url}`)
  const outcome = await adapter!.apply({ page, entry, profile })
  if (outcome.kind === 'failed') log.warn(`Failed: ${outcome.reason}`)
  else log.info(`Form ready for review (${outcome.note})`)

  if (config.headless) return // no window to look at

  log.action('Look over the form in Chrome. Close the Chrome window or press Ctrl+C here when done.')
  await new Promise<void>(resolve => {
    context.on('close', () => resolve())
    page.on('close', () => resolve())
  })
}

process.on('SIGINT', () => {
  void closeBrowser().then(() => process.exit(0))
})

main()
  .catch(err => log.error(err instanceof Error ? err.message : err))
  .finally(async () => {
    await closeBrowser()
    process.exit(0)
  })
