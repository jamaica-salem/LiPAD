<template>
  <nav class="bg-[#FAFBFA] rounded-2xl shadow mt-4 mr-4 px-6 py-6 flex items-center justify-between">
    <!-- Left Side: Logo -->
    <div class="text-xl font-semibold text-primary-darkest">
    </div>

    <!-- Right Side -->
    <div class="flex items-center gap-10 relative">
      <!-- Mail & Notification Icons -->
      <div class="flex items-center gap-6 text-accent">
        <div class="bg-white p-2 rounded-full cursor-pointer hover:text-primary-darkest hover:shadow transition">
          <Mail class="text-primary-darkest" :size="24" />
        </div>

        <!-- Notification Bell -->
        <div
          class="bg-white p-2 rounded-full cursor-pointer hover:text-primary-darkest hover:shadow transition relative"
          @click="toggleNotifications"
          ref="notificationRef"
        >
          <Bell class="text-primary-darkest" :size="24" />

          <div
            v-if="showNotifications"
            class="absolute right-0 mt-3 w-64 bg-white rounded-xl shadow-lg border border-gray-100 z-50 overflow-hidden"
          >
            <div class="p-4 text-sm font-semibold text-primary-darkest border-b border-gray-100">
              Notifications
            </div>
            <ul class="max-h-60 overflow-y-auto text-sm text-primary-darkest divide-y divide-gray-100">
              <li class="p-3 hover:bg-primary-lightest cursor-pointer">📢 New announcement posted</li>
              <li class="p-3 hover:bg-primary-lightest cursor-pointer">🔔 You have 3 new messages</li>
              <li class="p-3 hover:bg-primary-lightest cursor-pointer">✅ Task completed successfully</li>
            </ul>
            <div class="text-center p-3 border-t border-gray-100 text-xs text-accent hover:underline cursor-pointer">
              View All Notifications
            </div>
          </div>
        </div>
      </div>

      <!-- Profile Section -->
      <div class="relative" ref="profileRef">
        <div
          class="flex items-center gap-4 cursor-pointer"
          @click="toggleProfileMenu"
        >
          <!-- JS Initials Avatar -->
          <div class="w-12 h-12 rounded-full bg-[#cfe0f1] text-[#0E2247] flex items-center justify-center text-sm">
            JS
          </div>

          <!-- Name & Email -->
          <div class="text-[#0E2247] leading-tight text-accent">
            <div class="font-semibold text-lg">{{ user.name }}</div>
            <div class="text-sm">{{ user.email }}</div>
          </div>
        </div>

        <!-- Profile Dropdown -->
        <div
          v-if="showProfileMenu"
          class="absolute right-0 mt-3 w-52 bg-white rounded-xl shadow-lg border border-gray-100 z-50 overflow-hidden"
        >
          <ul class="text-sm text-primary-darkest divide-y divide-gray-100">
            <li
              class="flex items-center gap-3 p-3 hover:bg-primary-lightest cursor-pointer"
              @click="goTo('/profile')"
            >
              <User :size="18" /> Profile
            </li>
            <li
              class="flex items-center gap-3 p-3 hover:bg-primary-lightest cursor-pointer"
              @click="goTo('/settings')"
            >
              <Settings :size="18" /> Settings
            </li>
            <li
              class="flex items-center gap-3 p-3 hover:bg-primary-lightest cursor-pointer text-red-500"
              @click="logout"
            >
              <LogOut :size="18" /> Log out
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
