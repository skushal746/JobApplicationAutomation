import type { JobType } from '../types'
import { oracleAdapter } from './oracle'
import type { Adapter } from './types'

/** Job types without an adapter are skipped and stay PENDING. */
export const adapters: Partial<Record<JobType, Adapter>> = {
  // Oracle Recruiting Cloud sites share one script; add a line per company type.
  AKAMAI_ORACLECLOUD: oracleAdapter,
  // WORKDAY: not implemented yet
  // DIGICERT: not implemented yet
}
