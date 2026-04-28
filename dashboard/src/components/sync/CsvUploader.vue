<template>
  <div class="card uploader-card">
    <div class="card-header">
      <Upload class="icon text-primary" />
      <h3 class="card-title">Upload CSV</h3>
    </div>
    
    <p class="description">Upload data ulasan manual (format CSV).</p>
    
    <div 
      class="drop-zone" 
      :class="{ 'is-dragover': isDragover }"
      @dragover.prevent="isDragover = true"
      @dragleave.prevent="isDragover = false"
      @drop.prevent="handleDrop"
    >
      <FileText class="icon-large text-secondary" />
      <p class="drop-text">Drag & drop file CSV di sini, atau</p>
      <button class="btn btn-outline btn-sm" @click="$refs.fileInput.click()">Pilih File</button>
      <input type="file" ref="fileInput" class="hidden-input" accept=".csv" @change="handleFileSelect" />
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { Upload, FileText } from 'lucide-vue-next'

const isDragover = ref(false)
const fileInput = ref(null)

const emit = defineEmits(['upload'])

const handleDrop = (e) => {
  isDragover.value = false
  const files = e.dataTransfer.files
  if (files.length > 0) {
    processFile(files[0])
  }
}

const handleFileSelect = (e) => {
  const files = e.target.files
  if (files.length > 0) {
    processFile(files[0])
  }
}

const processFile = (file) => {
  if (file.type === 'text/csv' || file.name.endsWith('.csv')) {
    emit('upload', file)
  } else {
    alert('Hanya file CSV yang diperbolehkan.')
  }
}
</script>

<style scoped>
.uploader-card {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  height: 100%;
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

.description {
  font-size: 0.875rem;
  color: var(--text-secondary);
}

.drop-zone {
  flex: 1;
  border: 2px dashed var(--accent-light);
  border-radius: var(--radius-md);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  padding: 1.5rem;
  background-color: rgba(244, 143, 177, 0.05);
  transition: all var(--transition-fast);
}

.drop-zone.is-dragover {
  background-color: rgba(244, 143, 177, 0.15);
  border-color: var(--accent);
}

.icon-large {
  width: 32px;
  height: 32px;
  opacity: 0.5;
}

.drop-text {
  font-size: 0.875rem;
  color: var(--text-secondary);
  text-align: center;
}

.hidden-input {
  display: none;
}

.btn-sm {
  padding: 0.25rem 0.75rem;
  font-size: 0.875rem;
}
</style>
