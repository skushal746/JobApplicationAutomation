import { chromium, type BrowserContext } from 'playwright-core'
import { config } from './config'

let active: BrowserContext | null = null

/**
 * Opens your installed Google Chrome with a dedicated profile folder, so employer
 * sessions survive between runs. This is not your everyday Chrome profile.
 */
export async function openBrowser(): Promise<BrowserContext> {
  active = await chromium.launchPersistentContext(config.browserProfileDir, {
    channel: 'chrome',
    headless: config.headless,
    viewport: null, // use the real window size
    slowMo: 150, // human-paced input
    args: ['--start-maximized'],
  })
  return active
}

export async function closeBrowser() {
  const context = active
  active = null
  await context?.close().catch(() => {})
}
