<template>
  <div class="min-h-screen bg-orange-100 text-[#1f2937]">
    <Navbar />
    <main class="">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import Navbar from '@/components/partials/NavbarWithLogo.vue'
</script>
