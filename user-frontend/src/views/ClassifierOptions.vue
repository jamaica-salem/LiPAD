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

      <!-- Actions -->
      <div class="space-y-4">
        <!-- Auto-classify button -->
        <button
          type="button"
          class="w-full bg-[#265d9c] hover:bg-[#1d4b81] text-white text-lg font-semibold py-4 px-6 rounded-xl shadow transition cursor-pointer disabled:opacity-60 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          @click="proceedAuto(imageId ? parseInt(imageId) : null)"
          :disabled="busyAuto"
          aria-label="Let LiPAD detect the distortion automatically"
        >
          <span v-if="!busyAuto">Let LiPAD classify the distortion automatically</span>
          <span v-else class="flex items-center gap-2">
            Processing...
          </span>
        </button>

        <!-- Manual classification button -->
        <button
          type="button"
          class="w-full bg-white border border-[#265d9c] hover:bg-gray-100 text-[#265d9c] text-lg font-semibold py-4 px-6 rounded-xl shadow transition cursor-pointer disabled:opacity-60 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          @click="proceedManual"
          :disabled="busyManual"
          aria-label="I will choose the distortion myself"
        >
          <span v-if="!busyManual">I’ll choose the distortion myself</span>
          <span v-else class="flex items-center gap-2">
            Loading...
          </span>
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
const busyAuto = ref(false)
const busyManual = ref(false)
const error = ref('')

// Proceed with auto-classification route
const proceedAuto = async (imageId: number | null) => {
  if (busyAuto.value) return
  error.value = ''
  busyAuto.value = true

  if (!imageId) {
    error.value = 'No imageId provided.'
    busyAuto.value = false
    return
  }

  try {
    await http.post('/process/', { image_id: imageId })
    await router.push({ name: 'LoadingPage', query: { imageId: String(imageId) } })
  } catch (err: any) {
    const msg = err?.response?.data?.errors ||
                err?.response?.data?.detail ||
                err?.message ||
                'Processing failed.'
    error.value = Array.isArray(msg) ? msg.join(', ') : String(msg)
    busyAuto.value = false
  }
}

const proceedManual = async () => {
  if (busyManual.value) return
  error.value = ''
  busyManual.value = true

  try {
    await router.push({ name: 'ManualClassifier', query: imageId ? { imageId } : {} })
  } catch (err) {
    console.error(err)
    error.value = 'Navigation failed. Please try again.'
    busyManual.value = false
  }
}

</script>
