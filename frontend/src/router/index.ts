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
let statusChecked = false

router.beforeEach(async (to, _from, next) => {
  const authStore = useAuthStore()

  // Check system status only once on first load
  if (!statusChecked) {
    await authStore.checkStatus()
    statusChecked = true
  }

  // Redirect to setup if not initialized
  if (!authStore.isInitialized && to.name !== 'setup') {
    return next({ name: 'setup' })
  }

  // Redirect to login if locked and trying to access protected route
  if (to.meta.requiresAuth && authStore.isLocked && !authStore.token) {
    return next({ name: 'login' })
  }

  // Redirect to home if already authenticated
  if (to.meta.guest && authStore.isAuthenticated) {
    return next({ name: 'home' })
  }

  next()
})

export default router
