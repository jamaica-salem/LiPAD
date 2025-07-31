<template>
  <aside class="w-64 h-screen bg-primary-light border-r border-gray-200 p-8 flex flex-col rounded-2xl shadow-lg mx-4 mt-1 sm:mt-2 md:mt-5">
    <!-- App Logo and Name -->
    <div class="flex items-center gap-4 mb-12">
      <Coffee class="text-accent" :size="32" />
      <span class="text-2xl font-extrabold text-accent">{{ appName }}</span>
    </div>

    <div class="flex-1 flex flex-col justify-between">
      <div>
        <!-- MENU TITLE -->
        <div class="mb-5 text-base font-bold text-accent uppercase tracking-widest">Menu</div>

        <!-- MAIN NAVIGATION -->
        <nav class="space-y-2">
          <RouterLink
            to="/users"
            class="group flex items-center gap-4 text-lg font-medium rounded-lg px-3 py-2 transition-colors"
            :class="isActive('/users')"
          >
            <User :size="22" />
            <span>Users</span>
          </RouterLink>

          <RouterLink
            to="/history"
            class="group flex items-center gap-4 text-lg font-medium rounded-lg px-3 py-2 transition-colors"
            :class="isActive('/history')"
          >
            <Table2 :size="22" />
            <span>Overall History</span>
          </RouterLink>
        </nav>
      </div>
    </div>
  </aside>
</template>

<script setup>
// Icon imports (Lucide Vue)
import { Coffee, User, Table2 } from 'lucide-vue-next'

// Props
defineProps({
  appName: {
    type: String,
    default: 'LiPAD',
  },
})

// Router hook to check active path
import { useRoute } from 'vue-router'
const route = useRoute()

// Function to determine active class dynamically
const isActive = (path) => {
  return route.path === path
    ? 'text-accent bg-primary-light border-l-4 border-accent'
    : 'text-primary-darkest hover:text-accent hover:bg-primary-lightest'
}
</script>
