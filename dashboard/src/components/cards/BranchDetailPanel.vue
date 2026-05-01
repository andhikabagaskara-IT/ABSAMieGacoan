<template>
  <div class="card detail-panel">
    <div v-if="!branchName" class="empty-state">
      <Store class="icon-large" />
      <p>Pilih cabang untuk melihat detail performa</p>
    </div>
    
    <div v-else class="panel-content">
      <div class="panel-header">
        <h3 class="branch-title">{{ displayName }}</h3>
        <div class="sentiment-badges">
          <span class="badge badge-positive">{{ positivePct }}% Positif</span>
          <span v-if="branchData.netral" class="badge badge-neutral">{{ neutralPct }}% Netral</span>
          <span class="badge badge-negative">{{ negativePct }}% Negatif</span>
        </div>
      </div>
      
      <div class="panel-body">
        <div class="donut-section">
          <SentimentDonut :positif="branchData.positif || 0" :negatif="branchData.negatif || 0" :netral="branchData.netral || 0" />
        </div>
        
        <div class="aspect-section">
          <h4>Distribusi Aspek</h4>
          <div class="aspect-list">
            <div v-for="[aspect, count] in sortedAspects" :key="aspect" class="aspect-item">
              <div class="aspect-info">
                <span class="aspect-name">{{ getAspectLabel(aspect) }}</span>
                <span class="aspect-count">{{ formatNumber(count) }}</span>
              </div>
              <div class="progress-bar-container">
                <div class="progress-bar" :style="{ width: `${(count / totalAspects) * 100}%` }"></div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Sampel Komentar Positif Dominan -->
        <div class="sample-section">
          <h4 class="section-positive">✅ Komentar Positif Dominan</h4>
          <div v-if="positiveSamples.length === 0" class="no-data">Tidak ada sampel ulasan positif.</div>
          <div class="sample-list">
            <div v-for="(review, index) in positiveSamples" :key="'pos-'+index" class="review-card review-positive">
              <div class="review-header">
                <span class="reviewer">{{ review.nama_pelanggan }}</span>
                <div class="review-meta">
                  <span class="rating">⭐ {{ review.rating }}</span>
                  <span class="badge badge-positive">positif</span>
                </div>
              </div>
              <p class="review-text">"{{ review.teks_komentar }}"</p>
              <div class="review-footer">
                <span class="aspect-tag">{{ getAspectLabel(review.aspek_lda) }}</span>
                <span class="date">{{ review.tanggal_ulasan }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Sampel Komentar Negatif Dominan -->
        <div class="sample-section">
          <h4 class="section-negative">⚠️ Komentar Negatif Dominan</h4>
          <div v-if="negativeSamples.length === 0" class="no-data">Tidak ada sampel ulasan negatif.</div>
          <div class="sample-list">
            <div v-for="(review, index) in negativeSamples" :key="'neg-'+index" class="review-card review-negative">
              <div class="review-header">
                <span class="reviewer">{{ review.nama_pelanggan }}</span>
                <div class="review-meta">
                  <span class="rating">⭐ {{ review.rating }}</span>
                  <span class="badge badge-negative">negatif</span>
                </div>
              </div>
              <p class="review-text">"{{ review.teks_komentar }}"</p>
              <div class="review-footer">
                <span class="aspect-tag">{{ getAspectLabel(review.aspek_lda) }}</span>
                <span class="date">{{ review.tanggal_ulasan }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Store } from 'lucide-vue-next'
import SentimentDonut from '../charts/SentimentDonut.vue'

const props = defineProps({
  branchName: { type: String, default: '' },
  branchData: { type: Object, default: () => ({ positif: 0, negatif: 0, netral: 0 }) },
  aspectData: { type: Object, default: () => ({}) },
  sampleReviews: { type: Array, default: () => [] },
  getAspectLabel: { type: Function, required: true }
})

const displayName = computed(() => {
  if (!props.branchName) return ''
  return props.branchName.replace('Mie Gacoan - ', '').replace('Mie Gacoan ', '')
})

const totalSentiment = computed(() => (props.branchData.positif || 0) + (props.branchData.negatif || 0) + (props.branchData.netral || 0))

const positivePct = computed(() => {
  if (totalSentiment.value === 0) return 0
  return (((props.branchData.positif || 0) / totalSentiment.value) * 100).toFixed(1)
})

const neutralPct = computed(() => {
  if (totalSentiment.value === 0) return 0
  return (((props.branchData.netral || 0) / totalSentiment.value) * 100).toFixed(1)
})

const negativePct = computed(() => {
  if (totalSentiment.value === 0) return 0
  return (((props.branchData.negatif || 0) / totalSentiment.value) * 100).toFixed(1)
})

const totalAspects = computed(() => {
  return Object.values(props.aspectData).reduce((a, b) => a + b, 0)
})

const sortedAspects = computed(() => {
  return Object.entries(props.aspectData).sort((a, b) => b[1] - a[1])
})

// Filter branch reviews and split into 2 positif + 2 negatif samples
const branchReviews = computed(() => {
  return props.sampleReviews.filter(r => r.nama_cabang === props.branchName)
})

const positiveSamples = computed(() => {
  return branchReviews.value
    .filter(r => r.sentimen === 'positif')
    .slice(0, 2) // 2 komentar positif dominan
})

const negativeSamples = computed(() => {
  return branchReviews.value
    .filter(r => r.sentimen === 'negatif')
    .slice(0, 2) // 2 komentar negatif dominan
})

const formatNumber = (num) => {
  return new Intl.NumberFormat('id-ID').format(num)
}
</script>

<style scoped>
.detail-panel {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  min-height: 400px;
  color: var(--text-secondary);
  gap: 1rem;
}

.icon-large {
  width: 48px;
  height: 48px;
  color: var(--border);
}

.panel-content {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  height: 100%;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid var(--border);
  padding-bottom: 1rem;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.branch-title {
  font-size: 1.25rem;
  margin: 0;
}

.sentiment-badges {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.badge-neutral {
  background-color: rgba(245, 158, 11, 0.12);
  color: #D97706;
}

.panel-body {
  display: flex;
  flex-direction: column;
  gap: 2rem;
  flex: 1;
  overflow-y: auto;
}

.donut-section {
  height: 250px;
}

h4 {
  font-size: 1rem;
  margin-bottom: 1rem;
  color: var(--text-primary);
}

.section-positive {
  color: var(--positive, #10B981);
}

.section-negative {
  color: var(--negative, #EF4444);
}

.aspect-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.aspect-info {
  display: flex;
  justify-content: space-between;
  font-size: 0.875rem;
  margin-bottom: 0.25rem;
}

.aspect-name {
  font-weight: 500;
}

.aspect-count {
  color: var(--text-secondary);
}

.progress-bar-container {
  height: 8px;
  background-color: var(--bg-subtle);
  border-radius: 4px;
  overflow: hidden;
}

.progress-bar {
  height: 100%;
  background-color: var(--primary-light);
  border-radius: 4px;
}

.sample-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.review-card {
  background-color: var(--bg-subtle);
  padding: 1rem;
  border-radius: var(--radius-md);
  border: 1px solid var(--border);
  transition: transform 0.15s ease;
}

.review-card:hover {
  transform: translateY(-1px);
}

.review-positive {
  border-left: 3px solid var(--positive, #10B981);
}

.review-negative {
  border-left: 3px solid var(--negative, #EF4444);
}

.review-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 0.5rem;
}

.reviewer {
  font-weight: 600;
  font-size: 0.875rem;
}

.review-meta {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.rating {
  font-size: 0.75rem;
  font-weight: 600;
}

.review-text {
  font-size: 0.875rem;
  color: var(--text-primary);
  margin-bottom: 0.75rem;
  line-height: 1.4;
  font-style: italic;
}

.review-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.75rem;
}

.aspect-tag {
  background-color: rgba(3, 169, 244, 0.1);
  color: var(--primary-dark);
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-weight: 500;
}

.date {
  color: var(--text-secondary);
}

.no-data {
  font-size: 0.85rem;
  color: var(--text-secondary);
  font-style: italic;
  padding: 0.5rem 0;
}
</style>
