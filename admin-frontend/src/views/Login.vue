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
import { ScanLine as ScanLineIcon } from 'lucide-vue-next'

const email = ref('')
const password = ref('')
const router = useRouter()
const errorMessage = ref('')  // for login errors

const handleLogin = async () => {
  errorMessage.value = ''  // reset error
  try {
    const response = await fetch('http://localhost:8000/auth/admin-login/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        email: email.value,
        password: password.value
      }),
    })

    if (!response.ok) {
      const errorData = await response.json()
      errorMessage.value = errorData.detail || 'Login failed.'
      return
    }

    const data = await response.json()

    // Store tokens securely (session-based)
    sessionStorage.setItem('access_token', data.access_token)
    sessionStorage.setItem('refresh_token', data.refresh_token)

    // Optionally store admin info
    sessionStorage.setItem('admin', JSON.stringify(data.admin))

    // ✅ Redirect to Users dashboard
    router.push({ name: 'Users' })
  } catch (err) {
    errorMessage.value = 'Network error. Please try again.'
  }
}
</script>

