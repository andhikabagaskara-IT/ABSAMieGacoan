<template>
  <div class="explorer-page">
    <div class="section-title">
      <h2>📋 Data Explorer</h2>
      <p>Telusuri {{ totalFiltered.toLocaleString() }} ulasan dari {{ totalAll.toLocaleString() }} data yang tersedia.</p>
    </div>

    <!-- Search & Filter Bar -->
    <div class="card filter-bar">
      <div class="search-row">
        <div class="search-wrapper">
          <Search class="search-icon" />
          <input 
            type="text" 
            v-model="searchQuery" 
            placeholder="Cari ulasan..." 
            class="input-field search-input"
            @input="onFilterChange"
          />
          <button v-if="searchQuery" class="clear-btn" @click="searchQuery = ''; onFilterChange()">
            <X class="clear-icon" />
          </button>
        </div>
      </div>
      <div class="filter-row">
        <div class="filter-group">
          <label>Cabang</label>
          <select v-model="filterBranch" class="input-field select-field" @change="onFilterChange">
            <option value="">Semua Cabang</option>
            <option v-for="branch in branches" :key="branch" :value="branch">{{ shortBranch(branch) }}</option>
          </select>
        </div>
        <div class="filter-group">
          <label>Sentimen</label>
          <select v-model="filterSentiment" class="input-field select-field" @change="onFilterChange">
            <option value="">Semua</option>
            <option value="positif">Positif</option>
            <option value="negatif">Negatif</option>
            <option value="netral">Netral</option>
          </select>
        </div>
        <div class="filter-group">
          <label>Aspek</label>
          <select v-model="filterAspect" class="input-field select-field" @change="onFilterChange">
            <option value="">Semua Aspek</option>
            <option v-for="(label, key) in ASPECT_LABELS" :key="key" :value="key">{{ label }}</option>
          </select>
        </div>
        <div class="filter-group">
          <label>Rating</label>
          <select v-model="filterRating" class="input-field select-field" @change="onFilterChange">
            <option value="">Semua</option>
            <option value="5">⭐⭐⭐⭐⭐</option>
            <option value="4">⭐⭐⭐⭐</option>
            <option value="3">⭐⭐⭐</option>
            <option value="2">⭐⭐</option>
            <option value="1">⭐</option>
          </select>
        </div>
        <button class="btn btn-outline reset-btn" @click="resetFilters">
          <RotateCcw class="btn-icon" />
          Reset
        </button>
      </div>
    </div>

    <!-- Data Table -->
    <div class="card table-container">
      <div class="table-header-bar">
        <span class="result-count">
          Menampilkan {{ paginatedData.length }} dari {{ totalFiltered.toLocaleString() }} ulasan
        </span>
        <button class="btn btn-primary export-btn" @click="exportCsv">
          <Download class="btn-icon" />
          Export CSV
        </button>
      </div>

      <div class="table-wrapper">
        <table class="data-table">
          <thead>
            <tr>
              <th class="col-num">#</th>
              <th class="col-branch sortable" @click="toggleSort('nama_cabang')">
                Cabang
                <span class="sort-icon" v-if="sortKey === 'nama_cabang'">{{ sortDir === 'asc' ? '▲' : '▼' }}</span>
              </th>
              <th class="col-customer">Pelanggan</th>
              <th class="col-rating sortable" @click="toggleSort('rating')">
                ⭐
                <span class="sort-icon" v-if="sortKey === 'rating'">{{ sortDir === 'asc' ? '▲' : '▼' }}</span>
              </th>
              <th class="col-review">Ulasan</th>
              <th class="col-sentiment sortable" @click="toggleSort('sentimen')">
                Sentimen
                <span class="sort-icon" v-if="sortKey === 'sentimen'">{{ sortDir === 'asc' ? '▲' : '▼' }}</span>
              </th>
              <th class="col-aspect">Aspek</th>
            </tr>
          </thead>
          <tbody>
            <tr 
              v-for="(review, index) in paginatedData" 
              :key="index"
              class="data-row"
              :class="{ expanded: expandedRow === index }"
              @click="toggleExpand(index)"
            >
              <td class="col-num">{{ (currentPage - 1) * perPage + index + 1 }}</td>
              <td class="col-branch">
                <span class="branch-tag">{{ shortBranch(review.nama_cabang) }}</span>
              </td>
              <td class="col-customer">{{ review.nama_pelanggan }}</td>
              <td class="col-rating">
                <span class="rating-badge" :class="'rating-' + review.rating">{{ review.rating }}</span>
              </td>
              <td class="col-review">
                <span v-if="expandedRow !== index" class="review-text truncated">{{ truncate(review.teks_komentar, 60) }}</span>
                <span v-else class="review-text full">{{ review.teks_komentar }}</span>
              </td>
              <td class="col-sentiment">
                <span class="sentiment-label" :class="'sentiment-' + review.sentimen">
                  {{ capitalize(review.sentimen) }}
                </span>
              </td>
              <td class="col-aspect">
                <span class="aspect-tag-small" :title="getAspectLabel(review.aspek_lda)">
                  {{ getAspectLabel(review.aspek_lda) }}
                </span>
              </td>
            </tr>
            <tr v-if="paginatedData.length === 0">
              <td colspan="7" class="empty-state">
                <SearchX class="empty-icon" />
                <p>Tidak ada ulasan yang cocok dengan filter.</p>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination -->
      <div class="pagination" v-if="totalPages > 1">
        <button class="page-btn" :disabled="currentPage === 1" @click="currentPage--">
          <ChevronLeft class="page-icon" /> Prev
        </button>
        <div class="page-numbers">
          <button 
            v-for="page in visiblePages" 
            :key="page"
            class="page-num"
            :class="{ active: page === currentPage, dots: page === '...' }"
            @click="page !== '...' && (currentPage = page)"
            :disabled="page === '...'"
          >
            {{ page }}
          </button>
        </div>
        <button class="page-btn" :disabled="currentPage === totalPages" @click="currentPage++">
          Next <ChevronRight class="page-icon" />
        </button>
        <span class="page-info">{{ perPage }}/halaman</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Search, X, Download, ChevronLeft, ChevronRight, RotateCcw, SearchX } from 'lucide-vue-next'
