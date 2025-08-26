// src/services/csrf.ts
import http from './http'

let csrfReady: Promise<void> | null = null

export function ensureCsrfCookie(): Promise<void> {
  // Avoid multiple parallel hits
  if (!csrfReady) {
    csrfReady = http.get('/csrf/').then(() => undefined).catch(() => undefined)
  }
  return csrfReady
}
