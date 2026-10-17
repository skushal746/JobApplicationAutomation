// Mirrors the backend's JobType and JobEntryStatus enums.
export type JobType = 'WORKDAY' | 'DIGICERT' | 'ORACLE'
export type JobEntryStatus = 'PENDING' | 'IN_PROGRESS' | 'NEEDS_REVIEW' | 'SUBMITTED' | 'FAILED'

export interface JobEntry {
  id: number
  userId: number
  url: string
  jobType: JobType
  status: JobEntryStatus
  createdAt: string
  updatedAt: string | null
}

export interface ApplicantProfile {
  /** Email used to sign in to the employer's candidate site. */
  email: string
  /** Absolute path to the resume file to upload. */
  resumePath?: string
  /** Visible form label → value. Labels must match the site's wording exactly. */
  fields: Record<string, string>
}
