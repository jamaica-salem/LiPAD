<template>
  <div class="flex gap-4 bg-orange-50 p-4 h-full">
    <!-- Left: Image Slider (75%) -->
    <div
      class="w-3/4 bg-white rounded-xl shadow-md p-3 flex flex-col justify-center items-center relative overflow-hidden"
    >
      <h2 class="text-xl font-bold text-[#265d9c] mb-3">Before & After</h2>

      <!-- Image Comparison Slider -->
      <div
        ref="sliderContainer"
        class="relative w-full max-w-2xl aspect-[4/2] overflow-hidden rounded-lg border border-gray-300"
      >
        <!-- Output Image -->
        <img
          :src="outputImage"
          alt="Output Image"
          class="absolute inset-0 w-full h-full object-cover select-none"
          draggable="false"
        />

        <!-- Input Image -->
        <img
          :src="inputImage"
          alt="Input Image"
          class="absolute inset-0 w-full h-full object-cover select-none pointer-events-none"
          :style="{
            clipPath: `inset(0 ${100 - sliderPosition}% 0 0)`,
          }"
          draggable="false"
        />

        <!-- Slider Handle -->
        <div
          class="absolute top-0 bottom-0 z-10 flex items-center justify-center w-5 h-full -ml-2.5 cursor-col-resize"
          :style="{ left: sliderPosition + '%' }"
          @mousedown="startDragging"
        >
          <div class="w-0.5 h-full bg-[#265d9c]"></div>
          <MoveHorizontal
            class="absolute text-[#265d9c] w-5 h-5 pointer-events-none"
            style="top: 50%; transform: translateY(-50%)"
          />
        </div>
      </div>

      <p class="text-xs text-gray-500 mt-1">Drag the slider to compare input and output.</p>
    </div>

    <!-- Right: Image Details (25%) -->
    <div
      class="w-1/4 bg-white rounded-xl shadow-md p-4 text-xs text-[#0e2247] flex flex-col"
    >
      <div class="flex-1">
        <!-- Results -->
        <div class="mb-4">
          <h3 class="text-lg font-bold text-[#265d9c] mb-1">Results</h3>
          <p>
            <span class="font-semibold">Status: </span>
            <span
              :class="{
                'text-green-600 bg-green-100 font-semibold px-1.5 py-0.5 rounded-md':
                  status === 'SUCCESSFUL',
                'text-red-600 bg-red-100 font-semibold px-1.5 py-0.5 rounded-md':
                  status === 'FAILED',
              }"
            >
              {{ status }}
            </span>
          </p>
          <p class="mt-0.5">
            <span class="font-semibold">Time Elapsed: </span> {{ timeElapsed }}
          </p>
          <p class="mt-0.5">
            <span class="font-semibold">Confidence Level: </span> {{ confidenceLevel }}%
          </p>
        </div>

        <!-- Input Image Info -->
        <div class="mb-4">
          <h3 class="text-lg font-bold text-[#265d9c] mb-1">Input Image</h3>
          <p>
            <span class="font-semibold">Distortion Type: </span> {{ inputDistortion }}
          </p>
        </div>

        <!-- Output Image Info -->
        <div>
          <h3 class="text-lg font-bold text-[#265d9c] mb-1">Output Image</h3>
          <p>
            <span class="font-semibold">Distortion Type: </span> {{ outputDistortion }}
          </p>
          <p><span class="font-semibold">Plate No.: </span> {{ plateNumber }}</p>
        </div>
      </div>

      <!-- Buttons Grouped Together -->
      <div class="flex flex-col mt-4">
        <button
          class="bg-[#265d9c] text-white font-semibold py-1.5 px-3 rounded-lg mb-2 hover:bg-[#1d3e73] transition cursor-pointer"
          @click="showFullScreen = true"
        >
          Show Result
        </button>

        <button
          class="bg-[#265d9c] text-white font-semibold py-1.5 px-3 rounded-lg hover:bg-[#1d3e73] transition cursor-pointer"
          @click="downloadResult"
        >
          Download Result
        </button>
      </div>
    </div>

    <!-- Full-Screen Modal for Output Image -->
    <div
      v-if="showFullScreen"
      class="fixed inset-0 z-50 flex justify-center items-center p-3.5 bg-black/20"
    >
      <!-- Card Container -->
      <div
        class="relative bg-white rounded-3xl shadow-2xl max-w-6xl w-[60%] max-h-[100vh] flex flex-col items-center p-4"
      >
        <!-- Close Button -->
        <button
          @click="showFullScreen = false"
          class="absolute top-3 right-3 text-white cursor-pointer bg-red-600 hover:bg-red-800 rounded-2xl w-8 h-8 flex items-center justify-center shadow-sm transition"
          aria-label="Close"
        >
          ✕
        </button>

        <!-- Enlarged Output Image -->
        <img
          :src="outputImage"
          alt="Full Output"
          class="rounded-4xl max-h-[70vh] object-contain w-full border border-gray-200 shadow"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import beforeImage from '@/assets/before.png'
import afterImage from '@/assets/after.png'
import { MoveHorizontal } from 'lucide-vue-next'

// Mocked Data
const inputImage = beforeImage
const outputImage = afterImage
const status = 'SUCCESSFUL'
const timeElapsed = '1.52s'
const confidenceLevel = 92
const inputDistortion = 'Low Light'
const outputDistortion = 'Normal'
const plateNumber = 'ABC1234'

// Slider logic
const sliderPosition = ref(50)
let isDragging = false

const startDragging = () => {
  isDragging = true
  window.addEventListener('mousemove', dragSlider)
  window.addEventListener('mouseup', stopDragging)
}
const stopDragging = () => {
  isDragging = false
  window.removeEventListener('mousemove', dragSlider)
  window.removeEventListener('mouseup', stopDragging)
}
const dragSlider = (e) => {
  const container = document.querySelector('.aspect-\\[4\\/2\\]')
  if (!container) return
  const rect = container.getBoundingClientRect()
  const offsetX = e.clientX - rect.left
  sliderPosition.value = Math.max(0, Math.min(100, (offsetX / rect.width) * 100))
}

// Full-screen modal logic
const showFullScreen = ref(false)

// Download handler
const downloadResult = () => {
  try {
    const link = document.createElement('a')
    link.href = outputImage
    link.download = 'deblurred_result.jpg'
    link.click()
  } catch (error) {
    alert('Failed to download the result. Please try again.')
    console.error(error)
  }
}
</script>

<style scoped>
.aspect-\[4\/2\] {
  aspect-ratio: 4 / 2;
  max-height: 400px;
}
</style>
