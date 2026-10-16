const TOKEN_KEY = 'token'

export const LOGIN_EXPIRED_PATH = '/login?reason=expired'

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY)
}

export function clearToken() {
  localStorage.removeItem(TOKEN_KEY)
}

// Reads the "exp" claim (seconds since epoch) from the JWT payload.
// This only decodes the token; the backend still verifies its signature on every request.
function getTokenExpiry(token: string): number | null {
  try {
    const payload = token.split('.')[1]
    const base64 = payload.replace(/-/g, '+').replace(/_/g, '/')
    const padded = base64.padEnd(base64.length + ((4 - (base64.length % 4)) % 4), '=')
    const { exp } = JSON.parse(atob(padded))
    return typeof exp === 'number' ? exp : null
  } catch {
    return null
  }
}

/** True when a token is stored and its expiry time has not passed. */
export function hasValidToken(): boolean {
  const token = getToken()
  if (!token) return false
  const exp = getTokenExpiry(token)
  return exp !== null && exp * 1000 > Date.now()
}

/** Drops the stored token and does a full page load of the login screen. */
export function redirectToLogin() {
  clearToken()
  window.location.replace(LOGIN_EXPIRED_PATH)
}

/**
 * fetch() for authenticated API calls. Adds the Bearer token, and sends the user to
 * /login when the token is missing or expired, or when the backend answers 401.
 */
export async function apiFetch(input: string, init: RequestInit = {}): Promise<Response> {
  if (!hasValidToken()) {
    redirectToLogin()
    return new Promise<Response>(() => {}) // never settles: the page is navigating away
  }

  const headers = new Headers(init.headers)
  headers.set('Authorization', `Bearer ${getToken()}`)

  const res = await fetch(input, { ...init, headers })
  if (res.status === 401) {
    redirectToLogin()
    return new Promise<Response>(() => {})
  }
  return res
}
