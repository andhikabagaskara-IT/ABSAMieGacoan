<template>
  <div class="card chart-container">
    <h3 class="chart-title">Distribusi Aspek per Cabang</h3>
    <div class="chart-wrapper">
      <Bar :data="chartData" :options="chartOptions" />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Bar } from 'vue-chartjs'
import { Chart as ChartJS, Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale } from 'chart.js'
import { useDashboardData } from '../../composables/useDashboardData'

ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale)

const props = defineProps({
  branchAspectData: {
    type: Object,
    required: true
  }
})

const { getAspectLabel, ASPECT_LABELS } = useDashboardData()

const chartData = computed(() => {
  const branches = Object.keys(props.branchAspectData)
  const labels = branches.map(b => b.replace('Mie Gacoan - ', '').replace('Mie Gacoan ', ''))
  
  const topics = Object.keys(ASPECT_LABELS)
  const colors = ['#03A9F4', '#4FC3F7', '#10B981', '#F48FB1', '#EC407A']
  
  const datasets = topics.map((topic, index) => {
    return {
      label: getAspectLabel(topic),
      backgroundColor: colors[index % colors.length],
      data: branches.map(b => props.branchAspectData[b][topic] || 0),
      borderRadius: 2
    }
  })

  return {
    labels,
    datasets
  }
})

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  scales: {
    x: {
      stacked: true,
      grid: {
        display: false
      },
      ticks: {
        font: {
          family: "'Inter', sans-serif"
        }
      }
    },
    y: {
      stacked: true,
      grid: {
        color: '#E2E8F0'
      },
      ticks: {
        font: {
          family: "'Inter', sans-serif"
        }
      }
    }
  },
  plugins: {
    legend: {
      position: 'bottom',
      labels: {
        usePointStyle: true,
        padding: 15,
        font: {
          family: "'Inter', sans-serif",
          size: 11
        }
      }
    },
    tooltip: {
      mode: 'index',
      intersect: false
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
  min-height: 350px;
  position: relative;
}
</style>
