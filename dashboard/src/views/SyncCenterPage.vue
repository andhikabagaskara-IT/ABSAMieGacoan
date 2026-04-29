<template>
  <div class="sync-page">
    <div class="section-title">
      <h2>Metode Update Data</h2>
      <p>Pilih cara untuk memperbarui dataset ulasan.</p>
    </div>

    <!-- Manajemen Data -->
    <div class="card management-card">
      <div class="card-header mb-0">
        <Database class="icon text-primary" />
        <h3 class="card-title">Manajemen Data</h3>
      </div>
      <p class="description">Kelola seluruh proses pipeline dari awal hingga akhir.</p>
      
      <div class="management-actions">
        <button class="btn btn-primary" @click="requestAction('restart')">
          <RefreshCw class="icon-small mr-2" />
          Restart Data
        </button>
        <button class="btn btn-outline border-negative text-negative" @click="requestAction('delete')">
          <Trash2 class="icon-small mr-2" />
          Hapus Data
        </button>
      </div>
      <div class="notes-section">
        <p><strong>Note Restart Data:</strong> Akan menjalankan ulang skrip code dan meregenerate seluruh file data dan visualisasi.</p>
        <p><strong>Note Hapus Data:</strong> Akan menghapus seluruh file grafik (.png) tanpa menyentuh data mentah.</p>
      </div>
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

    <!-- Modals -->
    <!-- Export Completion Modal -->
    <div class="modal-overlay" v-if="showExportModal">
      <div class="modal-content card">
        <h3 class="modal-title">Proses Selesai!</h3>
        <p class="modal-body">
          Apakah Anda ingin export otomatis masuk di (dashboard_data.json) yang otomatis menghapus data dashboard_data.json lama dengan yang baru atau anda ingin download secara manual menjadi file .csv?
        </p>
        <div class="modal-actions">
          <button class="btn btn-primary" @click="handleExportChoice('auto')">Generate AUTO</button>
          <button class="btn btn-outline" @click="handleExportChoice('download')">Download</button>
        </div>
      </div>
    </div>

    <!-- Confirm Action Modal -->
    <div class="modal-overlay" v-if="confirmModalData">
      <div class="modal-content card">
        <h3 class="modal-title">{{ confirmModalData.title }}</h3>
        <p class="modal-body">{{ confirmModalData.message }}</p>
        <div class="modal-actions">
          <button class="btn btn-outline" @click="confirmModalData = null">Batal</button>
          <button class="btn btn-primary" @click="executeAction">Yakin</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { Database, RefreshCw, Trash2 } from 'lucide-vue-next'
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
        showExportModal.value = true
      }, 1000)
    }
  }, 1000)
}

const handleUpload = (file) => {
  startSimulation()
}

// Modals State
const showExportModal = ref(false)
const confirmModalData = ref(null)

const requestAction = (type) => {
  if (type === 'restart') {
    confirmModalData.value = {
      type: 'restart',
      title: 'Konfirmasi Restart Data',
      message: 'Apakah Anda yakin ingin menjalankan ulang proses dari tahap Quality Check hingga Export? Seluruh file grafik (.png) di folder results akan dihapus.'
    }
  } else if (type === 'delete') {
    confirmModalData.value = {
      type: 'delete',
      title: 'Konfirmasi Hapus Data',
      message: 'Apakah Anda yakin ingin menghapus seluruh file grafik (.png) di folder results?'
    }
  }
}

const executeAction = () => {
  const type = confirmModalData.value.type
  confirmModalData.value = null
  
  // Simulate process
  if (type === 'restart') {
    startSimulation() // reuse pipeline animation for restart
  } else {
    alert('File grafik berhasil dihapus.')
  }
}

const handleExportChoice = (choice) => {
  showExportModal.value = false
  if (choice === 'auto') {
    alert('Data dashboard_data.json berhasil diperbarui secara otomatis.')
  } else {
    alert('Mendownload file .csv...')
  }
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

/* Management Card */
.management-card {
  margin-bottom: 1rem;
}

.card-header.mb-0 {
  margin-bottom: 0.5rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.card-title {
  margin: 0;
  font-size: 1.125rem;
}

.description {
  font-size: 0.875rem;
  color: var(--text-secondary);
  margin-bottom: 1.5rem;
}

.management-actions {
  display: flex;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.btn {
  display: flex;
  align-items: center;
}

.mr-2 {
  margin-right: 0.5rem;
}

.icon-small {
  width: 18px;
  height: 18px;
}

.border-negative {
  border-color: var(--negative);
}

.text-negative {
  color: var(--negative);
}

.text-negative:hover {
  background-color: rgba(239, 68, 68, 0.1);
}

.notes-section {
  background-color: var(--bg-subtle);
  padding: 1rem;
  border-radius: var(--radius-md);
  border-left: 3px solid var(--primary-light);
  font-size: 0.85rem;
  color: var(--text-secondary);
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.notes-section p {
  margin: 0;
}

.notes-section strong {
  color: var(--text-primary);
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
  
  .management-actions {
    flex-direction: column;
  }
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
}

.modal-content {
  max-width: 500px;
  width: 90%;
  animation: modalPop 0.3s ease;
}

@keyframes modalPop {
  0% { transform: scale(0.9); opacity: 0; }
  100% { transform: scale(1); opacity: 1; }
}

.modal-title {
  margin: 0 0 1rem 0;
  font-size: 1.25rem;
  color: var(--text-primary);
}

.modal-body {
  font-size: 0.95rem;
  color: var(--text-secondary);
  line-height: 1.5;
  margin-bottom: 2rem;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
}
</style>
