<template>
  <div class="card leaderboard-container">
    <h3 class="card-title">Branch Leaderboard</h3>
    
    <div class="leaderboard-grid">
      <!-- Top Branches -->
      <div class="leaderboard-section">
        <h4 class="section-title text-positive">
          <Trophy class="icon-small" /> Terbaik (Positif Tertinggi)
        </h4>
        <div class="branch-list">
          <div 
            v-for="(branch, index) in topBranches" 
            :key="branch.name" 
            class="branch-item"
            :class="{ 'is-selected': selectedBranch === branch.name }"
            @click="$emit('select-branch', branch.name)"
          >
            <div class="rank" :class="`rank-${index + 1}`">{{ index + 1 }}</div>
            <div class="branch-info">
              <div class="branch-name">{{ branch.displayName }}</div>
              <div class="branch-bar-container">
                <div class="branch-bar positive-bg" :style="{ width: `${branch.positivePct}%` }"></div>
              </div>
            </div>
            <div class="branch-score text-positive">{{ branch.positivePct }}%</div>
          </div>
        </div>
      </div>
      
      <!-- Bottom Branches -->
      <div class="leaderboard-section">
        <h4 class="section-title text-negative">
          <AlertTriangle class="icon-small" /> Perlu Evaluasi (Negatif Tertinggi)
        </h4>
        <div class="branch-list">
          <div 
            v-for="(branch, index) in bottomBranches" 
            :key="branch.name" 
            class="branch-item"
            :class="{ 'is-selected': selectedBranch === branch.name }"
            @click="$emit('select-branch', branch.name)"
          >
            <div class="rank rank-warn">{{ index + 1 }}</div>
            <div class="branch-info">
              <div class="branch-name">{{ branch.displayName }}</div>
              <div class="branch-bar-container">
                <div class="branch-bar negative-bg" :style="{ width: `${branch.negativePct}%` }"></div>
              </div>
            </div>
            <div class="branch-score text-negative">{{ branch.negativePct }}%</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Trophy, AlertTriangle } from 'lucide-vue-next'

const props = defineProps({
  branchData: {
    type: Object,
    required: true
  },
  selectedBranch: {
    type: String,
    default: ''
  }
})

defineEmits(['select-branch'])

const processedBranches = computed(() => {
  return Object.keys(props.branchData).map(name => {
    const data = props.branchData[name]
    const total = (data.positif || 0) + (data.negatif || 0) + (data.netral || 0)
    const positivePct = total > 0 ? (((data.positif || 0) / total) * 100).toFixed(1) : 0
    const negativePct = total > 0 ? (((data.negatif || 0) / total) * 100).toFixed(1) : 0
    
    return {
      name,
      displayName: name.replace('Mie Gacoan - ', '').replace('Mie Gacoan ', ''),
      positif: data.positif || 0,
      negatif: data.negatif || 0,
      netral: data.netral || 0,
      total,
      positivePct: parseFloat(positivePct),
      negativePct: parseFloat(negativePct)
    }
  })
})

const topBranches = computed(() => {
  return [...processedBranches.value]
    .sort((a, b) => b.positivePct - a.positivePct)
    .slice(0, 5) // Top 5
})

const bottomBranches = computed(() => {
  return [...processedBranches.value]
    .sort((a, b) => b.negativePct - a.negativePct)
    .slice(0, 5) // Bottom 5
})
</script>

<style scoped>
.leaderboard-container {
  padding: 1.5rem;
}

.card-title {
  font-size: 1rem;
  margin-bottom: 1.5rem;
  color: var(--text-primary);
}

.leaderboard-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
}

@media (max-width: 768px) {
  .leaderboard-grid {
    grid-template-columns: 1fr;
  }
}

.section-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  margin-bottom: 1rem;
}

.icon-small {
  width: 16px;
  height: 16px;
}

.branch-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.branch-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.5rem;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.branch-item:hover {
  background-color: var(--bg-subtle);
}

.branch-item.is-selected {
  background-color: rgba(3, 169, 244, 0.1);
  border: 1px solid var(--primary-light);
}

.rank {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  font-weight: 600;
  background-color: var(--bg-subtle);
  color: var(--text-secondary);
}

.rank-1 { background-color: rgba(251, 191, 36, 0.2); color: #D97706; }
.rank-2 { background-color: rgba(156, 163, 175, 0.2); color: #4B5563; }
.rank-3 { background-color: rgba(180, 83, 9, 0.2); color: #92400E; }
.rank-warn { background-color: rgba(239, 68, 68, 0.1); color: var(--negative); }

.branch-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.branch-name {
  font-size: 0.875rem;
  font-weight: 500;
}

.branch-bar-container {
  height: 6px;
  background-color: var(--bg-subtle);
  border-radius: 3px;
  overflow: hidden;
}

.branch-bar {
  height: 100%;
  border-radius: 3px;
}

.positive-bg { background-color: var(--primary); }
.negative-bg { background-color: var(--accent); }

.branch-score {
  font-size: 0.875rem;
  font-weight: 600;
  width: 45px;
  text-align: right;
}
</style>
