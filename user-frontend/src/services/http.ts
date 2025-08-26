// src/services/http.ts
// Centralized axios instance configured for session auth & CSRF.
import axios from 'axios'

const http = axios.create({
  baseURL: '/api',                // matches Django router included under /api/
  withCredentials: true,          // send session cookie
  timeout: 20000,
  xsrfCookieName: 'csrftoken',
  xsrfHeaderName: 'X-CSRFToken',
  headers: { 'X-Requested-With': 'XMLHttpRequest' }
})

// normalize network errors
http.interceptors.response.use(
  res => res,
  err => {
    if (!err.response) {
      return Promise.reject(new Error('Network error. Check your connection.'))
    }
    return Promise.reject(err)
  }
)

export default http
