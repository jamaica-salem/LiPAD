// user-frontend/src/composables/useAuth.ts
import { reactive } from "vue";
import api, { getCookie, setFallbackCsrf, refreshCsrf } from "@/api/axios";

type User = { id: number; first_name: string; middle_name?: string; last_name: string; email: string; position: string; is_active: boolean; } | null;
type AuthState = { user: User; isAuthenticated: boolean; loading: boolean; sessionExpiry: Date | null; };

const state = reactive<AuthState>({
  user: null,
  isAuthenticated: false,
  loading: true,
  sessionExpiry: null,
});


/**
 * Ensure CSRF cookie is set for secure requests
 */
async function ensureCsrfCookie(retries = 2): Promise<boolean> {
  try {
    // Because axios baseURL is '/api', this calls '/api/csrf/' on the server.
    const res = await refreshCsrf();
    // server may return token or may only set cookie. Accept both.
    const token = res?.data?.csrfToken ?? getCookie('csrftoken') ?? null;
    if (token) setFallbackCsrf(token);
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
    const res = await api.get("/user/session/"); // becomes '/api/user/session/'
    if (res.data?.isAuthenticated) {
      state.user = res.data.user;
      state.isAuthenticated = true;
      state.sessionExpiry = res.data.sessionExpiry ? new Date(res.data.sessionExpiry) : null;
    } else {
      state.user = null;
      state.isAuthenticated = false;
      state.sessionExpiry = null;
    }
  } catch (err) {
    console.warn("Auth initialization failed:", err);
    state.user = null;
    state.isAuthenticated = false;
    state.sessionExpiry = null;
  } finally {
    state.loading = false;
  }
}

/**
 * Secure user login
 */
export async function login(email: string, password: string) {
  try {
    const normalizedEmail = email.trim().toLowerCase();
    if (!normalizedEmail || !password) return { success: false, message: "Email and password are required" };

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(normalizedEmail)) return { success: false, message: "Please enter a valid email address" };

    await ensureCsrfCookie();

    // call '/api/user/login/'
    const res = await api.post("/user/login/", { email: normalizedEmail, password });

    if (res.data?.user) {
      state.user = res.data.user;
      state.isAuthenticated = true;
      state.sessionExpiry = res.data.sessionExpiry ? new Date(res.data.sessionExpiry) : null;
      return { success: true };
    }

    return { success: false, message: "Invalid response from server" };
  } catch (err: any) {
    console.error("Login error:", err);
    if (err?.response) {
      const detail = err.response.data?.detail;
      const status = err.response.status;
      if (status === 401) return { success: false, message: "Invalid email or password" };
      if (status === 429) return { success: false, message: "Too many login attempts. Please try later." };
      return { success: false, message: detail || "Login failed", status };
    }
    return { success: false, message: "Network error. Please check your connection." };
  }
}

/** logout */
export async function logout(): Promise<void> {
  try {
    await api.post("/user/logout/", {});
  } catch (err) {
    console.error("Logout request failed:", err);
  } finally {
    state.user = null;
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
 * Auto-logout when session expires
 */
export function checkSessionExpiry(): void {
  if (state.isAuthenticated && isSessionExpired()) {
    console.warn("Session expired, logging out");
    logout();
  }
}

/**
 * Refresh session information
 */
export async function refreshSession(): Promise<boolean> {
  try {
    const res = await api.get("/user/session/");
    
    if (res.data?.isAuthenticated) {
      state.user = res.data.user;
      state.isAuthenticated = true;
      state.sessionExpiry = res.data.sessionExpiry ? new Date(res.data.sessionExpiry) : null;
      return true;
    } else {
      state.user = null;
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
 * Upload image with proper authentication
 */
export async function uploadImage(formData: FormData) {
  try {
    if (!state.isAuthenticated) {
      throw new Error("Authentication required");
    }

    // Check session expiry before upload
    if (isSessionExpired()) {
      await logout();
      throw new Error("Session expired. Please log in again.");
    }

    const res = await api.post("/images/", formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      timeout: 30000, // 30 second timeout for uploads
    });

    return { success: true, data: res.data };
  } catch (err: any) {
    console.error("Image upload error:", err);
    
    if (err?.response) {
      const detail = err.response.data?.detail;
      const status = err.response.status;
      
      if (status === 403) {
        // Session may have expired
        await logout();
        return { success: false, message: "Please log in again", shouldRedirect: true };
      }
      
      return {
        success: false,
        message: detail || "Upload failed",
      };
    }
    
    return { success: false, message: err.message || "Network error" };
  }
}

/**
 * Get user's image history
 */
export async function getUserImages() {
  try {
    if (!state.isAuthenticated) {
      throw new Error("Authentication required");
    }

    const res = await api.get("/images/");
    return { success: true, data: res.data };
  } catch (err: any) {
    console.error("Get images error:", err);
    
    if (err?.response?.status === 403) {
      await logout();
      return { success: false, message: "Please log in again", shouldRedirect: true };
    }
    
    return { 
      success: false, 
      message: err?.response?.data?.detail || "Failed to load images" 
    };
  }
}

/**
 * Process image with selected distortion type
 */
export async function processImage(imageId: number, distortionType?: string) {
  try {
    if (!state.isAuthenticated) {
      throw new Error("Authentication required");
    }

    const endpoint = distortionType ? "/process-gan/" : "/process/";
    const payload = distortionType 
      ? { image_id: imageId, distortion_type: distortionType }
      : { image_id: imageId };

    const res = await api.post(endpoint, payload, {
      timeout: 60000, // 1 minute timeout for processing
    });

    return { success: true, data: res.data };
  } catch (err: any) {
    console.error("Image processing error:", err);
    
    if (err?.response?.status === 403) {
      await logout();
      return { success: false, message: "Please log in again", shouldRedirect: true };
    }
    
    return {
      success: false,
      message: err?.response?.data?.error || "Processing failed",
    };
  }
}

/**
 * Reactive auth state accessor
 */
export function useAuth() {
  return {
    ...state,
    isSessionExpired,
    checkSessionExpiry,
    refreshSession,
    uploadImage,
    getUserImages,
    processImage,
  };
}