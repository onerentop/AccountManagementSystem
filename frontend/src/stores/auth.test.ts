/**
 * Tests for auth store
 */
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useAuthStore } from '@/stores/auth'

// Mock the auth API
vi.mock('@/api/auth', () => ({
  authApi: {
    getStatus: vi.fn(),
    setup: vi.fn(),
    login: vi.fn(),
    logout: vi.fn(),
    lock: vi.fn(),
  },
}))

import { authApi } from '@/api/auth'

describe('Auth Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  describe('Initial State', () => {
    it('should have correct initial state', () => {
      const store = useAuthStore()

      expect(store.token).toBeNull()
      expect(store.isInitialized).toBe(false)
      expect(store.isLocked).toBe(true)
    })

    it('should not be authenticated initially', () => {
      const store = useAuthStore()

      expect(store.isAuthenticated).toBe(false)
    })
  })

  describe('checkStatus', () => {
    it('should update state from API response', async () => {
      const store = useAuthStore()
      vi.mocked(authApi.getStatus).mockResolvedValue({
        data: { is_initialized: true, is_locked: false },
      } as any)

      const result = await store.checkStatus()

      expect(result).toEqual({ is_initialized: true, is_locked: false })
      expect(store.isInitialized).toBe(true)
      expect(store.isLocked).toBe(false)
    })

    it('should return null on error', async () => {
      const store = useAuthStore()
      vi.mocked(authApi.getStatus).mockRejectedValue(new Error('Network error'))

      const result = await store.checkStatus()

      expect(result).toBeNull()
    })
  })

  describe('setup', () => {
    it('should call setup API', async () => {
      const store = useAuthStore()
      vi.mocked(authApi.setup).mockResolvedValue({
        data: { message: 'Success' },
      } as any)

      const result = await store.setup('password123', 'password123')

      expect(authApi.setup).toHaveBeenCalledWith('password123', 'password123')
      expect(result).toEqual({ message: 'Success' })
    })
  })

  describe('login', () => {
    it('should store token and update state on success', async () => {
      const store = useAuthStore()
      const mockToken = 'test-jwt-token'
      vi.mocked(authApi.login).mockResolvedValue({
        data: { access_token: mockToken, expires_in: 3600 },
      } as any)

      await store.login('password123')

      expect(store.token).toBe(mockToken)
      expect(store.isLocked).toBe(false)
      // Note: localStorage.setItem is called but we verify state instead
    })

    it('should be authenticated after login', async () => {
      const store = useAuthStore()
      vi.mocked(authApi.login).mockResolvedValue({
        data: { access_token: 'token', expires_in: 3600 },
      } as any)

      await store.login('password123')

      expect(store.isAuthenticated).toBe(true)
    })
  })

  describe('logout', () => {
    it('should clear token and lock application', async () => {
      const store = useAuthStore()
      store.token = 'existing-token'
      store.isLocked = false
      vi.mocked(authApi.logout).mockResolvedValue({} as any)

      await store.logout()

      expect(store.token).toBeNull()
      expect(store.isLocked).toBe(true)
      // Note: localStorage.removeItem is called but we verify state instead
    })

    it('should clear state even if API fails', async () => {
      const store = useAuthStore()
      store.token = 'existing-token'
      vi.mocked(authApi.logout).mockRejectedValue(new Error('Network error'))

      await store.logout()

      expect(store.token).toBeNull()
      expect(store.isLocked).toBe(true)
    })
  })

  describe('lock', () => {
    it('should set isLocked to true', async () => {
      const store = useAuthStore()
      store.isLocked = false
      vi.mocked(authApi.lock).mockResolvedValue({} as any)

      await store.lock()

      expect(store.isLocked).toBe(true)
    })

    it('should lock even if API fails', async () => {
      const store = useAuthStore()
      store.isLocked = false
      vi.mocked(authApi.lock).mockRejectedValue(new Error('Network error'))

      await store.lock()

      expect(store.isLocked).toBe(true)
    })
  })

  describe('isAuthenticated computed', () => {
    it('should be false when no token', () => {
      const store = useAuthStore()
      store.token = null
      store.isLocked = false

      expect(store.isAuthenticated).toBe(false)
    })

    it('should be false when locked', () => {
      const store = useAuthStore()
      store.token = 'valid-token'
      store.isLocked = true

      expect(store.isAuthenticated).toBe(false)
    })

    it('should be true when has token and not locked', () => {
      const store = useAuthStore()
      store.token = 'valid-token'
      store.isLocked = false

      expect(store.isAuthenticated).toBe(true)
    })
  })
})
