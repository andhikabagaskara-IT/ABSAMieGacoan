import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { 
    path: '/login', 
    name: 'Login', 
    component: () => import('../views/LoginPage.vue'),
    meta: { requiresAuth: false, hideLayout: true }
  },
  { path: '/', name: 'Overview', component: () => import('../views/OverviewPage.vue') },
  { path: '/sync', name: 'SyncCenter', component: () => import('../views/SyncCenterPage.vue') },
  { path: '/branches', name: 'Branches', component: () => import('../views/BranchesPage.vue') },
  { path: '/aspects', name: 'AspectDive', component: () => import('../views/AspectDivePage.vue') },
  { path: '/algorithm', name: 'AlgorithmLab', component: () => import('../views/AlgorithmLabPage.vue') },
  { path: '/explorer', name: 'Explorer', component: () => import('../views/ExplorerPage.vue') },
  { path: '/profile', name: 'Profile', component: () => import('../views/ProfilePage.vue') },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// Navigation Guard — redirect to login if not authenticated
router.beforeEach((to, from, next) => {
  const isAuthenticated = !!localStorage.getItem('gacoan_user')
  
  if (to.path === '/login' && isAuthenticated) {
    // Already logged in, go to dashboard
    next('/')
  } else if (to.path !== '/login' && !isAuthenticated) {
    // Not logged in, redirect to login
    next('/login')
  } else {
    next()
  }
})

export default router
