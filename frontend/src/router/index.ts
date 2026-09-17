import { createRouter, createWebHashHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'

const routes = [
  { path: '/', name: 'home', component: () => import('@/views/HomeView.vue') },
  { path: '/login', name: 'login', component: () => import('@/views/LoginView.vue') },
  {
    path: '/create',
    name: 'create',
    component: () => import('@/views/TripCreateView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/trips',
    name: 'trips',
    component: () => import('@/views/TripsView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/trips/:id',
    name: 'trip-detail',
    component: () => import('@/views/TripDetailView.vue'),
    meta: { requiresAuth: true },
  },
]

const router = createRouter({
  history: createWebHashHistory(),
  routes,
})

router.beforeEach(async (to) => {
  const store = useUserStore()
  if (to.meta.requiresAuth) {
    if (!store.token) return { name: 'login', query: { redirect: to.fullPath } }
    if (!store.user) {
      const ok = await store.fetchMe()
      if (!ok) return { name: 'login', query: { redirect: to.fullPath } }
    }
  }
  return true
})

export default router
