<template>
  <div
    class="bg-orange-50 min-h-[calc(100vh-90px)] flex items-center justify-center"
    aria-labelledby="distortion-options-title"
  >
    <div class="max-w-3xl w-full px-6 sm:px-8 py-10">
      <!-- Title -->
      <h1
        id="distortion-options-title"
        class="text-3xl sm:text-4xl font-bold text-[#265d9c] text-center mb-6"
      >
        Choose how you’d like to proceed
      </h1>

      <!-- Subtext (plain, non-technical) -->
      <p class="text-gray-700 text-center text-lg mb-10">
        You can let LiPAD analyze your license plate image to figure out what kind of blur or
        distortion it has. Or, if you already know, you can pick it yourself.
      </p>

      <!-- Gentle notice if no imageId was provided -->
      <!-- <div
        v-if="!imageId"
        class="bg-white/80 border border-[#265d9c]/30 rounded-xl p-4 text-sm text-gray-700 mb-6"
      >
        <strong class="text-[#265d9c]">Note:</strong> We don’t see a recent upload.
        You can still continue, but some steps may ask for an image first.
      </div> -->

      <!-- Actions -->
      <div class="space-y-4">
        <!-- Auto-classify button -->
        <button
          type="button"
          class="w-full bg-[#265d9c] hover:bg-[#1d4b81] text-white text-lg font-semibold py-4 px-6 rounded-xl shadow transition cursor-pointer disabled:opacity-60 disabled:cursor-not-allowed"
          @click="proceedAuto(imageId ? parseInt(imageId) : null)"
          :disabled="busy"
          aria-label="Let LiPAD detect the distortion automatically"
        >
          <span class="sr-only">Primary Action:</span>
          Let LiPAD classify the distortion automatically
        </button>

        <!-- Manual classification button -->
        <button
          type="button"
          class="w-full bg-white border border-[#265d9c] hover:bg-gray-100 text-[#265d9c] text-lg font-semibold py-4 px-6 rounded-xl shadow transition cursor-pointer disabled:opacity-60 disabled:cursor-not-allowed"
          @click="proceedManual"
          :disabled="busy"
          aria-label="I will choose the distortion myself"
        >
          <span class="sr-only">Secondary Action:</span>
          I’ll choose the distortion myself
        </button>
      </div>

      <!-- Non-blocking status/error -->
      <p
        v-if="error"
        class="mt-6 text-center text-red-600 text-sm"
        role="alert"
      >
        {{ error }}
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import http from '@/services/http'
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { errorMessages } from 'vue/compiler-sfc'


const router = useRouter()
const route = useRoute()

// Image identifier 
const imageId = (route.query?.imageId as string | undefined) || undefined

// Busy flag to prevent double clicks / race conditions
const busy = ref(false)
const error = ref<string>('')

// Centralized guarded navigation
const safeNavigate = async (name: string, query: Record<string, string | undefined> = {}) => {
  if (busy.value) return
  busy.value = true
  error.value = ''
  try {
    // Always prefer named routes for clarity and refactor-safety
    await router.push({ name, query })
  } catch (e) {
    // Do not leak internal errors
    error.value = 'Navigation failed. Please try again.'
    // Optionally log to your telemetry here
  } finally {
    busy.value = false
  }
}

// Proceed with auto-classification route.
const proceedAuto = async (imageId: number | null): Promise<void> => {
  error.value = ''
  if (!imageId) {
    error.value = 'No imageId provided.'
    return
  }

  try {
    const { data } = await http.post('/process/', { image_id: imageId })
    await safeNavigate('LoadingPage', { imageId: String(imageId) })
  } catch (err: any) {
    const msg =
      err?.response?.data?.errors ||
      err?.response?.data?.detail ||
      err?.message ||
      'Processing failed.'
    error.value = Array.isArray(msg) ? msg.join(', ') : String(msg)
  }
}

// Proceed with manual classification route.

const proceedManual = async () => {
  await safeNavigate('ManualClassifier', imageId ? { imageId } : {})
}
</script>
