<template>
  <div class="p-4 bg-orange-50">
    <!-- Toast Notifications -->
    <Toast v-if="toast.visible" :type="toast.type" :message="toast.message" @close="toast.visible = false" />

    <!-- KPI Cards -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 mb-4">
      <!-- Total Plates -->
      <div
        class="bg-[#265d9c] rounded-xl p-4 shadow text-white transition-transform duration-300 hover:scale-105 hover:shadow-lg"
      >
        <div class="flex items-center justify-between mb-3">
          <h3 class="font-semibold text-sm">Total Plates</h3>
          <ScanLine class="w-5 h-5" />
        </div>
        <p class="text-3xl font-extrabold mb-1.5">{{ totalCount }}</p>
        <div class="flex items-center text-xs">
          <component :is="percentageIcon" :class="['mr-1 w-3.5 h-3.5', percentageColor]" />
          <span>{{ percentageChange }}</span>
        </div>
      </div>

      <!-- Distortion Type Count -->
      <div
        class="bg-[#f8fafd] rounded-xl p-4 shadow text-[#0E2247] relative transition-transform duration-300 hover:scale-105 hover:shadow-lg"
      >
        <div class="flex justify-between items-center mb-3">
          <h3 class="font-semibold text-sm">Total License Plate Distortions</h3>
          <div class="relative">
            <button
              class="cursor-pointer transition-colors duration-200 hover:text-[#265d9c]"
              @click="showDistortionDropdown = !showDistortionDropdown"
              aria-haspopup="true"
              :aria-expanded="showDistortionDropdown"
            >
              <Filter class="w-4 h-4" />
            </button>
            <transition name="fade-slide">
              <div
                v-if="showDistortionDropdown"
                class="absolute right-0 mt-1.5 w-40 bg-white border border-gray-200 rounded shadow z-10"
              >
                <ul class="text-xs">
                  <li><button @click="setKpiDistortionFilter('All')" class="dropdown-item cursor-pointer">All</button></li>
                  <li><button @click="setKpiDistortionFilter('Low Quality')" class="dropdown-item cursor-pointer">Low Quality</button></li>
                  <li><button @click="setKpiDistortionFilter('Low Light')" class="dropdown-item cursor-pointer">Low Light</button></li>
                  <li><button @click="setKpiDistortionFilter('Horizontal Blur')" class="dropdown-item cursor-pointer">Horizontal Blur</button></li>
                  <li><button @click="setKpiDistortionFilter('Vertical Blur')" class="dropdown-item cursor-pointer">Vertical Blur</button></li>
                </ul>
              </div>
            </transition>
          </div>
        </div>
        <p class="text-2xl font-bold">{{ filteredDistortions.length }}</p>
        <p class="text-xs mt-0.5">Filtered by: {{ kpiDistortionFilter }}</p>
      </div>

      <!-- Deblur Status -->
      <div
        class="bg-white rounded-xl p-4 shadow text-[#0E2247] relative transition-transform duration-300 hover:scale-105 hover:shadow-lg"
      >
        <div class="flex justify-between items-center mb-3">
          <h3 class="font-semibold text-sm">Deblur Status Results</h3>
          <div class="relative">
            <button
              class="cursor-pointer transition-colors duration-200 hover:text-[#265d9c]"
              @click="showDeblurDropdown = !showDeblurDropdown"
              aria-haspopup="true"
              :aria-expanded="showDeblurDropdown"
            >
              <Filter class="w-4 h-4" />
            </button>
            <transition name="fade-slide">
              <div
                v-if="showDeblurDropdown"
                class="absolute right-0 mt-1.5 w-36 bg-white border border-gray-200 rounded shadow z-10"
              >
                <ul class="text-xs">
                  <li><button @click="setKpiDeblurFilter('All')" class="dropdown-item cursor-pointer">All</button></li>
                  <li><button @click="setKpiDeblurFilter('Successful')" class="dropdown-item cursor-pointer">Successful</button></li>
                  <li><button @click="setKpiDeblurFilter('Failed')" class="dropdown-item cursor-pointer">Failed</button></li>
                </ul>
              </div>
            </transition>
          </div>
        </div>
        <p class="text-2xl font-bold">{{ filteredDeblurs.length }}</p>
        <p class="text-xs mt-0.5">Filtered by: {{ kpiDeblurFilter }}</p>
      </div>
    </div>

    <!-- History Table -->
    <div class="bg-[#ffffff] shadow-md rounded-2xl mt-2 px-4 py-4 max-w-full">
      <h2 class="text-xl font-bold mb-3 text-[#1d3557]">Overall History</h2>

      <!-- Table Filters -->
      <div class="flex flex-col md:flex-row md:justify-between md:items-center gap-3 mb-4">
        <!-- Search -->
        <div class="relative w-full md:w-1/2">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Search plate history..."
            class="border border-gray-300 rounded-lg pl-3 pr-8 py-1.5 w-full text-xs focus:outline-none focus:ring-1 focus:ring-[#265d9c] transition-shadow duration-200 focus:shadow-md"
            aria-label="Search plate history"
          />
          <Search class="absolute right-2.5 top-1/2 transform -translate-y-1/2 text-gray-400 w-3.5 h-3.5" />
        </div>

        <!-- Right controls -->
        <div ref="rightControlsRef" class="flex items-center gap-1.5 text-xs md:ml-auto">
          <label class="text-gray-600 hidden md:block">From:</label>
          <input v-model="startDate" type="date" class="date-input" />
          <label class="text-gray-600 hidden md:block">To:</label>
          <input v-model="endDate" type="date" class="date-input" />

          <div class="relative" ref="tableFilterRef">
            <button
              class="cursor-pointer border border-gray-300 rounded-lg px-2 py-1.5 flex items-center justify-center transition-colors duration-200 hover:bg-gray-100"
              @click="toggleTableDistortionDropdown"
              :aria-expanded="showTableDistortionDropdown"
              aria-haspopup="true"
              aria-label="Filter by distortion"
              title="Filter by distortion"
            >
              <Filter class="w-4 h-4" />
            </button>

            <transition name="fade-slide">
              <div
                v-if="showTableDistortionDropdown"
                class="absolute right-0 mt-1.5 w-44 bg-white border border-gray-200 rounded shadow z-10 text-xs"
              >
                <ul>
                  <li><button @click="setTableDistortionFilter('All')" class="dropdown-item cursor-pointer">All</button></li>
                  <li><button @click="setTableDistortionFilter('Low Quality')" class="dropdown-item cursor-pointer">Low Quality</button></li>
                  <li><button @click="setTableDistortionFilter('Low Light')" class="dropdown-item cursor-pointer">Low Light</button></li>
                  <li><button @click="setTableDistortionFilter('Horizontal Blur')" class="dropdown-item cursor-pointer">Horizontal Blur</button></li>
                  <li><button @click="setTableDistortionFilter('Vertical Blur')" class="dropdown-item cursor-pointer">Vertical Blur</button></li>
                </ul>
              </div>
            </transition>
          </div>
        </div>
      </div>

      <!-- Table -->
      <div class="bg-white rounded-2xl shadow p-4 border border-gray-200 overflow-x-auto">
        <table class="min-w-full text-xs">
          <thead class="bg-[#265d9c] text-white uppercase text-[0.65rem] rounded-t-xl">
            <tr>
              <th class="px-3 py-1.5 text-left rounded-tl-lg">NO.</th>
              <th class="px-3 py-1.5 text-left">User</th>
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
              v-for="(entry, index) in filteredTableHistory"
              :key="entry.id"
              class="border-t rounded-lg border-gray-200 hover:bg-[#edf5ff] transition duration-200 hover:scale-[1.01]"
            >
              <td class="px-3 py-1.5 font-semibold text-[#383f49]">#{{ totalCount - ((currentPage - 1) * pageSize + index) }}</td>
              <td class="px-3 py-1.5 text-gray-600">{{ entry.user || 'N/A' }}</td>
              <td class="px-3 py-1.5">
                <img :src="entry.image" alt="plate" class="w-8 h-8 object-cover rounded-full border transition-transform duration-200 hover:scale-110" />
              </td>
              <td class="px-3 py-1.5 text-gray-600">{{ entry.date }}</td>
              <td class="px-3 py-1.5 font-mono text-blue-600">{{ entry.plate }}</td>
              <td class="px-3 py-1.5">
                <span
                  :class="[
                    'text-[0.65rem] font-semibold px-2 py-0.5 rounded-full transition-colors duration-200',
                    entry.status === 'Successful' ? 'bg-green-100 text-green-700 hover:bg-green-200' : 'bg-red-100 text-red-700 hover:bg-red-200'
                  ]"
                >
                  {{ entry.status.toUpperCase() }}
                </span>
              </td>
              <td class="px-3 py-1.5 text-gray-600">{{ entry.distortion }}</td>
              <td class="px-3 py-1.5 text-right align-middle">
                <div class="flex justify-end items-center space-x-1.5">
                  <button
                    class="icon-btn text-[#1d3557] hover:text-[#2a486e] cursor-pointer"
                    title="View"
                    @click="goToResult(entry.id)"
                    :aria-label="`View result for ${entry.id}`"
                  >
                    <Eye class="w-4 h-4" />
                  </button>

                  <button
                    class="icon-btn text-red-600 hover:text-red-800 cursor-pointer"
                    title="Delete"
                    @click="deleteImage(entry.id)"
                    :disabled="deletingIds.has(entry.id)"
                    :aria-busy="deletingIds.has(entry.id) ? 'true' : 'false'"
                  >
                    <Trash2 class="w-4 h-4" />
                  </button>
                </div>
              </td>
            </tr>
            <tr v-if="filteredTableHistory.length === 0">
              <td colspan="8" class="px-3 py-4 text-center text-gray-500">No records found for the selected filters.</td>
            </tr>
          </tbody>
        </table>

        <!-- Pagination Controls -->
        <div class="flex justify-between items-center mt-4 text-sm">
          <button
            :disabled="!prevPage"
            @click="fetchHistory(currentPage - 1)"
            class="px-3 py-1 rounded bg-gray-200 hover:bg-gray-300 disabled:opacity-50 cursor-pointer active:scale-95 transition-transform duration-150"
          >
            Previous
          </button>
          <span>Page {{ currentPage }} of {{ Math.max(1, Math.ceil(totalCount / pageSize)) }}</span>
          <button
            :disabled="!nextPage"
            @click="fetchHistory(currentPage + 1)"
            class="px-3 py-1 rounded bg-gray-200 hover:bg-gray-300 disabled:opacity-50 cursor-pointer active:scale-95 transition-transform duration-150"
          >
            Next
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { ArrowUp, ArrowDown, Minus, Trash2, Eye, ScanLine, Search, Filter } from 'lucide-vue-next'
import http from '@/utils/http'
import { useRouter } from 'vue-router'
import Toast from '@/components/Toast.vue'

