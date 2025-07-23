<template>
  <div id="app" class="min-h-screen flex flex-col bg-gray-50 text-gray-900">
    <!-- Main content area -->
    <main class="flex-1">
      <!-- Error boundary wrapper to catch render errors -->
      <ErrorBoundary>
        <!-- Use keep-alive for performance (if applicable) -->
        <Suspense>
          <template #default>
            <!-- Renders child components inside the layout -->
            <slot />
          </template>
          <template #fallback>
            <!-- Optional fallback UI during lazy loading -->
            <div class="text-center p-4 animate-pulse text-gray-500">Loading content…</div>
          </template>
        </Suspense>
      </ErrorBoundary>
    </main>
  </div>
</template>

<script setup lang="ts">
// Import error boundary wrapper component
import ErrorBoundary from 'src/components/common/ErrorBoundary.vue';
</script>

<style scoped>
/* Scoped global layout styling */
#app {
  font-family: system-ui, sans-serif;
}
</style>
