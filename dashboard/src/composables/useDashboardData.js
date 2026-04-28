import { ref, reactive, readonly, computed } from 'vue'

// Reactive state singleton to share across components
const state = reactive({
  data: null,
  loading: true,
  error: null
})

// Aspect Label Mapping based on LDA evaluation
const ASPECT_LABELS = {
  'Topik 1': 'Rasa & Bumbu',
  'Topik 2': 'Tempat & Kebersihan',
  'Topik 3': 'Pelayanan',
  'Topik 4': 'Harga & Porsi',
  'Topik 5': 'Kualitas Keseluruhan'
}

let isFetching = false

export function useDashboardData() {
  const fetchData = async () => {
    if (state.data || isFetching) return
    
    isFetching = true
    state.loading = true
    state.error = null
    
    try {
      // In Vite, files in public/ are served at the root path
      const response = await fetch('/dashboard_data.json')
      if (!response.ok) {
        throw new Error(`Failed to fetch data: ${response.statusText}`)
      }
      
      const jsonData = await response.json()
      state.data = jsonData
    } catch (err) {
      console.error('Error fetching dashboard data:', err)
      state.error = err.message
    } finally {
      state.loading = false
      isFetching = false
    }
  }

  // Computed properties for easy access to specific data parts
  const totalReviews = computed(() => state.data?.total_reviews || 0)
  
  const sentimentDistribution = computed(() => state.data?.sentiment_distribution || { positif: 0, negatif: 0 })
  
  const sentimentPercentage = computed(() => {
    const total = sentimentDistribution.value.positif + sentimentDistribution.value.negatif
    if (total === 0) return { positif: 0, negatif: 0 }
    
    return {
      positif: ((sentimentDistribution.value.positif / total) * 100).toFixed(1),
      negatif: ((sentimentDistribution.value.negatif / total) * 100).toFixed(1)
    }
  })
  
  const branchSentiment = computed(() => state.data?.branch_sentiment || {})
  
  const branchList = computed(() => Object.keys(branchSentiment.value))
  
  const aspectDistribution = computed(() => state.data?.aspect_distribution || {})
  
  const branchAspect = computed(() => state.data?.branch_aspect || {})
  
  const sampleReviews = computed(() => state.data?.sample_reviews || [])

  const getAspectLabel = (topicId) => ASPECT_LABELS[topicId] || topicId

  return {
    state: readonly(state),
    fetchData,
    totalReviews,
    sentimentDistribution,
    sentimentPercentage,
    branchSentiment,
    branchList,
    aspectDistribution,
    branchAspect,
    sampleReviews,
    getAspectLabel,
    ASPECT_LABELS
  }
}
