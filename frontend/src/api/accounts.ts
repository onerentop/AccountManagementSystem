import api from './index'
import type { Account, AccountListResponse, AccountCreate, AccountUpdate, ImportResult } from '@/types'

export interface AccountFilters {
  page?: number
  page_size?: number
  search?: string
  source?: string
  tag_ids?: string[]
  gpt_membership?: string
}

export const accountApi = {
  // List accounts
  list: (filters: AccountFilters = {}) => {
    const params = new URLSearchParams()
    if (filters.page) params.append('page', filters.page.toString())
    if (filters.page_size) params.append('page_size', filters.page_size.toString())
    if (filters.search) params.append('search', filters.search)
    if (filters.source) params.append('source', filters.source)
    if (filters.tag_ids?.length) params.append('tag_ids', filters.tag_ids.join(','))
    if (filters.gpt_membership) params.append('gpt_membership', filters.gpt_membership)
    return api.get<AccountListResponse>(`/accounts?${params.toString()}`)
  },

  // Get single account
  get: (id: string) => api.get<Account>(`/accounts/${id}`),

  // Get password
  getPassword: (id: string) => api.get<{ password: string | null }>(`/accounts/${id}/password`),

  // Get TOTP
  getTotp: (id: string) => api.get<{ totp_secret: string | null }>(`/accounts/${id}/totp`),

  // Create account
  create: (data: AccountCreate) => api.post<Account>('/accounts', data),

  // Update account
  update: (id: string, data: AccountUpdate) => api.put<Account>(`/accounts/${id}`, data),

  // Delete account
  delete: (id: string, hard = false) => api.delete(`/accounts/${id}?hard=${hard}`),

  // Get sources
  getSources: () => api.get<string[]>('/accounts/sources'),

  // Get stats
  getStats: () => api.get<{ total: number; with_gpt_membership: number; by_source: Record<string, number> }>('/accounts/stats'),

  // Import from Excel
  import: (file: File, conflictStrategy = 'skip') => {
    const formData = new FormData()
    formData.append('file', file)
    // Let axios handle Content-Type automatically for FormData (includes boundary)
    return api.post<ImportResult>(`/accounts/import?conflict_strategy=${conflictStrategy}`, formData)
  },

  // Export - uses axios to include auth header
  export: async (format = 'excel', includePassword = false, accountIds?: string[]) => {
    const params = new URLSearchParams()
    params.append('format', format)
    params.append('include_password', includePassword.toString())
    if (accountIds?.length) params.append('account_ids', accountIds.join(','))

    const response = await api.get(`/accounts/export/download?${params.toString()}`, {
      responseType: 'blob'
    })

    // Get filename from Content-Disposition header or use default
    const contentDisposition = response.headers['content-disposition']
    let filename = `accounts.${format === 'excel' ? 'xlsx' : format}`
    if (contentDisposition) {
      const match = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/)
      if (match?.[1]) {
        filename = match[1].replace(/['"]/g, '')
      }
    }

    // Create download link
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', filename)
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)
  },

  // Batch operations
  batchDelete: (accountIds: string[], hard = false) =>
    api.post<{ deleted: number; failed: number }>(`/accounts/batch/delete?hard=${hard}`, { account_ids: accountIds }),

  batchUpdateTags: (accountIds: string[], tagIds: string[], action: 'add' | 'remove' | 'set' = 'add') =>
    api.post<{ updated: number; failed: number }>(
      `/accounts/batch/tags?action=${action}`,
      { account_ids: accountIds, tag_ids: tagIds }
    ),

  batchUpdate: (accountIds: string[], data: Partial<AccountUpdate>) =>
    api.post<{ updated: number; failed: number }>('/accounts/batch/update', {
      account_ids: accountIds,
      ...data,
    }),
}
