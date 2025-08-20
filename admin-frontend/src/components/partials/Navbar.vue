<template>
  <nav class="bg-[#FAFBFA] rounded-2xl shadow mt-4 mr-4 px-4 py-4 flex items-center justify-between">
    <!-- Left Side: Logo -->
    <div class="text-lg font-semibold text-primary-darkest">
    </div>

    <!-- Right Side -->
    <div class="flex items-center gap-6 relative">
      <!-- Mail & Notification Icons -->
      <div class="flex items-center gap-4 text-accent">
        <div class="bg-white p-1.5 rounded-full cursor-pointer hover:text-primary-darkest hover:shadow transition">
          <Mail class="text-primary-darkest" :size="20" />
        </div>

        <!-- Notification Bell -->
        <div
          class="bg-white p-1.5 rounded-full cursor-pointer hover:text-primary-darkest hover:shadow transition relative"
          @click="toggleNotifications"
          ref="notificationRef"
        >
          <Bell class="text-primary-darkest" :size="20" />

          <div
            v-if="showNotifications"
            class="absolute right-0 mt-2 w-56 bg-white rounded-xl shadow-lg border border-gray-100 z-50 overflow-hidden"
          >
            <div class="p-3 text-xs font-semibold text-primary-darkest border-b border-gray-100">
              Notifications
            </div>
            <ul class="max-h-56 overflow-y-auto text-xs text-primary-darkest divide-y divide-gray-100">
              <li class="p-2 hover:bg-primary-lightest cursor-pointer">📢 New announcement posted</li>
              <li class="p-2 hover:bg-primary-lightest cursor-pointer">🔔 You have 3 new messages</li>
              <li class="p-2 hover:bg-primary-lightest cursor-pointer">✅ Task completed successfully</li>
            </ul>
            <div class="text-center p-2 border-t border-gray-100 text-[11px] text-accent hover:underline cursor-pointer">
              View All Notifications
            </div>
          </div>
        </div>
      </div>

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

        <!-- Profile Dropdown -->
        <div
          v-if="showProfileMenu"
          class="absolute right-0 mt-2 w-48 bg-white rounded-xl shadow-lg border border-gray-100 z-50 overflow-hidden"
        >
          <ul class="text-xs text-primary-darkest divide-y divide-gray-100">
            <li
              class="flex items-center gap-2 p-2 hover:bg-primary-lightest cursor-pointer"
              @click="goTo('/profile')"
            >
              <User :size="16" /> Profile
            </li>
            <li
              class="flex items-center gap-2 p-2 hover:bg-primary-lightest cursor-pointer"
              @click="goTo('/settings')"
            >
              <Settings :size="16" /> Settings
            </li>
            <li
              class="flex items-center gap-2 p-2 hover:bg-primary-lightest cursor-pointer text-red-500"
              @click="goTo('/admin-login')"
            >
              <LogOut :size="16" /> Log out
            </li>
          </ul>
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
