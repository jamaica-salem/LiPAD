<template>
  <nav class="bg-[#265d9c] rounded-xl shadow mt-3 mx-1 px-4 py-4 flex items-center justify-between">
    <!-- Left Side: Logo -->
    <div class="flex items-center gap-2 text-[#0E2247] font-bold text-lg">
      <div class="bg-[#4574aa] p-1.5 rounded-full shadow">
        <ScanLineIcon :size="20" class="text-white" />
      </div>
      <span class="text-white">LiPAD</span>
    </div>

    <!-- Right Side: Profile only -->
    <div class="relative" ref="profileRef">
      <div class="flex items-center gap-3 cursor-pointer" @click="toggleProfileMenu">
        <!-- Avatar -->
        <div class="w-10 h-10 rounded-full bg-[#cfe0f1] text-[#0E2247] flex items-center justify-center text-xs font-semibold">
          {{ initials }}
        </div>

        <!-- User Info -->
        <div class="text-white leading-tight text-accent">
          <div class="font-semibold text-base">{{ user.name }}</div>
          <div class="text-xs">{{ user.email }}</div>
        </div>
      </div>

      <!-- Profile Dropdown -->
      <div
        v-if="showProfileMenu"
        class="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-100 z-50 overflow-hidden"
      >
        <ul class="text-sm text-primary-darkest divide-y divide-gray-100">
          <li
            class="flex items-center gap-2.5 p-2.5 hover:bg-primary-lightest cursor-pointer"
            @click="goTo('/profile')"
          >
            <User :size="16" /> Profile
          </li>
          <li
            class="flex items-center gap-2.5 p-2.5 hover:bg-primary-lightest cursor-pointer"
            @click="goTo('/settings')"
          >
            <Settings :size="16" /> Settings
          </li>
          <li
            class="flex items-center gap-2.5 p-2.5 hover:bg-primary-lightest cursor-pointer text-red-500"
            @click="goTo('/login')"
          >
            <LogOut :size="16" /> Log out
          </li>
        </ul>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import { ScanLine as ScanLineIcon, User, Settings, LogOut } from 'lucide-vue-next'

const props = defineProps({
  user: {
    type: Object,
    default: () => ({
      name: 'Jamaica Salem',
      email: 'jamaica.salem@lipad.com',
    }),
  },
})

const router = useRouter()
const showProfileMenu = ref(false)
const profileRef = ref(null)

const initials = computed(() => {
  const names = props.user.name.split(' ')
  return names.map(n => n[0]).slice(0, 2).join('')
})

const toggleProfileMenu = () => {
  showProfileMenu.value = !showProfileMenu.value
}

const goTo = (path) => {
  router.push(path)
  showProfileMenu.value = false
}

const logout = () => {
  alert('Logged out')
  showProfileMenu.value = false
}

const handleClickOutside = (e) => {
  if (profileRef.value && !profileRef.value.contains(e.target)) {
    showProfileMenu.value = false
  }
}

onMounted(() => {
  document.addEventListener('mousedown', handleClickOutside)
})

onBeforeUnmount(() => {
  document.removeEventListener('mousedown', handleClickOutside)
})
</script>
