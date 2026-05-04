<template>
  <aside class="sidebar" :class="{ 'is-open': isOpen }">
    <div class="sidebar-header">
      <div class="logo">
        <img v-if="companyLogo" :src="companyLogo" alt="Logo" class="custom-logo" />
        <span v-else class="logo-icon">🍜</span>
        <div class="logo-text">
          <h2>GACOAN INSIGHT</h2>
          <p>Analysis Platform <span>by DhikaIT</span></p>
        </div>
      </div>
    </div>
    
    <nav class="sidebar-nav">
      <ul>
        <li>
          <router-link to="/" class="nav-item" @click="$emit('close')">
            <LayoutDashboard class="icon" />
            <span>Overview</span>
          </router-link>
        </li>
        <li v-if="role === 'admin'">
          <router-link to="/sync" class="nav-item" @click="$emit('close')">
            <RefreshCw class="icon" />
            <span>Sync Center</span>
          </router-link>
        </li>
        <li>
          <router-link to="/branches" class="nav-item" @click="$emit('close')">
            <Store class="icon" />
            <span>Analisis Cabang</span>
          </router-link>
        </li>
        <li>
          <router-link to="/aspects" class="nav-item" @click="$emit('close')">
            <PieChart class="icon" />
            <span>Aspek Deep Dive</span>
          </router-link>
        </li>
        <li v-if="['admin', 'analyst'].includes(role)">
          <router-link to="/algorithm" class="nav-item" @click="$emit('close')">
            <FlaskConical class="icon" />
            <span>Algorithm Lab</span>
          </router-link>
        </li>
        <li>
          <router-link to="/explorer" class="nav-item" @click="$emit('close')">
            <Database class="icon" />
            <span>Data Explorer</span>
          </router-link>
        </li>
      </ul>
      
      <div class="nav-divider"></div>
      
      <ul>
        <li>
          <router-link to="/profile" class="nav-item" @click="$emit('close')">
            <UserCircle class="icon" />
            <span>Profil</span>
          </router-link>
        </li>
      </ul>
    </nav>
    
    <div class="sidebar-footer">
      <div class="stat-item">
        <TrendingUp class="icon-small" />
        <span>57.560 Ulasan</span>
      </div>
      <div class="stat-item">
        <Clock class="icon-small" />
        <span>Last sync: Hari ini</span>
      </div>
    </div>
  </aside>
</template>

<script setup>
import { 
  LayoutDashboard, 
  RefreshCw, 
  Store, 
  PieChart, 
  FlaskConical, 
  Database,
  UserCircle,
  TrendingUp,
  Clock
} from 'lucide-vue-next'

import { ref, onMounted, computed } from 'vue'
import { useAuthStore } from '../../stores/auth'

const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false
  }
})

const authStore = useAuthStore()
const role = computed(() => authStore.user?.role?.toLowerCase() || 'user')

defineEmits(['close'])

const companyLogo = ref('')

onMounted(() => {
  companyLogo.value = localStorage.getItem('companyLogo') || ''
  
  window.addEventListener('profile-updated', () => {
    companyLogo.value = localStorage.getItem('companyLogo') || ''
  })
})
</script>

<style scoped>
.sidebar {
  width: 260px;
  background-color: var(--bg-sidebar);
  color: var(--text-light);
  display: flex;
  flex-direction: column;
  height: 100vh;
  position: fixed;
  left: 0;
  top: 0;
  border-right: 1px solid rgba(255, 255, 255, 0.1);
  border-top-right-radius: 24px;
  border-bottom-right-radius: 24px;
  z-index: 50;
  transform: translateX(-100%);
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 4px 0 15px rgba(0, 0, 0, 0.05);
}

.sidebar.is-open {
  transform: translateX(0);
}

.sidebar-header {
  padding: 1.5rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.logo {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.logo-icon {
  font-size: 1.5rem;
}

.custom-logo {
  width: 32px;
  height: 32px;
  object-fit: contain;
  border-radius: 4px;
}

.logo-text h2 {
  font-size: 1.125rem;
  font-weight: 700;
  color: white;
  letter-spacing: 0.5px;
  margin: 0;
}

.logo-text p {
  font-size: 0.75rem;
  color: var(--primary-light);
  margin: 0;
  opacity: 0.8;
}

.sidebar-nav {
  flex: 1;
  padding: 1.5rem 0;
  overflow-y: auto;
}

/* Custom Scrollbar for Sidebar */
.sidebar-nav::-webkit-scrollbar {
  width: 5px;
}
.sidebar-nav::-webkit-scrollbar-track {
  background: transparent;
}
.sidebar-nav::-webkit-scrollbar-thumb {
  background-color: rgba(255, 255, 255, 0.2);
  border-radius: 10px;
}
.sidebar-nav::-webkit-scrollbar-thumb:hover {
  background-color: rgba(255, 255, 255, 0.4);
}

.sidebar-nav ul {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  padding: 0 1rem;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  border-radius: var(--radius-md);
  color: rgba(255, 255, 255, 0.7);
  transition: all var(--transition-fast);
}

.nav-item:hover {
  background-color: rgba(255, 255, 255, 0.05);
  color: white;
}

.nav-item.router-link-active {
  background-color: var(--primary-dark);
  color: white;
  border-left: 3px solid var(--accent);
}

.icon {
  width: 20px;
  height: 20px;
}

.nav-divider {
  height: 1px;
  background: rgba(255, 255, 255, 0.1);
  margin: 0.5rem 1rem;
}

.sidebar-footer {
  padding: 1.5rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  font-size: 0.875rem;
  color: rgba(255, 255, 255, 0.5);
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.icon-small {
  width: 14px;
  height: 14px;
}

/* Responsive */
@media (max-width: 1024px) {
  /* Sidebar styles handled globally now for collapsing */
}
</style>
