import { config } from './config'
import { log } from './log'
import type { JobEntry, JobEntryStatus } from './types'

/**
 * Talks to the Spring backend as the configured user. Logs in lazily and once more
 * when a request gets 401, since backend tokens expire after 24 hours.
 */
export class BackendClient {
  private token: string | null = null

  private async login(): Promise<string> {
    const res = await fetch(`${config.apiUrl}/api/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: config.appEmail, password: config.appPassword }),
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

  async setStatus(id: number, status: JobEntryStatus): Promise<JobEntry> {
    const res = await this.request(`/api/job-entries/${id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status }),
    })
    return (await res.json()) as JobEntry
  }
}
