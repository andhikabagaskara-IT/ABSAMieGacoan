<template>
  <div class="card chart-container">
    <h3 class="chart-title">Distribusi Sentimen Keseluruhan</h3>
    <div class="chart-wrapper">
      <Doughnut :data="chartData" :options="chartOptions" />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Doughnut } from 'vue-chartjs'
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js'

ChartJS.register(ArcElement, Tooltip, Legend)

const props = defineProps({
  positif: { type: Number, required: true },
  negatif: { type: Number, required: true }
})

const chartData = computed(() => ({
  labels: ['Positif', 'Negatif'],
  datasets: [
    {
      backgroundColor: ['#03A9F4', '#EC407A'],
      borderWidth: 0,
      hoverOffset: 4,
      data: [props.positif, props.negatif]
    }
  ]
}))

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  cutout: '70%',
  plugins: {
    legend: {
      position: 'bottom',
      labels: {
        usePointStyle: true,
        padding: 20,
        font: {
          family: "'Inter', sans-serif",
          size: 14
        }
      }
    },
    tooltip: {
      callbacks: {
        label: function(context) {
          let label = context.label || '';
          if (label) {
            label += ': ';
          }
          if (context.parsed !== null) {
            const total = context.dataset.data.reduce((a, b) => a + b, 0);
            const percentage = ((context.parsed / total) * 100).toFixed(1);
            label += new Intl.NumberFormat('id-ID').format(context.parsed) + ` (${percentage}%)`;
          }
          return label;
        }
      }
    }
  }
}
</script>

<style scoped>
.chart-container {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.chart-title {
  font-size: 1rem;
  margin-bottom: 1.5rem;
  color: var(--text-primary);
}

.chart-wrapper {
  flex: 1;
  min-height: 250px;
  position: relative;
}
</style>
