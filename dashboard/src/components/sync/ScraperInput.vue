<template>
  <div class="card scraper-card">
    <div class="card-header">
      <Globe class="icon text-primary" />
      <h3 class="card-title">Live Scraper</h3>
    </div>
    
    <p class="description">Tarik ulasan terbaru langsung dari Google Maps.</p>
    
    <div class="input-group">
      <label>URL Google Maps:</label>
      <input 
        type="text" 
        class="input-field" 
        placeholder="https://maps.google.com/?cid=..." 
        v-model="url"
      />
    </div>
    
    <button class="btn btn-primary start-btn" @click="$emit('start')">
      Mulai Scraping
    </button>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { Globe } from 'lucide-vue-next'

const url = ref('')

defineEmits(['start'])
</script>

<style scoped>
.scraper-card {
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

.input-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.input-group label {
  font-size: 0.875rem;
  font-weight: 500;
}

.start-btn {
  margin-top: auto;
  width: 100%;
}
</style>
