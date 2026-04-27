<template>
  <header class="app-header">
    <div class="header-title">
      <h1>{{ title }}</h1>
    </div>
    <div class="header-actions">
      <div class="user-profile">
        <span class="avatar">A</span>
        <span class="user-name">Admin</span>
      </div>
    </div>
  </header>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

const title = computed(() => {
  const routeName = route.name
  switch (routeName) {
    case 'Overview': return 'Executive Overview'
    case 'SyncCenter': return 'Sync Center'
    case 'Branches': return 'Analisis Cabang'
    case 'AspectDive': return 'Aspect Deep Dive'
    case 'AlgorithmLab': return 'Algorithm Lab'
    case 'Explorer': return 'Data Explorer'
    default: return 'Dashboard'
  }
})
</script>

<style scoped>
.app-header {
  height: 70px;
  background-color: var(--bg-base);
  border-bottom: 1px solid var(--border);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 2rem;
  position: sticky;
  top: 0;
  z-index: 10;
}

.header-title h1 {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.user-profile {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.25rem 0.75rem 0.25rem 0.25rem;
  background-color: var(--bg-subtle);
  border-radius: 9999px;
  border: 1px solid var(--border);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.user-profile:hover {
  background-color: white;
  border-color: var(--primary-light);
}

.avatar {
  width: 32px;
  height: 32px;
  background: var(--gradient-accent);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 0.875rem;
}

.user-name {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--text-primary);
}
</style>
