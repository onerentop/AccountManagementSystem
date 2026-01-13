import api from './index'
import type { Tag } from '@/types'

export interface TagCreate {
  name: string
  color?: string
}

export interface TagUpdate {
  name?: string
  color?: string
}

export const tagApi = {
  // List all tags
  list: () => api.get<Tag[]>('/tags'),

  // Get single tag
  get: (id: string) => api.get<Tag>(`/tags/${id}`),

  // Create tag
  create: (data: TagCreate) => api.post<Tag>('/tags', data),

  // Update tag
  update: (id: string, data: TagUpdate) => api.put<Tag>(`/tags/${id}`, data),

  // Delete tag
  delete: (id: string) => api.delete(`/tags/${id}`),
}
