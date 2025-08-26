<template>
  <div class="p-4 bg-orange-50">
    <!-- KPI Cards -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 mb-4">
      <!-- Total Plates -->
      <div class="bg-[#265d9c] rounded-xl p-4 shadow text-white">
        <div class="flex items-center justify-between mb-3">
          <h3 class="font-semibold text-sm">Total Plates</h3>
          <ScanLine class="w-5 h-5" />
        </div>
        <p class="text-3xl font-extrabold mb-1.5">{{ filteredHistory.length }}</p>
        <div class="flex items-center text-xs">
          <ArrowUp class="text-green-500 mr-1 w-3.5 h-3.5" />
          <span>+8% from last week</span>
        </div>
      </div>

      <!-- Distortion Type Count -->
      <div class="bg-[#f8fafd] rounded-xl p-4 shadow text-[#0E2247] relative">
        <div class="flex justify-between items-center mb-3">
          <h3 class="font-semibold text-sm">Total License Plate Distortions</h3>
          <div class="relative">
            <button @click="showDistortionDropdown = !showDistortionDropdown">
              <Filter class="w-4 h-4" />
            </button>
            <div
              v-if="showDistortionDropdown"
              class="absolute right-0 mt-1.5 w-40 bg-white border border-gray-200 rounded shadow z-10"
            >
              <ul class="text-xs">
                <li>
                  <button @click="setDistortionFilter('All')" class="block w-full text-left px-3 py-1.5 hover:bg-gray-100">All</button>
                </li>
                <li>
                  <button @click="setDistortionFilter('Low Quality')" class="block w-full text-left px-3 py-1.5 hover:bg-gray-100">Low Quality</button>
                </li>
                <li>
                  <button @click="setDistortionFilter('Low Light')" class="block w-full text-left px-3 py-1.5 hover:bg-gray-100">Low Light</button>
                </li>
                <li>
                  <button @click="setDistortionFilter('Horizontal Blur')" class="block w-full text-left px-3 py-1.5 hover:bg-gray-100">Horizontal Blur</button>
                </li>
                <li>
                  <button @click="setDistortionFilter('Vertical Blur')" class="block w-full text-left px-3 py-1.5 hover:bg-gray-100">Vertical Blur</button>
                </li>
              </ul>
            </div>
          </div>
        </div>
        <p class="text-2xl font-bold">{{ filteredDistortions.length }}</p>
        <p class="text-xs mt-0.5">Filtered by: {{ distortionFilter }}</p>
      </div>

      <!-- Deblur Status -->
      <div class="bg-white rounded-xl p-4 shadow text-[#0E2247] relative">
        <div class="flex justify-between items-center mb-3">
          <h3 class="font-semibold text-sm">Deblur Status Results</h3>
          <div class="relative">
            <button @click="showDeblurDropdown = !showDeblurDropdown">
              <Filter class="w-4 h-4" />
            </button>
            <div
              v-if="showDeblurDropdown"
              class="absolute right-0 mt-1.5 w-36 bg-white border border-gray-200 rounded shadow z-10"
            >
              <ul class="text-xs">
                <li>
                  <button @click="setDeblurFilter('All')" class="block w-full text-left px-3 py-1.5 hover:bg-gray-100">All</button>
                </li>
                <li>
                  <button @click="setDeblurFilter('Successful')" class="block w-full text-left px-3 py-1.5 hover:bg-gray-100">Successful</button>
                </li>
                <li>
                  <button @click="setDeblurFilter('Failed')" class="block w-full text-left px-3 py-1.5 hover:bg-gray-100">Failed</button>
                </li>
              </ul>
            </div>
          </div>
        </div>
        <p class="text-2xl font-bold">{{ filteredDeblurs.length }}</p>
        <p class="text-xs mt-0.5">Filtered by: {{ deblurFilter }}</p>
      </div>
    </div>

    <!-- History Table -->
    <div class="bg-[#ffffff] shadow-md rounded-2xl mt-2 px-4 py-4 max-w-full">
      <h2 class="text-xl font-bold mb-3 text-[#1d3557]">History</h2>

      <!-- Filters -->
      <div class="flex flex-col md:flex-row md:justify-between md:items-center gap-3 mb-4">
        <!-- Search -->
        <div class="relative w-full max-w-xs">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Search plate history..."
            class="border border-gray-300 rounded-lg pl-3 pr-8 py-1.5 w-full text-xs focus:outline-none focus:ring-2 focus:ring-[#1d3557]"
          />
          <Search class="absolute right-2.5 top-1/2 transform -translate-y-1/2 text-gray-400 w-3.5 h-3.5" />
        </div>

        <!-- Date Range -->
        <div class="flex items-center gap-1.5 text-xs">
          <label class="text-gray-600">From:</label>
          <input v-model="startDate" type="date" class="border border-gray-300 rounded-lg px-2 py-1.5" />
          <label class="text-gray-600">To:</label>
          <input v-model="endDate" type="date" class="border border-gray-300 rounded-lg px-2 py-1.5" />
        </div>
      </div>

      <!-- Table -->
      <div class="bg-white rounded-2xl shadow p-4 border border-gray-200 overflow-x-auto">
        <table class="min-w-full text-xs">
          <thead class="bg-[#265d9c] text-white uppercase text-[0.65rem] rounded-t-xl">
            <tr>
              <th class="px-3 py-1.5 text-left rounded-tl-lg">ID</th>
              <th class="px-3 py-1.5 text-left">Image</th>
              <th class="px-3 py-1.5 text-left">Date</th>
              <th class="px-3 py-1.5 text-left">Plate No.</th>
              <th class="px-3 py-1.5 text-left">Status</th>
              <th class="px-3 py-1.5 text-left">Distortion Type</th>
              <th class="px-3 py-1.5 text-right rounded-tr-lg">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="entry in filteredHistory"
              :key="entry.id"
              class="border-t border-gray-200 hover:bg-[#edf5ff]"
            >
              <td class="px-3 py-1.5 font-semibold text-[#1d3557]">#{{ entry.id }}</td>
              <td class="px-3 py-1.5">
                <img :src="entry.image" alt="plate" class="w-8 h-8 object-cover rounded-full border" />
              </td>
              <td class="px-3 py-1.5 text-gray-600">{{ entry.date }}</td>
              <td class="px-3 py-1.5 font-mono text-blue-600">{{ entry.plate }}</td>
              <td class="px-3 py-1.5">
                <span
                  :class="[
                    'text-[0.65rem] font-semibold px-2 py-0.5 rounded-full',
                    entry.status === 'Successful'
                      ? 'bg-green-100 text-green-700'
                      : 'bg-red-100 text-red-700'
                  ]"
                >
                  {{ entry.status.toUpperCase() }}
                </span>
              </td>
              <td class="px-3 py-1.5 text-gray-600">{{ entry.distortion }}</td>
              <td class="px-3 py-1.5 flex justify-end items-center space-x-1.5">
                <button class="text-[#1d3557] hover:text-[#2a486e]" title="View">
                  <Eye class="w-3.5 h-3.5" />
                </button>
                <button class="text-red-600 hover:text-red-800" title="Delete">
                  <Trash2 class="w-3.5 h-3.5" />
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
import { ArrowUp, Trash2, Eye, ScanLine, Search, Filter } from 'lucide-vue-next'