const router = useRouter()

// Shared reactive state (same as History.vue)
const searchQuery = ref('')
const startDate = ref('')
const endDate = ref('')
const tableDistortionFilter = ref('All')
const showTableDistortionDropdown = ref(false)
const tableFilterRef = ref(null)
const rightControlsRef = ref(null)

const kpiDistortionFilter = ref('All')
const kpiDeblurFilter = ref('All')
const showDistortionDropdown = ref(false)
const showDeblurDropdown = ref(false)

const toast = ref({ visible: false, message: '', type: 'info' })
const showToast = (message, type = 'info', duration = 3000) => {
  toast.value = { visible: true, message: String(message || ''), type }
  setTimeout(() => { if (toast.value.visible) toast.value.visible = false }, duration)
}

const allHistory = ref([])
const history = ref([])
const totalCount = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)
const nextPage = ref(null)
const prevPage = ref(null)
const deletingIds = ref(new Set())

// --- Fetch All for KPI ---
const fetchAllHistoryForKPI = async () => {
  try {
    let page = 1
    let results = []
    const MAX_PAGES = 500
    while (page <= MAX_PAGES) {
      const { data } = await http.get(`/images/?page=${page}`)
      const mapped = (data.results || []).map(entry => ({
        id: entry.id,
        user: entry.user?.username || 'Unknown',
        image: entry.after_image_url || entry.before_image_url,
        date: entry.date_deblurred ? entry.date_deblurred.split('T')[0] : 'N/A',
        plate: entry.plate_no || '—',
        status: entry.status || 'Unknown',
        distortion: entry.distortion_type || 'Unknown',
      }))
      results = results.concat(mapped)
      if (!data.next) break
      page++
    }
    allHistory.value = results
  } catch (err) {
    console.error('KPI fetch failed', err)
    showToast('Unable to load KPI data.', 'error')
  }
}

