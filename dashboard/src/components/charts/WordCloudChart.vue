<template>
  <div class="card word-cloud-container">
    <div class="header">
      <h3 class="card-title">Top Keywords per Aspek</h3>
      <select v-model="selectedTopic" class="input-field select-field">
        <option v-for="(label, key) in aspectMap" :key="key" :value="key">
          {{ label }}
        </option>
      </select>
    </div>
    
    <div class="cloud-wrapper">
      <img 
        :src="`/wordcloud_${selectedTopic.toLowerCase().replace(' ', '_')}.png`" 
        :alt="`Word Cloud ${selectedTopic}`"
        class="wordcloud-image"
        @error="handleImageError"
        v-if="!imageErrorMap[selectedTopic]"
      />
      <div v-else class="cloud-fallback">
        <p>Silakan letakkan gambar <strong>wordcloud_{{ selectedTopic.toLowerCase().replace(' ', '_') }}.png</strong> di folder public.</p>
        <div class="fallback-keywords">
          <span v-for="word in currentWords" :key="word" class="fallback-word">{{ word }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  aspectMap: {
    type: Object,
    required: true
  }
})

const selectedTopic = ref('Topik 1')
const imageErrorMap = ref({})

// Hardcoded dari LDA topics report
const keywordData = {
  'Topik 1': ['enak', 'pedas', 'bumbu', 'mienya', 'nyaman', 'level', 'meresap', 'khas', 'gurih', 'mantap'],
  'Topik 2': ['tempat', 'bersih', 'nyaman', 'makan', 'luas', 'nagih', 'parkir', 'cozy', 'keluarga', 'suasana'],
  'Topik 3': ['layan', 'ramah', 'cepat', 'pesan', 'goreng', 'kecewa', 'antri', 'kasir', 'staf', 'sopan'],
  'Topik 4': ['mie', 'porsi', 'harga', 'cocok', 'nongkrong', 'surabaya', 'terjangkau', 'murah', 'pas', 'banyak']
}

const currentWords = computed(() => {
  return keywordData[selectedTopic.value] || []
})

const handleImageError = () => {
  imageErrorMap.value[selectedTopic.value] = true
}
</script>

<style scoped>
.word-cloud-container {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.card-title {
  font-size: 1rem;
  margin: 0;
  color: var(--text-primary);
}

.select-field {
  width: auto;
  min-width: 180px;
}

.cloud-wrapper {
  flex: 1;
  min-height: 250px;
  background: var(--bg-subtle);
  border-radius: var(--radius-lg);
  border: 1px dashed var(--border);
  position: relative;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
}

.wordcloud-image {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

.cloud-fallback {
  text-align: center;
  color: var(--text-secondary);
}

.cloud-fallback p {
  font-size: 0.875rem;
  margin-bottom: 1rem;
}

.fallback-keywords {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  justify-content: center;
}

.fallback-word {
  background-color: var(--primary-light);
  color: var(--primary-dark);
  padding: 0.25rem 0.5rem;
  border-radius: var(--radius-sm);
  font-size: 0.75rem;
  font-weight: 500;
}
</style>
