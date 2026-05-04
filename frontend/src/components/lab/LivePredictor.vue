<template>
  <div class="card predictor-card">
    <div class="card-header">
      <Sparkles class="icon text-primary" />
      <h3 class="card-title">Live Predictor</h3>
      <span class="beta-badge">BETA</span>
    </div>
    
    <div class="predictor-content">
      <div class="input-section">
        <label>Uji Teks Ulasan:</label>
        <textarea 
          v-model="inputText" 
          class="input-field textarea-field" 
          placeholder="Ketik ulasan di sini... (contoh: 'Mienya keasinan, nunggunya lama banget padahal sepi')"
          rows="4"
        ></textarea>
        <button 
          class="btn btn-primary predict-btn" 
          @click="predict"
          :disabled="!inputText.trim() || isPredicting"
        >
          <Loader2 v-if="isPredicting" class="icon-small spinning mr-2" />
          {{ isPredicting ? 'Memproses...' : 'Prediksi Sentimen & Aspek' }}
        </button>
      </div>
      
      <div class="result-section" v-if="result">
        <h4 class="result-title">Hasil Prediksi (SVM + LDA):</h4>
        
        <div class="result-grid">
          <div class="result-box">
            <span class="box-label">Sentimen</span>
            <div class="box-value sentiment-value" :class="result.sentiment === 'Positif' ? 'text-positive' : 'text-negative'">
              <span class="sentiment-icon">{{ result.sentiment === 'Positif' ? '🟢' : '🔴' }}</span>
              {{ result.sentiment }}
            </div>
            <div class="confidence">Confidence: {{ result.confidence }}%</div>
          </div>
          
          <div class="result-box">
            <span class="box-label">Aspek Terdeteksi</span>
            <div class="box-value aspect-value">
              {{ result.aspects.join(', ') || '-' }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { Sparkles, Loader2 } from 'lucide-vue-next'

import api from '../../services/api'

const inputText = ref('')
const isPredicting = ref(false)
const result = ref(null)

const predict = async () => {
  if (!inputText.value.trim()) return
  
  isPredicting.value = true
  result.value = null
  
  try {
    const response = await api.post('/predict', { text: inputText.value })
    const data = response.data
    
    // Asumsikan model terbaik adalah SVM untuk ditampilkan, namun bisa diganti sesuai data
    const svmPred = data.predictions?.svm
    if (svmPred) {
      result.value = {
        sentiment: svmPred.label === 'positif' ? 'Positif' : (svmPred.label === 'negatif' ? 'Negatif' : 'Netral'),
        confidence: svmPred.confidence ? Math.max(...Object.values(svmPred.confidence)) * 100 : 0,
        aspects: [] // API predict saat ini hanya prediksi sentimen, aspek bisa ditambahkan nanti atau dikosongkan
      }
    } else {
      throw new Error('Gagal memuat hasil prediksi SVM')
    }
  } catch (error) {
    console.error('Prediction error:', error)
    alert(error.response?.data?.error || 'Gagal menghubungi server prediksi.')
  } finally {
    isPredicting.value = false
  }
}
</script>

<style scoped>
.predictor-card {
  display: flex;
  flex-direction: column;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
}

.card-title {
  margin: 0;
  font-size: 1.125rem;
}

.icon {
  width: 20px;
  height: 20px;
}

.beta-badge {
  background-color: var(--accent);
  color: white;
  font-size: 0.65rem;
  font-weight: 700;
  padding: 0.15rem 0.4rem;
  border-radius: 4px;
  margin-left: 0.5rem;
}

.predictor-content {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.input-section {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.input-section label {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--text-secondary);
}

.textarea-field {
  resize: vertical;
  min-height: 100px;
}

.predict-btn {
  align-self: flex-start;
  display: flex;
  align-items: center;
}

.mr-2 {
  margin-right: 0.5rem;
}

.spinning {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  100% { transform: rotate(360deg); }
}

.result-section {
  border-top: 1px solid var(--border);
  padding-top: 1.5rem;
  animation: fadeIn 0.4s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.result-title {
  font-size: 1rem;
  margin-bottom: 1rem;
  color: var(--text-primary);
}

.result-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.result-box {
  background-color: var(--bg-subtle);
  padding: 1rem;
  border-radius: var(--radius-md);
  border: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  text-align: center;
}

.box-label {
  font-size: 0.875rem;
  color: var(--text-secondary);
  font-weight: 500;
}

.box-value {
  font-size: 1.25rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.sentiment-icon {
  font-size: 1rem;
}

.aspect-value {
  color: var(--primary-dark);
}

.confidence {
  font-size: 0.75rem;
  color: var(--text-secondary);
  margin-top: 0.25rem;
}

@media (max-width: 576px) {
  .result-grid {
    grid-template-columns: 1fr;
  }
}
</style>
