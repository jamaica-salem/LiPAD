<template>
  <aside class="w-56 bg-[#265d9c] border-r border-gray-200 p-6 flex flex-col rounded-3xl shadow-lg mx-3 mt-3 h-[calc(100vh-1.5rem)] overflow-hidden">
    <!-- App Logo -->
    <div class="flex items-center gap-1 mb-6">
      <img 
        src="@/assets/logo.png" 
        alt="LiPAD Logo" 
        class="h-8 w-auto object-contain"
      />
      <span class="text-xl font-extrabold text-[#eef3f8]">LiPAD Admin</span>
    </div>

    <div class="flex-1 flex flex-col justify-between">
      <div>
        <!-- MENU -->
        <div class="mb-4 text-sm font-bold text-white uppercase tracking-widest">Menu</div>
        <nav class="space-y-1.5 mb-8">
          <router-link
            v-for="item in navItems"
            :key="item.to"
            :to="item.to"
            custom
            v-slot="{ navigate, isActive }"
          >
            <div
              @click="navigate"
              class="group flex items-center gap-3 text-base font-medium rounded-lg px-2.5 py-1.5 transition-colors cursor-pointer"
              :class="isActive
                ? 'text-white border-l-4 border-white'
                : 'text-[#d1d1d5] hover:text-white hover:bg-[#265d9c]'"
            >
              <component :is="item.icon" :size="18" />
              <span>{{ item.label }}</span>
            </div>
          </router-link>
        </nav>
      </div>

      <!-- Secure Logout Button -->
      <div>
        <button
          @click="handleLogout"
          :disabled="logoutLoading"
          class="w-full flex items-center gap-3 text-base font-medium rounded-lg px-2.5 py-1.5 transition-colors text-[#d1d1d5] hover:text-white hover:bg-[#265d9c] cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <LogOut :size="18" />
          <span v-if="!logoutLoading">Log Out</span>
          <span v-else>Logging out...</span>
        </button>
      </div>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { FolderClock, User, LogOut } from 'lucide-vue-next';
import { useRouter } from 'vue-router';
import { logout, useAuth } from '@/composables/useAuth';

const router = useRouter();
const auth = useAuth();

// Nav items
const navItems = [
  { to: '/app/users', label: 'Users', icon: User },
  { to: '/app/history', label: 'Overall History', icon: FolderClock },
];

// Prevent double clicks
const logoutLoading = ref(false);

const handleLogout = async () => {
  if (logoutLoading.value) return;
  logoutLoading.value = true;

  try {
    // Call centralized composable logout
    await logout();

    // Clear any frontend storage (optional but good practice)
    localStorage.clear();
    sessionStorage.clear();

    // Reset reactive auth state (optional, but safer)
    auth.admin = null;
    auth.isAuthenticated = false;
    auth.sessionExpiry = null;

    // Redirect to admin login
    router.push({ path: '/admin-login' });
  } catch (err) {
    console.error('Logout failed:', err);
    router.push({ path: '/admin-login' }); // fallback redirect
  } finally {
    logoutLoading.value = false;
  }
};

</script>
