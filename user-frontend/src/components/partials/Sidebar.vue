<template>
  <aside
    class="w-64 bg-[#265d9c] border-r border-gray-200 p-8 flex flex-col rounded-3xl shadow-lg mx-4 mt-4 h-[calc(100vh-2rem)] overflow-hidden"
  >
    <!-- App Logo and Name -->
    <div class="flex items-center gap-4 mb-12">
      <ScanLine class="text-white" size="32" />
      <span class="text-2xl font-extrabold text-white">{{ appName }}</span>
    </div>

    <div class="flex-1 flex flex-col justify-between">
      <div>
        <!-- MENU -->
        <div class="mb-5 text-base font-bold text-white uppercase tracking-widest">Menu</div>
        <nav class="space-y-2 mb-12">
          <router-link
            v-for="item in navItems"
            :key="item.to"
            :to="item.to"
            custom
            v-slot="{ navigate, isActive }"
          >
            <div
              @click="navigate"
              class="group flex items-center gap-4 text-lg font-medium rounded-lg px-3 py-2 transition-colors cursor-pointer"
              :class="isActive
                ? 'text-white border-l-4 border-white'
                : 'text-[#d1d1d5] hover:text-white hover:bg-[#265d9c]'"
            >
              <component :is="item.icon" :size="22" />
              <span>{{ item.label }}</span>
            </div>
          </router-link>
        </nav>
      </div>
    </div>
  </aside>
</template>

<script setup>
import { ScanLine, ImageDown, Clock4 } from 'lucide-vue-next'; // Replace with appropriate icons

const props = defineProps({
  appName: String
});

// Navigation items for the sidebar
const navItems = [
  { to: '/app/result', label: 'Result', icon: ImageDown },
  { to: '/app/history', label: 'History', icon: Clock4 }
];
</script>
