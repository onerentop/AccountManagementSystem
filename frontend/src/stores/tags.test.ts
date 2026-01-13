/**
 * Tests for tags store
 */
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useTagStore } from '@/stores/tags'

// Mock the tags API
vi.mock('@/api/tags', () => ({
  tagApi: {
    list: vi.fn(),
    create: vi.fn(),
    update: vi.fn(),
    delete: vi.fn(),
  },
}))

import { tagApi } from '@/api/tags'

const mockTag = {
  id: '1',
  name: 'Test Tag',
  color: '#6366f1',
  created_at: '2024-01-01T00:00:00Z',
  account_count: 5,
}

describe('Tag Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  describe('Initial State', () => {
    it('should have correct initial state', () => {
      const store = useTagStore()

      expect(store.tags).toEqual([])
      expect(store.loading).toBe(false)
    })
  })

  describe('fetchTags', () => {
    it('should fetch and store tags', async () => {
      const store = useTagStore()
      vi.mocked(tagApi.list).mockResolvedValue({
        data: [mockTag],
      } as any)

      await store.fetchTags()

      expect(store.tags).toHaveLength(1)
      expect(store.tags[0].name).toBe('Test Tag')
    })

    it('should set loading state during fetch', async () => {
      const store = useTagStore()
      let loadingDuringFetch = false

      vi.mocked(tagApi.list).mockImplementation(async () => {
        loadingDuringFetch = store.loading
        return { data: [] } as any
      })

      await store.fetchTags()

      expect(loadingDuringFetch).toBe(true)
      expect(store.loading).toBe(false)
    })
  })

  describe('createTag', () => {
    it('should create tag and add to store', async () => {
      const store = useTagStore()
      vi.mocked(tagApi.create).mockResolvedValue({
        data: mockTag,
      } as any)

      const result = await store.createTag({ name: 'Test Tag' })

      expect(result.name).toBe('Test Tag')
      expect(store.tags).toHaveLength(1)
      expect(store.tags[0].name).toBe('Test Tag')
    })
  })

  describe('updateTag', () => {
    it('should update tag in store', async () => {
      const store = useTagStore()
      store.tags = [mockTag]
      const updatedTag = { ...mockTag, name: 'Updated Tag' }
      vi.mocked(tagApi.update).mockResolvedValue({
        data: updatedTag,
      } as any)

      await store.updateTag('1', { name: 'Updated Tag' })

      expect(store.tags[0].name).toBe('Updated Tag')
    })

    it('should not fail if tag not found in store', async () => {
      const store = useTagStore()
      store.tags = [mockTag]
      const updatedTag = { ...mockTag, id: '999', name: 'Updated Tag' }
      vi.mocked(tagApi.update).mockResolvedValue({
        data: updatedTag,
      } as any)

      // Should not throw
      await store.updateTag('999', { name: 'Updated Tag' })
    })
  })

  describe('deleteTag', () => {
    it('should remove tag from store', async () => {
      const store = useTagStore()
      store.tags = [mockTag, { ...mockTag, id: '2', name: 'Another Tag' }]
      vi.mocked(tagApi.delete).mockResolvedValue({} as any)

      await store.deleteTag('1')

      expect(store.tags).toHaveLength(1)
      expect(store.tags[0].id).toBe('2')
    })
  })
})
