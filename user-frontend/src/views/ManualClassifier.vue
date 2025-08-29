<template>
    <div class="flex flex-col items-center py-10 px-6 bg-orange-50 min-h-[calc(100vh-90px)]">
      <!-- Page Title -->
      <h1 class="text-3xl font-bold text-[#265d9c] mb-8">Manual Classifier</h1>
      <p class="text-center text-gray-600 mb-10"> Choose the type of distortion you see in the license plate image for manual classification. </p>

      <!-- Button Grid -->
      <div class="grid grid-cols-2 gap-6 w-full max-w-4xl">
        <!-- Low Quality -->
        <button
          class="flex flex-col items-center p-4 rounded-2xl shadow-md transition duration-200 bg-[#265d9c] hover:bg-[#1d4b81] text-white cursor-pointer"
          @click="submitDistortion('low_qual')"
          >
          <img :src="lowQuality" alt="Low Quality" class="w-50 h-28 rounded-xl mb-4 object-cover" />
          <h2 class="text-lg font-semibold mb-2">Low Quality</h2>
          <p class="text-sm text-center">
            Image suffers from pixelation or compression artifacts.
          </p>
        </button>

        <!-- Low Light -->
        <button
          class="flex flex-col items-center p-4 rounded-2xl shadow-md transition duration-200 bg-[#265d9c] hover:bg-[#1d4b81] text-white cursor-pointer"
          @click="submitDistortion('low_light')"
          >
          <img :src="lowLight" alt="Low Light" class="w-50 h-28 rounded-xl mb-4 object-cover" />
          <h2 class="text-lg font-semibold mb-2">Low Light</h2>
          <p class="text-sm text-center">
            Image is too dark due to poor lighting conditions.
          </p>
        </button>

        <!-- Horizontal Blur -->
        <button
          class="flex flex-col items-center p-4 rounded-2xl shadow-md transition duration-200 bg-[#265d9c] hover:bg-[#1d4b81] text-white cursor-pointer"
          @click="submitDistortion('h_blur')"
          >
          <img :src="horizontalBlur" alt="Horizontal Blur" class="w-50 h-28 rounded-xl mb-4 object-cover" />
          <h2 class="text-lg font-semibold mb-2">Horizontal Blur</h2>
          <p class="text-sm text-center">
            Motion blur along the horizontal axis reduces clarity.
          </p>
        </button>

        <!-- Vertical Blur -->
        <button
          class="flex flex-col items-center p-4 rounded-2xl shadow-md transition duration-200 bg-[#265d9c] hover:bg-[#1d4b81] text-white cursor-pointer"
          @click="submitDistortion('v_blur')"
          >
          <img :src="verticalBlur" alt="Vertical Blur" class="w-50 h-28 rounded-xl mb-4 object-cover" />
          <h2 class="text-lg font-semibold mb-2">Vertical Blur</h2>
          <p class="text-sm text-center">
            Motion blur along the vertical axis reduces visibility.
          </p>
        </button>
      </div>
    </div>
</template>

<script setup>

// Import images from assets folder
import lowQuality from '@/assets/low-quality.jpg'
import lowLight from '@/assets/low-light.jpg'
import horizontalBlur from '@/assets/horizontal-blur.jpg'
import verticalBlur from '@/assets/vertical-blur.jpg'

import { useRoute, useRouter } from 'vue-router'
import http from '@/services/http'

const route = useRoute()
const router = useRouter()
const imageId = route.query.imageId

const submitDistortion = async (distortionType) => {
  try {
    const { data } = await http.post('/process-gan/', {
      image_id: imageId,
      distortion_type: distortionType,
    })

    router.push({ name: 'LoadingPage', query: { imageId } })
  } catch (err) {
    const msg =
      err?.response?.data?.errors ||
      err?.response?.data?.detail ||
      err?.message ||
      'Processing failed.'
    error.value = Array.isArray(msg) ? msg.join(', ') : String(msg)
  }
}
</script>
