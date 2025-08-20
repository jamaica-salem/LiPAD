// src/composables/useAuth.ts
import { reactive } from "vue";
import api, { getCookie, setFallbackCsrf } from "@/api/axios";

/**
 * User type returned by the backend session endpoints.
 * Matches the safe user object returned by core.views_user_auth.login_user_view
 */
type User = {
  id: number;
  first_name: string;
  middle_name?: string;
  last_name: string;
  email: string;
} | null;

const state = reactive({
  user: null as User,
  isAuthenticated: false,
  loading: true,
});

/**
 * ensureCsrfCookie:
 * - Calls GET /api/user/csrf/ which sets the csrftoken cookie (if possible).
 * - Some dev setups (cross-origin + non-HTTPS) may not allow the cookie to be set.
 *   In that case we store the returned token as a fallback to send in the X-CSRFToken header.
 *
 * Notes:
 * - We call the *user* CSRF endpoint (user-side) because the server routes you added
 *   exposed a user-scoped csrf endpoint at /api/user/csrf/.
 */
async function ensureCsrfCookie(retries = 2) {
  try {
    const res = await api.get("/api/user/csrf/"); // user-side CSRF endpoint
    const token = res?.data?.csrfToken || null;
    if (token) {
      // store fallback token (used only if cookie is missing)
      setFallbackCsrf(token);
    }
    return true;
  } catch (err) {
    if (retries > 0) {
      // small backoff and retry (useful in flaky dev setups)
      await new Promise((r) => setTimeout(r, 300));
      return ensureCsrfCookie(retries - 1);
    }
    // bubble up the error to caller (initAuth/login will handle)
    throw err;
  }
}

/**
 * initAuth:
 * - Called once on app bootstrap to establish whether a session exists.
 * - Calls ensureCsrfCookie() first to make sure csrf token/cookie is available.
 * - Then calls GET /api/user/session/ which returns { isAuthenticated, user }.
 */
export async function initAuth() {
  state.loading = true;
  try {
    await ensureCsrfCookie();
    const res = await api.get("/api/user/session/");
    if (res.data?.isAuthenticated) {
      state.user = res.data.user;
      state.isAuthenticated = true;
    } else {
      state.user = null;
      state.isAuthenticated = false;
    }
  } catch (err) {
    // network or server error: treat as unauthenticated but keep app running
    state.user = null;
    state.isAuthenticated = false;
    console.warn("initAuth: could not establish session", err);
  } finally {
    state.loading = false;
  }
}

/**
 * login:
 * - Session-based login using POST /api/user/login/
 * - Ensures CSRF cookie is present, then posts credentials.
 * - On success the server sets the session cookie (sessionid) and returns user data.
 *
 * Returns: { success: boolean, message?: string, status?: number }
 */
export async function login(email: string, password: string) {
  try {
    // normalize email to avoid trivial mismatches (whitespace)
    const normalizedEmail = (email || "").trim();

    await ensureCsrfCookie();

    // POST to user login endpoint (session-based)
    const res = await api.post("/api/user/login/", {
      email: normalizedEmail,
      password,
    });

    if (res.data?.user) {
      state.user = res.data.user;
      state.isAuthenticated = true;
      return { success: true };
    }

    return { success: false, message: "Invalid response from server" };
  } catch (err: any) {
    // Attempt to extract useful message from server response
    if (err?.response) {
      const detail = err.response.data?.detail || err.response.data?.message;
      return {
        success: false,
        message: detail || "Login failed",
        status: err.response.status,
      };
    }
    return { success: false, message: "Network error" };
  }
}

/**
 * logout:
 * - Calls POST /api/user/logout/ to clear the server-side session.
 * - Clears local state regardless of network result (defensive).
 */
export async function logout() {
  try {
    await api.post("/api/user/logout/", {});
  } catch (err) {
    console.error("Logout request failed:", err);
  } finally {
    state.user = null;
    state.isAuthenticated = false;
  }
}

/** Simple accessor for reactive auth state */
export function useAuth() {
  return state;
}
