<template>
  <aside
    class="w-56 bg-[#265d9c] border-r border-gray-200 p-6 flex flex-col rounded-3xl shadow-lg mx-3 mt-3 h-[calc(100vh-1.5rem)] overflow-hidden"
  >
    <!-- App Logo -->
    <div class="flex items-center gap-2 mb-6">
      <img 
        src="@/assets/logo.png" 
        alt="LiPAD Logo" 
        class="h-10 w-auto object-contain"
      />
      <span class="text-2xl font-extrabold text-[#eef3f8]">LiPAD</span>
    </div>


    <div class="flex-1 flex flex-col justify-between">
      <div>
        <!-- MENU -->
        <div class="mb-4 text-sm font-bold text-white uppercase tracking-wider">Menu</div>
        <nav class="space-y-1.5 mb-10">
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
              <component :is="item.icon" :size="20" />
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
          class="w-full flex items-center gap-3 text-base font-medium rounded-lg px-2.5 py-1.5 transition-colors text-[#d1d1d5] hover:text-white hover:bg-[#265d9c] cursor-pointer isabled:opacity-50 disabled:cursor-not-allowed "
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
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ScanLine, ImageDown, Clock4, LogOut } from 'lucide-vue-next'
import { logout as logoutSession } from '@/composables/useAuth'

const props = defineProps({
  appName: String
})

// Sidebar navigation items
const navItems = [
  { to: '/result', label: 'Result', icon: ImageDown },
  { to: '/history', label: 'History', icon: Clock4 }
]

const router = useRouter()
const logoutLoading = ref(false)

const handleLogout = async () => {
  logoutLoading.value = true
  try {
    await logoutSession()                // call your logout API/session function
    router.push('/lipad/login')          // redirect to login page
  } catch (err) {
    console.error('Logout failed:', err)
  } finally {
    logoutLoading.value = false
  }
}
</script>
