<template>
  <transition name="fade-slide">
    <div
      v-if="visible"
      class="fixed bottom-4 right-4 px-4 py-3 rounded-lg shadow-lg text-white flex items-center gap-2"
      :class="{
        'bg-green-600': type === 'success',
        'bg-red-600': type === 'error',
        'bg-blue-600': type === 'info'
      }"
    >
      <span>{{ message }}</span>
      <button @click="$emit('close')" class="ml-2 text-white/80 hover:text-white cursor-pointer">
        ✕
      </button>
    </div>
  </transition>
</template>

<script setup>
defineProps({
  type: {
    type: String,
    default: 'info'
  },
  message: {
    type: String,
    required: true
  },
  visible: {
    type: Boolean,
    default: true
  }
})

defineEmits(['close'])
</script>

<style scoped>
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.3s ease;
}
.fade-slide-enter-from,
.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(10px);
}
</style>
