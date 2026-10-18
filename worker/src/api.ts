import { config } from './config'
import { log } from './log'
import type { JobEntry, JobEntryStatus, WorkerState, WorkerStatus } from './types'

/**
 * Talks to the Spring backend as the configured user. Logs in lazily and once more
 * when a request gets 401, since backend tokens expire after 24 hours.
 */
export class BackendClient {
  // Read here so a missing APP_EMAIL / APP_PASSWORD stops the worker at startup.
  private readonly email = config.appEmail
  private readonly password = config.appPassword
  private token: string | null = null
  // Shared so the heartbeat and a run starting at the same moment log in only once.
  private loginInFlight: Promise<string> | null = null

  private login(): Promise<string> {
    this.loginInFlight ??= this.doLogin().finally(() => {
      this.loginInFlight = null
    })
    return this.loginInFlight
  }

  private async doLogin(): Promise<string> {
    const res = await fetch(`${config.apiUrl}/api/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: this.email, password: this.password }),
    })
    if (!res.ok) throw new Error(`Backend login failed with HTTP ${res.status}. Check APP_EMAIL and APP_PASSWORD.`)
    const { token } = (await res.json()) as { token: string }
    log.info('Logged in to the backend')
    return token
  }

  private async request(path: string, init: RequestInit = {}, retried = false): Promise<Response> {
    this.token ??= await this.login()
    const headers = new Headers(init.headers)
    headers.set('Authorization', `Bearer ${this.token}`)

    const res = await fetch(`${config.apiUrl}${path}`, { ...init, headers })
    if (res.status === 401 && !retried) {
      this.token = null
      return this.request(path, init, true)
    }
    if (!res.ok) throw new Error(`${init.method ?? 'GET'} ${path} failed with HTTP ${res.status}`)
    return res
  }

  /** Oldest first, so entries are applied to in the order they were added. */
  async listByStatus(status: JobEntryStatus): Promise<JobEntry[]> {
    const res = await this.request(`/api/job-entries?status=${status}`)
    const entries = (await res.json()) as JobEntry[]
    return entries.reverse()
  }

  /** Reports the worker's state; the answer says whether "Run now" was clicked. */
  async heartbeat(state: WorkerState): Promise<WorkerStatus> {
    const res = await this.request('/api/worker/heartbeat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ state }),
    })
    return (await res.json()) as WorkerStatus
  }

  /** Takes the pending "Run now" request. False if there was none left to take. */
  async claimRun(): Promise<boolean> {
    const res = await this.request('/api/worker/run/claim', { method: 'POST' })
    const { claimed } = (await res.json()) as { claimed: boolean }
    return claimed
  }

  async setStatus(id: number, status: JobEntryStatus): Promise<JobEntry> {
    const res = await this.request(`/api/job-entries/${id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status }),
    })
    return (await res.json()) as JobEntry
  }
}
