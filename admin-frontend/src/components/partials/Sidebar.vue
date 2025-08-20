<template>
  <aside
    class="w-56 bg-[#265d9c] border-r border-gray-200 p-6 flex flex-col rounded-3xl shadow-lg mx-3 mt-3 h-[calc(100vh-1.5rem)] overflow-hidden"
  >
    <!-- App Logo and Name -->
    <div class="flex items-center gap-3 mb-8">
      <ScanLine class="text-white" size="26" />
      <span class="text-xl font-extrabold text-white">{{ appName }}</span>
    </div>

    <!-- Wrapper ensures menu stays top, logout stays bottom -->
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

      <!-- Secure Logout Button (bottom aligned) -->
      <div>
        <button
          @click="handleLogout"
          class="w-full flex items-center gap-3 text-base font-medium rounded-lg px-2.5 py-1.5 transition-colors text-[#d1d1d5] hover:text-white hover:bg-[#265d9c]"
        >
          <LogOut size="18" />
          <span>Log Out</span>
        </button>
      </div>
    </div>
  </aside>
</template>

<script setup>
/* -------------------------------
   Imports
-------------------------------- */
import { ScanLine, FolderClock, User, LogOut } from 'lucide-vue-next';
import axios from 'axios';
import { useRouter } from 'vue-router';

/* -------------------------------
   Props
-------------------------------- */
const props = defineProps({
  appName: String
});

/* -------------------------------
   Router
-------------------------------- */
const router = useRouter();

/* -------------------------------
   Navigation Items
-------------------------------- */
const navItems = [
  { to: '/app/users', label: 'Users', icon: User },
  { to: '/app/history', label: 'Overall History', icon: FolderClock },
];

/* -------------------------------
   Secure Logout Function
-------------------------------- */
const handleLogout = async () => {
  try {
    // Send secure request to Django logout endpoint
    await axios.post(
      '/api/logout/',
      {},
      {
        headers: {
          'X-CSRFToken': getCSRFToken(), // CSRF protection (best practice in Django)
        },
        withCredentials: true, // ensures cookies (sessionid/csrftoken) are sent
      }
    );

    // Clear any localStorage/sessionStorage if used for auth state
    localStorage.clear();
    sessionStorage.clear();

    // Redirect to login page
    router.push({ path: '/admin-login' });
  } catch (error) {
    console.error('Logout failed:', error);

    // Fallback: force redirect even if server fails
    router.push({ path: '/admin-login' });
  }
};

/* -------------------------------
   Utility: Get CSRF Token
   - Extract from cookies
   - Prevents CSRF vulnerabilities
-------------------------------- */
function getCSRFToken() {
  const name = 'csrftoken';
  const cookies = document.cookie.split(';');
  for (let cookie of cookies) {
    let c = cookie.trim();
    if (c.startsWith(name + '=')) {
      return c.substring(name.length + 1);
    }
  }
  return '';
}
</script>
