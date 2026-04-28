<template>
  <div class="card parameter-card">
    <div class="card-header">
      <Settings class="icon text-primary" />
      <h3 class="card-title">Parameter Scraper</h3>
    </div>
    
    <div class="parameter-grid">
      <div class="form-group">
        <label>Tahun Minimum:</label>
        <select v-model="year" class="input-field">
          <option value="2026">2026</option>
          <option value="2025">2025</option>
          <option value="2024">2024</option>
          <option value="2023">2023</option>
        </select>
      </div>
      
      <div class="form-group">
        <label>Batas Ulasan: <span class="text-primary font-bold">{{ limit }}</span></label>
        <input type="range" v-model="limit" min="100" max="5000" step="100" class="range-slider" />
      </div>
    </div>
    
    <div class="form-group mt-3">
      <label>Target Cabang:</label>
      <div class="branch-checkboxes">
        <label class="checkbox-label" v-for="branch in branchList" :key="branch">
          <input type="checkbox" :value="branch" v-model="selectedBranches" />
          {{ branch.replace('Mie Gacoan - ', '').replace('Mie Gacoan ', '') }}
        </label>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { Settings } from 'lucide-vue-next'
import { useDashboardData } from '../../composables/useDashboardData'

const { branchList } = useDashboardData()

const year = ref('2026')
const limit = ref(2000)
const selectedBranches = ref([])

// Initialize with all branches
if (branchList.value.length > 0) {
  selectedBranches.value = [...branchList.value]
}
</script>

<style scoped>
.parameter-card {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.card-title {
  margin: 0;
  font-size: 1.125rem;
}

.icon {
  width: 20px;
  height: 20px;
}

.parameter-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  font-size: 0.875rem;
  font-weight: 500;
}

.mt-3 {
  margin-top: 1rem;
}

.font-bold {
  font-weight: 700;
}

.range-slider {
  width: 100%;
  accent-color: var(--primary);
}

.branch-checkboxes {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 0.5rem;
  margin-top: 0.5rem;
  max-height: 120px;
  overflow-y: auto;
  padding: 0.5rem;
  background-color: var(--bg-subtle);
  border-radius: var(--radius-md);
  border: 1px solid var(--border);
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  font-weight: 400 !important;
  cursor: pointer;
}

@media (max-width: 576px) {
  .parameter-grid {
    grid-template-columns: 1fr;
  }
}
</style>
