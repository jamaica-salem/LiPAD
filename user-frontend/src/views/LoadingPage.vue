<template>
  <div class="min-h-[calc(100vh-90px)] flex flex-col items-center justify-center bg-gradient-to-br from-orange-50 via-orange-100 to-orange-200 text-[#265d9c]">
    <!-- Animated Icon -->
    <div class="mb-10 animate-pulse">
      <ScanLineIcon class="w-50 h-50 text-orange-800" />
    </div>

    <!-- Random Loading Text -->
    <p class="text-3xl sm:text-3xl font-bold text-center px-10 transition-opacity duration-500" :key="currentText">
      {{ currentText }}
    </p>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { ScanLine as ScanLineIcon } from 'lucide-vue-next'

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

const currentText = ref(messages[0])
let intervalId

onMounted(() => {
  intervalId = setInterval(() => {
    const randomIndex = Math.floor(Math.random() * messages.length)
    currentText.value = messages[randomIndex]
  }, 3500)
})

onBeforeUnmount(() => {
  clearInterval(intervalId)
})
</script>
