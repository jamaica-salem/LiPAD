<template>
  <nav class="bg-[#FAFBFA] rounded-2xl shadow mt-4 mr-4 px-4 py-4 flex items-center justify-between">
    <!-- Left Side: Logo -->
    <div class="text-lg font-semibold text-primary-darkest">
    </div>

    <!-- Right Side -->
    <div class="flex items-center gap-6 relative">
      <!-- Profile Section -->
      <div class="relative" ref="profileRef">
        <div
          class="flex items-center gap-3 cursor-pointer"
          @click="toggleProfileMenu"
        >
          <!-- JS Initials Avatar -->
          <div class="w-9 h-9 rounded-full bg-[#cfe0f1] text-[#0E2247] flex items-center justify-center text-xs">
            JS
          </div>

          <!-- Name & Email -->
          <div class="text-[#0E2247] leading-tight text-accent">
            <div class="font-semibold text-base">{{ user.name }}</div>
            <div class="text-xs">{{ user.email }}</div>
          </div>
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import { Bell, Mail, User, Settings, LogOut } from 'lucide-vue-next'

const props = defineProps({
  appName: { type: String, default: 'LiPAD Admin' },
  user: {
    type: Object,
    default: () => ({
      name: 'John Smith',
      email: 'john@lipad.com',
    }),
  },
})

const router = useRouter()

const showNotifications = ref(false)
const showProfileMenu = ref(false)
const notificationRef = ref(null)
const profileRef = ref(null)

const toggleNotifications = () => {
  showNotifications.value = !showNotifications.value
  showProfileMenu.value = false
}

const toggleProfileMenu = () => {
  showProfileMenu.value = !showProfileMenu.value
  showNotifications.value = false
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
  if (
    notificationRef.value &&
    !notificationRef.value.contains(e.target)
  ) {
    showNotifications.value = false
  }
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
