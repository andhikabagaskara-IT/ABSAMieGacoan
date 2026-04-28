<template>
  <div class="sync-page">
    <div class="section-title">
      <h2>Metode Update Data</h2>
      <p>Pilih cara untuk memperbarui dataset ulasan.</p>
    </div>

    <!-- Row 1: Scraper & Upload -->
    <div class="top-row">
      <div class="scraper-wrapper">
        <ScraperInput @start="startSimulation" />
      </div>
      <div class="upload-wrapper">
        <CsvUploader @upload="handleUpload" />
      </div>
    </div>

    <!-- Row 2: Parameters -->
    <div class="parameter-wrapper">
      <ParameterFilter />
    </div>

    <!-- Row 3: Monitor -->
    <div class="monitor-wrapper">
      <PipelineMonitor 
        :isActive="isProcessing" 
        :currentStage="currentStage"
        :progress="progress"
        :speed="speed"
        :eta="eta"
      />
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import ScraperInput from '../components/sync/ScraperInput.vue'
import CsvUploader from '../components/sync/CsvUploader.vue'
import ParameterFilter from '../components/sync/ParameterFilter.vue'
import PipelineMonitor from '../components/sync/PipelineMonitor.vue'

// Simulation State
const isProcessing = ref(false)
const currentStage = ref('idle')
const progress = ref(0)
const speed = ref(0)
const eta = ref('--:--')

let simInterval = null

const startSimulation = () => {
  if (isProcessing.value) return
  
  isProcessing.value = true
  progress.value = 0
  
  const stages = ['scraping', 'labeling', 'preprocessing', 'classification', 'lda', 'export']
  let stageIdx = 0
  currentStage.value = stages[stageIdx]
  
  // Simulate speed and progress
  simInterval = setInterval(() => {
    // Increase progress randomly
    progress.value += Math.floor(Math.random() * 5) + 1
    
    // Simulate changing speed
    speed.value = Math.floor(Math.random() * 15) + 10
    
    // Calculate dummy ETA
    const remaining = 100 - progress.value
    const secondsLeft = Math.ceil((remaining / speed.value) * 10) // arbitrary multiplier for effect
    const mins = Math.floor(secondsLeft / 60)
    const secs = secondsLeft % 60
    eta.value = `${mins}m ${secs}s`
    
    // Advance stages based on progress
    if (progress.value > 16 && stageIdx === 0) { stageIdx++; currentStage.value = stages[stageIdx] }
    if (progress.value > 33 && stageIdx === 1) { stageIdx++; currentStage.value = stages[stageIdx] }
    if (progress.value > 50 && stageIdx === 2) { stageIdx++; currentStage.value = stages[stageIdx] }
    if (progress.value > 66 && stageIdx === 3) { stageIdx++; currentStage.value = stages[stageIdx] }
    if (progress.value > 83 && stageIdx === 4) { stageIdx++; currentStage.value = stages[stageIdx] }
    
    if (progress.value >= 100) {
      progress.value = 100
      speed.value = 0
      eta.value = 'Selesai'
      currentStage.value = 'completed'
      clearInterval(simInterval)
      setTimeout(() => {
        isProcessing.value = false
        // Option to reset or keep state
      }, 3000)
    }
  }, 1000)
}

const handleUpload = (file) => {
  // Start simulation directly from preprocessing maybe, or just full run
  startSimulation()
}
</script>

<style scoped>
.sync-page {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  max-width: 1000px;
  margin: 0 auto;
}

.section-title h2 {
  margin: 0 0 0.25rem 0;
  font-size: 1.25rem;
  color: var(--text-primary);
}

.section-title p {
  margin: 0;
  font-size: 0.875rem;
  color: var(--text-secondary);
}

.top-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
}

.scraper-wrapper, .upload-wrapper {
  height: 100%;
}

@media (max-width: 768px) {
  .top-row {
    grid-template-columns: 1fr;
  }
}
</style>
