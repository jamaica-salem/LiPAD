<template>
  <div class="flex h-screen bg-orange-50 text-[#265d9c] overflow-hidden">
    <!-- Sidebar -->
    <Sidebar :appName="'LiPAD'" />

    <!-- Main Content Area -->
    <div class="flex flex-col flex-1 overflow-hidden pr-4">
      <!-- Navbar -->
      <Navbar :user="user" class="mr-2" />

      <!-- Page Content -->
      <main class="flex-1 overflow-y-auto p-6 mt-2 bg-orange-50 rounded-2xl mx-2">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup>
import Navbar from '@/components/partials/NavbarWithoutLogo.vue'
import Sidebar from '@/components/partials/Sidebar.vue'

const user = {
  name: 'Jamaica Salem',
  email: 'jamaica.salem@lipad.com',
}
</script>

