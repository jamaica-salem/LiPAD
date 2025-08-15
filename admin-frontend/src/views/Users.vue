<template>
  <div class="p-4">
    <!-- KPI Cards -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 mb-5">
      <div class="bg-[#265d9c] rounded-xl p-5 shadow text-white">
        <div class="flex items-center justify-between mb-3">
          <h3 class="font-semibold text-sm">Total Users</h3>
          <UsersRound class="w-5 h-5" />
        </div>
        <p class="text-3xl font-extrabold mb-1.5">{{ users.length }}</p>
        <div class="flex items-center text-xs">
          <ArrowUp class="text-green-500 mr-1 w-3.5 h-3.5" />
          <span>+12% from last week</span>
        </div>
    </div>
    </div>

    <!-- Card Container -->
    <div class="bg-[#f8fafd] shadow-md rounded-xl mt-8 px-4 py-4 max-w-full">
      <h2 class="text-xl font-bold mb-3 text-[#1d3557]">Users</h2>

      <!-- Search and Add Button -->
      <div class="flex justify-between items-center mb-5">
        <div class="relative w-full max-w-sm">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Search users..."
            class="border border-gray-300 rounded-lg pl-3.5 pr-9 py-1.5 w-full text-xs focus:outline-none focus:ring-2 focus:ring-[#1d3557]"
          />
          <svg class="absolute right-2.5 top-1/2 transform -translate-y-1/2 text-gray-400" xmlns="http://www.w3.org/2000/svg" width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-4.35-4.35m2.4-5.65a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </div>
        <button
          @click="isAddUserModalOpen = true"
          class="ml-3 bg-[#265d9c] text-white font-semibold px-3 py-1.5 rounded-lg text-xs hover:bg-[#16324f] flex items-center gap-1.5"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M12 5v14M5 12h14" />
          </svg>
          Add User
        </button>
      </div>

      <!-- Users Table -->
      <div class="bg-white rounded-2xl shadow p-5 border border-gray-200">
        <table class="min-w-full text-xs">
          <thead class="bg-[#265d9c] text-white uppercase text-[10px] rounded-t-xl">
            <tr>
              <th class="px-3 py-1.5 text-left rounded-tl-lg">ID</th>
              <th class="px-3 py-1.5 text-left">User</th>
              <th class="px-3 py-1.5 text-left">Email</th>
              <th class="px-3 py-1.5 text-left">Password</th>
              <th class="px-3 py-1.5 text-left">Position</th>
              <th class="px-3 py-1.5 text-left rounded-tr-lg">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="user in filteredUsers" :key="user.id" class="border-t border-gray-200 hover:bg-[#edf5ff]">
              <td class="px-3 py-1.5 text-[#1d3557] font-semibold">#{{ user.id }}</td>
              <td class="px-3 py-1.5 flex items-center space-x-2.5">
                <div class="w-7 h-7 rounded-full bg-[#cfe0f1] flex items-center justify-center text-[10px] text-[#1d3557] border border-white uppercase">
                  {{ getInitials(user.name) }}
                </div>
                <div class="font-medium text-[#1d3557]">{{ user.name }}</div>
              </td>
              <td class="px-3 py-1.5 text-gray-700">{{ user.email }}</td>
              <td class="px-3 py-1.5 text-gray-400 font-mono">********{{ user.id }}</td>
              <td class="px-3 py-1.5">{{ user.role }}</td>
              <td class="px-3 py-1.5 flex items-center space-x-1.5">
                <button class="text-[#1d3557] hover:text-[#2a486e]" title="Edit">✏️</button>
                <button class="text-red-600 hover:text-red-800" title="Delete">🗑</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Add User Modal -->
    <div
      v-if="isAddUserModalOpen"
      class="fixed inset-0 z-50 flex justify-center items-center p-3.5"
      role="dialog"
      aria-modal="true"
    >
      <div class="bg-white w-full max-w-2xl p-5 rounded-2xl shadow-2xl relative overflow-auto max-h-screen border border-gray-200">
        <div class="flex justify-between items-center border-b border-gray-200 pb-2.5 mb-3">
          <h2 class="text-lg font-semibold text-gray-800">Add User</h2>
          <button @click="isAddUserModalOpen = false" class="text-gray-500 hover:text-red-600 text-xl leading-none">&times;</button>
        </div>

        <!-- Form -->
        <div class="space-y-5 text-xs">
          <div class="flex">
            <div class="flex flex-col gap-1.5 relative group">
              <div
                @dblclick="fileInputRef?.click()"
                class="w-[6.5rem] h-[6.5rem] border border-gray-300 rounded-lg bg-gray-100 flex items-center justify-center cursor-pointer relative"
              >
                <img v-if="newUser.photoPreview" :src="newUser.photoPreview" class="object-cover h-full w-full rounded-lg" />
                <span v-else class="text-[10px] text-gray-400 text-center px-2">Double click to upload</span>
                <button
                  v-if="newUser.photoPreview"
                  @click="deletePhoto"
                  class="absolute top-0.5 right-0.5 text-red-500 opacity-0 group-hover:opacity-100"
                  title="Remove"
                >
                  🗑
                </button>
              </div>
              <input
                :ref="el => (fileInputRef = el)"
                type="file"
                accept="image/*"
                class="hidden"
                @change="handlePhotoUpload"
              />
            </div>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
            <input v-model="newUser.firstName" type="text" placeholder="First Name"
              class="border border-gray-300 rounded-md px-2.5 py-1.5 w-full focus:outline-none focus:ring-2 focus:ring-[#1d3557]" />
            <input v-model="newUser.middleName" type="text" placeholder="Middle Name"
              class="border border-gray-300 rounded-md px-2.5 py-1.5 w-full focus:outline-none focus:ring-2 focus:ring-[#1d3557]" />
            <input v-model="newUser.lastName" type="text" placeholder="Last Name"
              class="border border-gray-300 rounded-md px-2.5 py-1.5 w-full focus:outline-none focus:ring-2 focus:ring-[#1d3557]" />
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
            <input v-model="newUser.email" type="email" placeholder="Email"
              class="border border-gray-300 rounded-md px-2.5 py-1.5 w-full focus:outline-none focus:ring-2 focus:ring-[#1d3557]" />
            <input v-model="newUser.password" type="password" placeholder="Password"
              class="border border-gray-300 rounded-md px-2.5 py-1.5 w-full focus:outline-none focus:ring-2 focus:ring-[#1d3557]" />
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
            <input v-model="newUser.birthdate" type="date"
              class="border border-gray-300 rounded-md px-2.5 py-1.5 w-full focus:outline-none focus:ring-2 focus:ring-[#1d3557]" />
            <input v-model="newUser.position" type="text" placeholder="Position"
              class="border border-gray-300 rounded-md px-2.5 py-1.5 w-full focus:outline-none focus:ring-2 focus:ring-[#1d3557]" />
          </div>
        </div>

        <div class="mt-6 flex justify-end gap-2.5">
          <button @click="isAddUserModalOpen = false" class="bg-white border border-gray-300 px-3 py-1.5 rounded hover:bg-gray-100">
            Cancel
          </button>
          <button @click="saveUser" class="bg-[#265d9c] text-white px-4 py-1.5 rounded-md hover:bg-[#16324f]">
            Save
          </button>
        </div>
      </div>
    </div>

  </div>
