<template>
  <div class="card model-card" :class="{ 'is-best': isBest }">
    <div class="card-header">
      <div class="title-group">
        <Cpu class="icon text-primary" v-if="!isBest" />
        <Zap class="icon text-accent" v-else />
        <h3 class="card-title">{{ title }}</h3>
      </div>
      <div class="badge" :class="isBest ? 'badge-accent' : 'badge-primary'">
        {{ accuracy }}% Akurasi
      </div>
    </div>
    
    <div class="model-content">
      <div class="metrics">
        <div class="metric-item">
          <span class="label">Presisi</span>
          <span class="value">{{ precision }}%</span>
        </div>
        <div class="metric-item">
          <span class="label">Recall</span>
          <span class="value">{{ recall }}%</span>
        </div>
        <div class="metric-item">
          <span class="label">F1-Score</span>
          <span class="value">{{ f1Score }}%</span>
        </div>
      </div>
      
      <div class="cm-wrapper">
        <h4 class="cm-title">Confusion Matrix</h4>
        <img :src="cmImage" :alt="`Confusion Matrix ${title}`" class="cm-image" @error="imageError = true" v-if="!imageError" />
        <div v-else class="cm-fallback">
          <span class="fallback-text">Matrix Image Not Available</span>
        </div>
      </div>
    </div>
    
    <div class="best-indicator" v-if="isBest">
      Model Terpilih
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { Cpu, Zap } from 'lucide-vue-next'

const props = defineProps({
  title: String,
  accuracy: Number,
  precision: Number,
  recall: Number,
  f1Score: Number,
  cmImage: String,
  isBest: { type: Boolean, default: false }
})

const imageError = ref(false)
</script>

<style scoped>
.model-card {
  display: flex;
  flex-direction: column;
  position: relative;
  overflow: hidden;
  height: 100%;
}

.model-card.is-best {
  border-color: var(--accent);
  box-shadow: 0 4px 20px rgba(236, 64, 122, 0.15);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.title-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.card-title {
  margin: 0;
  font-size: 1.125rem;
}

.badge {
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-weight: 600;
  font-size: 0.875rem;
}

.badge-primary {
  background-color: rgba(3, 169, 244, 0.1);
  color: var(--primary-dark);
}

.badge-accent {
  background-color: rgba(236, 64, 122, 0.1);
  color: var(--accent);
}

.model-content {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  flex: 1;
}

.metrics {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
  background-color: var(--bg-subtle);
  padding: 1rem;
  border-radius: var(--radius-md);
  border: 1px solid var(--border);
}

.metric-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.25rem;
}

.metric-item .label {
  font-size: 0.75rem;
  color: var(--text-secondary);
  font-weight: 500;
}

.metric-item .value {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--text-primary);
}

.cm-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.cm-title {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--text-secondary);
  margin: 0;
}

.cm-image {
  width: 100%;
  height: auto;
  border-radius: var(--radius-md);
  border: 1px solid var(--border);
  object-fit: contain;
}

.cm-fallback {
  width: 100%;
  aspect-ratio: 4/3;
  background-color: var(--bg-subtle);
  border-radius: var(--radius-md);
  border: 1px dashed var(--border);
  display: flex;
  align-items: center;
  justify-content: center;
}

.fallback-text {
  font-size: 0.875rem;
  color: var(--text-secondary);
}

.best-indicator {
  position: absolute;
  top: 1rem;
  right: -2.5rem;
  background-color: var(--accent);
  color: white;
  font-size: 0.65rem;
  font-weight: 700;
  padding: 0.25rem 3rem;
  transform: rotate(45deg);
  text-transform: uppercase;
  letter-spacing: 1px;
}
</style>