// --- Fetch Paginated Table ---
const fetchHistory = async (page = 1) => {
  try {
    if (page < 1) page = 1
    const { data } = await http.get(`/images/?page=${page}`)
    history.value = (data.results || []).map(entry => ({
      id: entry.id,
      user: entry.user ? `${entry.user.first_name} ${entry.user.last_name}` : '—',
      image: entry.after_image_url || entry.before_image_url,
      date: entry.date_deblurred ? entry.date_deblurred.split('T')[0] : 'N/A',
      plate: entry.plate_no || '—',
      status: entry.status || 'Unknown',
      distortion: entry.distortion_type || 'Unknown',
    }))
    totalCount.value = Number(data.count || history.value.length)
    nextPage.value = data.next
    prevPage.value = data.previous
    currentPage.value = page
  } catch (err) {
    console.error('History fetch failed', err)
    showToast('Unable to load history.', 'error')
  }
}

onMounted(() => {
  Promise.allSettled([fetchAllHistoryForKPI(), fetchHistory(1)])
  document.addEventListener('click', handleDocumentClick)
  document.addEventListener('keydown', handleKeyDown)
})

onBeforeUnmount(() => {
  document.removeEventListener('click', handleDocumentClick)
  document.removeEventListener('keydown', handleKeyDown)
})

