import { ref, reactive, readonly, computed } from 'vue'

// Reactive state singleton to share across components
const state = reactive({
  data: null,
  loading: true,
  error: null
})

// Default fallback aspect labels — will be overridden dynamically from LDA results
const DEFAULT_ASPECT_LABELS = {
  'Topik 1': 'Topik 1',
  'Topik 2': 'Topik 2',
  'Topik 3': 'Topik 3',
  'Topik 4': 'Topik 4'
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
  
  const sentimentDistribution = computed(() => state.data?.sentiment_distribution || { positif: 0, negatif: 0, netral: 0 })
  
  const sentimentPercentage = computed(() => {
    const dist = sentimentDistribution.value
    const total = (dist.positif || 0) + (dist.negatif || 0) + (dist.netral || 0)
    if (total === 0) return { positif: 0, negatif: 0, netral: 0 }
    
    return {
      positif: ((dist.positif / total) * 100).toFixed(1),
      negatif: ((dist.negatif / total) * 100).toFixed(1),
      netral: ((dist.netral / total) * 100).toFixed(1)
    }
  })
  
  const branchSentiment = computed(() => state.data?.branch_sentiment || {})
  
  const branchList = computed(() => Object.keys(branchSentiment.value))
  
  const aspectDistribution = computed(() => state.data?.aspect_distribution || {})
  
  const branchAspect = computed(() => state.data?.branch_aspect || {})
  
  const sampleReviews = computed(() => state.data?.sample_reviews || [])

  // Dynamic ASPECT_LABELS — built from LDA results topics_keywords
  // Generates labels like "Topik 1", "Topik 2" etc based on how many topics LDA found
  const ASPECT_LABELS = computed(() => {
    const ldaResults = state.data?.lda_results
    if (ldaResults && ldaResults.topics_keywords) {
      const labels = {}
      Object.keys(ldaResults.topics_keywords).forEach(key => {
        // Use the topic key directly (e.g., "Topik 1" -> "Topik 1")
        // Users can manually rename in the dashboard later
        labels[key] = key
      })
      return labels
    }
    // Fallback: build from aspect_distribution keys
    const aspectDist = state.data?.aspect_distribution
    if (aspectDist) {
      const labels = {}
      Object.keys(aspectDist).forEach(key => {
        labels[key] = key
      })
      return labels
    }
    return DEFAULT_ASPECT_LABELS
  })

  // LDA-specific data
  const ldaResults = computed(() => state.data?.lda_results || null)
  const kfoldResults = computed(() => state.data?.kfold_results || null)

  const getAspectLabel = (topicId) => {
    const labels = ASPECT_LABELS.value
    return labels[topicId] || topicId
  }

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
    ASPECT_LABELS,
    ldaResults,
    kfoldResults
  }
}
