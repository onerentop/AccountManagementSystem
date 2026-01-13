import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/api/auth'
import type { SystemStatus } from '@/types'

export const useAuthStore = defineStore('auth', () => {
  // State
  const token = ref<string | null>(localStorage.getItem('token'))
  const isInitialized = ref(false)
  const isLocked = ref(true)

  // Getters
  const isAuthenticated = computed(() => !!token.value && !isLocked.value)

  // Actions
  async function checkStatus() {
    try {
      const { data } = await authApi.getStatus()
      isInitialized.value = data.is_initialized
      isLocked.value = data.is_locked
      return data
    } catch {
      return null
    }
  }

  async function setup(password: string, confirmPassword: string) {
    const { data } = await authApi.setup(password, confirmPassword)
    return data
  }

  async function login(password: string) {
    const { data } = await authApi.login(password)
    token.value = data.access_token
    isLocked.value = false
    localStorage.setItem('token', data.access_token)
    return data
  }

  async function logout() {
    try {
      await authApi.logout()
    } catch {
      // Ignore errors
    }
    token.value = null
    isLocked.value = true
    localStorage.removeItem('token')
  }

  async function lock() {
    try {
      await authApi.lock()
    } catch {
      // Ignore errors
    }
    isLocked.value = true
  }

  return {
    token,
    isInitialized,
    isLocked,
    isAuthenticated,
    checkStatus,
    setup,
    login,
    logout,
    lock,
  }
})
