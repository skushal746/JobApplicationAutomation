import { existsSync, readFileSync } from 'node:fs'
import { config } from './config'
import type { ApplicantProfile } from './types'

/** Read fresh on every run, so edits to profile.json apply without restarting the worker. */
export function loadProfile(): ApplicantProfile {
  if (!existsSync(config.profilePath)) {
    throw new Error(`No applicant profile at ${config.profilePath}. Copy profile.example.json to profile.json and fill it in.`)
  }
  const profile = JSON.parse(readFileSync(config.profilePath, 'utf8')) as ApplicantProfile
  if (!profile.email) throw new Error('profile.json needs an "email"')
  profile.fields ??= {}
  if (profile.resumePath && !existsSync(profile.resumePath)) {
    throw new Error(`Resume not found at ${profile.resumePath}`)
  }
  return profile
}