import { useDashboardData } from '../composables/useDashboardData'

const { sampleReviews, branchList, getAspectLabel, ASPECT_LABELS } = useDashboardData()

const searchQuery = ref('')
const filterBranch = ref('')
const filterSentiment = ref('')
const filterAspect = ref('')
const filterRating = ref('')
const sortKey = ref('')
const sortDir = ref('asc')
const currentPage = ref(1)
const perPage = 25
const expandedRow = ref(null)

const branches = computed(() => branchList.value)
const totalAll = computed(() => sampleReviews.value.length)

const filteredData = computed(() => {
  let data = [...sampleReviews.value]

  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    data = data.filter(r => r.teks_komentar?.toLowerCase().includes(q) || r.nama_pelanggan?.toLowerCase().includes(q))
  }
  if (filterBranch.value) data = data.filter(r => r.nama_cabang === filterBranch.value)
  if (filterSentiment.value) data = data.filter(r => r.sentimen === filterSentiment.value)
  if (filterAspect.value) data = data.filter(r => r.aspek_lda === filterAspect.value)
  if (filterRating.value) data = data.filter(r => String(r.rating) === filterRating.value)

  if (sortKey.value) {
    data.sort((a, b) => {
      const va = a[sortKey.value]
      const vb = b[sortKey.value]
      const cmp = typeof va === 'number' ? va - vb : String(va).localeCompare(String(vb))
      return sortDir.value === 'asc' ? cmp : -cmp
    })
  }

  return data
})

const totalFiltered = computed(() => filteredData.value.length)
const totalPages = computed(() => Math.ceil(totalFiltered.value / perPage))

const paginatedData = computed(() => {
  const start = (currentPage.value - 1) * perPage
  return filteredData.value.slice(start, start + perPage)
})

const visiblePages = computed(() => {
  const pages = []
  const total = totalPages.value
  const current = currentPage.value

  if (total <= 7) {
    for (let i = 1; i <= total; i++) pages.push(i)
  } else {
    pages.push(1)
    if (current > 3) pages.push('...')
    for (let i = Math.max(2, current - 1); i <= Math.min(total - 1, current + 1); i++) pages.push(i)
    if (current < total - 2) pages.push('...')
    pages.push(total)
  }
  return pages
})

