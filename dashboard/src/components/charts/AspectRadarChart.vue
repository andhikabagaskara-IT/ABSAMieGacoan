<template>
  <div class="card chart-container">
    <h3 class="chart-title">Distribusi Aspek</h3>
    <div class="chart-wrapper">
      <Radar :data="chartData" :options="chartOptions" />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Radar } from 'vue-chartjs'
import { Chart as ChartJS, RadialLinearScale, PointElement, LineElement, Filler, Tooltip, Legend } from 'chart.js'
import { useDashboardData } from '../../composables/useDashboardData'

ChartJS.register(RadialLinearScale, PointElement, LineElement, Filler, Tooltip, Legend)

const props = defineProps({
  aspectData: {
    type: Object,
    required: true
  }
})

const { getAspectLabel } = useDashboardData()

const chartData = computed(() => {
  const labels = Object.keys(props.aspectData).map(getAspectLabel)
  const data = Object.values(props.aspectData)

  return {
    labels,
    datasets: [
      {
        label: 'Frekuensi Kemunculan Aspek',
        backgroundColor: 'rgba(3, 169, 244, 0.2)',
        borderColor: '#03A9F4',
        pointBackgroundColor: '#EC407A',
        pointBorderColor: '#fff',
        pointHoverBackgroundColor: '#fff',
        pointHoverBorderColor: '#EC407A',
        data
      }
    ]
  }
})

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  scales: {
    r: {
      angleLines: {
        color: 'rgba(0, 0, 0, 0.1)'
      },
      grid: {
        color: 'rgba(0, 0, 0, 0.1)'
      },
      pointLabels: {
        font: {
          family: "'Inter', sans-serif",
          size: 12
        }
      },
      ticks: {
        display: false // hide numbers on the axes
      }
    }
  },
  plugins: {
    legend: {
      position: 'bottom',
      labels: {
        usePointStyle: true,
        font: {
          family: "'Inter', sans-serif"
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
  min-height: 300px;
  position: relative;
}
</style>
