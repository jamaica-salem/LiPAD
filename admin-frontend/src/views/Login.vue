<template>
  <div class="flex min-h-screen bg-[#e6f0fb]">

    <!-- Left-side branding -->
    <div class="hidden lg:flex flex-1 bg-gradient-to-br from-[#d9e7f6] to-[#e2effb] items-center justify-center">
      <div class="text-center px-8">
        <div class="flex justify-center mb-4">
          <div class="bg-[#ccdef0] p-3 rounded-2xl shadow-lg">
            <ScanLineIcon class="text-[#265d9c]" size="32" />
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
            <ScanLineIcon class="text-[#265d9c]" size="28" />
          </div>
        </div>

        <h1 class="text-xl font-bold text-[#1f2f44] mb-4 text-center">Admin Login</h1>

        <!-- Login form -->
        <form @submit.prevent="handleLogin" class="space-y-3 mb-3">
          <input
            type="email"
            v-model="email"
            placeholder="Email"
            class="w-full border border-gray-300 rounded-lg px-3 py-1.5 focus:outline-none focus:ring-2 focus:ring-[#a3c1e9] focus:border-[#a3c1e9]"
          />
          <input
            type="password"
            v-model="password"
            placeholder="Password"
            class="w-full border border-gray-300 rounded-lg px-3 py-1.5 focus:outline-none focus:ring-2 focus:ring-[#a3c1e9] focus:border-[#a3c1e9]"
          />
          <div class="flex justify-between items-center text-xs">
            <label class="flex items-center gap-1 text-[#1f2f44]">
              <input type="checkbox" class="rounded text-[#265d9c] focus:ring-[#265d9c]" />
              Remember me
            </label>
            <a href="#" class="text-[#265d9c] hover:underline">Forgot password?</a>
          </div>
          <!-- Error Message -->
          <p v-if="errorMessage" class="text-red-600 text-sm text-center mt-2">
            {{ errorMessage }}
          </p>
          <button
            type="submit"
            class="w-full bg-[#265d9c] text-white rounded-lg py-1.5 hover:bg-[#1f2f44] transition"
          >
            Log In
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { ScanLine as ScanLineIcon } from 'lucide-vue-next'

const email = ref('')
const password = ref('')
const router = useRouter()
const errorMessage = ref('')

// Handle admin login securely
const handleLogin = async () => {
  errorMessage.value = '' // reset error before each attempt

  // Frontend validation to avoid unnecessary API calls
  if (!email.value && !password.value) {
    errorMessage.value = 'Email and password are required.'
    return
  }
  if (!email.value) {
    errorMessage.value = 'Email is required.'
    return
  }
  if (!password.value) {
    errorMessage.value = 'Password is required.'
    return
  }

  try {
    // Use axios for consistent API calls
    const response = await axios.post('http://localhost:8000/api/auth/admin-login/', {
      email: email.value,
      password: password.value,
    })

    // Store tokens securely (sessionStorage keeps session scoped)
    sessionStorage.setItem('access_token', response.data.access_token)
    sessionStorage.setItem('refresh_token', response.data.refresh_token)
    sessionStorage.setItem('admin', JSON.stringify(response.data.admin))

    // Debug log: Print admin name to verify correct login
    console.log(
      `Logged in admin: ${response.data.admin.first_name} ${response.data.admin.last_name}`
    )

    // Redirect securely to admin dashboard
    router.push({ name: 'Users' })
  } catch (err) {
    if (err.response && err.response.data) {
      const data = err.response.data

      // Check if credentials are invalid
      if (
        (typeof data === 'string' && data === 'Invalid credentials.') ||
        (Array.isArray(data) && data[0] === 'Invalid credentials.') ||
        (data.detail && Array.isArray(data.detail) && data.detail[0] === 'Invalid credentials.')
      ) {
        errorMessage.value = 'Invalid credentials.'
      } else {
        // All other backend errors
        errorMessage.value = 'Login failed. Please try again.'
      }
    } else {
      // Network or unexpected error
      errorMessage.value = 'Network error. Please try again.'
      console.error('Admin login error:', err)
    }
  }
}
</script>
