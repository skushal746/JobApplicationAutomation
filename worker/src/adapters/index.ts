import type { JobType } from '../types'
import { oracleAdapter } from './oracle'
import type { Adapter } from './types'

/** Job types without an adapter are skipped and stay PENDING. */
export const adapters: Partial<Record<JobType, Adapter>> = {
  ORACLE: oracleAdapter,
  // WORKDAY: not implemented yet
  // DIGICERT: not implemented yet
}
