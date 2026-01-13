import { defineStore } from 'pinia'
import { ref } from 'vue'
import { tagApi, type TagCreate, type TagUpdate } from '@/api/tags'
import type { Tag } from '@/types'

export const useTagStore = defineStore('tags', () => {
  const tags = ref<Tag[]>([])
  const loading = ref(false)

  async function fetchTags() {
    loading.value = true
    try {
      const { data } = await tagApi.list()
      tags.value = data
    } finally {
      loading.value = false
    }
  }

  async function createTag(data: TagCreate) {
    const { data: tag } = await tagApi.create(data)
    tags.value.push(tag)
    return tag
  }

  async function updateTag(id: string, data: TagUpdate) {
    const { data: tag } = await tagApi.update(id, data)
    const index = tags.value.findIndex(t => t.id === id)
    if (index >= 0) {
      tags.value[index] = tag
    }
    return tag
  }

  async function deleteTag(id: string) {
    await tagApi.delete(id)
    tags.value = tags.value.filter(t => t.id !== id)
  }

  return {
    tags,
    loading,
    fetchTags,
    createTag,
    updateTag,
    deleteTag,
  }
})
