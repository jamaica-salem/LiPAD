<template>
  <div class="flex min-h-screen bg-[#e6f0fb]">
    <!-- Left-side branding -->
    <div class="hidden lg:flex flex-1 bg-gradient-to-br from-[#d9e7f6] to-[#e2effb] items-center justify-center">
      <div class="text-center px-10">
        <div class="flex justify-center mb-5">
          <div class="bg-[#265d9c] p-3 rounded-2xl shadow-lg">
            <img
              src="@/assets/logo.png"
              alt="LiPAD Logo"
              class="w-8 h-8 object-contain"
            />
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
            <ScanLineIcon class="text-[#265d9c]" :size="28" />
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

          <div class="flex justify-between items-center text-xs">
            <label class="flex items-center gap-1 text-[#1f2f44]">
              Forgot password? Please contact the admin.
            </label>
          </div>

          <!-- Error message container -->
          <p v-if="errorMessage" class="text-red-600 text-sm text-center mt-2">
            {{ errorMessage }}
          </p>

          <button
            type="submit"
            class="w-full bg-[#265d9c] text-white rounded-lg py-1.5 hover:bg-[#1f2f44] transition disabled:opacity-60 cursor-pointer"
            :disabled="loading"
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
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ScanLine as ScanLineIcon } from 'lucide-vue-next'
import { login, useAuth } from '@/composables/useAuth'

const router = useRouter()
const auth = useAuth()

const email = ref('')
const password = ref('')
const errorMessage = ref('')
const loading = ref(false)

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
    const res = await login(email.value.trim(), password.value)
    if (res.success) {
      // Session-based login successful. Redirect to upload page.
      router.push({ name: 'LicensePlateUpload' })
    } else {
      errorMessage.value = res.message || 'Login failed. Please try again.'
    }
  } catch (err) {
    console.error('Login error (unexpected):', err)
    errorMessage.value = 'Network error. Please try again.'
  } finally {
    loading.value = false
  }

  router.replace({ name: 'LicensePlateUpload' });
  
}
</script>
