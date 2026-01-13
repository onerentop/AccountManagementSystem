<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50" @click.self="$emit('close')">
    <div class="bg-white dark:bg-gray-800 rounded-xl shadow-xl w-full max-w-md">
      <!-- Header -->
      <div class="px-6 py-4 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between">
        <h2 class="text-lg font-semibold text-gray-900 dark:text-white">导入账户</h2>
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
        <!-- File upload -->
        <div
          @dragover.prevent="isDragging = true"
          @dragleave="isDragging = false"
          @drop.prevent="handleDrop"
          :class="[
            'border-2 border-dashed rounded-lg p-8 text-center transition-colors',
            isDragging ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20' : 'border-gray-300 dark:border-gray-600'
          ]"
        >
          <input
            ref="fileInput"
            type="file"
            accept=".xlsx,.xls"
            class="hidden"
            @change="handleFileSelect"
          />
          <svg class="w-12 h-12 mx-auto text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M9 13h6m-3-3v6m5 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <p class="mt-2 text-gray-600 dark:text-gray-400">
            拖拽 Excel 文件到这里，或
            <button
              type="button"
              @click="fileInput?.click()"
              class="text-primary-600 hover:text-primary-700 font-medium"
            >
              点击选择
            </button>
          </p>
          <p class="mt-1 text-xs text-gray-400">支持 .xlsx, .xls 格式</p>
        </div>

        <!-- Selected file -->
        <div v-if="selectedFile" class="flex items-center gap-3 p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
          <svg class="w-8 h-8 text-emerald-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <div class="flex-1 min-w-0">
            <p class="text-sm font-medium text-gray-900 dark:text-white truncate">{{ selectedFile.name }}</p>
            <p class="text-xs text-gray-500">{{ formatFileSize(selectedFile.size) }}</p>
          </div>
          <button
            @click="selectedFile = null"
            class="p-1 text-gray-400 hover:text-gray-600"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <!-- Conflict strategy -->
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            重复账户处理
          </label>
          <div class="space-y-2">
            <label class="flex items-center gap-2">
              <input v-model="conflictStrategy" type="radio" value="skip" class="text-primary-600" />
              <span class="text-sm text-gray-700 dark:text-gray-300">跳过 - 保留已存在的账户</span>
            </label>
            <label class="flex items-center gap-2">
              <input v-model="conflictStrategy" type="radio" value="overwrite" class="text-primary-600" />
              <span class="text-sm text-gray-700 dark:text-gray-300">覆盖 - 用新数据替换</span>
            </label>
            <label class="flex items-center gap-2">
              <input v-model="conflictStrategy" type="radio" value="merge" class="text-primary-600" />
              <span class="text-sm text-gray-700 dark:text-gray-300">合并 - 只填充空字段</span>
            </label>
          </div>
        </div>

        <!-- Result -->
        <div v-if="result" class="p-4 rounded-lg" :class="result.errors.length ? 'bg-amber-50 dark:bg-amber-900/20' : 'bg-emerald-50 dark:bg-emerald-900/20'">
          <p class="font-medium" :class="result.errors.length ? 'text-amber-700 dark:text-amber-400' : 'text-emerald-700 dark:text-emerald-400'">
            导入完成
          </p>
          <div class="mt-2 text-sm text-gray-600 dark:text-gray-400">
            <p>总计: {{ result.total }} 条</p>
            <p>导入: {{ result.imported }} 条</p>
            <p>跳过: {{ result.skipped }} 条</p>
            <div v-if="result.errors.length" class="mt-2">
              <p class="text-amber-700 dark:text-amber-400">错误:</p>
              <ul class="list-disc list-inside text-xs">
                <li v-for="(err, i) in result.errors" :key="i">{{ err }}</li>
              </ul>
            </div>
          </div>
        </div>

        <!-- Error -->
        <div v-if="error" class="text-rose-500 text-sm">{{ error }}</div>

        <!-- Actions -->
        <div class="flex justify-end gap-3 pt-2">
          <button
            v-if="result"
            @click="$emit('imported')"
            class="px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg transition-colors"
          >
            完成
          </button>
          <template v-else>
            <button
              @click="$emit('close')"
              class="px-4 py-2 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
            >
              取消
            </button>
            <button
              @click="handleImport"
              :disabled="!selectedFile || loading"
              class="px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg transition-colors disabled:opacity-50"
            >
              {{ loading ? '导入中...' : '开始导入' }}
            </button>
          </template>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { accountApi } from '@/api/accounts'
import type { ImportResult } from '@/types'

defineEmits<{
  (e: 'close'): void
  (e: 'imported'): void
}>()

const fileInput = ref<HTMLInputElement>()
const selectedFile = ref<File | null>(null)
const conflictStrategy = ref('skip')
const loading = ref(false)
const error = ref('')
const result = ref<ImportResult | null>(null)
const isDragging = ref(false)

function handleFileSelect(e: Event) {
  const input = e.target as HTMLInputElement
  if (input.files?.[0]) {
    selectedFile.value = input.files[0]
    result.value = null
    error.value = ''
  }
}

function handleDrop(e: DragEvent) {
  isDragging.value = false
  const file = e.dataTransfer?.files[0]
  if (file && (file.name.endsWith('.xlsx') || file.name.endsWith('.xls'))) {
    selectedFile.value = file
    result.value = null
    error.value = ''
  } else {
    error.value = '请上传 Excel 文件 (.xlsx, .xls)'
  }
}

function formatFileSize(bytes: number): string {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / 1024 / 1024).toFixed(1) + ' MB'
}

async function handleImport() {
  if (!selectedFile.value) return

  loading.value = true
  error.value = ''

  try {
    const { data } = await accountApi.import(selectedFile.value, conflictStrategy.value)
    result.value = data
  } catch (e: any) {
    error.value = e.response?.data?.detail || '导入失败'
  } finally {
    loading.value = false
  }
}
</script>
