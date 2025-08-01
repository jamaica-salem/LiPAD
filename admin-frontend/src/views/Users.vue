<template>
  <div class="p-6">
    <!-- KPI Cards -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      <div class="bg-[#265d9c] rounded-xl p-6 shadow text-white">
        <div class="flex items-center justify-between mb-4">
          <h3 class="font-semibold text-base">Total Users</h3>
          <svg xmlns="http://www.w3.org/2000/svg" class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M9 20H4v-2a3 3 0 015.356-1.857M15 11a4 4 0 10-8 0 4 4 0 008 0z" />
          </svg>
        </div>
        <p class="text-4xl font-extrabold mb-2">{{ users.length }}</p>
        <div class="flex items-center text-sm">
          <svg xmlns="http://www.w3.org/2000/svg" class="text-green-500 mr-1" width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 10l7-7m0 0l7 7m-7-7v18" />
          </svg>
          <span>+12% from last month</span>
        </div>
      </div>
    </div>

    <!-- Card Container -->
    <div class="bg-[#f8fafd] shadow-md rounded-2xl mt-3 px-6 py-6 max-w-full">
      <h2 class="text-2xl font-bold mb-4 text-[#1d3557]">Users</h2>

      <!-- Search and Add Button -->
      <div class="flex justify-between items-center mb-6">
        <div class="relative w-full max-w-sm">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Search users..."
            class="border border-gray-300 rounded-lg pl-4 pr-10 py-2 w-full text-sm focus:outline-none focus:ring-2 focus:ring-[#1d3557]"
          />
          <svg class="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400" xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-4.35-4.35m2.4-5.65a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </div>
        <button
          class="ml-4 bg-[#265d9c] text-white font-semibold px-4 py-2 rounded-lg text-sm hover:bg-[#16324f] flex items-center gap-2"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M12 5v14M5 12h14" />
          </svg>
          Add User
        </button>
      </div>

      <!-- Users Table -->
      <div class="bg-white rounded-2xl shadow p-6 border border-gray-200">
        <h2 class="text-lg font-semibold mb-4 text-[#1d3557]"></h2>
        <table class="min-w-full text-sm">
          <thead class="bg-[#265d9c] text-white uppercase text-xs rounded-t-xl">
            <tr>
              <th class="px-4 py-2 text-left rounded-tl-lg">ID</th>
              <th class="px-4 py-2 text-left">User</th>
              <th class="px-4 py-2 text-left">Email</th>
              <th class="px-4 py-2 text-left">Password</th>
              <th class="px-4 py-2 text-left ">Position</th>
              <th class="px-4 py-2 text-left rounded-tr-lg">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="user in filteredUsers"
              :key="user.id"
              class="border-t border-gray-200 hover:bg-[#edf5ff]"
            >
              <td class="px-4 py-2 text-[#1d3557] font-semibold">#{{ user.id }}</td>
              <td class="px-4 py-2 flex items-center space-x-3">
                <div
                  class="w-8 h-8 rounded-full bg-[#cfe0f1] flex items-center justify-center text-xs text-[#1d3557] border border-white uppercase"
                >
                  {{ getInitials(user.name) }}
                </div>
                <div class="font-medium text-[#1d3557]">{{ user.name }}</div>
              </td>
              <td class="px-4 py-2 text-gray-700">{{ user.email }}</td>
              <td class="px-4 py-2 text-gray-400 font-mono">********{{ user.id }}</td>
              <td class="px-4 py-2">{{ user.role }}</td>
              <td class="px-4 py-2 flex items-center space-x-2">
                <button class="text-[#1d3557] hover:text-[#2a486e]" title="Edit">
                  <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M12 20h9" />
                    <path stroke-linecap="round" stroke-linejoin="round" d="M16.5 3.5a2.121 2.121 0 113 3L7 19l-4 1 1-4 12.5-12.5z" />
                  </svg>
                </button>
                <button class="text-red-600 hover:text-red-800" title="Delete">
                  <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M3 6h18M8 6v12a2 2 0 002 2h4a2 2 0 002-2V6m-6 0V4a2 2 0 012-2h0a2 2 0 012 2v2" />
                  </svg>
                </button>
                <button @click="selectedUser = user" class="text-[#457b9d] hover:text-[#1d3557]" title="View">
                  <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8S1 12 1 12z" />
                    <circle cx="12" cy="12" r="3" />
                  </svg>
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const users = ref([
  { id: 1, name: 'John Doe', email: 'john.doe@example.com', role: 'Admin' },
  { id: 2, name: 'Jane Smith', email: 'jane.smith@example.com', role: 'Author' },
  { id: 3, name: 'Michael Lee', email: 'michael.lee@example.com', role: 'Moderator' },
  { id: 4, name: 'Anna Reyes', email: 'anna.reyes@example.com', role: 'Contributor' },
  { id: 5, name: 'Carlos Dela Cruz', email: 'carlos.delacruz@example.com', role: 'Subscriber' },
  { id: 6, name: 'Emily Santos', email: 'emily.santos@example.com', role: 'Editor' },
])

const searchQuery = ref('')
const selectedUser = ref(null)

const getInitials = (name) => {
  const words = name.trim().split(' ')
  return words.length === 1 ? words[0][0] : words[0][0] + words[1][0]
}

const filteredUsers = computed(() => {
  if (!searchQuery.value) return users.value
  return users.value.filter((user) =>
    user.name.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
    user.email.toLowerCase().includes(searchQuery.value.toLowerCase())
  )
})
</script>

<style scoped>
</style>
