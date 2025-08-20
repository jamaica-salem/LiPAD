<template>
  <div class="bg-orange-50 min-h-[calc(100vh-90px)] flex items-center justify-center">
    <div class="max-w-3xl mx-auto py-12">
      <!-- Header Title -->
      <h1 class="text-3xl sm:text-3xl font-bold text-[#265d9c] mb-6 text-center">
        LiPAD: AI-Powered Philippine License Plate Deblurring and Recognition
      </h1>

      <!-- Description -->
      <p class="text-base sm:text-lg text-gray-700 mb-8 leading-relaxed text-center">
        Enhance license plate visibility effortlessly with LiPAD, your smart AI solution for deblurring and recognition.
        Designed to process low-quality images with precision, LiPAD restores clarity and extracts essential plate details in seconds.
      </p>

      <!-- Upload area -->
      <div
        class="bg-white border-2 border-dashed border-[#265d9c] rounded-2xl p-8 text-center shadow-md hover:shadow-lg transition-all duration-200"
        @dragover.prevent="handleDragOver"
        @drop.prevent="handleDrop"
      >
        <!-- Lucide Icon -->
        <div class="mb-4 text-[#265d9c] opacity-60">
          <Upload class="mx-auto w-16 h-16" />
        </div>

        <p class="text-gray-600 text-sm sm:text-base mb-4">Drag & drop a license plate image here or</p>

        <!-- File Picker Button -->
        <input
          ref="fileInput"
          type="file"
          accept="image/*"
          @change="handleFileChange"
          class="hidden"
        />
        <button
          @click="triggerFileInput"
          class="bg-[#265d9c] hover:bg-[#1d4b81] text-white font-medium py-2.5 px-6 rounded-lg shadow text-base"
        >
          Upload Image
        </button>

        <!-- Selected file info -->
        <div v-if="selectedFile" class="mt-4 text-gray-800 text-sm">
          <p><strong>Selected:</strong> {{ selectedFile.name }}</p>
        </div>

        <!-- Error message -->
        <div v-if="errorMessage" class="mt-4 text-red-600 font-semibold text-sm">
          {{ errorMessage }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
// Imports
import { ref } from 'vue'
import { Upload } from 'lucide-vue-next'
import { useRouter } from 'vue-router'

// Refs
const fileInput = ref(null)
const selectedFile = ref(null)
const errorMessage = ref('')
const router = useRouter()

// Trigger file picker
const triggerFileInput = () => {
  fileInput.value?.click()
}

// Validate image
const isValidImage = (file) => {
  return file && file.type.startsWith('image/')
}

// Handle file selection
const handleFileChange = (event) => {
  const file = event.target.files[0]
  processFile(file)
}

// Handle drag events
const handleDragOver = (event) => {
  event.dataTransfer.dropEffect = 'copy'
}

// Handle drop events
const handleDrop = (event) => {
  const file = event.dataTransfer.files[0]
  processFile(file)
}

// Process file
const processFile = (file) => {
  if (!file) {
    errorMessage.value = 'No file was selected.'
    selectedFile.value = null
    return
  }

  if (!isValidImage(file)) {
    errorMessage.value = 'Please upload a valid image file (JPG, PNG, etc).'
    selectedFile.value = null
    return
  }

  // Reset error and save file
  errorMessage.value = ''
  selectedFile.value = file

  // Navigate to loading page
  router.push({ name: 'LoadingPage' })
}

</script>

<style scoped>
.dropzone-hover {
  border-color: #1d4b81;
  background-color: #f0f8ff;
}
</style>
