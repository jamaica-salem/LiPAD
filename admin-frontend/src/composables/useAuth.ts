// src/composables/useAuth.ts
import { reactive } from "vue";
import api, { getCookie, setFallbackCsrf } from "@/api/axios";

type Admin = {
  id: number;
  first_name: string;
  middle_name?: string;
  last_name: string;
  email: string;
} | null;

const state = reactive({
  admin: null as Admin,
  isAuthenticated: false,
  loading: true,
});

/**
 * ensureCsrfCookie:
 * - Calls GET /api/csrf/ which sets the csrftoken cookie (if possible).
 * - Some dev setups (cross-origin + non-HTTPS) may not allow the cookie to be set.
 *   In that case we store the returned token as a fallback to send in the X-CSRFToken header.
 */
async function ensureCsrfCookie(retries = 2) {
  try {
    const res = await api.get("/api/csrf/"); // calls /api/csrf/
    // server returns { csrfToken: "<token>" } and normally sets csrftoken cookie
    const token = res?.data?.csrfToken || null;
    if (token) {
      // store fallback token (used only if cookie is missing)
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

export async function initAuth() {
  state.loading = true;
  try {
    await ensureCsrfCookie();
    const res = await api.get("/api/user/");
    if (res.data?.isAuthenticated) {
      state.admin = res.data.admin;
      state.isAuthenticated = true;
    } else {
      state.admin = null;
      state.isAuthenticated = false;
    }
  } catch (err) {
    state.admin = null;
    state.isAuthenticated = false;
    console.warn("initAuth: could not establish session", err);
  } finally {
    state.loading = false;
  }
}

export async function login(email: string, password: string) {
  try {
    await ensureCsrfCookie();
    const res = await api.post("/api/login/", { email, password });
    if (res.data?.admin) {
      state.admin = res.data.admin;
      state.isAuthenticated = true;
      return { success: true };
    }
    return { success: false, message: "Invalid response from server" };
  } catch (err: any) {
    if (err?.response) {
      return { success: false, message: err.response.data?.detail || "Login failed", status: err.response.status };
    }
    return { success: false, message: "Network error" };
  }
}

export async function logout() {
  try {
    await api.post("/api/logout/", {});
  } catch (err) {
    console.error("Logout request failed:", err);
  } finally {
    state.admin = null;
    state.isAuthenticated = false;
  }
}

export function useAuth() {
  return state;
}
