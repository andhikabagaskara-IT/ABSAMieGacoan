<template>
  <header class="app-header">
    <div class="header-title">
      <button class="mobile-toggle" @click="$emit('toggle-sidebar')">
        <Menu class="icon" />
      </button>
      <h1>{{ title }}</h1>
    </div>
    <div class="header-actions">
      <!-- Realtime Clock -->
      <div class="clock-widget">
        <Clock class="icon-small text-primary" />
        <span class="clock-date">{{ currentDate }}</span>
        <span class="clock-time">{{ currentTime }}</span>
      </div>

      <!-- Theme Toggle -->
      <button class="theme-toggle" @click="toggleTheme">
        <Sun v-if="isDark" class="icon text-primary" />
        <Moon v-else class="icon text-primary" />
      </button>

      <!-- User Profile Dropdown -->
      <div class="user-menu-wrapper" @click="toggleDropdown" v-click-outside="closeDropdown">
        <div class="user-profile">
          <img v-if="profileImage" :src="profileImage" alt="Profile" class="avatar-img" />
          <span v-else class="avatar">A</span>
          <span class="user-name">Admin</span>
          <ChevronDown class="icon-tiny" />
        </div>
        
        <transition name="dropdown-anim">
          <div v-if="isDropdownOpen" class="dropdown-menu">
            <router-link to="/profile" class="dropdown-item">
              <User class="icon-small" /> Profil
            </router-link>
            <div class="dropdown-divider"></div>
            <router-link to="/login" class="dropdown-item text-negative" @click="handleLogout">
              <LogOut class="icon-small" /> Keluar
            </router-link>
          </div>
        </transition>
      </div>
    </div>
  </header>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Menu, Moon, Sun, Clock, ChevronDown, User, LogOut } from 'lucide-vue-next'

defineEmits(['toggle-sidebar'])

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

// Clock Logic
const currentDate = ref('')
const currentTime = ref('')
let timer

const updateTime = () => {
  const now = new Date()
  
  // Format Date: Hari, Tanggal Bulan Tahun
  const optionsDate = { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' }
  currentDate.value = now.toLocaleDateString('id-ID', optionsDate)
  
  // Format Time: HH:MM:SS GMT+7
  const hours = String(now.getHours()).padStart(2, '0')
  const minutes = String(now.getMinutes()).padStart(2, '0')
  const seconds = String(now.getSeconds()).padStart(2, '0')
  currentTime.value = `${hours}:${minutes}:${seconds} GMT+7`
}

// Dark Mode Logic
const isDark = ref(false)
const toggleTheme = () => {
  isDark.value = !isDark.value
  document.documentElement.setAttribute('data-theme', isDark.value ? 'dark' : 'light')
  localStorage.setItem('theme', isDark.value ? 'dark' : 'light')
}

// Dropdown Logic
const isDropdownOpen = ref(false)
const toggleDropdown = () => { isDropdownOpen.value = !isDropdownOpen.value }
const closeDropdown = () => { isDropdownOpen.value = false }
const profileImage = ref(localStorage.getItem('profileImage') || '')

const router = useRouter()
const handleLogout = () => {
  localStorage.removeItem('gacoan_user')
  // We can also let the router guard handle it, but explicit routing is better
  router.push('/login')
}

// Click outside directive
const vClickOutside = {
  mounted(el, binding) {
    el.clickOutsideEvent = function(event) {
      if (!(el === event.target || el.contains(event.target))) {
        binding.value(event)
      }
    }
    document.body.addEventListener('click', el.clickOutsideEvent)
  },
  unmounted(el) {
    document.body.removeEventListener('click', el.clickOutsideEvent)
  }
}

onMounted(() => {
  updateTime()
  timer = setInterval(updateTime, 1000)
  
  // Init theme
  const savedTheme = localStorage.getItem('theme') || 'light'
  isDark.value = savedTheme === 'dark'
  document.documentElement.setAttribute('data-theme', savedTheme)
  
  // Listen for profile picture updates
  window.addEventListener('profile-updated', () => {
    profileImage.value = localStorage.getItem('profileImage') || ''
  })
})

onUnmounted(() => {
  clearInterval(timer)
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

.header-title {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.mobile-toggle {
  display: none;
  background: none;
  border: none;
  color: var(--text-primary);
  padding: 0.25rem;
  border-radius: var(--radius-md);
  cursor: pointer;
}

.mobile-toggle:hover {
  background-color: var(--bg-subtle);
}

.mobile-toggle .icon {
  width: 24px;
  height: 24px;
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

.avatar-img {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  object-fit: cover;
}

.icon-tiny {
  width: 14px;
  height: 14px;
  color: var(--text-secondary);
}

/* Clock Widget */
.clock-widget {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background-color: var(--bg-subtle);
  border-radius: var(--radius-md);
  border: 1px solid var(--border);
  font-size: 0.875rem;
}

.clock-date {
  color: var(--text-secondary);
  font-weight: 500;
  margin-right: 0.5rem;
}

.clock-time {
  color: var(--primary-dark);
  font-weight: 700;
  font-family: monospace;
  font-size: 1rem;
}

.icon-small {
  width: 16px;
  height: 16px;
}

/* Theme Toggle */
.theme-toggle {
  background: none;
  border: 1px solid var(--border);
  background-color: var(--bg-subtle);
  padding: 0.5rem;
  border-radius: var(--radius-md);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all var(--transition-fast);
}

.theme-toggle:hover {
  background-color: var(--bg-base);
  border-color: var(--primary-light);
}

/* Dropdown */
.user-menu-wrapper {
  position: relative;
}

.dropdown-menu {
  position: absolute;
  top: calc(100% + 0.5rem);
  right: 0;
  background-color: var(--bg-base);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-md);
  min-width: 180px;
  display: flex;
  flex-direction: column;
  padding: 0.5rem 0;
  z-index: 50;
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  font-size: 0.875rem;
  color: var(--text-primary);
  text-decoration: none;
  transition: background-color var(--transition-fast);
}

.dropdown-item:hover {
  background-color: var(--bg-subtle);
}

.dropdown-divider {
  height: 1px;
  background-color: var(--border);
  margin: 0.25rem 0;
}

.text-negative {
  color: var(--negative);
}

.text-negative:hover {
  background-color: rgba(239, 68, 68, 0.05);
}

.dropdown-anim-enter-active,
.dropdown-anim-leave-active {
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.dropdown-anim-enter-from,
.dropdown-anim-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

/* Responsive */
@media (max-width: 1024px) {
  .mobile-toggle {
    display: flex;
    align-items: center;
    justify-content: center;
  }
  
  .app-header {
    padding: 0 1rem;
  }
  
  .clock-date {
    display: none;
  }
}

@media (max-width: 576px) {
  .user-name, .clock-widget {
    display: none;
  }
}
</style>
