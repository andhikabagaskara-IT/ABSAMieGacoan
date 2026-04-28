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
      <div 
        v-for="(word, index) in currentWords" 
        :key="word" 
        class="cloud-word"
        :style="getWordStyle(index, currentWords.length)"
      >
        {{ word }}
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

// Hardcoded from LDA topics report
const keywordData = {
  'Topik 1': ['enak', 'pedas', 'bumbu', 'mienya', 'nyaman', 'level', 'meresap', 'khas', 'gurih', 'mantap'],
  'Topik 2': ['tempat', 'bersih', 'nyaman', 'makan', 'luas', 'nagih', 'parkir', 'cozy', 'keluarga', 'suasana'],
  'Topik 3': ['layan', 'ramah', 'cepat', 'pesan', 'goreng', 'kecewa', 'antri', 'kasir', 'staf', 'sopan'],
  'Topik 4': ['mie', 'porsi', 'harga', 'cocok', 'nongkrong', 'surabaya', 'terjangkau', 'murah', 'pas', 'banyak'],
  'Topik 5': ['makan', 'konsisten', 'bintang', 'kecewa', 'enak', 'cepat', 'rekomendasi', 'langganan', 'kualitas', 'puas']
}

const currentWords = computed(() => {
  return keywordData[selectedTopic.value] || []
})

// Generate random but deterministic style based on index
const getWordStyle = (index, total) => {
  // Largest font for index 0, smallest for last
  const sizeRatio = 1 - (index / total)
  const minSize = 14
  const maxSize = 36
  const fontSize = minSize + (sizeRatio * (maxSize - minSize))
  
  // Mix colors
  const colors = [
    'var(--primary)', 
    'var(--accent)', 
    'var(--primary-dark)', 
    '#64748B', 
    '#10B981', 
    '#8B5CF6'
  ]
  const color = colors[index % colors.length]
  
  // Random margin to make it look scattered
  const ml = Math.random() * 20
  const mt = Math.random() * 10
  
  return {
    fontSize: `${fontSize}px`,
    color,
    marginLeft: `${ml}px`,
    marginTop: `${mt}px`,
    fontWeight: index < 3 ? 700 : (index < 6 ? 600 : 400),
    opacity: 0.8 + (sizeRatio * 0.2)
  }
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
  display: flex;
  flex-wrap: wrap;
  align-content: center;
  justify-content: center;
  gap: 1rem;
  padding: 1rem;
  min-height: 250px;
  background-color: var(--bg-subtle);
  border-radius: var(--radius-md);
  border: 1px dashed var(--border);
}

.cloud-word {
  line-height: 1;
  transition: transform 0.2s ease;
  cursor: default;
}

.cloud-word:hover {
  transform: scale(1.1);
  z-index: 10;
}
</style>
