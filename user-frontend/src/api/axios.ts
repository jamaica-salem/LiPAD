import axios, { type InternalAxiosRequestConfig } from "axios";

/**
 * Axios instance used by the app.
 *
 * Important:
 * - Use relative baseURL so we can use Vite/webpack dev proxy in development
 *   and keep the same code for production where front & backend may be same origin.
 * - withCredentials true -> required so browser sends/receives cookies (sessionid, csrftoken)
 */
const api = axios.create({
  baseURL: "", // use relative URLs, e.g. api.get("/api/csrf/")
  withCredentials: true,
  timeout: 15000,
});

export function getCookie(name: string): string | null {
  if (!document?.cookie) return null;
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop()!.split(";").shift() || null;
  return null;
}

/**
 * CSRF token fallback storage:
 * If the cookie wasn't present for any reason, the last token will be stored
 * returned by /api/csrf/ (response JSON) in this variable and use it.
 * Prefer cookie (browser-managed)
 */
let FALLBACK_CSRF_TOKEN: string | null = null;

export function setFallbackCsrf(token: string | null) {
  FALLBACK_CSRF_TOKEN = token;
}

// attach CSRF header for unsafe methods
api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const method = (config.method || "get").toLowerCase();
  if (["post", "put", "patch", "delete"].includes(method)) {
    // prefer cookie value
    const csrftoken = getCookie("csrftoken") || FALLBACK_CSRF_TOKEN;
    if (csrftoken) {
      (config.headers as any)["X-CSRFToken"] = csrftoken;
    }
    (config.headers as any)["X-Requested-With"] = "XMLHttpRequest";
  }
  return config;
});

// global response handler for auth issues
api.interceptors.response.use(
  (resp) => resp,
  (error) => {
    if (error?.response?.status === 401 || error?.response?.status === 403) {
      // helpful console message; you can also emit an event for global auth handling
      console.warn("API auth error (401/403). Response:", error.response?.data);
    }
    return Promise.reject(error);
  }
);

export default api;
