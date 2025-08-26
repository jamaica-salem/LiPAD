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
// ------------------------------
// Imports
// ------------------------------
import { ref } from 'vue';
import { Upload } from 'lucide-vue-next';
import { useRouter } from 'vue-router';
import axios from 'axios';

// ------------------------------
// Refs and Router
// ------------------------------
const fileInput = ref<HTMLInputElement | null>(null);
const selectedFile = ref<File | null>(null);
const errorMessage = ref<string>('');
const isUploading = ref<boolean>(false);
const router = useRouter();

// ------------------------------
// Trigger file picker
// ------------------------------
const triggerFileInput = (): void => {
  fileInput.value?.click();
};

// ------------------------------
// Validate image (security + format checks)
// ------------------------------
const isValidImage = (file: File): boolean => {
  const validTypes = ['image/jpeg', 'image/png', 'image/jpg', 'image/webp'];
  const maxSizeMB = 5; // Limit file size to 5MB
  return validTypes.includes(file.type) && file.size <= maxSizeMB * 1024 * 1024;
};

// ------------------------------
// Handle file selection
// ------------------------------
const handleFileChange = (event: Event): void => {
  const target = event.target as HTMLInputElement;
  const file = target.files?.[0] || null;
  processFile(file);
};

// ------------------------------
// Handle drag events (visual feedback)
// ------------------------------
const handleDragOver = (event: DragEvent): void => {
  event.dataTransfer!.dropEffect = 'copy';
};

// ------------------------------
// Handle drop events
// ------------------------------
const handleDrop = (event: DragEvent): void => {
  const file = event.dataTransfer?.files?.[0] || null;
  processFile(file);
};

// ------------------------------
// Core logic: Validate and upload file
// ------------------------------
const processFile = async (file: File | null): Promise<void> => {
  if (!file) {
    errorMessage.value = 'No file was selected.';
    selectedFile.value = null;
    return;
  }

  if (!isValidImage(file)) {
    errorMessage.value = 'Invalid file. Please upload a JPG, PNG, or WEBP under 5MB.';
    selectedFile.value = null;
    return;
  }

  // Reset states and mark as uploading
  errorMessage.value = '';
  selectedFile.value = file;
  isUploading.value = true;

  try {
    const formData = new FormData();
    formData.append('image', file);

    // Secure axios POST request to Django API
    const response = await axios.post('/api/upload-license-plate', formData, {
      withCredentials: true, // sends session cookie for Django auth
      headers: {
        'X-Requested-With': 'XMLHttpRequest',
        'Content-Type': 'multipart/form-data',
      },
      timeout: 15000, // safety timeout for slow networks 
    });

    console.log('Upload success:', response.data);

    // Navigate back to LicensePlateUpload page with status
    router.push({ name: 'LicensePlateUpload', query: { status: 'success' } });
  } catch (error: any) {
    console.error('Upload error:', error);

    // Distinguish between server and network errors
    if (error.response) {
      errorMessage.value = `Upload failed: ${error.response.data?.message || 'Server error.'}`;
    } else if (error.request) {
      errorMessage.value = 'No response from server. Please check your network.';
    } else {
      errorMessage.value = 'Unexpected error occurred during upload.';
    }
  } finally {
    isUploading.value = false;

    // Clear the file input to allow re-upload of the same file
    if (fileInput.value) fileInput.value.value = '';
  }
};
</script>

<style scoped>
.dropzone-hover {
  border-color: #1d4b81;
  background-color: #f0f8ff;
}
</style>
