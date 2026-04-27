import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', name: 'Overview', component: () => import('../views/OverviewPage.vue') },
  { path: '/sync', name: 'SyncCenter', component: () => import('../views/SyncCenterPage.vue') },
  { path: '/branches', name: 'Branches', component: () => import('../views/BranchesPage.vue') },
  { path: '/aspects', name: 'AspectDive', component: () => import('../views/AspectDivePage.vue') },
  { path: '/algorithm', name: 'AlgorithmLab', component: () => import('../views/AlgorithmLabPage.vue') },
  { path: '/explorer', name: 'Explorer', component: () => import('../views/ExplorerPage.vue') },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