const onFilterChange = () => { currentPage.value = 1; expandedRow.value = null }
const resetFilters = () => {
  searchQuery.value = ''; filterBranch.value = ''; filterSentiment.value = ''
  filterAspect.value = ''; filterRating.value = ''; sortKey.value = ''; currentPage.value = 1
}
const toggleSort = (key) => {
  if (sortKey.value === key) { sortDir.value = sortDir.value === 'asc' ? 'desc' : 'asc' }
  else { sortKey.value = key; sortDir.value = 'asc' }
}
const toggleExpand = (index) => { expandedRow.value = expandedRow.value === index ? null : index }
const truncate = (text, len) => text && text.length > len ? text.substring(0, len) + '...' : text
const shortBranch = (name) => name?.replace('Mie Gacoan - ', '').replace('Mie Gacoan ', '')
const capitalize = (str) => str ? str.charAt(0).toUpperCase() + str.slice(1) : ''

const exportCsv = () => {
  const headers = ['Cabang', 'Pelanggan', 'Tanggal', 'Rating', 'Ulasan', 'Sentimen', 'Aspek']
  const rows = filteredData.value.map(r => [
    r.nama_cabang, r.nama_pelanggan, r.tanggal_ulasan, r.rating,
    `"${(r.teks_komentar || '').replace(/"/g, '""')}"`, r.sentimen, getAspectLabel(r.aspek_lda)
  ])
  const csv = [headers.join(','), ...rows.map(r => r.join(','))].join('\n')
  const blob = new Blob(['\ufeff' + csv], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = 'ulasan_mie_gacoan_export.csv'
  link.click()
}
</script>

<style scoped>
.explorer-page {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  max-width: 1200px;
  margin: 0 auto;
}

.section-title h2 { margin: 0 0 0.25rem 0; font-size: 1.25rem; }
.section-title p { margin: 0; font-size: 0.875rem; color: var(--text-secondary); }

/* Filter Bar */
.filter-bar { display: flex; flex-direction: column; gap: 1rem; }

.search-row { position: relative; }
.search-wrapper { position: relative; display: flex; align-items: center; }
.search-icon { position: absolute; left: 0.75rem; width: 18px; height: 18px; color: var(--text-secondary); pointer-events: none; }
.search-input { padding-left: 2.5rem !important; padding-right: 2.5rem !important; }
.clear-btn { position: absolute; right: 0.5rem; background: none; border: none; padding: 0.25rem; border-radius: 50%; color: var(--text-secondary); }
.clear-btn:hover { background: var(--bg-subtle); color: var(--text-primary); }
.clear-icon { width: 16px; height: 16px; }

.filter-row { display: flex; gap: 0.75rem; flex-wrap: wrap; align-items: flex-end; }
.filter-group { display: flex; flex-direction: column; gap: 0.25rem; min-width: 140px; flex: 1; }
.filter-group label { font-size: 0.7rem; font-weight: 600; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.5px; }
.select-field { font-size: 0.85rem; }
.reset-btn { gap: 0.4rem; font-size: 0.8rem; height: fit-content; white-space: nowrap; }
.btn-icon { width: 14px; height: 14px; }

/* Table */
.table-container { padding: 0; overflow: hidden; }
.table-header-bar { display: flex; justify-content: space-between; align-items: center; padding: 1rem 1.5rem; border-bottom: 1px solid var(--border); }
.result-count { font-size: 0.8rem; color: var(--text-secondary); }
.export-btn { font-size: 0.8rem; gap: 0.4rem; padding: 0.4rem 0.75rem; }

.table-wrapper { overflow-x: auto; }

.data-table { width: 100%; border-collapse: collapse; font-size: 0.825rem; }
.data-table thead { background: var(--bg-subtle); position: sticky; top: 0; z-index: 1; }
.data-table th { padding: 0.75rem 0.75rem; text-align: left; font-weight: 600; font-size: 0.75rem; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.5px; white-space: nowrap; border-bottom: 2px solid var(--border); }
.data-table td { padding: 0.65rem 0.75rem; border-bottom: 1px solid var(--border); vertical-align: top; }

.sortable { cursor: pointer; user-select: none; }
.sortable:hover { color: var(--primary); }
.sort-icon { font-size: 0.65rem; margin-left: 0.25rem; }

.col-num { width: 40px; text-align: center !important; color: var(--text-secondary); font-size: 0.75rem; }
.col-branch { min-width: 100px; }
.col-customer { min-width: 100px; max-width: 130px; }
.col-rating { width: 40px; text-align: center !important; }
.col-review { min-width: 200px; }
.col-sentiment { width: 80px; text-align: center !important; }
.col-aspect { width: 80px; text-align: center !important; }

/* Badges */
.branch-tag { font-size: 0.75rem; font-weight: 500; color: var(--primary-dark); background: rgba(3, 169, 244, 0.08); padding: 0.15rem 0.5rem; border-radius: 4px; white-space: nowrap; }

.rating-badge { display: inline-flex; align-items: center; justify-content: center; width: 24px; height: 24px; border-radius: 50%; font-size: 0.7rem; font-weight: 700; }
.rating-5 { background: rgba(16, 185, 129, 0.15); color: var(--positive); }
.rating-4 { background: rgba(3, 169, 244, 0.15); color: var(--primary); }
.rating-3 { background: rgba(245, 158, 11, 0.15); color: #D97706; }
.rating-2 { background: rgba(245, 158, 11, 0.15); color: #D97706; }
.rating-1 { background: rgba(239, 68, 68, 0.15); color: var(--negative); }

/* Sentiment Label — text only, no emoticons */
.sentiment-label {
  display: inline-block;
  font-size: 0.75rem;
  font-weight: 600;
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
  text-transform: capitalize;
}
.sentiment-positif {
  background: rgba(16, 185, 129, 0.12);
  color: var(--positive, #10B981);
}
.sentiment-negatif {
  background: rgba(239, 68, 68, 0.12);
  color: var(--negative, #EF4444);
}
.sentiment-netral {
  background: rgba(245, 158, 11, 0.12);
  color: #D97706;
}

.aspect-tag-small {
  font-size: 0.7rem;
  background-color: rgba(3, 169, 244, 0.08);
  color: var(--primary-dark);
  padding: 0.15rem 0.4rem;
  border-radius: 4px;
  white-space: nowrap;
}

.review-text { line-height: 1.5; }
.review-text.truncated { color: var(--text-secondary); }
.review-text.full { color: var(--text-primary); font-weight: 400; }

.data-row { cursor: pointer; transition: background 0.15s; }
.data-row:hover { background: rgba(3, 169, 244, 0.03); }
.data-row.expanded { background: rgba(3, 169, 244, 0.05); }

.empty-state { text-align: center; padding: 3rem !important; color: var(--text-secondary); }
.empty-icon { width: 32px; height: 32px; margin-bottom: 0.5rem; opacity: 0.4; }

/* Pagination */
.pagination { display: flex; align-items: center; justify-content: center; gap: 0.5rem; padding: 1rem 1.5rem; border-top: 1px solid var(--border); flex-wrap: wrap; }

.page-btn { display: flex; align-items: center; gap: 0.25rem; padding: 0.4rem 0.75rem; background: var(--bg-base); border: 1px solid var(--border); border-radius: var(--radius-md); font-size: 0.8rem; color: var(--text-primary); cursor: pointer; transition: all 0.15s; }
.page-btn:hover:not(:disabled) { border-color: var(--primary); color: var(--primary); }
.page-btn:disabled { opacity: 0.4; cursor: not-allowed; }
.page-icon { width: 14px; height: 14px; }

.page-numbers { display: flex; gap: 0.25rem; }
.page-num { width: 32px; height: 32px; display: flex; align-items: center; justify-content: center; border: 1px solid var(--border); border-radius: var(--radius-md); background: var(--bg-base); font-size: 0.8rem; cursor: pointer; transition: all 0.15s; }
.page-num:hover:not(.active):not(.dots) { border-color: var(--primary); color: var(--primary); }
.page-num.active { background: var(--primary); color: white; border-color: var(--primary); }
.page-num.dots { border: none; cursor: default; }

.page-info { font-size: 0.75rem; color: var(--text-secondary); margin-left: 0.5rem; }

@media (max-width: 768px) {
  .filter-row { flex-direction: column; }
  .filter-group { min-width: 100%; }
  .col-customer, .col-aspect { display: none; }
}
</style>
