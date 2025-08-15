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
          class="ml-3 bg-[#265d9c] text-white font-semibold px-3 py-1.5 rounded-lg text-xs hover:bg-[#16324f] flex items-center gap-1.5 cursor-pointer"
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
              <th class="px-3 py-1.5 text-left rounded-tl-lg">NO.</th>
              <th class="px-3 py-1.5 text-left">User</th>
              <th class="px-3 py-1.5 text-left">Email</th>
              <th class="px-3 py-1.5 text-left">Password</th>
              <th class="px-3 py-1.5 text-left">Position</th>
              <th class="px-3 py-1.5 text-left rounded-tr-lg">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(user, index) in filteredUsers" :key="user.id" class="border-t border-gray-200 hover:bg-[#edf5ff]">
              <!-- Use index + 1 for sequential row numbers -->
              <td class="px-3 py-1.5 text-[#1d3557] font-semibold">#{{ index + 1 }}</td>

              <td class="px-3 py-1.5 flex items-center space-x-2.5">
                <div class="w-7 h-7 rounded-full bg-[#cfe0f1] flex items-center justify-center text-[10px] text-[#1d3557] border border-white uppercase">
                  {{ getInitials(user.name) }}
                </div>
                <div class="font-medium text-[#1d3557]">{{ user.name }}</div>
              </td>

              <td class="px-3 py-1.5 text-gray-700">{{ user.email }}</td>
              <td class="px-3 py-1.5 text-gray-400 font-mono">********</td>
              <td class="px-3 py-1.5">{{ user.role }}</td>

              <td class="px-3 py-1.5 flex items-center space-x-1.5">
                <!-- Edit Button -->
                <button 
                  class="text-[#1d3557] hover:text-[#2a486e] cursor-pointer" 
                  title="Edit"
                  @click="openEditUserModal(user)"
                >
                  <SquarePen class="w-4 h-4" />
                </button>

                <!-- Delete Button -->
                <button
                  class="text-red-600 hover:text-red-800 cursor-pointer"
                  title="Delete"
                  @click="deleteUser(user.id)"
                >
                  <Trash2 class="w-4 h-4" />
                </button>
              </td>
            </tr>
          </tbody>

        </table>
      </div>
    </div>

    <!-- Add User Modal -->
    <div
      v-if="isAddUserModalOpen"
      class="fixed inset-0 z-50 flex justify-center items-center p-3.5 bg-black/20"
      role="dialog"
      aria-modal="true"
    >
      <div class="bg-white w-full max-w-2xl p-5 rounded-2xl shadow-2xl relative overflow-auto max-h-screen border border-gray-200">
        <div class="flex justify-between items-center border-b border-gray-200 pb-2.5 mb-3">
          <h2 class="text-lg font-semibold text-gray-800">Add User</h2>
          <button @click="isAddUserModalOpen = false" class="text-gray-500 hover:text-red-600 text-xl leading-none cursor-pointer">&times;</button>
        </div>

        <!-- Form -->
        <div class="space-y-5 text-xs">
          <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
            <input v-model="newUser.firstName" type="text" placeholder="First Name" class="border border-gray-300 rounded-md px-2.5 py-1.5 w-full focus:outline-none focus:ring-2 focus:ring-[#1d3557]" />
            <input v-model="newUser.middleName" type="text" placeholder="Middle Name" class="border border-gray-300 rounded-md px-2.5 py-1.5 w-full focus:outline-none focus:ring-2 focus:ring-[#1d3557]" />
            <input v-model="newUser.lastName" type="text" placeholder="Last Name" class="border border-gray-300 rounded-md px-2.5 py-1.5 w-full focus:outline-none focus:ring-2 focus:ring-[#1d3557]" />
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
            <input v-model="newUser.email" type="email" placeholder="Email" class="border border-gray-300 rounded-md px-2.5 py-1.5 w-full focus:outline-none focus:ring-2 focus:ring-[#1d3557]" />
            <input v-model="newUser.password" type="password" placeholder="Password" class="border border-gray-300 rounded-md px-2.5 py-1.5 w-full focus:outline-none focus:ring-2 focus:ring-[#1d3557]" />
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
            <input v-model="newUser.birthdate" type="date" class="border border-gray-300 rounded-md px-2.5 py-1.5 w-full focus:outline-none focus:ring-2 focus:ring-[#1d3557]" />
            <input v-model="newUser.position" type="text" placeholder="Position" class="border border-gray-300 rounded-md px-2.5 py-1.5 w-full focus:outline-none focus:ring-2 focus:ring-[#1d3557]" />
          </div>
        </div>

        <div class="mt-6 flex justify-end gap-2.5">
          <button @click="isAddUserModalOpen = false" class="bg-white border border-gray-300 px-3 py-1.5 rounded hover:bg-gray-100 cursor-pointer">
            Cancel
          </button>
          <button @click="saveUser" class="bg-[#265d9c] text-white px-4 py-1.5 rounded-md hover:bg-[#16324f] cursor-pointer">
            Save
          </button>
        </div>
      </div>
    </div>

    <!-- Edit User Modal -->
    <div
      v-if="isEditUserModalOpen"
      class="fixed inset-0 z-50 flex justify-center items-center p-3.5 bg-black/20"
      role="dialog"
      aria-modal="true"
    >
      <div class="bg-white w-full max-w-2xl p-5 rounded-2xl shadow-2xl relative overflow-auto max-h-screen border border-gray-200">
        <div class="flex justify-between items-center border-b border-gray-200 pb-2.5 mb-3">
          <h2 class="text-lg font-semibold text-gray-800">Edit User</h2>
          <button @click="isEditUserModalOpen = false" class="text-gray-500 hover:text-red-600 text-xl leading-none cursor-pointer">&times;</button>
        </div>

        <!-- Form -->
        <div class="space-y-5 text-xs">
          <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
            <input v-model="editUser.firstName" type="text" placeholder="First Name" class="border border-gray-300 rounded-md px-2.5 py-1.5 w-full focus:outline-none focus:ring-2 focus:ring-[#1d3557]" />
            <input v-model="editUser.middleName" type="text" placeholder="Middle Name" class="border border-gray-300 rounded-md px-2.5 py-1.5 w-full focus:outline-none focus:ring-2 focus:ring-[#1d3557]" />
            <input v-model="editUser.lastName" type="text" placeholder="Last Name" class="border border-gray-300 rounded-md px-2.5 py-1.5 w-full focus:outline-none focus:ring-2 focus:ring-[#1d3557]" />
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
            <input v-model="editUser.email" type="email" placeholder="Email" class="border border-gray-300 rounded-md px-2.5 py-1.5 w-full focus:outline-none focus:ring-2 focus:ring-[#1d3557]" />
            <input v-model="editUser.password" type="password" placeholder="Password" class="border border-gray-300 rounded-md px-2.5 py-1.5 w-full focus:outline-none focus:ring-2 focus:ring-[#1d3557]" />
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
            <input v-model="editUser.birthdate" type="date" class="border border-gray-300 rounded-md px-2.5 py-1.5 w-full focus:outline-none focus:ring-2 focus:ring-[#1d3557]" />
            <input v-model="editUser.position" type="text" placeholder="Position" class="border border-gray-300 rounded-md px-2.5 py-1.5 w-full focus:outline-none focus:ring-2 focus:ring-[#1d3557]" />
          </div>
        </div>

        <div class="mt-6 flex justify-end gap-2.5">
          <button @click="isEditUserModalOpen = false" class="bg-white border border-gray-300 px-3 py-1.5 rounded hover:bg-gray-100 cursor-pointer">
            Cancel
          </button>
          <button @click="updateUser" class="bg-[#265d9c] text-white px-4 py-1.5 rounded-md hover:bg-[#16324f] cursor-pointer">
            Save
          </button>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ArrowUp, UsersRound, SquarePen, Trash2 } from 'lucide-vue-next'
