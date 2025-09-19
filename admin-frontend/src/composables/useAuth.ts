import { reactive } from "vue";
import api, { getCookie, setFallbackCsrf } from "@/api/axios";

type Admin = {
  id: number;
  first_name: string;
  middle_name?: string;
  last_name: string;
  email: string;
  is_active: boolean;
} | null;

type AuthState = {
  admin: Admin;
  isAuthenticated: boolean;
  loading: boolean;
  sessionExpiry: Date | null;
};

const state = reactive<AuthState>({
  admin: null,
  isAuthenticated: false,
  loading: true,
  sessionExpiry: null,
});

/**
 * Ensure CSRF cookie is set for secure requests
 */
async function ensureCsrfCookie(retries = 2): Promise<boolean> {
  try {
    const res = await api.get("/csrf/");
    const token = res?.data?.csrfToken || null;
    if (token) {
      setFallbackCsrf(token);
    }
    return true;
  } catch (err) {
    if (retries > 0) {
      await new Promise((r) => setTimeout(r, 300));
      return ensureCsrfCookie(retries - 1);
    }
    throw err;
  }
}

/**
 * Initialize authentication state on app startup
 */
export async function initAuth(): Promise<void> {
  state.loading = true;
  try {
    await ensureCsrfCookie();
    const res = await api.get("/admin/session/");
    
    if (res.data?.isAuthenticated) {
      state.admin = res.data.admin;
      state.isAuthenticated = true;
      state.sessionExpiry = res.data.sessionExpiry ? new Date(res.data.sessionExpiry) : null;
    } else {
      state.admin = null;
      state.isAuthenticated = false;
      state.sessionExpiry = null;
    }
  } catch (err) {
    console.warn("Auth initialization failed:", err);
    state.admin = null;
    state.isAuthenticated = false;
    state.sessionExpiry = null;
  } finally {
    state.loading = false;
  }
}

/**
 * Secure admin login
 */
export async function login(email: string, password: string) {
  try {
    // Normalize email and validate input
    const normalizedEmail = email.trim().toLowerCase();
    
    if (!normalizedEmail || !password) {
      return { success: false, message: "Email and password are required" };
    }

    await ensureCsrfCookie();

    const res = await api.post("/admin/login/", {
      email: normalizedEmail,
      password,
    });

    if (res.data?.admin) {
      state.admin = res.data.admin;
      state.isAuthenticated = true;
      state.sessionExpiry = res.data.sessionExpiry ? new Date(res.data.sessionExpiry) : null;
      
      return { success: true };
    }

    return { success: false, message: "Invalid response from server" };
  } catch (err: any) {
    console.error("Login error:", err);
    
    if (err?.response) {
      const detail = err.response.data?.detail;
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
 * Secure admin logout
 */
export async function logout(): Promise<void> {
  try {
    await api.post("/admin/logout/", {});
  } catch (err) {
    console.error("Logout request failed:", err);
  } finally {
    // Always clear local state
    state.admin = null;
    state.isAuthenticated = false;
    state.sessionExpiry = null;
  }
}

/**
 * Check if session is expired
 */
export function isSessionExpired(): boolean {
  if (!state.sessionExpiry) return false;
  return new Date() >= state.sessionExpiry;
}

/**
 * Refresh session information
 */
export async function refreshSession(): Promise<boolean> {
  try {
    const res = await api.get("/admin/session/");
    
    if (res.data?.isAuthenticated) {
      state.admin = res.data.admin;
      state.isAuthenticated = true;
      state.sessionExpiry = res.data.sessionExpiry ? new Date(res.data.sessionExpiry) : null;
      return true;
    } else {
      state.admin = null;
      state.isAuthenticated = false;
      state.sessionExpiry = null;
      return false;
    }
  } catch (err) {
    console.error("Session refresh failed:", err);
    return false;
  }
}

/**
 * Reactive auth state accessor
 */
export function useAuth() {
  return {
    ...state,
    isSessionExpired,
    refreshSession,
  };
}