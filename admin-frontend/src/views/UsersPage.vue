<template>
  <div class="p-4 bg-orange-50">
    <!-- Toast Notifications -->
    <Toast
      v-if="toast.visible"
      :type="toast.type"
      :message="toast.message"
      @close="toast.visible = false"
    />

    <!-- KPI Cards -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 mb-4">
      <div
        class="bg-[#265d9c] rounded-xl p-4 shadow text-white transition-transform duration-300 hover:scale-105 hover:shadow-lg"
      >
        <div class="flex items-center justify-between mb-3">
          <h3 class="font-semibold text-sm">Total Users</h3>
          <UsersRound class="w-5 h-5" />
        </div>
        <p class="text-3xl font-extrabold mb-1.5">{{ totalUsers }}</p>
        <div class="flex items-center text-xs">
          <component
            :is="percentageIcon"
            :class="['mr-1 w-3.5 h-3.5', percentageColor]"
          />
          <span>{{ percentageChange }}</span>
        </div>
      </div>
    </div>

    <!-- Users Table -->
    <div class="bg-[#ffffff] shadow-md rounded-2xl mt-2 px-4 py-4 max-w-full">
      <h2 class="text-xl font-bold mb-3 text-[#1d3557]">Users</h2>

      <!-- Search -->
      <div class="flex justify-between items-center mb-5">
        <div class="relative w-full max-w-sm">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Search users..."
            class="border border-gray-300 rounded-lg pl-3 pr-9 py-1.5 w-full text-xs focus:outline-none focus:ring-1 focus:ring-[#265d9c] transition-shadow duration-200 focus:shadow-md"
          />
          <Search class="absolute right-2.5 top-1/2 transform -translate-y-1/2 text-gray-400 w-3.5 h-3.5" />
        </div>
      </div>

      <!-- Table -->
      <div class="bg-white rounded-2xl shadow p-4 border border-gray-200 overflow-x-auto">
        <table class="min-w-full text-xs">
          <thead class="bg-[#265d9c] text-white uppercase text-[0.65rem] rounded-t-xl">
            <tr>
              <th class="px-3 py-1.5 text-left">Name</th>
              <th class="px-3 py-1.5 text-left">Email</th>
              <th class="px-3 py-1.5 text-left">Role</th>
              <th class="px-3 py-1.5 text-left">Joined</th>
              <th class="px-3 py-1.5 text-center">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="user in filteredUsers"
              :key="user.id"
              class="border-t rounded-lg border-gray-200 hover:bg-[#edf5ff] transition duration-200 hover:scale-[1.01]"
            >
              <td class="px-3 py-1.5">{{ user.name }}</td>
              <td class="px-3 py-1.5">{{ user.email }}</td>
              <td class="px-3 py-1.5">{{ user.role }}</td>
              <td class="px-3 py-1.5">{{ user.joined }}</td>
              <td class="px-3 py-1.5 text-center">
                <div class="flex justify-center items-center space-x-1.5">
                  <button
                    @click="editUser(user)"
                    class="icon-btn text-[#1d3557] hover:text-[#2a486e] cursor-pointer"
                  >
                    <SquarePen class="w-4 h-4" />
                  </button>
                  <button
                    @click="deleteUser(user.id)"
                    class="icon-btn text-red-600 hover:text-red-800 cursor-pointer"
                  >
                    <Trash2 class="w-4 h-4" />
                  </button>
                </div>
              </td>
            </tr>
            <tr v-if="filteredUsers.length === 0">
              <td colspan="5" class="px-3 py-4 text-center text-gray-500">
                No users found.
              </td>
            </tr>
          </tbody>
        </table>

        <!-- Pagination -->
        <div class="flex justify-between items-center mt-4 text-sm">
          <button
            :disabled="!prev"
            @click="prevPage"
            class="px-3 py-1 rounded bg-gray-200 hover:bg-gray-300 disabled:opacity-50 cursor-pointer active:scale-95 transition-transform duration-150"
          >
            Previous
          </button>

          <span>Page {{ currentPage }}</span>

          <button
            :disabled="!next"
            @click="nextPage"
            class="px-3 py-1 rounded bg-gray-200 hover:bg-gray-300 disabled:opacity-50 cursor-pointer active:scale-95 transition-transform duration-150"
          >
            Next
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import {
  ArrowUp,
  ArrowDown,
  Minus,
  UsersRound,
  SquarePen,
  Trash2,
  Search
} from 'lucide-vue-next'
import http from '@/utils/http'
import Toast from '@/components/Toast.vue'

// Toast state
const toast = ref({ visible: false, type: '', message: '' })
const showToast = (message: string, type = 'info') => {
  toast.value = { visible: true, type, message }
  setTimeout(() => (toast.value.visible = false), 3000)
}