// Filters
const searchQuery = ref('')
const startDate = ref('')
const endDate = ref('')
const distortionFilter = ref('All')
const deblurFilter = ref('All')
const showDistortionDropdown = ref(false)
const showDeblurDropdown = ref(false)

const setDistortionFilter = (filter) => {
  distortionFilter.value = filter
  showDistortionDropdown.value = false
}

const setDeblurFilter = (filter) => {
  deblurFilter.value = filter
  showDeblurDropdown.value = false
}

// Sample data (10 rows)
const history = ref([
  { id: 1, image: '', date: '2025-07-29', plate: 'ABC1234', status: 'Successful', distortion: 'Low Quality' },
  { id: 2, image: '',  date: '2025-07-30', plate: 'XYZ5678', status: 'Failed', distortion: 'Horizontal Blur' },
  { id: 3, image: '',  date: '2025-07-31', plate: 'LMN3456', status: 'Successful', distortion: 'Low Light' },
  { id: 4, image: '',  date: '2025-07-28', plate: 'DEF2222', status: 'Failed', distortion: 'Vertical Blur' },
  { id: 5, image: '',  date: '2025-07-28', plate: 'GHI3333', status: 'Successful', distortion: 'Low Quality' },
])

// Filtered history
const filteredHistory = computed(() => {
  return history.value.filter((entry) => {
    const matchesSearch =

      entry.plate.toLowerCase().includes(searchQuery.value.toLowerCase())

    const entryDate = new Date(entry.date)
    const start = startDate.value ? new Date(startDate.value) : null
    const end = endDate.value ? new Date(endDate.value) : null
    const withinDateRange = (!start || entryDate >= start) && (!end || entryDate <= end)

    return matchesSearch && withinDateRange
  })
})

const filteredDistortions = computed(() => {
  return distortionFilter.value === 'All'
    ? history.value
    : history.value.filter((entry) => entry.distortion === distortionFilter.value)
})

const filteredDeblurs = computed(() => {
  return deblurFilter.value === 'All'
    ? history.value
    : history.value.filter((entry) => entry.status === deblurFilter.value)
})
</script>
