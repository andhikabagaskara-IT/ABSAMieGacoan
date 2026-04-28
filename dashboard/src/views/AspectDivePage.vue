<template>
  <div class="aspect-page">
    <div class="page-actions">
      <div class="filter-group">
        <label>Filter Cabang:</label>
        <select v-model="selectedBranch" class="input-field select-field">
          <option value="">Semua Cabang</option>
          <option v-for="branch in branchList" :key="branch" :value="branch">
            {{ branch.replace('Mie Gacoan - ', '').replace('Mie Gacoan ', '') }}
          </option>
        </select>
      </div>
    </div>

    <!-- Row 1: Radar & Branch Aspects -->
    <div class="top-row">
      <div class="radar-wrapper">
        <AspectRadarChart :aspectData="filteredAspectData" />
      </div>
      <div class="branch-aspect-wrapper">
        <AspectBranchChart :branchAspectData="filteredBranchAspectData" />
      </div>
    </div>

    <!-- Row 2: Word Cloud & Evaluation -->
    <div class="bottom-row">
      <div class="word-cloud-wrapper">
        <WordCloudChart :aspectMap="ASPECT_LABELS" />
      </div>
      <div class="evaluation-wrapper">
        <DbiEvaluationCard />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useDashboardData } from '../composables/useDashboardData'
import AspectRadarChart from '../components/charts/AspectRadarChart.vue'
import AspectBranchChart from '../components/charts/AspectBranchChart.vue'
import WordCloudChart from '../components/charts/WordCloudChart.vue'
import DbiEvaluationCard from '../components/cards/DbiEvaluationCard.vue'

const { 
  aspectDistribution, 
  branchAspect,
  branchList,
  ASPECT_LABELS
} = useDashboardData()

const selectedBranch = ref('')

const filteredAspectData = computed(() => {
  if (!selectedBranch.value) {
    return aspectDistribution.value
  }
  return branchAspect.value[selectedBranch.value] || {}
})

const filteredBranchAspectData = computed(() => {
  if (!selectedBranch.value) {
    return branchAspect.value
  }
  return {
    [selectedBranch.value]: branchAspect.value[selectedBranch.value]
  }
})
</script>

<style scoped>
.aspect-page {
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

.top-row {
  display: grid;
  grid-template-columns: 1fr 2fr;
  gap: 1.5rem;
  height: 400px;
}

.bottom-row {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 1.5rem;
}

.radar-wrapper, .branch-aspect-wrapper, .word-cloud-wrapper, .evaluation-wrapper {
  height: 100%;
}

/* Responsive */
@media (max-width: 1024px) {
  .top-row, .bottom-row {
    grid-template-columns: 1fr;
    height: auto;
  }
  
  .radar-wrapper {
    height: 350px;
  }
  
  .branch-aspect-wrapper {
    height: 400px;
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
