<template>
  <div class="branches-page">
    <div class="page-actions">
      <div class="filter-group">
        <label>Pilih Cabang:</label>
        <select v-model="selectedBranch" class="input-field select-field">
          <option value="">Semua Cabang</option>
          <option v-for="branch in branchList" :key="branch" :value="branch">
            {{ branch.replace('Mie Gacoan - ', '').replace('Mie Gacoan ', '') }}
          </option>
        </select>
      </div>
    </div>

    <!-- Main Comparison Chart -->
    <div class="full-width-chart">
      <SentimentBarChart :branchData="filteredBranchData" />
    </div>

    <!-- Bottom Section: Leaderboard & Detail -->
    <div class="bottom-section">
      <div class="leaderboard-wrapper">
        <BranchLeaderboard 
          :branchData="branchSentiment" 
          :selectedBranch="selectedBranch"
          @select-branch="handleSelectBranch"
        />
      </div>
      
      <div class="detail-wrapper">
        <BranchDetailPanel 
          :branchName="selectedBranch"
          :branchData="selectedBranchData"
          :aspectData="selectedAspectData"
          :sampleReviews="sampleReviews"
          :getAspectLabel="getAspectLabel"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useDashboardData } from '../composables/useDashboardData'
import SentimentBarChart from '../components/charts/SentimentBarChart.vue'
import BranchLeaderboard from '../components/cards/BranchLeaderboard.vue'
import BranchDetailPanel from '../components/cards/BranchDetailPanel.vue'

const { 
  branchSentiment, 
  branchList, 
  branchAspect,
  sampleReviews,
  getAspectLabel
} = useDashboardData()

const selectedBranch = ref('')

const handleSelectBranch = (branchName) => {
  // If clicking the already selected branch, deselect it
  if (selectedBranch.value === branchName) {
    selectedBranch.value = ''
  } else {
    selectedBranch.value = branchName
  }
}

// If a branch is selected, show only that branch in the chart
// Otherwise show all
const filteredBranchData = computed(() => {
  if (!selectedBranch.value) {
    return branchSentiment.value
  }
  
  return {
    [selectedBranch.value]: branchSentiment.value[selectedBranch.value]
  }
})

const selectedBranchData = computed(() => {
  if (!selectedBranch.value) return null
  return branchSentiment.value[selectedBranch.value]
})

const selectedAspectData = computed(() => {
  if (!selectedBranch.value) return null
  return branchAspect.value[selectedBranch.value]
})
</script>

<style scoped>
.branches-page {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.page-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: var(--bg-base);
  padding: 1rem 1.5rem;
  border-radius: var(--radius-lg);
  border: 1px solid var(--border);
  box-shadow: var(--shadow-sm);
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.filter-group label {
  font-weight: 500;
  color: var(--text-secondary);
}

.select-field {
  width: 250px;
}

.full-width-chart {
  height: 400px;
}

.bottom-section {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
}

/* Responsive */
@media (max-width: 1024px) {
  .bottom-section {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 576px) {
  .page-actions {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .select-field {
    width: 100%;
  }
}
</style>
