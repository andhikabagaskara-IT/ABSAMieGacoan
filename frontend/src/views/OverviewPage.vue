<template>
  <div class="overview-page">
    <!-- Row 1: KPI Cards -->
    <div class="kpi-grid">
      <StatCard 
        label="Total Review" 
        :value="totalReviews" 
        :icon="MessageSquare" 
      />
      <StatCard 
        label="Sentimen Positif" 
        :value="`${sentimentPercentage.positif}%`" 
        :subtitle="`${formatNumber(sentimentDistribution.positif || 0)} ulasan`"
        type="positive"
        :icon="Smile" 
      />
      <StatCard 
        label="Sentimen Netral" 
        :value="`${sentimentPercentage.netral}%`" 
        :subtitle="`${formatNumber(sentimentDistribution.netral || 0)} ulasan`"
        type="warning"
        :icon="Meh" 
      />
      <StatCard 
        label="Sentimen Negatif" 
        :value="`${sentimentPercentage.negatif}%`" 
        :subtitle="`${formatNumber(sentimentDistribution.negatif || 0)} ulasan`"
        type="negative"
        :icon="Frown" 
      />
      <StatCard 
        label="Total Cabang" 
        :value="branchList.length" 
        :icon="Store" 
      />
    </div>

    <!-- Row 2: Charts -->
    <div class="charts-grid">
      <div class="bar-chart-wrapper">
        <SentimentBarChart :branchData="branchSentiment" />
      </div>
      <div class="donut-chart-wrapper">
        <SentimentDonut 
          :positif="sentimentDistribution.positif || 0" 
          :negatif="sentimentDistribution.negatif || 0" 
          :netral="sentimentDistribution.netral || 0"
        />
      </div>
    </div>

    <!-- Row 3: Leaderboard -->
    <div class="leaderboard-wrapper">
      <BranchLeaderboard :branchData="branchSentiment" />
    </div>

    <!-- Row 4: Branch Gallery -->
    <div class="gallery-wrapper">
      <BranchGallery />
    </div>
  </div>
</template>

<script setup>
import { MessageSquare, Smile, Meh, Frown, Store } from 'lucide-vue-next'
import { useDashboardData } from '../composables/useDashboardData'
import StatCard from '../components/cards/StatCard.vue'
import SentimentDonut from '../components/charts/SentimentDonut.vue'
import SentimentBarChart from '../components/charts/SentimentBarChart.vue'
import BranchLeaderboard from '../components/cards/BranchLeaderboard.vue'
import BranchGallery from '../components/cards/BranchGallery.vue'

const { 
  totalReviews, 
  sentimentDistribution, 
  sentimentPercentage,
  branchSentiment,
  branchList
} = useDashboardData()

const formatNumber = (num) => {
  return new Intl.NumberFormat('id-ID').format(num)
}
</script>

<style scoped>
.overview-page {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

/* KPI Grid */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 1.5rem;
}

/* Charts Grid */
.charts-grid {
  display: grid;
  grid-template-columns: 8fr 4fr;
  gap: 1.5rem;
  height: 400px;
}

.bar-chart-wrapper, .donut-chart-wrapper {
  height: 100%;
}

/* Leaderboard & Gallery */
.leaderboard-wrapper, .gallery-wrapper {
  margin-top: 2rem;
}

/* Responsive */
@media (max-width: 1200px) {
  .charts-grid {
    grid-template-columns: 1fr;
    height: auto;
  }
  
  .bar-chart-wrapper {
    height: 400px;
  }
  
  .donut-chart-wrapper {
    height: 350px;
  }
}

@media (max-width: 992px) {
  .kpi-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 576px) {
  .kpi-grid {
    grid-template-columns: 1fr;
  }
}
</style>
