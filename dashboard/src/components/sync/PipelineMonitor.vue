<template>
  <div class="card monitor-card">
    <div class="card-header">
      <Activity class="icon text-primary" />
      <h3 class="card-title">Processing Monitor</h3>
      <div v-if="isActive" class="status-indicator">
        <span class="pulse"></span> Active
      </div>
    </div>

    <div class="pipeline-stages">
      <div 
        v-for="(stage, index) in stages" 
        :key="stage.id"
        class="stage-item"
        :class="{ 
          'is-completed': currentStageIndex > index,
          'is-active': currentStageIndex === index,
          'is-pending': currentStageIndex < index
        }"
      >
        <div class="stage-icon">
          <Check v-if="currentStageIndex > index" class="icon-small" />
          <Loader2 v-else-if="currentStageIndex === index" class="icon-small spinning" />
          <Circle v-else class="icon-small" />
        </div>
        <div class="stage-name">{{ stage.name }}</div>
        <div v-if="index < stages.length - 1" class="stage-connector"></div>
      </div>
    </div>

    <div class="progress-section" v-if="isActive || currentStageIndex > 0">
      <div class="progress-stats">
        <span class="percentage">{{ progress }}%</span>
        <span class="speed">{{ speed }} ulasan/detik</span>
      </div>
      
      <div class="progress-bar-container">
        <div class="progress-bar" :style="{ width: `${progress}%` }"></div>
      </div>
      
      <div class="eta">
        ETA: {{ eta }} tersisa
      </div>
    </div>
    
    <div class="empty-state" v-else>
      <p>Sistem idle. Menunggu perintah sinkronisasi data.</p>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Activity, Check, Circle, Loader2 } from 'lucide-vue-next'

const props = defineProps({
  isActive: { type: Boolean, default: false },
  currentStage: { type: String, default: 'idle' },
  progress: { type: Number, default: 0 },
  speed: { type: Number, default: 0 },
  eta: { type: String, default: '--:--' }
})

const stages = [
  { id: 'scraping', name: 'Scraping' },
  { id: 'labeling', name: 'Labeling' },
  { id: 'preprocessing', name: 'Preprocessing' },
  { id: 'classification', name: 'Classification' },
  { id: 'lda', name: 'LDA' },
  { id: 'export', name: 'Export' }
]

const currentStageIndex = computed(() => {
  if (props.currentStage === 'completed') return stages.length
  if (props.currentStage === 'idle') return -1
  return stages.findIndex(s => s.id === props.currentStage)
})
</script>

<style scoped>
.monitor-card {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.card-title {
  margin: 0;
  font-size: 1.125rem;
}

.icon {
  width: 20px;
  height: 20px;
}

.status-indicator {
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--primary);
  background-color: rgba(3, 169, 244, 0.1);
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
}

.pulse {
  width: 8px;
  height: 8px;
  background-color: var(--primary);
  border-radius: 50%;
  box-shadow: 0 0 0 0 rgba(3, 169, 244, 0.7);
  animation: pulse-animation 1.5s infinite;
}

@keyframes pulse-animation {
  0% { box-shadow: 0 0 0 0 rgba(3, 169, 244, 0.7); }
  70% { box-shadow: 0 0 0 6px rgba(3, 169, 244, 0); }
  100% { box-shadow: 0 0 0 0 rgba(3, 169, 244, 0); }
}

.pipeline-stages {
  display: flex;
  justify-content: space-between;
  position: relative;
  overflow-x: auto;
  padding-bottom: 0.5rem;
}

.stage-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  position: relative;
  flex: 1;
  min-width: 80px;
}

.stage-icon {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--bg-subtle);
  color: var(--text-secondary);
  z-index: 2;
}

.icon-small {
  width: 14px;
  height: 14px;
}

.spinning {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  100% { transform: rotate(360deg); }
}

.stage-name {
  font-size: 0.75rem;
  font-weight: 500;
  color: var(--text-secondary);
  text-align: center;
}

.stage-connector {
  position: absolute;
  top: 12px;
  left: 50%;
  width: 100%;
  height: 2px;
  background-color: var(--border);
  z-index: 1;
}

/* States */
.is-completed .stage-icon {
  background-color: var(--primary);
  color: white;
}
.is-completed .stage-name {
  color: var(--text-primary);
}
.is-completed .stage-connector {
  background-color: var(--primary);
}

.is-active .stage-icon {
  background-color: var(--accent);
  color: white;
}
.is-active .stage-name {
  color: var(--accent);
  font-weight: 600;
}

.progress-section {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  background-color: var(--bg-subtle);
  padding: 1.5rem;
  border-radius: var(--radius-md);
  border: 1px solid var(--border);
}

.progress-stats {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
}

.percentage {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--primary-dark);
  line-height: 1;
}

.speed {
  font-size: 0.875rem;
  color: var(--text-secondary);
}

.progress-bar-container {
  height: 8px;
  background-color: var(--border);
  border-radius: 4px;
  overflow: hidden;
}

.progress-bar {
  height: 100%;
  background-color: var(--primary);
  border-radius: 4px;
  transition: width 0.3s ease;
  background-image: linear-gradient(
    45deg,
    rgba(255, 255, 255, 0.15) 25%,
    transparent 25%,
    transparent 50%,
    rgba(255, 255, 255, 0.15) 50%,
    rgba(255, 255, 255, 0.15) 75%,
    transparent 75%,
    transparent
  );
  background-size: 1rem 1rem;
  animation: progress-stripes 1s linear infinite;
}

@keyframes progress-stripes {
  from { background-position: 1rem 0; }
  to { background-position: 0 0; }
}

.eta {
  font-size: 0.75rem;
  color: var(--text-secondary);
  text-align: right;
}

.empty-state {
  text-align: center;
  padding: 2rem;
  color: var(--text-secondary);
  font-size: 0.875rem;
  background-color: var(--bg-subtle);
  border-radius: var(--radius-md);
  border: 1px dashed var(--border);
}
</style>
