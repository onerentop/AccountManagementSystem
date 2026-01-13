/**
 * Tests for accounts store
 */
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useAccountStore } from '@/stores/accounts'

// Mock the accounts API
vi.mock('@/api/accounts', () => ({
  accountApi: {
    list: vi.fn(),
    getSources: vi.fn(),
    getStats: vi.fn(),
    create: vi.fn(),
    update: vi.fn(),
    delete: vi.fn(),
    getPassword: vi.fn(),
    getTotp: vi.fn(),
  },
}))

import { accountApi } from '@/api/accounts'

const mockAccount = {
  id: '1',
  email: 'test@example.com',
  note: 'Test note',
  sub2api: false,
  source: '购买',
  browser: null,
  gpt_membership: null,
  family_group: null,
  recovery_email: null,
  has_password: true,
  has_totp: false,
  tags: [],
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-01T00:00:00Z',
}

describe('Account Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  describe('Initial State', () => {
    it('should have correct initial state', () => {
      const store = useAccountStore()

      expect(store.accounts).toEqual([])
      expect(store.total).toBe(0)
      expect(store.page).toBe(1)
      expect(store.pageSize).toBe(20)
      expect(store.loading).toBe(false)
    })
  })

  describe('fetchAccounts', () => {
    it('should fetch and store accounts', async () => {
      const store = useAccountStore()
      vi.mocked(accountApi.list).mockResolvedValue({
        data: {
          items: [mockAccount],
          total: 1,
          page: 1,
          page_size: 20,
          total_pages: 1,
        },
      } as any)

      await store.fetchAccounts()

      expect(store.accounts).toHaveLength(1)
      expect(store.accounts[0].email).toBe('test@example.com')
      expect(store.total).toBe(1)
    })

    it('should set loading state during fetch', async () => {
      const store = useAccountStore()
      let loadingDuringFetch = false

      vi.mocked(accountApi.list).mockImplementation(async () => {
        loadingDuringFetch = store.loading
        return {
          data: { items: [], total: 0, page: 1, page_size: 20, total_pages: 1 },
        } as any
      })

      await store.fetchAccounts()

      expect(loadingDuringFetch).toBe(true)
      expect(store.loading).toBe(false)
    })

    it('should apply filters', async () => {
      const store = useAccountStore()
      vi.mocked(accountApi.list).mockResolvedValue({
        data: { items: [], total: 0, page: 1, page_size: 20, total_pages: 1 },
      } as any)

      await store.fetchAccounts({ search: 'test', source: '购买' })

      expect(accountApi.list).toHaveBeenCalledWith(
        expect.objectContaining({
          search: 'test',
          source: '购买',
        })
      )
    })
  })

  describe('fetchSources', () => {
    it('should fetch and store sources', async () => {
      const store = useAccountStore()
      vi.mocked(accountApi.getSources).mockResolvedValue({
        data: ['购买', '注册', '赠送'],
      } as any)

      await store.fetchSources()

      expect(store.sources).toEqual(['购买', '注册', '赠送'])
    })
  })

  describe('fetchStats', () => {
    it('should fetch and store stats', async () => {
      const store = useAccountStore()
      const mockStats = { total: 10, with_gpt_membership: 5, by_source: { '购买': 7 } }
      vi.mocked(accountApi.getStats).mockResolvedValue({
        data: mockStats,
      } as any)

      await store.fetchStats()

      expect(store.stats).toEqual(mockStats)
    })
  })

  describe('createAccount', () => {
    it('should create account and refresh list', async () => {
      const store = useAccountStore()
      vi.mocked(accountApi.create).mockResolvedValue({
        data: mockAccount,
      } as any)
      vi.mocked(accountApi.list).mockResolvedValue({
        data: { items: [mockAccount], total: 1, page: 1, page_size: 20, total_pages: 1 },
      } as any)

      const result = await store.createAccount({ email: 'test@example.com' })

      expect(result.email).toBe('test@example.com')
      expect(accountApi.list).toHaveBeenCalled() // Refreshes list
    })
  })

  describe('updateAccount', () => {
    it('should update account in store', async () => {
      const store = useAccountStore()
      store.accounts = [mockAccount]
      const updatedAccount = { ...mockAccount, note: 'Updated note' }
      vi.mocked(accountApi.update).mockResolvedValue({
        data: updatedAccount,
      } as any)

      await store.updateAccount('1', { note: 'Updated note' })

      expect(store.accounts[0].note).toBe('Updated note')
    })
  })

  describe('deleteAccount', () => {
    it('should delete account and refresh list', async () => {
      const store = useAccountStore()
      vi.mocked(accountApi.delete).mockResolvedValue({} as any)
      vi.mocked(accountApi.list).mockResolvedValue({
        data: { items: [], total: 0, page: 1, page_size: 20, total_pages: 1 },
      } as any)

      await store.deleteAccount('1')

      expect(accountApi.delete).toHaveBeenCalledWith('1')
      expect(accountApi.list).toHaveBeenCalled()
    })
  })

  describe('getPassword', () => {
    it('should fetch decrypted password', async () => {
      const store = useAccountStore()
      vi.mocked(accountApi.getPassword).mockResolvedValue({
        data: { password: 'secret123' },
      } as any)

      const password = await store.getPassword('1')

      expect(password).toBe('secret123')
    })
  })

  describe('getTotp', () => {
    it('should fetch decrypted TOTP', async () => {
      const store = useAccountStore()
      vi.mocked(accountApi.getTotp).mockResolvedValue({
        data: { totp_secret: 'JBSWY3DPEHPK3PXP' },
      } as any)

      const totp = await store.getTotp('1')

      expect(totp).toBe('JBSWY3DPEHPK3PXP')
    })
  })

  describe('Pagination', () => {
    it('setPage should update page and fetch', async () => {
      const store = useAccountStore()
      vi.mocked(accountApi.list).mockResolvedValue({
        data: { items: [], total: 0, page: 2, page_size: 20, total_pages: 1 },
      } as any)

      store.setPage(2)

      expect(store.page).toBe(2)
      expect(accountApi.list).toHaveBeenCalled()
    })

    it('setPageSize should reset to page 1', async () => {
      const store = useAccountStore()
      store.page = 5
      vi.mocked(accountApi.list).mockResolvedValue({
        data: { items: [], total: 0, page: 1, page_size: 50, total_pages: 1 },
      } as any)

      store.setPageSize(50)

      expect(store.page).toBe(1)
      expect(store.pageSize).toBe(50)
    })
  })

  describe('resetFilters', () => {
    it('should clear filters and reset page', async () => {
      const store = useAccountStore()
      store.filters = { search: 'test', source: '购买' }
      store.page = 3
      vi.mocked(accountApi.list).mockResolvedValue({
        data: { items: [], total: 0, page: 1, page_size: 20, total_pages: 1 },
      } as any)

      store.resetFilters()

      expect(store.filters).toEqual({})
      expect(store.page).toBe(1)
    })
  })
})
