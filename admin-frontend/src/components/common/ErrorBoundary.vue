<template>
  <div>
    <slot v-if="!hasError" />
    <div v-else class="text-center text-red-600 p-4">
      <strong>Error:</strong> Something went wrong while rendering this view.
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue'

export default defineComponent({
  name: 'ErrorBoundary',
  setup(_, { slots }) {
    const hasError = ref(false)

    // Capture rendering errors
    function errorCaptured(err: unknown, instance: any, info: string) {
      console.error('Captured error in ErrorBoundary:', err, info)
      hasError.value = true
      return false // allow further propagation if needed
    }

    return {
      hasError,
      errorCaptured,
      slots
    }
  },
  errorCaptured(err, instance, info) {
    return (this as any).errorCaptured(err, instance, info)
  }
})
</script>
