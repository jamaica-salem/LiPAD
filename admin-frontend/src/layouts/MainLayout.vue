<template>
  <div class="flex h-screen overflow-hidden">
    <div class="h-screen sticky top-0">
      <Sidebar :app-name="'LiPAD'" />
    </div>

    <div class="flex flex-col flex-1 h-screen overflow-hidden">
      <div
        class="transition-transform duration-300"
        :class="showNavbar ? 'translate-y-0' : '-translate-y-full'"
      >
        <Navbar :app-name="'LiPAD'" :user="user" />
      </div>

      <main ref="mainContent" class="flex-1 overflow-auto p-6 bg-white">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import Sidebar from '../components/partials/Sidebar.vue';
import Navbar from '../components/partials/Navbar.vue';

const user = {
  name: 'Jamaica Salem',
  email: 'jamaica.esalem@gmail.com',
};

const showNavbar = ref(true);
const lastScrollY = ref(0);
const mainContent = ref(null);

let timeout;
const handleScroll = () => {
  clearTimeout(timeout);
  timeout = setTimeout(() => {
    const currentScrollY = mainContent.value?.scrollTop || 0;
    lastScrollY.value = currentScrollY;
  }, 100);
};

onMounted(() => {
  mainContent.value?.addEventListener('scroll', handleScroll);
});
onUnmounted(() => {
  mainContent.value?.removeEventListener('scroll', handleScroll);
});
</script>
