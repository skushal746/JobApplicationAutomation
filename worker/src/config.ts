import path from 'node:path'
import { fileURLToPath } from 'node:url'

const WORKER_ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..')

function required(name: string): string {
  const value = process.env[name]
  if (!value) throw new Error(`Missing ${name}. Copy .env.example to .env and set it.`)
  return value
}

function minutes(name: string, fallback: number): number {
  const raw = process.env[name]
  const value = raw ? Number(raw) : fallback
  if (!Number.isFinite(value) || value <= 0) throw new Error(`${name} must be a positive number of minutes`)
  return value * 60_000
}

export const config = {
  apiUrl: (process.env.API_URL ?? 'http://localhost:8080').replace(/\/$/, ''),
  appEmail: required('APP_EMAIL'),
  appPassword: required('APP_PASSWORD'),
  pollIntervalMs: minutes('POLL_INTERVAL_MINUTES', 30),
  signInTimeoutMs: minutes('SIGN_IN_TIMEOUT_MINUTES', 10),
  reviewTimeoutMs: minutes('REVIEW_TIMEOUT_MINUTES', 30),
  profilePath: path.resolve(WORKER_ROOT, process.env.PROFILE_PATH ?? './profile.json'),
  headless: process.env.HEADLESS === 'true',
  // Chrome keeps cookies here between runs, so you only re-enter a code when the site's session ends.
  browserProfileDir: path.join(WORKER_ROOT, '.browser-profile'),
  screenshotDir: path.join(WORKER_ROOT, 'screenshots'),
}
