import axios, { type InternalAxiosRequestConfig, type AxiosError } from "axios";

/**
 * Production-ready Axios instance with security best practices
 */
const api = axios.create({
  baseURL: import.meta.env.PROD
    ? import.meta.env.VITE_API_URL || '/api' // production API root
    : '/api', // dev proxy -> same origin /api
  withCredentials: true,
  timeout: 15_000,
  headers: {
    'Content-Type': 'application/json',
    'X-Requested-With': 'XMLHttpRequest',
  },
});

/**
 * Utility to get cookie value by name
 */
export function getCookie(name: string): string | null {
  if (typeof document === 'undefined') return null;
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) {
    const cookieValue = parts.pop()?.split(';').shift();
    return cookieValue ? decodeURIComponent(cookieValue) : null;
  }
  return null;
}

/**
 * Fallback CSRF token storage for cross-origin scenarios
 */
let fallbackCsrfToken: string | null = null;
export function setFallbackCsrf(token: string | null): void {
  fallbackCsrfToken = token;
}

export function refreshCsrf(): Promise<any> {
  // Because baseURL is '/api', hitting '/csrf/' will call '/api/csrf/' on the server.
  return api.get('/csrf/');
}

/**
 * Request interceptor: Add CSRF token and security headers
 */
api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const method = (config.method || 'get').toLowerCase();
    if (['post', 'put', 'patch', 'delete'].includes(method)) {
      const csrfToken = getCookie('csrftoken') || fallbackCsrfToken;
      if (csrfToken) {
        // axios header casing: Django expects 'X-CSRFToken' by default
        (config.headers as any)['X-CSRFToken'] = csrfToken;
      }
    }
    (config.headers as any)['X-Requested-With'] = 'XMLHttpRequest';

    if (import.meta.env.DEV) {
      (config as any).metadata = { requestStartTime: Date.now() };
      console.log('→', config.method?.toUpperCase(), config.url, config.params ?? config.data ?? '');
    }

    return config;
  },
  (error) => Promise.reject(error)
);

/**
 * Response interceptor: Handle auth errors and logging
 */
api.interceptors.response.use(
  (response) => {
    if (import.meta.env.DEV && (response.config as any).metadata) {
      const duration = Date.now() - (response.config as any).metadata.requestStartTime;
      console.log(`API ${response.config.method?.toUpperCase()} ${response.config.url} - ${duration}ms`);
    }
    return response;
  },
  (error: AxiosError) => {
    if (!error.response) {
      console.error('Network error:', error.message);
      return Promise.reject(new Error('Network error. Please check your connection.'));
    }

    const { status, data } = error.response;
    if (status === 401 || status === 403) {
      if (typeof window !== 'undefined') {
        window.dispatchEvent(new CustomEvent('auth-error', { detail: { status, data } }));
      }
    }

    if (status === 429) console.warn('Rate limit exceeded');
    if (status >= 500) console.error('Server error', status, data);

    return Promise.reject(error);
  }
);

/**
 * Helper function to make authenticated requests with retry logic
 */
export async function makeAuthenticatedRequest<T>(requestFn: () => Promise<T>, maxRetries = 1): Promise<T> {
  let retries = 0;
  while (retries <= maxRetries) {
    try {
      return await requestFn();
    } catch (error: any) {
      if (error?.response?.status === 403 && retries < maxRetries) {
        try {
          await refreshCsrf(); // POST: refresh CSRF on server (will set cookie)
          retries++;
          continue;
        } catch (refreshError) {
          break;
        }
      }
      throw error;
    }
  }
  throw new Error('Max retries exceeded');
}

/**
 * Upload helper with progress tracking
 */
export function createUploadRequest(
  url: string,
  formData: FormData,
  onProgress?: (percentage: number) => void
) {
  return api.post(url, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
    timeout: 60000, // 1 minute for uploads
    onUploadProgress: (progressEvent) => {
      if (onProgress && progressEvent.total) {
        const percentage = Math.round(
          (progressEvent.loaded * 100) / progressEvent.total
        );
        onProgress(percentage);
      }
    },
  });
}

/**
 * Helper to check if error is network-related
 */
export function isNetworkError(error: any): boolean {
  return !error.response && (
    error.code === 'NETWORK_ERROR' ||
    error.code === 'ECONNABORTED' ||
    error.message.includes('Network Error')
  );
}

/**
 * Helper to check if error requires re-authentication
 */
export function isAuthError(error: any): boolean {
  return error?.response?.status === 401 || error?.response?.status === 403;
}

/**
 * Development helper to log all requests (remove in production)
 */
if (import.meta.env.DEV) {
  api.interceptors.request.use((config) => {
    console.log('→', config.method?.toUpperCase(), config.url, config.data || config.params);
    return config;
  });
}

export default api;