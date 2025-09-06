<template>
  <div class="flex min-h-screen bg-[#e6f0fb]">

    <!-- Left-side branding -->
    <div class="hidden lg:flex flex-1 bg-gradient-to-br from-[#d9e7f6] to-[#e2effb] items-center justify-center">
      <div class="text-center px-8">
        <div class="flex justify-center mb-4">
          <div class="bg-[#265d9c] p-3 rounded-2xl shadow-lg">
            <img
              src="@/assets/logo.png"
              alt="LiPAD Logo"
              class="w-8 h-8 object-contain"
            />
          </div>
        </div>
        <h2 class="text-2xl font-bold text-[#0E2247]">LiPAD Admin</h2>
        <p class="mt-3 text-sm text-[#0E2247]/70">Log in to continue to your dashboard.</p>
      </div>
    </div>

    <!-- Login Card -->
    <div class="flex flex-1 items-center justify-center p-4">
      <div class="bg-white rounded-3xl shadow-2xl max-w-sm w-full p-8">

        <!-- Mobile logo -->
        <div class="flex justify-center mb-4 lg:hidden">
          <div class="bg-[#c9def3] p-3 rounded-2xl shadow-lg">
            <ScanLineIcon class="text-[#265d9c]" :size="28" />
          </div>
        </div>

        <h1 class="text-xl font-bold text-[#1f2f44] mb-4 text-center">Admin Login</h1>

        <!-- Login form -->
        <form @submit.prevent="handleLogin" class="space-y-3 mb-3" novalidate>
          <input
            type="email"
            v-model="email"
            placeholder="Email"
            class="w-full border border-gray-300 rounded-lg px-3 py-1.5 focus:outline-none focus:ring-2 focus:ring-[#a3c1e9] focus:border-[#a3c1e9]"
            autocomplete="email"
            required
          />
          <input
            type="password"
            v-model="password"
            placeholder="Password"
            class="w-full border border-gray-300 rounded-lg px-3 py-1.5 focus:outline-none focus:ring-2 focus:ring-[#a3c1e9] focus:border-[#a3c1e9]"
            autocomplete="current-password"
            required
          />
          <div class="flex justify-between items-center text-xs">
            <a href="#" class="text-[#265d9c] hover:underline">Forgot password?</a>
          </div>

          <!-- Error Message -->
          <p v-if="errorMessage" class="text-red-600 text-sm text-center mt-2">
            {{ errorMessage }}
          </p>

          <button
            type="submit"
            :disabled="loading"
            class="w-full bg-[#265d9c] text-white rounded-lg py-1.5 hover:bg-[#1f2f44] transition disabled:opacity-60 cursor-pointer"
          >
            <span v-if="!loading">Log In</span>
            <span v-else>Logging in...</span>
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/*
  Session-based login:
  - Uses useAuth.login(email, password) which calls /api/csrf/ and /api/login/
*/
import { ref, watchEffect, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ScanLine as ScanLineIcon } from 'lucide-vue-next'
import { login, useAuth } from '@/composables/useAuth' // composable provided earlier

// form fields (UI unchanged)
const email = ref('')
const password = ref('')
const rememberMe = ref(false) // UI control preserved; implementation notes below
const errorMessage = ref('')
const loading = ref(false)

const router = useRouter()
const auth = useAuth()

// If the user is already authenticated, redirect away from login.
// This prevents "going back" to login while session is active.
onMounted(() => {
  if (!auth.loading && auth.isAuthenticated) {
    router.replace({ path: '/app' })
  }
})

// Watch in case auth state becomes "authenticated" while on this page
watchEffect(() => {
  if (!auth.loading && auth.isAuthenticated) {
    router.replace({ path: '/app' })
  }
})

/**
 * handleLogin: client-side validation -> call composable login -> handle responses
 * - On success: user is redirected to the Users page (inside MainLayout).
 * - On failure: show an appropriate error message.

 */
const handleLogin = async () => {
  errorMessage.value = ''
  if (!email.value.trim() && !password.value) {
    errorMessage.value = 'Email and password are required.'
    return
  }
  if (!email.value.trim()) {
    errorMessage.value = 'Email is required.'
    return
  }
  if (!password.value) {
    errorMessage.value = 'Password is required.'
    return
  }

  loading.value = true
  try {
    // call composable login() which will:
    // 1) call /api/csrf/ to set csrftoken cookie
    // 2) call POST /api/login/ with { email, password }
    const res = await login(email.value.trim(), password.value)

    if (res.success) {
      // success: composable set state.admin & isAuthenticated
      // redirect to main section (Users page) — inside MainLayout
      router.push({ name: 'Users' })
    } else {
      // show server or network-provided message
      errorMessage.value = res.message || 'Login failed. Please try again.'
    }
  } catch (err) {
    // Unexpected error (should be covered above, but catch just in case)
    console.error('Login error (unexpected):', err)
    errorMessage.value = 'Network error. Please try again.'
  } finally {
    loading.value = false
  }
}
</script>