import axios from 'axios'

// Reactive state
const users = ref([])
const searchQuery = ref('')
const isAddUserModalOpen = ref(false)
const isEditUserModalOpen = ref(false) 
const editUser = ref({}) 


const newUser = ref({
  firstName: '',
  middleName: '',
  lastName: '',
  email: '',
  password: '',
  position: '',
  birthdate: ''
})

const resetNewUser = () => {
  newUser.value = { firstName: '', middleName: '', lastName: '', email: '', password: '', position: '', birthdate: '' }
}

// Fetch users on page load
onMounted(async () => {
  await fetchUsers()
})

// Function to fetch all users
const fetchUsers = async () => {
  try {
    const response = await axios.get('http://localhost:8000/api/users/')
    // Map response to desired frontend format
    users.value = response.data
      .sort((a, b) => a.id - b.id) // Ensure ascending order by user ID
      .map(user => ({
        id: user.id,
        name: `${user.first_name} ${user.middle_name || ''} ${user.last_name}`.replace(/\s+/g, ' ').trim(),
        email: user.email,
        role: user.position
      }))
  } catch (err) {
    console.error('Failed to fetch users:', err.response?.data || err.message)
  }
}

// Save user to backend
const saveUser = async () => {
  try {
    const payload = {
      first_name: newUser.value.firstName,
      middle_name: newUser.value.middleName,
      last_name: newUser.value.lastName,
      email: newUser.value.email,
      password: newUser.value.password,
      position: newUser.value.position,
      date_of_birth: newUser.value.birthdate
    }

    const response = await axios.post('http://localhost:8000/api/users/', payload)
    const user = response.data

    // Add to local state
    const fullName = `${user.first_name} ${user.middle_name || ''} ${user.last_name}`.replace(/\s+/g, ' ').trim()
    users.value.push({ id: user.id, name: fullName, email: user.email, role: user.position })

    // Close modal and reset form
    isAddUserModalOpen.value = false
    resetNewUser()
  } catch (err) {
    console.error('Failed to save user:', err.response?.data || err.message)
    alert('Error saving user. Please check the input fields.')
  }
}