</template>


<script setup>
import { ref, computed, onBeforeUnmount } from 'vue'
import { ArrowUp, UsersRound } from 'lucide-vue-next'

const users = ref([
  { id: 1, name: 'John Doe', email: 'john.doe@example.com', role: 'Admin' },
  { id: 2, name: 'Jane Smith', email: 'jane.smith@example.com', role: 'Author' },
  { id: 3, name: 'Michael Lee', email: 'michael.lee@example.com', role: 'Moderator' },
  { id: 4, name: 'Anna Reyes', email: 'anna.reyes@example.com', role: 'Contributor' },
  { id: 5, name: 'Carlos Dela Cruz', email: 'carlos.delacruz@example.com', role: 'Subscriber' },
  { id: 6, name: 'Emily Santos', email: 'emily.santos@example.com', role: 'Editor' },
])

const searchQuery = ref('')
const isAddUserModalOpen = ref(false)
let fileInputRef = null

const newUser = ref({
  firstName: '',
  middleName: '',
  lastName: '',
  email: '',
  password: '',
  position: '',
  birthdate: '',
  photoPreview: null
})

const resetNewUser = () => {
  newUser.value = {
    firstName: '',
    middleName: '',
    lastName: '',
    email: '',
    password: '',
    position: '',
    birthdate: '',
    photoPreview: null
  }
  if (fileInputRef) fileInputRef.value = ''
}

const handlePhotoUpload = (event) => {
  const file = event.target.files?.[0]
  if (!file) return
  // revoke old preview if any
  if (newUser.value.photoPreview) {
    URL.revokeObjectURL(newUser.value.photoPreview)
  }
  newUser.value.photoPreview = URL.createObjectURL(file)
}

const deletePhoto = () => {
  if (newUser.value.photoPreview) {
    URL.revokeObjectURL(newUser.value.photoPreview)
  }
  newUser.value.photoPreview = null
  if (fileInputRef) fileInputRef.value = ''
}

onBeforeUnmount(() => {
  if (newUser.value.photoPreview) {
    URL.revokeObjectURL(newUser.value.photoPreview)
  }
})

const saveUser = () => {
  const fullName = `${newUser.value.firstName} ${newUser.value.middleName} ${newUser.value.lastName}`.replace(/\s+/g, ' ').trim()
  users.value.push({
    id: users.value.length + 1,
    name: fullName || 'New User',
    email: newUser.value.email,
    role: newUser.value.position
  })
  isAddUserModalOpen.value = false
  resetNewUser()
}

const getInitials = (name) => {
  const words = name.trim().split(' ')
  return words.length === 1 ? words[0][0] : (words[0][0] + words[1][0])
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
/* no extra styles needed */
</style>
