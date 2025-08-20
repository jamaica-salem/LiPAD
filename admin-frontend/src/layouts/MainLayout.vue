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
        <Navbar :app-name="'LiPAD'" :user="displayUser" />
      </div>

      <main ref="mainContent" class="flex-1 overflow-auto p-6 bg-white">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed, watch } from 'vue';
import Sidebar from '../components/partials/Sidebar.vue';
import Navbar from '../components/partials/Navbar.vue';
import { useAuth } from '@/composables/useAuth';
import { useRouter } from 'vue-router';

const auth = useAuth();
const router = useRouter();

/**
 * If somehow a user navigates to /app while not authenticated (e.g., session expired),
 * redirect to login page.
 */
watch(
  () => auth.isAuthenticated,
  (isAuth) => {
    if (!isAuth && !auth.loading) {
      // session expired or not authenticated -> redirect to login
      router.replace({ name: 'Login' });
    }
  },
  { immediate: true }
);

const displayUser = computed(() => {
  if (!auth.admin) {
    return { name: "Unknown", email: "" };
  }
  const name = `${auth.admin.first_name} ${auth.admin.last_name}`;
  return { name, email: auth.admin.email };
});

const showNavbar = ref(true);
const lastScrollY = ref(0);
const mainContent = ref<HTMLElement | null>(null);
let timeout: any;

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
