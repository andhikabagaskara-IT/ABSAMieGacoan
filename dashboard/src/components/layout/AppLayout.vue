<script setup>
import { onMounted, ref } from 'vue'
import AppSidebar from './AppSidebar.vue'
import AppHeader from './AppHeader.vue'
import { useDashboardData } from '../../composables/useDashboardData'

const { fetchData, state } = useDashboardData()

const isSidebarOpen = ref(false)

const toggleSidebar = () => {
  isSidebarOpen.value = !isSidebarOpen.value
}

const closeSidebar = () => {
  isSidebarOpen.value = false
}

onMounted(() => {
  fetchData()
})
</script>

<template>
  <div class="app-container">
    <!-- Mobile overlay -->
    <div 
      class="sidebar-overlay" 
      :class="{ 'is-active': isSidebarOpen }"
      @click="closeSidebar"
    ></div>

    <AppSidebar :isOpen="isSidebarOpen" @close="closeSidebar" />
    <div class="main-content">
      <AppHeader @toggle-sidebar="toggleSidebar" />
      <main class="page-content">
        <div v-if="state.loading" class="loading-state">
          Loading dashboard data...
        </div>
        <div v-else-if="state.error" class="error-state">
          {{ state.error }}
        </div>
        <router-view v-else v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </main>
    </div>
  </div>
</template>

<style scoped>
.app-container {
  display: flex;
  min-height: 100vh;
  background-color: var(--bg-subtle);
  position: relative;
}

.sidebar-overlay {
  display: none;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 40;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.sidebar-overlay.is-active {
  display: block;
  opacity: 1;
}

.main-content {
  flex: 1;
  margin-left: 260px; /* Same as sidebar width */
  display: flex;
  flex-direction: column;
  transition: margin-left 0.3s ease;
  width: 100%;
}

.page-content {
  flex: 1;
  padding: 2rem;
  overflow-x: hidden;
}

/* Page transition */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Responsive */
@media (max-width: 1024px) {
  .main-content {
    margin-left: 0;
  }
  
  .page-content {
    padding: 1.5rem 1rem;
  }
}
</style>
