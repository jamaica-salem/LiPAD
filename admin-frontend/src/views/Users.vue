<template>
  <div class="p-6">
    <!-- Page Heading -->
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-2xl font-bold text-accent">Users</h1>
      <button class="bg-accent text-white px-4 py-2 rounded-lg hover:bg-accent-dark transition">Add User</button>
    </div>

    <!-- Search Bar -->
    <div class="mb-4">
      <input
        type="text"
        v-model="searchQuery"
        placeholder="Search users..."
        class="w-full p-2 border border-gray-300 rounded-lg"
      />
    </div>

    <!-- Users Table -->
    <div class="overflow-x-auto">
      <table class="min-w-full bg-white border border-gray-200 rounded-lg">
        <thead class="bg-primary-lightest">
          <tr>
            <th class="text-left py-3 px-4 font-semibold text-primary-darkest">Name</th>
            <th class="text-left py-3 px-4 font-semibold text-primary-darkest">Email</th>
            <th class="text-left py-3 px-4 font-semibold text-primary-darkest">Role</th>
            <th class="text-left py-3 px-4 font-semibold text-primary-darkest">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="user in filteredUsers"
            :key="user.id"
            class="border-t border-gray-200 hover:bg-gray-50 transition"
          >
            <td class="py-3 px-4">{{ user.name }}</td>
            <td class="py-3 px-4">{{ user.email }}</td>
            <td class="py-3 px-4">{{ user.role }}</td>
            <td class="py-3 px-4">
              <button class="text-accent hover:underline">View</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

// Dummy user data
const users = ref([
  { id: 1, name: 'Jamaica Salem', email: 'jamaica.salem@example.com', role: 'Frontend Developer' },
  { id: 2, name: 'Jansen Cruz', email: 'jansen.cruz@example.com', role: 'AI Engineer' },
  { id: 3, name: 'Aljunalei Alfonso', email: 'aljunalei.alfonso@example.com', role: 'Model Evaluator' },
  { id: 4, name: 'Wrenz Laylo', email: 'wrenz.laylo@example.com', role: 'AI Engineer' },
])

// Search query state
const searchQuery = ref('')

// Computed filtered users based on search
const filteredUsers = computed(() => {
  return users.value.filter((user) => {
    const query = searchQuery.value.toLowerCase()
    return (
      user.name.toLowerCase().includes(query) ||
      user.email.toLowerCase().includes(query) ||
      user.role.toLowerCase().includes(query)
    )
  })
})
</script>

