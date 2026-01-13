<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50" @click.self="$emit('close')">
    <div class="bg-white dark:bg-gray-800 rounded-xl shadow-xl w-full max-w-sm">
      <!-- Header -->
      <div class="px-6 py-4 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between">
        <h2 class="text-lg font-semibold text-gray-900 dark:text-white">管理标签</h2>
        <button
          @click="$emit('close')"
          class="p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <div class="p-6 space-y-4">
        <!-- Add new tag -->
        <form @submit.prevent="handleCreate" class="flex gap-2">
          <input
            v-model="newTagName"
            type="text"
            placeholder="新标签名称"
            class="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-700 dark:text-white text-sm"
          />
          <input
            v-model="newTagColor"
            type="color"
            class="w-10 h-10 rounded-lg border border-gray-300 dark:border-gray-600 cursor-pointer"
          />
          <button
            type="submit"
            :disabled="!newTagName.trim()"
            class="px-3 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg transition-colors disabled:opacity-50"
          >
            添加
          </button>
        </form>

        <!-- Tag list -->
        <div class="space-y-2 max-h-60 overflow-y-auto">
          <div
            v-for="tag in tagStore.tags"
            :key="tag.id"
            class="flex items-center gap-3 p-2 hover:bg-gray-50 dark:hover:bg-gray-700 rounded-lg"
          >
            <span
              class="w-4 h-4 rounded-full flex-shrink-0"
              :style="{ backgroundColor: tag.color }"
            />
            <span class="flex-1 text-sm text-gray-700 dark:text-gray-300">{{ tag.name }}</span>
            <span class="text-xs text-gray-400">{{ tag.account_count }}</span>
            <button
              @click="handleDelete(tag.id, tag.name)"
              class="p-1 text-gray-400 hover:text-rose-500"
              title="删除"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
            </button>
          </div>
          <p v-if="tagStore.tags.length === 0" class="text-center text-sm text-gray-400 py-4">
            暂无标签
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, inject } from 'vue'
import { useTagStore } from '@/stores/tags'

defineEmits<{
  (e: 'close'): void
}>()

const tagStore = useTagStore()
const showToast = inject('showToast') as (msg: string, type?: 'success' | 'error' | 'info') => void

const newTagName = ref('')
const newTagColor = ref('#6366f1')

async function handleCreate() {
  if (!newTagName.value.trim()) return

  try {
    await tagStore.createTag({
      name: newTagName.value.trim(),
      color: newTagColor.value,
    })
    newTagName.value = ''
    showToast('标签已创建', 'success')
  } catch (e: any) {
    showToast(e.response?.data?.detail || '创建失败', 'error')
  }
}

async function handleDelete(id: string, name: string) {
  if (confirm(`确定要删除标签 "${name}" 吗？`)) {
    try {
      await tagStore.deleteTag(id)
      showToast('标签已删除', 'success')
    } catch {
      showToast('删除失败', 'error')
    }
  }
}
</script>
