import type { JobType } from '../types'
import { akamaiOracleCloudAdapter } from './akamaiOracleCloud'
import type { Adapter } from './types'

/** Job types without an adapter are skipped and stay PENDING. */
export const adapters: Partial<Record<JobType, Adapter>> = {
  AKAMAI_ORACLECLOUD: akamaiOracleCloudAdapter,
  // WORKDAY: not implemented yet
  // DIGICERT: not implemented yet
}
