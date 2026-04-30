<template>
  <div class="card dbi-card">
    <div class="dbi-header">
      <h3 class="card-title">DBI Evaluation</h3>
      <div class="score-badge">Score: 0.1949</div>
    </div>
    
    <div class="dbi-content">
      <div class="optimal-k">
        <span class="label">Optimal Topics (K)</span>
        <span class="value">4</span>
      </div>
      
      <div class="description-box">
        <p class="description">
          <strong>Davies-Bouldin Index (DBI)</strong> digunakan untuk mengevaluasi kualitas pemisahan topik pada LDA.
        </p>
        <ul class="guide-list">
          <li><strong>Sumbu-X:</strong> Jumlah aspek (topik) yang diuji.</li>
          <li><strong>Sumbu-Y:</strong> Nilai skor DBI (tingkat tumpang tindih).</li>
          <li><strong>Cara Membaca:</strong> Cari titik terendah pada grafik. Titik tersebut (<strong>K=4</strong>) menunjukkan bahwa 4 topik adalah jumlah yang paling optimal dan unik (tidak saling tumpang tindih).</li>
        </ul>
      </div>
      
      <div class="image-wrapper">
        <img src="/lda_dbi_evaluation.png" alt="DBI Evaluation Chart" @error="handleImageError" />
        <div v-if="imageError" class="image-fallback">
          <div class="mock-chart">
            <div class="line"></div>
            <div class="points">
              <div class="point" style="bottom: 80%; left: 20%" title="K=2: 0.45"></div>
              <div class="point" style="bottom: 50%; left: 40%" title="K=3: 0.32"></div>
              <div class="point point-optimal" style="bottom: 10%; left: 60%" title="K=4: 0.1949"></div>
              <div class="point" style="bottom: 30%; left: 80%" title="K=5: 0.25"></div>
            </div>
            <div class="axes">
              <span class="x-axis">Jumlah Topik (K)</span>
              <span class="y-axis">DBI Score</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const imageError = ref(false)

const handleImageError = () => {
  imageError.value = true
}
</script>

<style scoped>
.dbi-card {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.dbi-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.card-title {
  font-size: 1rem;
  margin: 0;
  color: var(--text-primary);
}

.score-badge {
  background-color: rgba(3, 169, 244, 0.1);
  color: var(--primary-dark);
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-weight: 600;
  font-size: 0.875rem;
}

.dbi-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.optimal-k {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background-color: var(--bg-subtle);
  border-radius: var(--radius-md);
  border: 1px solid var(--border);
}

.optimal-k .label {
  font-weight: 500;
  color: var(--text-secondary);
}

.optimal-k .value {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--primary);
}

.description-box {
  background-color: var(--bg-base);
  padding: 1rem;
  border-radius: var(--radius-md);
  border-left: 4px solid var(--primary);
}

.description {
  font-size: 0.875rem;
  color: var(--text-primary);
  margin-bottom: 0.5rem;
}

.guide-list {
  font-size: 0.875rem;
  color: var(--text-secondary);
  padding-left: 1.2rem;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.guide-list li strong {
  color: var(--text-primary);
}

.image-wrapper {
  margin-top: auto;
  border-radius: var(--radius-md);
  overflow: hidden;
  border: 1px solid var(--border);
  height: 200px;
  position: relative;
  background-color: var(--bg-subtle);
}

.image-wrapper img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.image-fallback {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: var(--bg-subtle);
  padding: 1rem;
}

.mock-chart {
  width: 100%;
  height: 100%;
  position: relative;
  border-left: 2px solid var(--border);
  border-bottom: 2px solid var(--border);
}

.line {
  position: absolute;
  top: 20%;
  left: 10%;
  width: 80%;
  height: 70%;
  border-bottom: 2px dashed var(--primary-light);
  border-left: 2px dashed var(--primary-light);
  transform: skewY(15deg);
  transform-origin: bottom left;
  opacity: 0.5;
}

.points {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}

.point {
  position: absolute;
  width: 12px;
  height: 12px;
  background-color: var(--primary);
  border-radius: 50%;
  transform: translate(-50%, 50%);
}

.point-optimal {
  background-color: var(--accent);
  width: 16px;
  height: 16px;
  box-shadow: 0 0 0 4px rgba(236, 64, 122, 0.2);
}

.axes {
  position: absolute;
  bottom: -25px;
  left: -35px;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

.x-axis {
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  font-size: 0.75rem;
  color: var(--text-secondary);
}

.y-axis {
  position: absolute;
  bottom: 50%;
  left: 0;
  transform: rotate(-90deg) translateX(50%);
  transform-origin: left bottom;
  font-size: 0.75rem;
  color: var(--text-secondary);
}
</style>
