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
        <p class="text-3xl font-extrabold mb-1.5">{{ totalCount }}</p>
        <div class="flex items-center text-xs">
          <component
            :is="percentageIcon"
            :class="[
              'mr-1 w-3.5 h-3.5',
              percentageColor
            ]"
          />
          <span>{{ percentageChange }}</span>
        </div>
      </div>

      <!-- Distortion Type Count -->
      <div class="bg-[#f8fafd] rounded-xl p-4 shadow text-[#0E2247] relative">
        <div class="flex justify-between items-center mb-3">
          <h3 class="font-semibold text-sm">Total License Plate Distortions</h3>
          <div class="relative">
            <button class="cursor-pointer" @click="showDistortionDropdown = !showDistortionDropdown">
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
            <button class="cursor-pointer" @click="showDeblurDropdown = !showDeblurDropdown">
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
                <button class="text-[#1d3557] hover:text-[#2a486e] cursor-pointer" title="View" @click="goToResult(entry.id)">
                  <Eye class="w-3.5 h-3.5" />
                </button>
                <button class="text-red-600 hover:text-red-800 cursor-pointer" title="Delete" @click="deleteImage(entry.id)">
                  <Trash2 class="w-3.5 h-3.5" />
                </button>
              </td> 
            </tr>
          </tbody>
        </table>
        <!-- Pagination Controls -->
        <div class="flex justify-between items-center mt-4 text-sm">
          <button
            :disabled="!prevPage"
            @click="fetchHistory(currentPage - 1)"
            class="px-3 py-1 rounded bg-gray-200 hover:bg-gray-300 disabled:opacity-50"
          >
            Previous
          </button>

          <span>Page {{ currentPage }}</span>

          <button
            :disabled="!nextPage"
            @click="fetchHistory(currentPage + 1)"
            class="px-3 py-1 rounded bg-gray-200 hover:bg-gray-300 disabled:opacity-50"
          >
            Next
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ArrowUp,ArrowDown, Minus, Trash2, Eye, ScanLine, Search, Filter } from 'lucide-vue-next'
import http from '@/services/http'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()

const searchQuery = ref('')
const startDate = ref('')
const endDate = ref('')
const distortionFilter = ref('All')
const deblurFilter = ref('All')
const showDistortionDropdown = ref(false)
const showDeblurDropdown = ref(false)

const history = ref([])
const currentPage = ref(1)
const nextPage = ref(null)
const prevPage = ref(null)
const totalCount = ref(0)

// Load data with pagination
const fetchHistory = async (page = 1) => {
  try {
    const { data } = await http.get(`/images/?page=${page}`)
    history.value = data.results.map(entry => ({
      id: entry.id,
      image: entry.after_image_url || entry.before_image_url,
      date: entry.date_deblurred ? entry.date_deblurred.split('T')[0] : 'N/A',
      plate: entry.plate_no || '—',
      status: entry.status || 'Unknown',
      distortion: entry.distortion_type || 'Unknown',
      conf: entry.conf_score || '—',
      afterDistortion: entry.after_distortion_type || 'Unknown'
    }))
    totalCount.value = data.count
    nextPage.value = data.next
    prevPage.value = data.previous
    currentPage.value = page
  } catch (err) {
    console.error('Failed to fetch history:', err)
  }
}

onMounted(() => fetchHistory(1))

const setDistortionFilter = (filter) => {
  distortionFilter.value = filter
  showDistortionDropdown.value = false
}

const setDeblurFilter = (filter) => {
  deblurFilter.value = filter
  showDeblurDropdown.value = false
}

// Filtered history for current page
const filteredHistory = computed(() => {
  return history.value.filter((entry) => {
    const matchesSearch = entry.plate.toLowerCase().includes(searchQuery.value.toLowerCase())

    const entryDate = entry.date !== 'N/A' ? new Date(entry.date) : null
    const start = startDate.value ? new Date(startDate.value) : null
    const end = endDate.value ? new Date(endDate.value) : null
    const withinDateRange =
      (!start || (entryDate && entryDate >= start)) &&
      (!end || (entryDate && entryDate <= end))

    const matchesDistortion =
      distortionFilter.value === 'All' || entry.distortion === distortionFilter.value

    const matchesDeblur =
      deblurFilter.value === 'All' || entry.status === deblurFilter.value

    return matchesSearch && withinDateRange && matchesDistortion && matchesDeblur
  })
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

// Count current week and last week
const thisWeekCount = computed(() => {
  const now = new Date()
  const startOfWeek = new Date(now)
  startOfWeek.setDate(now.getDate() - now.getDay()) // Sunday
  return history.value.filter(entry => {
    const d = new Date(entry.date)
    return d >= startOfWeek && d <= now
  }).length
})

const lastWeekCount = computed(() => {
  const now = new Date()
  const startOfThisWeek = new Date(now)
  startOfThisWeek.setDate(now.getDate() - now.getDay())
  const startOfLastWeek = new Date(startOfThisWeek)
  startOfLastWeek.setDate(startOfThisWeek.getDate() - 7)
  return history.value.filter(entry => {
    const d = new Date(entry.date)
    return d >= startOfLastWeek && d < startOfThisWeek
  }).length
})

const percentageChange = computed(() => {
  if (lastWeekCount.value === 0) return '+0%' // avoid division by 0
  const diff = ((thisWeekCount.value - lastWeekCount.value) / lastWeekCount.value) * 100
  const rounded = diff.toFixed(1)
  return (diff >= 0 ? '+' : '') + rounded + '% from last week'
})

const filteredDistortions = computed(() => filteredHistory.value)
const filteredDeblurs = computed(() => filteredHistory.value)

const goToResult = (imageId) => {
  router.push({ path: '/result', query: { imageId } })
}

// Delete image
const deleteImage = async (id) => {
  if (!confirm('Are you sure you want to delete this record?')) return;

  try {
    await http.delete(`/images/${id}/`);
    // Remove locally from UI
    history.value = history.value.filter(entry => entry.id !== id);
    totalCount.value -= 1;
    alert('Image deleted successfully.');
  } catch (err) {
    console.error('Failed to delete image:', err);
    alert('Failed to delete image. Please try again.');
  }
}
</script>