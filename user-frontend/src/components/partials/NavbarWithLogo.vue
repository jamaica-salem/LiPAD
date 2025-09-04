<template>
  <nav class="bg-[#265d9c] rounded-xl shadow mt-3 mx-1 px-4 h-18 flex items-center justify-between">
  <!-- Left Side: Logo -->
  <div class="flex items-center h-full gap-2">
    <img 
        src="@/assets/logo.png" 
        alt="LiPAD Logo" 
        class="h-10 w-auto object-contain"
      />
      <span class="text-3xl font-extrabold text-[#eef3f8]">LiPAD</span>
  </div>

  <!-- Right Side: Profile -->
  <div class="relative" ref="profileRef">
    <div class="flex items-center gap-3 cursor-pointer" @click="toggleProfileMenu">
      <!-- Avatar -->
      <div class="w-10 h-10 rounded-full bg-[#cfe0f1] text-[#0E2247] flex items-center justify-center text-xs font-semibold">
        {{ initials }}
      </div>

      <!-- User Info -->
      <div class="text-white leading-tight text-accent">
        <div class="font-semibold text-base">{{ user?.first_name }} {{ user?.last_name }}</div>
        <div class="text-xs">{{ user?.email }}</div>
      </div>
    </div>

    <!-- Menu Dropdown -->
    <Transition
      enter-active-class="transition ease-out duration-200"
      enter-from-class="opacity-0 transform -translate-y-2"
      enter-to-class="opacity-100 transform translate-y-0"
      leave-active-class="transition ease-in duration-150"
      leave-from-class="opacity-100 transform translate-y-0"
      leave-to-class="opacity-0 transform -translate-y-2"
    >
      <div
        v-if="showProfileMenu"
        class="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-100 z-50 overflow-hidden"
      >
        <ul class="text-sm text-primary-darkest divide-y divide-gray-100">
          <li class="flex items-center gap-2.5 p-2.5 hover:bg-primary-lightest cursor-pointer" @click="goTo('/history')">
            <History :size="16" /> History
          </li>
          <li class="flex items-center gap-2.5 p-2.5 hover:bg-primary-lightest cursor-pointer text-red-500" @click="handleLogout">
            <LogOut :size="16" /> Log out
          </li>
        </ul>
      </div>
    </Transition>
  </div>
</nav>

</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import { ScanLine as ScanLineIcon, LogOut, History } from 'lucide-vue-next'
import { logout as logoutSession, useAuth } from '@/composables/useAuth'

const router = useRouter()
const state = useAuth()  // reactive auth state
const user = computed(() => state.user)

const showProfileMenu = ref(false)
const profileRef = ref<HTMLElement | null>(null)

const initials = computed(() => {
  if (!user.value) return ''
  const first = user.value.first_name?.[0] || ''
  const last = user.value.last_name?.[0] || ''
  return `${first}${last}`.toUpperCase()
})

const toggleProfileMenu = () => {
  showProfileMenu.value = !showProfileMenu.value
}

const goTo = (path: string) => {
  router.push(path)
  showProfileMenu.value = false
}

const handleLogout = async () => {
  try {
    await logoutSession()       // call composable logout (POST /api/logout/)
    router.push('/lipad/login')       // redirect to login
  } catch (err) {
    console.error('Logout failed:', err)
  } finally {
    showProfileMenu.value = false
  }
}

const handleClickOutside = (e: MouseEvent) => {
  if (profileRef.value && !profileRef.value.contains(e.target as Node)) {
    showProfileMenu.value = false
  }
}

onMounted(() => document.addEventListener('mousedown', handleClickOutside))
onBeforeUnmount(() => document.removeEventListener('mousedown', handleClickOutside))
</script>