// Data
const users = ref<any[]>([])
const allUsers = ref<any[]>([])
const next = ref<string | null>(null)
const prev = ref<string | null>(null)
const currentPage = ref(1)
const searchQuery = ref('')

// --- KPI logic (copied from History.vue) ---
const totalUsers = computed(() => allUsers.value.length)

const thisWeekCount = computed(() => {
  const now = new Date()
  const startOfWeek = new Date(now)
  startOfWeek.setDate(now.getDate() - now.getDay())
  return allUsers.value.filter(u => {
    if (!u.joined) return false
    const d = new Date(u.joined)
    return d >= startOfWeek && d <= now
  }).length
})

const lastWeekCount = computed(() => {
  const now = new Date()
  const startOfThisWeek = new Date(now)
  startOfThisWeek.setDate(now.getDate() - now.getDay())
  const startOfLastWeek = new Date(startOfThisWeek)
  startOfLastWeek.setDate(startOfThisWeek.getDate() - 7)
  return allUsers.value.filter(u => {
    if (!u.joined) return false
    const d = new Date(u.joined)
    return d >= startOfLastWeek && d < startOfThisWeek
  }).length
})

const percentageChange = computed(() => {
  if (lastWeekCount.value === 0) return '+0% from last week'
  const diff =
    ((thisWeekCount.value - lastWeekCount.value) / lastWeekCount.value) * 100
  const rounded = diff.toFixed(1)
  return (diff >= 0 ? '+' : '') + rounded + '% from last week'
})

const percentageIcon = computed(() => {
  if (percentageChange.value.startsWith('+')) return ArrowUp
  if (percentageChange.value.startsWith('-')) return ArrowDown
  return Minus
})

const percentageColor = computed(() => {
  if (percentageChange.value.startsWith('+')) return 'text-green-500'
  if (percentageChange.value.startsWith('-')) return 'text-red-500'
  return 'text-gray-500'
})

// --- Computed table filter ---
const filteredUsers = computed(() =>
  users.value.filter(user =>
    user.name.toLowerCase().includes(searchQuery.value.toLowerCase())
  )
)

// --- Fetch functions ---
const fetchAllUsersForKPI = async () => {
  try {
    let page = 1
    let results: any[] = []
    const MAX_PAGES = 500
    while (page <= MAX_PAGES) {
      const { data } = await http.get(`/users/?page=${page}`)
      results = results.concat(data.results || [])
      if (!data.next) break
      page++
    }
    allUsers.value = results.map((u: any) => ({
      id: u.id,
      name: `${u.first_name} ${u.middle_name || ''} ${u.last_name}`
        .replace(/\s+/g, ' ')
        .trim(),
      email: u.email,
      role: u.position,
      joined: u.date_joined ? u.date_joined.split('T')[0] : null
    }))
  } catch (err) {
    console.error('Failed to fetch KPI users:', err)
    showToast('Failed to load KPI data', 'error')
  }
}

const fetchUsers = async (page = 1) => {
  try {
    const { data } = await http.get(`/users/?page=${page}`)
    users.value = data.results.map((u: any) => ({
      id: u.id,
      name: `${u.first_name} ${u.middle_name || ''} ${u.last_name}`
        .replace(/\s+/g, ' ')
        .trim(),
      email: u.email,
      role: u.position,
      joined: u.date_joined ? u.date_joined.split('T')[0] : null
    }))
    next.value = data.next
    prev.value = data.previous
    currentPage.value = page
  } catch (err) {
    console.error('Failed to fetch users:', err)
    showToast('Failed to load users', 'error')
  }
}

// --- Actions ---
const editUser = (user: any) => {
  console.log('Edit user', user)
  showToast('Edit user feature coming soon', 'info')
}

const deleteUser = async (id: number) => {
  if (!confirm('Are you sure you want to delete this user?')) return
  try {
    await http.delete(`/users/${id}/`)
    showToast('User deleted', 'success')
    fetchUsers(currentPage.value)
    fetchAllUsersForKPI()
  } catch (err) {
    console.error('Delete failed:', err)
    showToast('Delete failed', 'error')
  }
}

// --- Pagination ---
const nextPage = () => {
  if (next.value) fetchUsers(currentPage.value + 1)
}
const prevPage = () => {
  if (prev.value) fetchUsers(currentPage.value - 1)
}

// Init*-/
onMounted(() => {
  fetchUsers(1)
  fetchAllUsersForKPI()
})
</script>

<style scoped>
@reference "tailwindcss";

/* Reusable hover animation */
.icon-btn {
  @apply transition-transform duration-150 hover:scale-110;
}
</style>
