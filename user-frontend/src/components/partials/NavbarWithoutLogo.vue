<template>
  <nav class="bg-[#265d9c] rounded-xl shadow mt-3 mx-1 px-4 py-4 flex items-center justify-between">
    <!-- Empty left side -->
    <div></div>

    <!-- Right Side: Profile -->
    <div class="relative" ref="profileRef">
      <div class="flex items-center gap-3" @click="toggleProfileMenu">
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
    </div>
  </nav>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
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
    await logoutSession()
    router.push('/lipad/login')
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
