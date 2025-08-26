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
import { ref, onMounted } from 'vue'
import { Upload } from 'lucide-vue-next'
import { useRouter } from 'vue-router'
import http from '@/services/http'
import { ensureCsrfCookie } from '@/services/csrf'

const fileInput = ref<HTMLInputElement | null>(null)
const selectedFile = ref<File | null>(null)
const errorMessage = ref<string>('')
const isUploading = ref<boolean>(false)
const router = useRouter()

// Ensure Django sets the csrftoken cookie before first POST
onMounted(() => {
  ensureCsrfCookie()
})

// Trigger file picker
const triggerFileInput = (): void => {
  fileInput.value?.click()
}

// Strict validation against allowed types + size
const isValidImage = (file: File): boolean => {
  const validTypes = ['image/jpeg', 'image/png', 'image/webp']
  const maxSizeMB = 5
  return validTypes.includes(file.type) && file.size <= maxSizeMB * 1024 * 1024
}

// Handle file selection
const handleFileChange = (event: Event): void => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0] || null
  processFile(file)
}

// Drag/drop helpers
const handleDragOver = (event: DragEvent): void => {
  event.dataTransfer!.dropEffect = 'copy'
}
const handleDrop = (event: DragEvent): void => {
  const file = event.dataTransfer?.files?.[0] || null
  processFile(file)
}

// Validate + upload to Django
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
    // IMPORTANT: the field name must be "before_image" to match the DRF serializer
    const formData = new FormData()
    formData.append('before_image', file)

    // POST to /api/images/ (ModelViewSet create)
    const { data } = await http.post('/images/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })

    // data.id is the new Image row; pass to next page
    router.push({ name: 'ClassifierOptions', query: { imageId: String(data.id) } })
  } catch (err: any) {
    // Avoid leaking backend internals; show safe message
    const msg =
      err?.response?.data?.errors ||
      err?.response?.data?.detail ||
      err?.message ||
      'Upload failed.'
    errorMessage.value = Array.isArray(msg) ? msg.join(', ') : String(msg)
  } finally {
    isUploading.value = false
    if (fileInput.value) fileInput.value.value = ''
  }
}
</script>


<style scoped>
.dropzone-hover {
  border-color: #1d4b81;
  background-color: #f0f8ff;
}
</style>
