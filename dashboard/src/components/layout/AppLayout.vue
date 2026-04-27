<template>
  <div class="app-container">
    <AppSidebar />
    <div class="main-content">
      <AppHeader />
      <main class="page-content">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </main>
    </div>
  </div>
</template>

<script setup>
import AppSidebar from './AppSidebar.vue'
import AppHeader from './AppHeader.vue'
</script>

<style scoped>
.app-container {
  display: flex;
  min-height: 100vh;
  background-color: var(--bg-subtle);
}

.main-content {
  flex: 1;
  margin-left: 260px; /* Same as sidebar width */
  display: flex;
  flex-direction: column;
}

.page-content {
  flex: 1;
  padding: 2rem;
  overflow-y: auto;
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
</style>
