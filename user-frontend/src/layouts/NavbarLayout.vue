<template>
  <div class="min-h-screen flex flex-col">
    <!-- Header/Navbar Component -->
    <Navbar />

    <!-- Routed Page Content -->
    <main class="flex-1 p-6 bg-gray-50">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import Navbar from '@/components/Navbar.vue'
</script>
