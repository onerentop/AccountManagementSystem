import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/LoginView.vue'),
      meta: { guest: true },
    },
    {
      path: '/setup',
      name: 'setup',
      component: () => import('@/views/SetupView.vue'),
      meta: { guest: true },
    },
    {
      path: '/',
      name: 'home',
      component: () => import('@/views/HomeView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/settings',
      name: 'settings',
      component: () => import('@/views/SettingsView.vue'),
      meta: { requiresAuth: true },
    },
  ],
})

// Navigation guard
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()

  // Check system status on first load
  if (!authStore.isInitialized || authStore.isLocked) {
    await authStore.checkStatus()
  }

  // Redirect to setup if not initialized
  if (!authStore.isInitialized && to.name !== 'setup') {
    return next({ name: 'setup' })
  }

  // Redirect to login if locked
  if (to.meta.requiresAuth && authStore.isLocked) {
    return next({ name: 'login' })
  }

  // Redirect to home if already authenticated
  if (to.meta.guest && authStore.isAuthenticated) {
    return next({ name: 'home' })
  }

  next()
})

export default router
