<template>
  <div class="flex min-h-screen bg-[#e6f0fb]">
    <!-- Left-side branding -->
    <div class="hidden lg:flex flex-1 bg-gradient-to-br from-[#d9e7f6] to-[#e2effb] items-center justify-center">
      <div class="text-center px-12">
        <div class="flex justify-center mb-6">
          <div class="bg-[#ccdef0] p-4 rounded-2xl shadow-lg">
            <ScanLineIcon class="text-[#265d9c]" size="40" />
          </div>
        </div>
        <h2 class="text-3xl font-bold text-[#0E2247]">Welcome to LiPAD</h2>
        <p class="mt-4 text-[#0E2247]/70">Log in to continue to your dashboard.</p>
      </div>
    </div>

    <!-- Login Card -->
    <div class="flex flex-1 items-center justify-center p-6">
      <div class="bg-white rounded-3xl shadow-2xl max-w-md w-full p-10">
        <!-- Mobile logo -->
        <div class="flex justify-center mb-6 lg:hidden">
          <div class="bg-[#c9def3] p-4 rounded-2xl shadow-lg">
            <ScanLineIcon class="text-[#265d9c]" size="36" />
          </div>
        </div>

        <h1 class="text-2xl font-bold text-[#1f2f44] mb-6 text-center">User Login</h1>

        <!-- Error message -->
        <p v-if="error" class="text-sm text-red-600 text-center mb-4">{{ error }}</p>

        <!-- Login form -->
        <form @submit.prevent="handleLogin" class="space-y-4 mb-4">
          <input
            type="email"
            v-model="email"
            placeholder="Email"
            class="w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-[#a3c1e9] focus:border-[#a3c1e9]"
            :disabled="loading"
          />
          <input
            type="password"
            v-model="password"
            placeholder="Password"
            class="w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-[#a3c1e9] focus:border-[#a3c1e9]"
            :disabled="loading"
          />
          <div class="flex justify-between items-center text-xs">
            <p class="text-gray">Forgot your password? Please contact the admin.</p>
          </div>
          <button
            type="submit"
            class="w-full bg-[#265d9c] text-white rounded-lg py-2 hover:bg-[#1f2f44] transition disabled:opacity-50"
            :disabled="loading"
          >
            {{ loading ? 'Logging in...' : 'Log In' }}
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
const error = ref('')
const loading = ref(false)

const router = useRouter()

const handleLogin = async () => {
  error.value = ''
  if (!email.value || !password.value) {
    error.value = 'Please enter both email and password.'
    return
  }

  try {
    loading.value = true

    // Simulate API delay 
    await new Promise((resolve) => setTimeout(resolve, 1000))

    if (email.value === 'user@example.com' && password.value === 'password') {
      router.push({ name: 'Users' })
    } else {
      error.value = 'Invalid email or password.'
    }
  } catch (err) {
    error.value = 'An unexpected error occurred. Please try again later.'
  } finally {
    loading.value = false
  }
}

</script>
