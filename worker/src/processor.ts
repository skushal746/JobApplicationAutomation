import { mkdirSync } from 'node:fs'
import path from 'node:path'
import type { BrowserContext, Page } from 'playwright-core'
import { adapters } from './adapters'
import type { Adapter } from './adapters/types'
import type { BackendClient } from './api'
import { closeBrowser, openBrowser } from './browser'
import { config } from './config'
import { keepSessionAlive } from './formFill'
import { log } from './log'
import { loadProfile } from './profile'
import type { ApplicantProfile, JobEntry } from './types'

let stopping = false
export function requestStop() {
  stopping = true
}

async function screenshot(page: Page, entry: JobEntry, label: string) {
  if (page.isClosed()) return
  mkdirSync(config.screenshotDir, { recursive: true })
  const file = path.join(config.screenshotDir, `entry-${entry.id}-${label}-${Date.now()}.png`)
  await page.screenshot({ path: file, fullPage: true }).catch(() => {})
  log.info(`Screenshot: ${file}`)
}

/**
 * Leaves the filled form open for you. Returns true if the platform's confirmation
 * page appears (you submitted), false if you close the tab or time runs out.
 */
async function waitForYourReview(page: Page, adapter: Adapter): Promise<boolean> {
  log.action(
    `Review the application in Chrome and click Submit if it looks right. ` +
      `Close the tab to leave it for later. Waiting up to ${config.reviewTimeoutMs / 60_000} minutes.`,
  )
  const deadline = Date.now() + config.reviewTimeoutMs
  while (Date.now() < deadline && !page.isClosed() && !stopping) {
    if (await adapter.isSubmitted(page)) return true
    await keepSessionAlive(page)
    await page.waitForTimeout(3_000).catch(() => {})
  }
  return false
}

async function processEntry(api: BackendClient, context: BrowserContext, entry: JobEntry, adapter: Adapter, profile: ApplicantProfile) {
  log.info(`Entry ${entry.id}: applying via ${adapter.name} → ${entry.url}`)
  await api.setStatus(entry.id, 'IN_PROGRESS')
  const page = await context.newPage()

  try {
    const outcome = await adapter.apply({ page, entry, profile })

    if (outcome.kind === 'failed') {
      log.warn(`Entry ${entry.id}: failed: ${outcome.reason}`)
      await screenshot(page, entry, 'failed')
      await api.setStatus(entry.id, 'FAILED')
      return
    }

    log.info(`Entry ${entry.id}: form ready for review (${outcome.note})`)
    await screenshot(page, entry, 'ready')
    await api.setStatus(entry.id, 'NEEDS_REVIEW')

    if (await waitForYourReview(page, adapter)) {
      await api.setStatus(entry.id, 'SUBMITTED')
      log.info(`Entry ${entry.id}: submitted`)
    } else {
      log.info(`Entry ${entry.id}: left as NEEDS_REVIEW`)
    }
  } catch (err) {
    const message = err instanceof Error ? err.message.split('\n')[0] : String(err)
    log.error(`Entry ${entry.id}: ${message}`)
    await screenshot(page, entry, 'error')
    await api.setStatus(entry.id, 'FAILED').catch(() => {})
  } finally {
    if (!page.isClosed()) await page.close().catch(() => {})
  }
}

/** One poll: fetch PENDING entries and work through the ones a platform adapter supports. */
export async function processPendingEntries(api: BackendClient) {
  stopping = false
  const profile = loadProfile()
  const pending = await api.listByStatus('PENDING')

  const runnable = pending.filter(entry => {
    if (adapters[entry.jobType]) return true
    log.info(`Entry ${entry.id}: no adapter for ${entry.jobType} yet; leaving it PENDING`)
    return false
  })
  log.info(`Found ${pending.length} pending entr${pending.length === 1 ? 'y' : 'ies'}, ${runnable.length} supported`)
  if (runnable.length === 0) return

  const context = await openBrowser()
  try {
    // Persistent contexts start with a blank tab; each entry gets its own tab instead.
    for (const blank of context.pages()) await blank.close().catch(() => {})
    for (const entry of runnable) {
      if (stopping) break
      await processEntry(api, context, entry, adapters[entry.jobType]!, profile)
    }
  } finally {
    await closeBrowser()
  }
}
