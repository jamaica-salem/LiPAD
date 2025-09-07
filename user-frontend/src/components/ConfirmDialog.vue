<template>
  <div v-if="visible" class="fixed inset-0 flex items-center justify-center bg-black bg-opacity-40 z-50">
    <div class="bg-white rounded-xl shadow-lg p-6 w-80 text-center">
      <h2 class="text-lg font-bold mb-3">{{ title }}</h2>
      <p class="text-sm text-gray-600 mb-5">{{ message }}</p>
      <div class="flex justify-center gap-3">
        <button @click="$emit('cancel')" class="px-4 py-2 rounded bg-gray-200 hover:bg-gray-300">Cancel</button>
        <button @click="$emit('confirm')" class="px-4 py-2 rounded bg-red-600 text-white hover:bg-red-700">Confirm</button>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  visible: Boolean,
  title: { type: String, default: "Confirm Action" },
  message: { type: String, default: "Are you sure you want to proceed?" }
})
</script>
