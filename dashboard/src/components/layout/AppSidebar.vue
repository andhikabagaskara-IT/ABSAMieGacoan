<template>
  <aside class="sidebar">
    <div class="sidebar-header">
      <div class="logo">
        <span class="logo-icon">🍜</span>
        <div class="logo-text">
          <h2>GACOAN INSIGHT</h2>
          <p>Sentiment Platform</p>
        </div>
      </div>
    </div>
    
    <nav class="sidebar-nav">
      <ul>
        <li>
          <router-link to="/" class="nav-item">
            <LayoutDashboard class="icon" />
            <span>Overview</span>
          </router-link>
        </li>
        <li>
          <router-link to="/sync" class="nav-item">
            <RefreshCw class="icon" />
            <span>Sync Center</span>
          </router-link>
        </li>
        <li>
          <router-link to="/branches" class="nav-item">
            <Store class="icon" />
            <span>Analisis Cabang</span>
          </router-link>
        </li>
        <li>
          <router-link to="/aspects" class="nav-item">
            <PieChart class="icon" />
            <span>Aspek Deep Dive</span>
          </router-link>
        </li>
        <li>
          <router-link to="/algorithm" class="nav-item">
            <FlaskConical class="icon" />
            <span>Algorithm Lab</span>
          </router-link>
        </li>
        <li>
          <router-link to="/explorer" class="nav-item">
            <Database class="icon" />
            <span>Data Explorer</span>
          </router-link>
        </li>
      </ul>
    </nav>
    
    <div class="sidebar-footer">
      <div class="stat-item">
        <TrendingUp class="icon-small" />
        <span>51.885 Ulasan</span>
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
  TrendingUp,
  Clock
} from 'lucide-vue-next'
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
</style>
