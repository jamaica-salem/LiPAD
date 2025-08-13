<template>
  <div
    class="min-h-[calc(100vh-90px)] flex flex-col items-center justify-center bg-orange-50 text-[#265d9c]"
  >
    <!-- Creative Failed Icon -->
    <div class="mb-8 animate-bounce">
      <ImageOffIcon class="w-32 h-32 text-orange-800" />
    </div>

    <!-- Random failure message -->
    <p class="text-4xl font-bold text-center mb-6 px-10 leading-snug">
      {{ failureMessage }}
    </p>

    <!-- Follow-up question -->
    <p class="text-2xl font-semibold mb-16">Would you still like to see the result?</p>

    <!-- Action buttons -->
    <div class="flex gap-8">
      <button
        class="w-48 bg-[#265d9c] hover:bg-[#1d4a80] text-white text-xl font-semibold py-3 px-8 rounded-full transition duration-300 shadow-lg"
        @click="goTo('/result')"
      >
        Yes
      </button>
      <button
        class="w-48 bg-white hover:bg-[#f4f4f4] text-[#265d9c] text-xl font-semibold py-3 px-8 rounded-full transition duration-300 shadow-lg"
        @click="goTo('/upload')"
      >
        No
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ImageOff as ImageOffIcon } from 'lucide-vue-next'

// --- List of humorous or gentle error messages ---
const messages = [
  'Failed to deblur the image.',
  'We couldn’t enhance your license plate.',
  'Image processing was unsuccessful.',
  'The AI couldn’t recover enough detail.',
  'Deblurring attempt failed.',
  'Oops! We couldn’t clarify that plate.',
  'Sorry, the image could not be processed.',
  'Your upload couldn’t be improved.',
  'AI enhancement didn’t work this time.',
  'We hit a roadblock deblurring the image.'
]

// --- Only choose a random message once per session ---
const failureMessage = ref('')
onMounted(() => {
  const index = Math.floor(Math.random() * messages.length)
  failureMessage.value = messages[index]
})

// --- Handle user clicking Yes or No ---
const handleUserChoice = (choice) => {
  if (choice) {
    // placeholder if yes
    console.log('User chose to view the result')
  } else {
    // placeholder if no
    console.log('User declined to view the result')
  }
}
</script>
