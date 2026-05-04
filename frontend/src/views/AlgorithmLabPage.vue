<template>
  <div class="lab-page">
    <div class="section-title">
      <h2>⚡ Pengujian Model Sentimen</h2>
      <p>Bandingkan performa algoritma klasifikasi dan lihat dampak SMOTE serta Stratified 5-Fold Cross-Validation pada data.</p>
    </div>

    <!-- Row 1: Models Comparison (Real Data) -->
    <div class="models-grid">
      <div class="model-wrapper">
        <ModelCard 
          title="Naive Bayes (Multinomial)"
          :accuracy="97.37"
          :precision="97.64"
          :recall="97.37"
          :f1Score="97.45"
          cmImage="/cm_nb.png"
          :isBest="false"
        />
      </div>
      <div class="model-wrapper">
        <ModelCard 
          title="Support Vector Machine (SVM)"
          :accuracy="99.00"
          :precision="99.05"
          :recall="99.00"
          :f1Score="99.01"
          cmImage="/cm_svm.png"
          :isBest="true"
        />
      </div>
    </div>

    <!-- Row 2: Live Predictor (Removed based on user request) -->

    <!-- Row 3: SMOTE Summary -->
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
