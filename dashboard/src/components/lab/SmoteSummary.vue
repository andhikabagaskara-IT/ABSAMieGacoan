<template>
  <div class="card smote-section">
    <div class="section-header">
      <div class="title-row">
        <Scale class="icon text-accent" />
        <h3>Ringkasan SMOTE (Oversampling)</h3>
      </div>
      <span class="badge badge-accent-outline">Synthetic Minority Over-sampling</span>
    </div>

    <p class="description">
      SMOTE digunakan untuk mengatasi <strong>ketidakseimbangan kelas</strong> pada dataset ulasan.
      Kelas mayoritas (positif) memiliki {{ smoteData.trainBefore.positif.toLocaleString() }} sampel,
      sedangkan kelas minoritas (negatif) hanya {{ smoteData.trainBefore.negatif.toLocaleString() }} sampel
      (rasio {{ smoteData.imbalanceRatio }}:1).
    </p>

    <!-- Distribution Before/After -->
    <div class="distribution-row">
      <div class="dist-card">
        <h4>Sebelum SMOTE</h4>
        <div class="dist-bars">
          <div class="dist-item">
            <span class="dist-label">Positif</span>
            <div class="bar-track">
              <div class="bar-fill positive" :style="{ width: beforePositifPct + '%' }"></div>
            </div>
            <span class="dist-value">{{ smoteData.trainBefore.positif.toLocaleString() }}</span>
          </div>
          <div class="dist-item">
            <span class="dist-label">Negatif</span>
            <div class="bar-track">
              <div class="bar-fill negative" :style="{ width: beforeNegatifPct + '%' }"></div>
            </div>
            <span class="dist-value">{{ smoteData.trainBefore.negatif.toLocaleString() }}</span>
          </div>
        </div>
        <span class="dist-total">Total: {{ smoteData.trainBeforeTotal.toLocaleString() }}</span>
      </div>
      <div class="arrow-divider">
        <ArrowRight class="arrow-icon" />
        <span class="synth-label">+{{ smoteData.syntheticAdded.toLocaleString() }} sintetis</span>
      </div>
      <div class="dist-card balanced">
        <h4>Sesudah SMOTE</h4>
        <div class="dist-bars">
          <div class="dist-item">
            <span class="dist-label">Positif</span>
            <div class="bar-track">
              <div class="bar-fill positive" style="width: 50%"></div>
            </div>
            <span class="dist-value">{{ smoteData.trainAfter.positif.toLocaleString() }}</span>
          </div>
          <div class="dist-item">
            <span class="dist-label">Negatif</span>
            <div class="bar-track">
              <div class="bar-fill accent" style="width: 50%"></div>
            </div>
            <span class="dist-value">{{ smoteData.trainAfter.negatif.toLocaleString() }}</span>
          </div>
        </div>
        <span class="dist-total balanced-badge">✅ Balanced: {{ smoteData.trainAfterTotal.toLocaleString() }}</span>
      </div>
    </div>

    <!-- Metrics Comparison Table -->
    <div class="comparison-section">
      <h4>Perbandingan Metrik: Tanpa SMOTE vs Dengan SMOTE</h4>
      <div class="comparison-tables">
        <table class="metrics-table" v-for="model in ['svm', 'nb']" :key="model">
          <thead>
            <tr>
              <th colspan="4" class="table-header" :class="model">
                {{ model === 'svm' ? '🤖 SVM (Support Vector Machine)' : '📊 Naive Bayes (Multinomial)' }}
              </th>
            </tr>
            <tr>
              <th>Metrik</th>
              <th>Tanpa SMOTE</th>
              <th>+ SMOTE</th>
              <th>Selisih</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="metric in metricKeys" :key="metric.key">
              <td class="metric-name">{{ metric.label }}</td>
              <td>{{ (smoteData.before[model][metric.key] * 100).toFixed(2) }}%</td>
              <td>{{ (smoteData.after[model][metric.key] * 100).toFixed(2) }}%</td>
              <td :class="getDiffClass(smoteData.after[model][metric.key] - smoteData.before[model][metric.key])">
                {{ formatDiff(smoteData.after[model][metric.key] - smoteData.before[model][metric.key]) }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Confusion Matrices -->
    <div class="cm-section">
      <h4>Confusion Matrix (Dengan SMOTE)</h4>
      <div class="cm-grid">
        <div class="cm-item">
          <img src="/cm_svm_smote.png" alt="CM SVM SMOTE" @error="svmImgErr = true" v-if="!svmImgErr" />
          <div v-else class="cm-fallback">SVM+SMOTE CM tidak tersedia</div>
          <span class="cm-label">SVM + SMOTE</span>
        </div>
        <div class="cm-item">
          <img src="/cm_nb_smote.png" alt="CM NB SMOTE" @error="nbImgErr = true" v-if="!nbImgErr" />
          <div v-else class="cm-fallback">NB+SMOTE CM tidak tersedia</div>
          <span class="cm-label">Naive Bayes + SMOTE</span>
        </div>
      </div>
    </div>

    <!-- Conclusion -->
    <div class="conclusion-box">
      <Lightbulb class="icon" />
      <div>
        <strong>Kesimpulan:</strong>
        <p>{{ smoteData.conclusion }}</p>
        <p class="note">Meskipun metrik keseluruhan tidak berubah drastis, SMOTE meningkatkan Recall pada kelas minoritas (negatif) — dari 97% menjadi 99% pada SVM.</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { Scale, ArrowRight, Lightbulb } from 'lucide-vue-next'

const svmImgErr = ref(false)
const nbImgErr = ref(false)

const metricKeys = [
  { key: 'accuracy', label: 'Accuracy' },
  { key: 'precision', label: 'Precision' },
  { key: 'recall', label: 'Recall' },
  { key: 'f1', label: 'F1-Score' }
]

// Real data from smote_classification_report.txt
const smoteData = {
  imbalanceRatio: '7.15',
  trainBeforeTotal: 41508,
  trainAfterTotal: 72828,
  syntheticAdded: 31320,
  trainBefore: { positif: 36414, negatif: 5094 },
  trainAfter: { positif: 36414, negatif: 36414 },
  before: {
    svm: { accuracy: 0.9962, precision: 0.9964, recall: 0.9993, f1: 0.9979 },
    nb: { accuracy: 0.9882, precision: 0.9907, recall: 0.9959, f1: 0.9933 }
  },
  after: {
    svm: { accuracy: 0.9890, precision: 0.9989, recall: 0.9886, f1: 0.9937 },
    nb: { accuracy: 0.9749, precision: 0.9954, recall: 0.9759, f1: 0.9856 }
  },
  conclusion: 'SVM: performa SETARA (tidak berubah signifikan). NB: sedikit menurun (kemungkinan overfitting pada data sintetis).'
}

const beforePositifPct = (smoteData.trainBefore.positif / smoteData.trainBeforeTotal * 100)
const beforeNegatifPct = (smoteData.trainBefore.negatif / smoteData.trainBeforeTotal * 100)

const getDiffClass = (diff) => {
  if (diff > 0.001) return 'diff-positive'
  if (diff < -0.001) return 'diff-negative'
  return 'diff-neutral'
}

const formatDiff = (diff) => {
  const sign = diff >= 0 ? '+' : ''
  return sign + (diff * 100).toFixed(2) + '%'
}
</script>

<style scoped>
.smote-section {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.title-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.title-row h3 { margin: 0; font-size: 1.125rem; }

.badge-accent-outline {
  border: 1px solid var(--accent);
  color: var(--accent);
  background: rgba(236, 64, 122, 0.06);
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 600;
}

.description {
  color: var(--text-secondary);
  font-size: 0.875rem;
  line-height: 1.6;
}

/* Distribution Row */
.distribution-row {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.dist-card {
  flex: 1;
  background: var(--bg-subtle);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  padding: 1rem;
}

.dist-card.balanced { border-color: var(--positive); background: rgba(16, 185, 129, 0.03); }

.dist-card h4 { font-size: 0.8rem; margin-bottom: 0.75rem; color: var(--text-secondary); font-weight: 600; }

.dist-bars { display: flex; flex-direction: column; gap: 0.5rem; }

.dist-item { display: flex; align-items: center; gap: 0.5rem; }
.dist-label { font-size: 0.75rem; width: 50px; color: var(--text-secondary); }
.bar-track { flex: 1; height: 8px; background: var(--border); border-radius: 4px; overflow: hidden; }
.bar-fill { height: 100%; border-radius: 4px; transition: width 0.8s ease; }
.bar-fill.positive { background: var(--primary); }
.bar-fill.negative { background: var(--negative); }
.bar-fill.accent { background: var(--accent); }
.dist-value { font-size: 0.75rem; font-weight: 600; min-width: 50px; text-align: right; }
.dist-total { font-size: 0.7rem; color: var(--text-secondary); margin-top: 0.5rem; display: block; }
.balanced-badge { color: var(--positive); font-weight: 600; }

.arrow-divider {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.25rem;
  color: var(--accent);
  flex-shrink: 0;
}
.arrow-icon { width: 24px; height: 24px; }
.synth-label { font-size: 0.65rem; font-weight: 600; white-space: nowrap; }

/* Comparison Tables */
.comparison-section h4 { font-size: 0.9rem; margin-bottom: 1rem; }

.comparison-tables {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.metrics-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.8rem;
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  overflow: hidden;
}

.table-header { text-align: center; padding: 0.6rem; font-size: 0.8rem; }
.table-header.svm { background: rgba(3, 169, 244, 0.1); color: var(--primary-dark); }
.table-header.nb { background: rgba(236, 64, 122, 0.1); color: var(--accent); }

.metrics-table th { background: var(--bg-subtle); padding: 0.5rem; font-weight: 600; text-align: center; border-bottom: 1px solid var(--border); }
.metrics-table td { padding: 0.5rem; text-align: center; border-bottom: 1px solid var(--border); }
.metric-name { font-weight: 500; text-align: left !important; }

.diff-positive { color: var(--positive); font-weight: 600; }
.diff-negative { color: var(--negative); font-weight: 600; }
.diff-neutral { color: var(--text-secondary); }

/* CM Section */
.cm-section h4 { font-size: 0.9rem; margin-bottom: 1rem; }
.cm-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
.cm-item { text-align: center; }
.cm-item img { width: 100%; border-radius: var(--radius-md); border: 1px solid var(--border); }
.cm-label { font-size: 0.75rem; color: var(--text-secondary); margin-top: 0.5rem; display: block; font-weight: 500; }
.cm-fallback { padding: 2rem; background: var(--bg-subtle); border-radius: var(--radius-md); color: var(--text-secondary); font-size: 0.8rem; }

/* Conclusion */
.conclusion-box {
  display: flex;
  gap: 0.75rem;
  background: rgba(3, 169, 244, 0.05);
  border: 1px solid rgba(3, 169, 244, 0.2);
  border-radius: var(--radius-md);
  padding: 1rem;
}
.conclusion-box .icon { width: 20px; height: 20px; color: var(--primary); flex-shrink: 0; margin-top: 2px; }
.conclusion-box strong { font-size: 0.875rem; color: var(--text-primary); }
.conclusion-box p { font-size: 0.8rem; color: var(--text-secondary); margin-top: 0.25rem; line-height: 1.5; }
.note { font-style: italic; opacity: 0.8; }

@media (max-width: 768px) {
  .distribution-row { flex-direction: column; }
  .arrow-divider { transform: rotate(90deg); }
  .comparison-tables, .cm-grid { grid-template-columns: 1fr; }
}
</style>