const handleDocumentClick = (e) => {
  const target = e?.target
  try {
    if (tableFilterRef.value && !tableFilterRef.value.contains(target)) showTableDistortionDropdown.value = false
    if (showDistortionDropdown.value && !target.closest('[aria-haspopup="true"]')) showDistortionDropdown.value = false
    if (showDeblurDropdown.value && !target.closest('[aria-haspopup="true"]')) showDeblurDropdown.value = false
  } catch {}
}
const handleKeyDown = (e) => {
  if (e.key === 'Escape') {
    showTableDistortionDropdown.value = false
    showDistortionDropdown.value = false
    showDeblurDropdown.value = false
  }
}

// --- KPI Filters ---
const setKpiDistortionFilter = (filter) => {
  kpiDistortionFilter.value = filter
  showDistortionDropdown.value = false
}

const setKpiDeblurFilter = (filter) => {
  kpiDeblurFilter.value = filter
  showDeblurDropdown.value = false
}

// --- Table Filters ---
const toggleTableDistortionDropdown = () => {
  showTableDistortionDropdown.value = !showTableDistortionDropdown.value
}
const setTableDistortionFilter = (filter) => {
  tableDistortionFilter.value = filter
  showTableDistortionDropdown.value = false
}

// --- Computed KPIs ---
const filteredDistortions = computed(() => {
  if (!allHistory.value.length) return []
  if (kpiDistortionFilter.value === 'All') return allHistory.value
  return allHistory.value.filter(h => h.distortion === kpiDistortionFilter.value)
})

const filteredDeblurs = computed(() => {
  if (!allHistory.value.length) return []
  if (kpiDeblurFilter.value === 'All') return allHistory.value
  return allHistory.value.filter(h => h.status === kpiDeblurFilter.value)
})

const percentageChange = computed(() => {
  if (!allHistory.value.length) return '0%'
  const recent = allHistory.value.slice(0, 10).length
  const previous = allHistory.value.slice(10, 20).length
  if (previous === 0) return '0%'
  const change = ((recent - previous) / previous) * 100
  return `${change.toFixed(1)}%`
})

const percentageIcon = computed(() => {
  if (percentageChange.value.startsWith('-')) return ArrowDown
  if (percentageChange.value === '0%') return Minus
  return ArrowUp
})

const percentageColor = computed(() => {
  if (percentageChange.value.startsWith('-')) return 'text-red-500'
  if (percentageChange.value === '0%') return 'text-gray-500'
  return 'text-green-500'
})

// --- Filtered Table Data ---
const filteredTableHistory = computed(() => {
  return history.value.filter(entry => {
    const matchesSearch =
      searchQuery.value === '' ||
      entry.plate.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
      entry.user.toLowerCase().includes(searchQuery.value.toLowerCase())

    const matchesDistortion =
      tableDistortionFilter.value === 'All' || entry.distortion === tableDistortionFilter.value

    const matchesDate =
      (!startDate.value || entry.date >= startDate.value) &&
      (!endDate.value || entry.date <= endDate.value)

    return matchesSearch && matchesDistortion && matchesDate
  })
})

// --- Actions ---
const goToResult = (id) => {
  router.push({ name: 'ResultPage', params: { id } })
}

const deleteImage = async (id) => {
  // confirm deletion
  if (!confirm('Are you sure you want to delete this record?')) return

  if (deletingIds.value.has(id)) return
  deletingIds.value.add(id)
  try {
    await http.delete(`/images/${id}/`)
    history.value = history.value.filter(entry => entry.id !== id)
    allHistory.value = allHistory.value.filter(entry => entry.id !== id)
    totalCount.value--
    showToast('Image deleted successfully.', 'success')
  } catch (err) {
    console.error('Delete failed', err)
    showToast('Failed to delete image.', 'error')
  } finally {
    deletingIds.value.delete(id)
  }
}
</script>

<style scoped>
@reference "tailwindcss";

.date-input {
  @apply border border-gray-300 rounded-lg px-2 py-1.5 text-xs focus:outline-none focus:ring-1 focus:ring-[#265d9c] transition-shadow duration-200 focus:shadow-md;
}
.icon-btn {
  @apply p-1 rounded transition-colors duration-200 active:scale-90;
}
.dropdown-item {
  @apply block w-full text-left px-3 py-1.5 hover:bg-gray-100 transition-colors duration-150;
}
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.2s ease;
}
.fade-slide-enter-from,
.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}
</style>
