<template>
  <div class="lab-page">
    <div class="section-title">
      <h2>⚡ Pengujian Model Sentimen</h2>
      <p>Bandingkan performa algoritma klasifikasi dan lihat dampak SMOTE pada data imbalance.</p>
    </div>

    <!-- Row 1: Models Comparison (Real Data) -->
    <div class="models-grid">
      <div class="model-wrapper">
        <ModelCard 
          title="Naive Bayes"
          :accuracy="98.82"
          :precision="99.07"
          :recall="99.59"
          :f1Score="99.33"
          cmImage="/cm_nb.png"
          :isBest="false"
        />
      </div>
      <div class="model-wrapper">
        <ModelCard 
          title="Support Vector Machine (SVM)"
          :accuracy="99.62"
          :precision="99.64"
          :recall="99.93"
          :f1Score="99.79"
          cmImage="/cm_svm.png"
          :isBest="true"
        />
      </div>
    </div>

    <!-- Row 2: SMOTE Summary (replaces LivePredictor) -->
    <SmoteSummary />
  </div>
</template>

<script setup>
import ModelCard from '../components/lab/ModelCard.vue'
import SmoteSummary from '../components/lab/SmoteSummary.vue'
</script>

<style scoped>
.lab-page {
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

.models-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
}

@media (max-width: 768px) {
  .models-grid {
    grid-template-columns: 1fr;
  }
}
</style>
