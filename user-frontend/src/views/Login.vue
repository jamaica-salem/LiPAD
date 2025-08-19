<template>
  <div class="flex min-h-screen bg-[#e6f0fb]">
    <!-- Left-side branding -->
    <div class="hidden lg:flex flex-1 bg-gradient-to-br from-[#d9e7f6] to-[#e2effb] items-center justify-center">
      <div class="text-center px-10">
        <div class="flex justify-center mb-5">
          <div class="bg-[#ccdef0] p-3 rounded-2xl shadow-lg">
            <ScanLineIcon class="text-[#265d9c]" size="32" />
          </div>
        </div>
        <h2 class="text-2xl font-bold text-[#0E2247]">Welcome to LiPAD</h2>
        <p class="mt-3 text-sm text-[#0E2247]/70">
          Please log in to continue with license plate deblurring.
        </p>
      </div>
    </div>

    <!-- Login Card -->
    <div class="flex flex-1 items-center justify-center p-4">
      <div class="bg-white rounded-3xl shadow-2xl max-w-sm w-full p-8">
        <!-- Mobile logo -->
        <div class="flex justify-center mb-5 lg:hidden">
          <div class="bg-[#c9def3] p-3 rounded-2xl shadow-lg">
            <ScanLineIcon class="text-[#265d9c]" size="28" />
          </div>
        </div>

        <h1 class="text-xl font-bold text-[#1f2f44] mb-5 text-center">User Login</h1>

        <!-- Login form -->
        <form @submit.prevent="handleLogin" class="space-y-3 mb-3">
          <input
            type="email"
            v-model="email"
            placeholder="Email"
            class="w-full border border-gray-300 rounded-lg px-3 py-2"
          />
          <input
            type="password"
            v-model="password"
            placeholder="Password"
            class="w-full border border-gray-300 rounded-lg px-3 py-2"
          />

          <!-- ✅ Error message container -->
          <p v-if="errorMessage" class="text-red-600 text-sm text-center mt-2">
            {{ errorMessage }}
          </p>

          <button
            type="submit"
            class="w-full bg-[#265d9c] text-white rounded-lg py-2 hover:bg-[#1f2f44] transition"
          >
            Log In
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { ref } from 'vue'
import axios from 'axios'
import { ScanLine as ScanLineIcon } from 'lucide-vue-next'

const router = useRouter()
const email = ref('')
const password = ref('')
const errorMessage = ref('')

// Handle login securely
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
    const response = await axios.post('http://localhost:8000/api/auth/login/', {
      email: email.value,
      password: password.value,
    })

    // Store tokens securely (sessionStorage keeps session scoped)
    sessionStorage.setItem('access_token', response.data.access_token)
    sessionStorage.setItem('refresh_token', response.data.refresh_token)
    sessionStorage.setItem('user', JSON.stringify(response.data.user))

    // Debug log: Print first + last name to verify correct user
    console.log(
      `Logged in user: ${response.data.user.first_name} ${response.data.user.last_name}`
    )

    // Redirect securely to main dashboard
    router.push({ name: 'LicensePlateUpload' })
  } catch (err) {
    if (err.response && err.response.data) {
      const data = err.response.data

      // Check if credentials are invalid
      if (
        (typeof data === 'string' && data === 'Invalid credentials.') ||
        (Array.isArray(data) && data[0] === 'Invalid credentials.')
      ) {
        errorMessage.value = 'Invalid credentials.'
      } else {
        // All other backend errors
        errorMessage.value = 'Login failed.'
      }
    } else {
      // Network or unexpected error
      errorMessage.value = 'Network error. Please try again.'
    }
  }
}
</script>
