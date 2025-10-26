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
          class="bg-[#265d9c] hover:bg-[#1d4b81] text-white font-medium py-2.5 px-6 rounded-lg shadow text-base cursor-pointer"
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

<script setup lang="ts">
import { ref } from 'vue'
import { Upload } from 'lucide-vue-next'
import { useRouter } from 'vue-router'
import api from '@/api/axios'

const fileInput = ref<HTMLInputElement | null>(null)
const selectedFile = ref<File | null>(null)
const errorMessage = ref<string>('')
const isUploading = ref<boolean>(false)
const router = useRouter()

const triggerFileInput = (): void => {
  fileInput.value?.click()
}

const isValidImage = (file: File): boolean => {
  const validTypes = ['image/jpeg', 'image/png', 'image/webp']
  const maxSizeMB = 5
  return validTypes.includes(file.type) && file.size <= maxSizeMB * 1024 * 1024
}

const handleFileChange = (event: Event): void => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0] || null
  processFile(file)
}

const handleDragOver = (event: DragEvent): void => {
  event.preventDefault()
  event.dataTransfer!.dropEffect = 'copy'
}

const handleDrop = (event: DragEvent): void => {
  event.preventDefault()
  const file = event.dataTransfer?.files?.[0] || null
  processFile(file)
}

const processFile = async (file: File | null): Promise<void> => {
  errorMessage.value = ''
  
  if (!file) {
    errorMessage.value = 'No file was selected.'
    selectedFile.value = null
    return
  }
  
  if (!isValidImage(file)) {
    errorMessage.value = 'Invalid file. Please upload a JPG, PNG, or WEBP under 5MB.'
    selectedFile.value = null
    return
  }

  selectedFile.value = file
  isUploading.value = true

  try {
    // Create FormData with correct field name
    const formData = new FormData()
    formData.append('before_image', file)

    console.log('Uploading to:', '/user/images/')
    console.log('File:', file.name, file.type, file.size)

    // Make the request - api instance should handle auth headers
    const response = await api.post('/user/images/', formData, {
      headers: { 
        'Content-Type': 'multipart/form-data'
      },
    })

    console.log('Upload successful:', response.data)

    // Navigate to next page with image ID
    if (response.data.id) {
      router.push({ 
        name: 'ClassifierOptions', 
        query: { imageId: String(response.data.id) } 
      })
    } else {
      throw new Error('No image ID returned from server')
    }

  } catch (err: any) {
    console.error('Upload error:', err)
    
    // Better error handling
    let msg = 'Upload failed.'
    
    if (err.response) {
      // Server responded with error
      console.error('Response error:', err.response.status, err.response.data)
      
      if (err.response.data?.errors) {
        // DRF validation errors
        msg = typeof err.response.data.errors === 'string' 
          ? err.response.data.errors
          : JSON.stringify(err.response.data.errors)
      } else if (err.response.data?.detail) {
        msg = err.response.data.detail
      } else if (err.response.data?.before_image) {
        // Field-specific error
        msg = Array.isArray(err.response.data.before_image)
          ? err.response.data.before_image.join(', ')
          : err.response.data.before_image
      } else {
        msg = `Server error: ${err.response.status}`
      }
    } else if (err.request) {
      // Request made but no response
      msg = 'No response from server. Please check your connection.'
    } else {
      // Other errors
      msg = err.message || 'Upload failed.'
    }
    
    errorMessage.value = msg
    
  } finally {
    isUploading.value = false
    if (fileInput.value) {
      fileInput.value.value = ''
    }
  }
}
</script>

<style scoped>
.dropzone-hover {
  border-color: #1d4b81;
  background-color: #f0f8ff;
}
</style>
