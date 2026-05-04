<script setup>
import { onMounted, ref } from 'vue'
import AppSidebar from './AppSidebar.vue'
import AppHeader from './AppHeader.vue'
import { useDashboardData } from '../../composables/useDashboardData'

const { fetchData, state } = useDashboardData()

const isSidebarOpen = ref(window.innerWidth > 1024)

const toggleSidebar = () => {
  isSidebarOpen.value = !isSidebarOpen.value
}

const closeSidebar = () => {
  if (window.innerWidth <= 1024) {
    isSidebarOpen.value = false
  }
}

const closeMobileSidebar = () => {
  if (window.innerWidth <= 1024) {
    isSidebarOpen.value = false
  }
}

const isMobile = ref(window.innerWidth <= 1024)

onMounted(() => {
  fetchData()
  window.addEventListener('resize', () => {
    isMobile.value = window.innerWidth <= 1024
    if (window.innerWidth > 1024 && !isSidebarOpen.value) {
      // Let user keep it closed if they want, but default to open on desktop
    }
  })
})
</script>

<template>
  <div class="app-container">
    <!-- Animated background -->
    <div class="animated-bg">
      <div class="blob blob-1"></div>
      <div class="blob blob-2"></div>
      <div class="blob blob-3"></div>
    </div>

    <!-- Mobile overlay -->
    <div class="sidebar-overlay" 
      :class="{ 'is-active': isSidebarOpen && isMobile }"
      @click="closeSidebar"
    ></div>

    <AppSidebar :isOpen="isSidebarOpen" @close="closeMobileSidebar" />
    <div class="main-content" :class="{ 'sidebar-closed': !isSidebarOpen }">
      <AppHeader @toggle-sidebar="toggleSidebar" />
      <main class="page-content">
        <div v-if="state.loading" class="loading-state">
          Loading dashboard data...
        </div>
        <div v-else-if="state.error" class="error-state">
          {{ state.error }}
        </div>
        <router-view v-else v-slot="{ Component }">
          <transition name="page" mode="out-in">
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
  z-index: 1;
}

.animated-bg {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  z-index: -1;
  overflow: hidden;
  pointer-events: none;
}

.blob {
  position: absolute;
  filter: blur(80px);
  opacity: 0.3;
  border-radius: 50%;
  animation: moveBlobs 20s infinite alternate cubic-bezier(0.4, 0, 0.2, 1);
}

.blob-1 {
  width: 400px;
  height: 400px;
  background-color: rgba(3, 169, 244, 0.4);
  top: -100px;
  left: -100px;
}

.blob-2 {
  width: 500px;
  height: 500px;
  background-color: rgba(236, 64, 122, 0.3);
  bottom: -200px;
  right: -100px;
  animation-delay: -5s;
  animation-duration: 25s;
}

.blob-3 {
  width: 300px;
  height: 300px;
  background-color: rgba(79, 195, 247, 0.3);
  top: 40%;
  left: 40%;
  animation-delay: -10s;
  animation-duration: 30s;
}

@keyframes moveBlobs {
  0% { transform: translate(0, 0) scale(1); }
  33% { transform: translate(30vw, 10vh) scale(1.1); }
  66% { transform: translate(-10vw, 30vh) scale(0.9); }
  100% { transform: translate(20vw, -20vh) scale(1); }
}

[data-theme="dark"] .blob {
  opacity: 0.1;
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
  transition: margin-left 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  width: 100%;
  z-index: 10;
  position: relative;
}

.main-content.sidebar-closed {
  margin-left: 0;
}

.page-content {
  flex: 1;
  padding: 2rem;
  overflow-x: hidden;
}

/* Page transition */
.page-enter-active,
.page-leave-active {
  transition: opacity 0.4s cubic-bezier(0.25, 1, 0.5, 1), transform 0.4s cubic-bezier(0.25, 1, 0.5, 1);
}

.page-enter-from {
  opacity: 0;
  transform: translateY(15px);
}

.page-leave-to {
  opacity: 0;
  transform: translateY(-15px);
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
