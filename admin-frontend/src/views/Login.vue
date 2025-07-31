<template>
  <div class="flex min-h-screen bg-[#e0ece6]">

    <!-- Left-side branding -->
    <div class="hidden lg:flex flex-1 bg-gradient-to-br from-[#f5faf7] to-[#e9f3ee] items-center justify-center">
      <div class="text-center px-12">
        <div class="flex justify-center mb-6">
          <div class="bg-[#d4e2da] p-4 rounded-2xl shadow-lg">
            <CoffeeIcon class="text-[#226440]" size="40" />
          </div>
        </div>
        <h2 class="text-3xl font-bold text-[#1f3329]">Welcome Back!</h2>
        <p class="mt-4 text-[#1f3329]/70">Sign in to continue to your dashboard</p>
      </div>
    </div>

    <!-- Login Card -->
    <div class="flex flex-1 items-center justify-center p-6">
      <div class="bg-white rounded-3xl shadow-2xl max-w-md w-full p-10">

        <!-- Mobile logo -->
        <div class="flex justify-center mb-6 lg:hidden">
          <div class="bg-[#d4e2da] p-4 rounded-2xl shadow-lg">
            <CoffeeIcon class="text-[#226440]" size="36" />
          </div>
        </div>

        <h1 class="text-2xl font-bold text-[#1f3329] mb-6 text-center">Admin Login</h1>

        <!-- Login form -->
        <form @submit.prevent="handleLogin" class="space-y-4 mb-4">
          <input
            type="email"
            v-model="email"
            placeholder="Email"
            class="w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-[#aacbb9] focus:border-[#aacbb9]"
          />
          <input
            type="password"
            v-model="password"
            placeholder="Password"
            class="w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-[#aacbb9] focus:border-[#aacbb9]"
          />
          <div class="flex justify-between items-center text-xs">
            <label class="flex items-center gap-1 text-[#1f3329]">
              <input type="checkbox" class="rounded text-[#226440] focus:ring-[#226440]" />
              Remember me
            </label>
            <a href="#" class="text-[#226440] hover:underline">Forgot password?</a>
          </div>
          <button
            type="submit"
            class="w-full bg-[#226440] text-white rounded-lg py-2 hover:bg-[#1f3329] transition"
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
import { Coffee as CoffeeIcon } from 'lucide-vue-next'

const email = ref('')
const password = ref('')
const router = useRouter()

const handleLogin = () => {
  // Dummy auth
  if (email.value && password.value) {
    router.push('/users')
  }
}
</script>
