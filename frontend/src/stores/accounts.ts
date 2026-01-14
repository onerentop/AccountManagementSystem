import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { accountApi, type AccountFilters } from '@/api/accounts'
import type { Account, AccountCreate, AccountUpdate } from '@/types'

export const useAccountStore = defineStore('accounts', () => {
  // State
  const accounts = ref<Account[]>([])
  const total = ref(0)
  const page = ref(1)
  const pageSize = ref(20)
  const totalPages = ref(1)
  const loading = ref(false)
  const filters = ref<AccountFilters>({})
  const sources = ref<string[]>([])
  const stats = ref<{ total: number; with_gpt_membership: number; by_source: Record<string, number> } | null>(null)

  // Current editing account
  const currentAccount = ref<Account | null>(null)

  // Selection state for batch operations
  const selectedIds = ref<Set<string>>(new Set())

  // Computed
  const selectedCount = computed(() => selectedIds.value.size)
  const isAllSelected = computed(() =>
    accounts.value.length > 0 && selectedIds.value.size === accounts.value.length
  )
  const selectedAccounts = computed(() =>
    accounts.value.filter(a => selectedIds.value.has(a.id))
  )

  // Actions
  async function fetchAccounts(newFilters?: AccountFilters) {
    loading.value = true
    try {
      if (newFilters) {
        filters.value = { ...filters.value, ...newFilters }
      }
      const { data } = await accountApi.list({
        ...filters.value,
        page: page.value,
        page_size: pageSize.value,
      })
      accounts.value = data.items
      total.value = data.total
      totalPages.value = data.total_pages
    } finally {
      loading.value = false
    }
  }

  async function fetchSources() {
    const { data } = await accountApi.getSources()
    sources.value = data
  }

  async function fetchStats() {
    const { data } = await accountApi.getStats()
    stats.value = data
  }

  async function createAccount(data: AccountCreate) {
    const { data: account } = await accountApi.create(data)
    await fetchAccounts()
    return account
  }

  async function updateAccount(id: string, data: AccountUpdate) {
    const { data: account } = await accountApi.update(id, data)
    const index = accounts.value.findIndex(a => a.id === id)
    if (index >= 0) {
      accounts.value[index] = account
    }
    return account
  }

  async function deleteAccount(id: string) {
    await accountApi.delete(id)
    await fetchAccounts()
  }

  async function getPassword(id: string) {
    const { data } = await accountApi.getPassword(id)
    return data.password
  }

  async function getTotp(id: string) {
    const { data } = await accountApi.getTotp(id)
    return data.totp_secret
  }

  function setPage(newPage: number) {
    page.value = newPage
    fetchAccounts()
  }

  function setPageSize(size: number) {
    pageSize.value = size
    page.value = 1
    fetchAccounts()
  }

  function resetFilters() {
    filters.value = {}
    page.value = 1
    fetchAccounts()
  }

  // Selection methods
  function toggleSelect(id: string) {
    if (selectedIds.value.has(id)) {
      selectedIds.value.delete(id)
    } else {
      selectedIds.value.add(id)
    }
    // Trigger reactivity
    selectedIds.value = new Set(selectedIds.value)
  }

  function toggleSelectAll() {
    if (isAllSelected.value) {
      selectedIds.value = new Set()
    } else {
      selectedIds.value = new Set(accounts.value.map(a => a.id))
    }
  }

  function clearSelection() {
    selectedIds.value = new Set()
  }

  function isSelected(id: string) {
    return selectedIds.value.has(id)
  }

  // Batch operations
  async function batchDelete() {
    if (selectedIds.value.size === 0) return { deleted: 0, failed: 0 }
    const ids = Array.from(selectedIds.value)
    const { data } = await accountApi.batchDelete(ids)
    clearSelection()
    await fetchAccounts()
    return data
  }

  async function batchUpdateTags(tagIds: string[], action: 'add' | 'remove' | 'set' = 'add') {
    if (selectedIds.value.size === 0) return { updated: 0, failed: 0 }
    const ids = Array.from(selectedIds.value)
    const { data } = await accountApi.batchUpdateTags(ids, tagIds, action)
    await fetchAccounts()
    return data
  }

  async function exportAccounts(format = 'excel', includePassword = false) {
    const ids = selectedIds.value.size > 0 ? Array.from(selectedIds.value) : undefined
    await accountApi.export(format, includePassword, ids)
  }

  return {
    accounts,
    total,
    page,
    pageSize,
    totalPages,
    loading,
    filters,
    sources,
    stats,
    currentAccount,
    // Selection
    selectedIds,
    selectedCount,
    isAllSelected,
    selectedAccounts,
    toggleSelect,
    toggleSelectAll,
    clearSelection,
    isSelected,
    // Actions
    fetchAccounts,
    fetchSources,
    fetchStats,
    createAccount,
    updateAccount,
    deleteAccount,
    getPassword,
    getTotp,
    setPage,
    setPageSize,
    resetFilters,
    // Batch
    batchDelete,
    batchUpdateTags,
    exportAccounts,
  }
})
