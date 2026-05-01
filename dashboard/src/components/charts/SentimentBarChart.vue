<template>
  <div class="card chart-container">
    <h3 class="chart-title">Perbandingan Sentimen per Cabang</h3>
    <div class="chart-wrapper">
      <Bar :data="chartData" :options="chartOptions" />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Bar } from 'vue-chartjs'
import { Chart as ChartJS, Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale } from 'chart.js'

ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale)

const props = defineProps({
  branchData: {
    type: Object,
    required: true
  }
})

const chartData = computed(() => {
  const branches = Object.keys(props.branchData)
  
  // Clean up branch names for display
  const labels = branches.map(b => b.replace('Mie Gacoan - ', '').replace('Mie Gacoan ', ''))
  
  const positifData = branches.map(b => props.branchData[b].positif || 0)
  const netralData = branches.map(b => props.branchData[b].netral || 0)
  const negatifData = branches.map(b => props.branchData[b].negatif || 0)

  return {
    labels,
    datasets: [
      {
        label: 'Positif',
        backgroundColor: '#10B981',
        data: positifData,
        borderRadius: 4
      },
      {
        label: 'Netral',
        backgroundColor: '#F59E0B',
        data: netralData,
        borderRadius: 4
      },
      {
        label: 'Negatif',
        backgroundColor: '#EF4444',
        data: negatifData,
        borderRadius: 4
      }
    ]
  }
})

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  indexAxis: 'y', // Horizontal bar chart
  scales: {
    x: {
      stacked: true,
      grid: {
        display: false
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
        padding: 20,
        font: {
          family: "'Inter', sans-serif"
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