// Delete user from backend and remove from local state
const deleteUser = async (userId) => {
  if (!confirm('Are you sure you want to delete this user?')) return // Safety confirmation

  try {
    await axios.delete(`http://localhost:8000/api/users/${userId}/`)
    // Remove from local users array
    users.value = users.value.filter(user => user.id !== userId)
  } catch (err) {
    console.error(`Failed to delete user #${userId}:`, err.response?.data || err.message)
    alert('Error deleting user. Please try again later.')
  }
}

// Search filter
const filteredUsers = computed(() => {
  if (!searchQuery.value) return users.value
  return users.value.filter(user =>
    user.name.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
    user.email.toLowerCase().includes(searchQuery.value.toLowerCase())
  )
})

// Helper for initials
const getInitials = (name) => {
  const words = name.trim().split(' ')
  if (words.length === 0) return ''
  if (words.length === 1) return words[0][0]  // only first name exists
  const firstInitial = words[0][0]            // first name
  const lastInitial = words[words.length - 1][0] // last name
  return (firstInitial + lastInitial).toUpperCase()
}

// Open the edit modal and pre-fill the form
const openEditUserModal = (user) => {
  editUser.value = {
    id: user.id,
    firstName: user.name.split(' ')[0] || '',
    middleName: user.name.split(' ')[1] || '',
    lastName: user.name.split(' ')[2] || '',
    email: user.email,
    password: '', // Password should not be pre-filled
    position: user.role,
    birthdate: user.birthdate || '' // fetch if available from backend
  }
  isEditUserModalOpen.value = true
}

const updateUser = async () => {
  try {
    // Build payload dynamically
    const payload = {
      first_name: editUser.value.firstName,
      middle_name: editUser.value.middleName,
      last_name: editUser.value.lastName,
      email: editUser.value.email,
      position: editUser.value.position
    }

    // Only include password if user typed a new one
    if (editUser.value.password && editUser.value.password.trim() !== '') {
      payload.password = editUser.value.password
    }

    // Include birthdate only if it's not empty
    if (editUser.value.birthdate) {
      payload.date_of_birth = editUser.value.birthdate
    }

    // Send PATCH request
    const response = await axios.patch(`http://localhost:8000/api/users/${editUser.value.id}/`, payload)
    const updated = response.data

    // Update frontend list
    const index = users.value.findIndex(u => u.id === updated.id)
    if (index !== -1) {
      users.value[index] = {
        id: updated.id,
        name: `${updated.first_name} ${updated.middle_name || ''} ${updated.last_name}`.replace(/\s+/g, ' ').trim(),
        email: updated.email,
        role: updated.position,
        birthdate: updated.date_of_birth // optional
      }
    }

    isEditUserModalOpen.value = false
    editUser.value = {}
  } catch (err) {
    console.error(`Failed to update user #${editUser.value.id}:`, err.response?.data || err.message)
    alert('Error updating user. Please check the input fields.')
  }
}


</script>
