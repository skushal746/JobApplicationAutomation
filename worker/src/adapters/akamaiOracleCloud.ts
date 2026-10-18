import type { Page } from 'playwright-core'
import { config } from '../config'
import { fillKnownFields, keepSessionAlive, listEmptyFields, uploadResume } from '../formFill'
import { log } from '../log'
import type { Adapter, ApplyContext, ApplyOutcome } from './types'

/*
 * Akamai's careers site (job type AKAMAI_ORACLECLOUD), hosted on Oracle Recruiting
 * Cloud's "Candidate Experience":
 *   https://<tenant>.oraclecloud.com/hcmUI/CandidateExperience/en/sites/<site>/job/<id>
 *
 * The flow was checked on another site built on the same Oracle platform, up to the
 * email screen (".../apply/email"): an "APPLY NOW" button, an "Email Address" field, an
 * "I agree with the terms and conditions" checkbox, a NEXT button, hidden CAPTCHA widgets
 * and a honeypot field. The screens after the emailed code have not been seen yet, so
 * form filling past sign-in is label-driven and stops for you whenever it is unsure.
 */

const MAX_FORM_STEPS = 15
const POLL_MS = 2_000

const APPLY_PAGE = /\/job\/[^/]+\/apply(\/|$|\?)/i
const EMAIL_SCREEN = /\/apply\/email/i
const CODE_SCREEN = /\/apply\/(pin|code|verif)/i

function isCandidateExperienceSite(url: string): boolean {
  try {
    const { hostname, pathname } = new URL(url)
    return hostname.endsWith('.oraclecloud.com') && /\/CandidateExperience\//i.test(pathname)
  } catch {
    return false
  }
}

async function isVisible(page: Page, selector: Parameters<Page['locator']>[0]) {
  return page.locator(selector).first().isVisible().catch(() => false)
}

async function settle(page: Page) {
  await page.waitForLoadState('networkidle', { timeout: 15_000 }).catch(() => {})
  await page.waitForTimeout(1_000)
}

/** Declines optional cookies. Only strictly necessary cookies remain. */
async function dismissCookieBanner(page: Page) {
  const decline = page.getByRole('button', { name: /^decline$/i })
  if (await decline.isVisible().catch(() => false)) await decline.click().catch(() => {})
}

async function onSignInScreens(page: Page): Promise<boolean> {
  const url = page.url()
  if (EMAIL_SCREEN.test(url) || CODE_SCREEN.test(url)) return true
  if (await isVisible(page, 'input[name="primary-email"]')) return true
  return isVisible(page, 'input[autocomplete="one-time-code"]')
}

/** Fills the email, then waits while you agree to the terms, click NEXT and enter the code. */
async function signIn(page: Page, email: string): Promise<boolean> {
  // Matched by name: the label "Email Address" also matches a second element on the
  // page, which makes a label lookup ambiguous.
  const emailInput = page.locator('input[name="primary-email"]').first()
  if (await emailInput.isVisible().catch(() => false)) {
    if ((await emailInput.inputValue()) === '') await emailInput.fill(email)
    log.info(`Entered ${email}`)
  } else {
    log.warn('Email field not found; enter your email in the browser yourself')
  }

  log.action(
    `In the Chrome window: tick "I agree with the terms and conditions", click NEXT, ` +
      `and enter the code sent to ${email}. Solve a CAPTCHA if one appears. ` +
      `Waiting up to ${config.signInTimeoutMs / 60_000} minutes.`,
  )

  const deadline = Date.now() + config.signInTimeoutMs
  while (Date.now() < deadline) {
    if (page.isClosed()) return false
    await keepSessionAlive(page)
    if (!(await onSignInScreens(page))) {
      await settle(page)
      if (!(await onSignInScreens(page))) return true
    }
    await page.waitForTimeout(POLL_MS)
  }
  return false
}

/** A cheap fingerprint of the current form step, to tell whether NEXT actually moved on. */
async function stepSignature(page: Page): Promise<string> {
  const heading = await page.locator('h1, h2, h3').allInnerTexts().catch(() => [])
  const inputs = await page.locator('input:visible, textarea:visible, select:visible').count().catch(() => 0)
  return `${page.url()}|${heading.join('|').slice(0, 300)}|${inputs}`
}

