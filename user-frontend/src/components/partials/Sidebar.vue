<template>
  <aside
    class="w-56 bg-[#265d9c] border-r border-gray-200 p-6 flex flex-col rounded-2xl shadow-lg mx-3 mt-3 h-[calc(100vh-1.5rem)] overflow-hidden"
  >
    <!-- App Logo and Name -->
    <div class="flex items-center gap-3 mb-10">
      <ScanLine class="text-white" size="28" />
      <span class="text-xl font-extrabold text-white">{{ appName }}</span>
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
    </div>
  </aside>
</template>

<script setup>
import { ScanLine, ImageDown, Clock4 } from 'lucide-vue-next'; 

const props = defineProps({
  appName: String
});

// Navigation items for the sidebar
const navItems = [
  { to: '/result', label: 'Result', icon: ImageDown },
  { to: '/history', label: 'History', icon: Clock4 }
];
</script>
