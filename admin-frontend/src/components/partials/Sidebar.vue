<template>
  <aside
    class="w-64 bg-[#FAFBFA] border-r border-gray-200 p-8 flex flex-col rounded-2xl shadow-lg mx-4 mt-4 h-[calc(100vh-2rem)] overflow-hidden"
  >
    <!-- App Logo and Name -->
    <div class="flex items-center gap-4 mb-12">
      <ScanLine class="text-[#1f2f44]" size="32" />
      <span class="text-2xl font-extrabold text-[#0E2247]">{{ appName }}</span>
    </div>

    <div class="flex-1 flex flex-col justify-between">
      <div>
        <!-- MENU -->
        <div class="mb-5 text-base font-bold text-[#0E2247] uppercase tracking-widest">Menu</div>
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
                ? 'text-[#0E2247] bg-[#FAFBFA] border-l-4 border-[#0E2247]'
                : 'text-gray-500 hover:text-[#0E2247] hover:bg-[#F9FAFB]'"
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
import { ScanLine, FolderClock, User } from 'lucide-vue-next';

const props = defineProps({
  appName: String
});

const navItems = [
  { to: '/app/users', label: 'Users', icon: User },
  { to: '/app/history', label: 'Overall History', icon: FolderClock },
];
</script>