/** Exported for testing against a local practice form. */
export async function fillApplication(page: Page, ctx: ApplyContext): Promise<ApplyOutcome> {
  const { profile } = ctx
  let resumeUploaded = false

  for (let step = 1; step <= MAX_FORM_STEPS; step++) {
    await keepSessionAlive(page)

    const filled = await fillKnownFields(page, profile.fields)
    if (filled.length) log.info(`Step ${step}: filled ${filled.join(', ')}`)

    if (profile.resumePath && !resumeUploaded) {
      resumeUploaded = await uploadResume(page, profile.resumePath)
      if (resumeUploaded) {
        log.info(`Step ${step}: uploaded resume`)
        await settle(page) // the site may parse it and pre-fill fields
        await fillKnownFields(page, profile.fields)
      }
    }

    const empty = await listEmptyFields(page)
    if (empty.length) log.warn(`Step ${step}: still empty: ${empty.join(', ')}`)

    const submit = page.getByRole('button', { name: /^submit( application)?$/i }).first()
    if (await submit.isVisible().catch(() => false)) {
      return { kind: 'ready', note: 'Reached the final Submit button' }
    }

    const next = page.getByRole('button', { name: /^(next|continue|save and continue)$/i }).first()
    if (!(await next.isVisible().catch(() => false)) || !(await next.isEnabled().catch(() => false))) {
      return { kind: 'ready', note: 'No Next or Submit button found; finish the remaining steps by hand' }
    }

    const before = await stepSignature(page)
    await next.click()
    await settle(page)
    if ((await stepSignature(page)) === before) {
      return { kind: 'ready', note: `Step ${step} did not advance; some fields need your input` }
    }
  }
  return { kind: 'ready', note: `Stopped after ${MAX_FORM_STEPS} steps` }
}

export const akamaiOracleCloudAdapter: Adapter = {
  name: 'Akamai (Oracle Recruiting Cloud)',

  async apply(ctx) {
    const { page, entry, profile } = ctx
    if (!isCandidateExperienceSite(entry.url)) {
      return { kind: 'failed', reason: 'URL is not an Akamai Candidate Experience job page on oraclecloud.com' }
    }

    await page.goto(entry.url, { waitUntil: 'domcontentloaded', timeout: 60_000 })
    await settle(page)
    await dismissCookieBanner(page)

    if (!APPLY_PAGE.test(page.url())) {
      const applyNow = page
        .getByRole('button', { name: /^apply( now)?$/i })
        .or(page.getByRole('link', { name: /^apply( now)?$/i }))
        .first()
      if (!(await applyNow.isVisible().catch(() => false))) {
        return { kind: 'failed', reason: 'No Apply button; the posting may be closed' }
      }
      await applyNow.click()
      // The app navigates client-side, so wait for the address to change rather than for a page load.
      const opened = await page.waitForURL(APPLY_PAGE, { timeout: 30_000 }).then(() => true, () => false)
      if (!opened) return { kind: 'failed', reason: 'Clicking Apply did not open the application' }
      await settle(page)
    }

    // With a saved session from an earlier run, the site can skip straight past sign-in.
    if (await onSignInScreens(page)) {
      const signedIn = await signIn(page, profile.email)
      if (!signedIn) return { kind: 'failed', reason: 'Sign-in was not completed in time' }
      log.info('Signed in')
    }

    // Never treat the job description or any other page as the application form.
    if (!APPLY_PAGE.test(page.url())) {
      return { kind: 'failed', reason: `Expected the application form but ended up at ${page.url()}` }
    }
    return fillApplication(page, ctx)
  },

  async isSubmitted(page) {
    if (/\/(confirmation|thank)/i.test(page.url())) return true
    const text = await page.locator('body').innerText().catch(() => '')
    return /thank you for (your application|applying)|application (has been |was )?(successfully )?submitted|you('ve| have) (successfully )?applied/i.test(text)
  },
}
