<template>
  <div class="min-h-[calc(100vh-90px)] flex flex-col items-center justify-center bg-orange-50 text-[#265d9c]">
    <!-- Animated Icon -->
    <div class="mb-8 animate-pulse">
      <ScanLineIcon class="w-32 h-32 text-orange-800" />
    </div>

    <!-- Random Loading Text -->
    <p
      class="text-2xl sm:text-2xl font-bold text-center px-8 transition-opacity duration-500"
      :key="currentText"
    >
      {{ currentText }}
    </p>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ScanLine as ScanLineIcon } from 'lucide-vue-next'
import http from '@/services/http'

const route = useRoute()
const router = useRouter()
const imageId = route.query.imageId

const messages = [
  'Enhancing image clarity...',
  'Sharpening license plate details...',
  'Processing your image with advanced AI...',
  'Improving visual accuracy...',
  'Analyzing image data...',
  'Optimizing for better plate recognition...',
  'Refining image resolution...',
  'Applying intelligent deblurring...',
  'Extracting plate information...',
  'LiPAD is processing your request...'
]

// Initialize with a random message
const currentText = ref(messages[Math.floor(Math.random() * messages.length)])

let intervalId
let pollerId

onMounted(() => {
  intervalId = setInterval(() => {
    const randomIndex = Math.floor(Math.random() * messages.length)
    currentText.value = messages[randomIndex]
  }, 3500)

  startPolling()
})

const startPolling = () => {
  pollerId = setInterval(async () => {
    try {
      const { data } = await http.get(`/images/${imageId}/`)
      if (data.after_image) {
        clearInterval(pollerId)
        clearInterval(intervalId)

        if (data.after_distortion_type === 'Normal' && data.status == 'Successful' && data.plate_no != "") {
          router.push({ name: 'Result', query: { imageId } })
        } else {
          router.push({ name: 'FailurePage', query: { imageId } })
        }
      }
    } catch (err) {
      console.error('Polling failed:', err)
    }
  }, 3000)
}

onBeforeUnmount(() => {
  clearInterval(intervalId)
  clearInterval(pollerId)
})
</script>
