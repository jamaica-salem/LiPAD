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
          class="flex items-center gap-3"
          @click="toggleProfileMenu"
        >
          <!-- Initials Avatar -->
          <div class="w-9 h-9 rounded-full bg-[#cfe0f1] text-[#0E2247] flex items-center justify-center text-xs">
            {{ initials }}
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
import { computed } from 'vue'

const props = defineProps({
  appName: { type: String, default: 'LiPAD Admin' },
  user: {
    type: Object,
    default: () => ({
      name: '',
      email: '',
    }),
  },
})

// Compute initials from first and last name
const initials = computed(() => {
  const names = props.user.name.trim().split(' ')
  const first = names[0]?.charAt(0).toUpperCase() || ''
  const last = names.length > 1 ? names[names.length - 1].charAt(0).toUpperCase() : ''
  return first + last
})

</script>
