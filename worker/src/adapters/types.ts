import type { Page } from 'playwright-core'
import type { ApplicantProfile, JobEntry } from '../types'

export interface ApplyContext {
  page: Page
  entry: JobEntry
  profile: ApplicantProfile
}

export type ApplyOutcome =
  /** The form is filled as far as the worker can go, and is waiting for you to check and submit. */
  | { kind: 'ready'; note: string }
  | { kind: 'failed'; reason: string }

/** One implementation per hiring platform. */
export interface Adapter {
  name: string
  /** Signs in, fills the application, and stops before the final submit. */
  apply(ctx: ApplyContext): Promise<ApplyOutcome>
  /** True once the page shows the platform's "application submitted" confirmation. */
  isSubmitted(page: Page): Promise<boolean>
}
