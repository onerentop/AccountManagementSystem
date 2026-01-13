<template>
  <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm overflow-hidden">
    <!-- Loading state -->
    <div v-if="accountStore.loading" class="p-8 text-center">
      <svg class="animate-spin h-8 w-8 mx-auto text-primary-500" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
      </svg>
      <p class="mt-2 text-gray-500 dark:text-gray-400">加载中...</p>
    </div>

    <!-- Empty state -->
    <div v-else-if="accountStore.accounts.length === 0" class="p-8 text-center">
      <svg class="w-16 h-16 mx-auto text-gray-300 dark:text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
      </svg>
      <p class="mt-4 text-gray-500 dark:text-gray-400">暂无账户</p>
      <p class="text-sm text-gray-400 dark:text-gray-500">点击右上角添加账户或导入 Excel</p>
    </div>

    <!-- Table -->
    <div v-else class="overflow-x-auto">
      <table class="w-full">
        <thead class="bg-gray-50 dark:bg-gray-700">
          <tr>
            <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">账号</th>
            <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">密码</th>
            <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">来源</th>
            <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">标签</th>
            <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">备注</th>
            <th class="px-4 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">操作</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-200 dark:divide-gray-700">
          <tr
            v-for="account in accountStore.accounts"
            :key="account.id"
            class="hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors"
          >
            <!-- Email -->
            <td class="px-4 py-3">
              <div class="flex items-center gap-2">
                <button
                  @click="$emit('copy', account.email, '账号')"
                  class="text-sm font-medium text-gray-900 dark:text-white hover:text-primary-600 dark:hover:text-primary-400 transition-colors"
                >
                  {{ account.email }}
                </button>
                <button
                  @click="$emit('copy', account.email, '账号')"
                  class="p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200"
                  title="复制账号"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                  </svg>
                </button>
              </div>
            </td>

            <!-- Password -->
            <td class="px-4 py-3">
              <div class="flex items-center gap-2">
                <span class="text-sm text-gray-500 dark:text-gray-400">
                  {{ visiblePasswords[account.id] || (account.has_password ? '••••••••' : '-') }}
                </span>
                <button
                  v-if="account.has_password"
                  @click="togglePassword(account.id)"
                  class="p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200"
                  :title="visiblePasswords[account.id] ? '隐藏密码' : '显示密码'"
                >
                  <svg v-if="visiblePasswords[account.id]" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
                  </svg>
                  <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                  </svg>
                </button>
                <button
                  v-if="account.has_password"
                  @click="copyPassword(account.id)"
                  class="p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200"
                  title="复制密码"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                  </svg>
                </button>
              </div>
            </td>

            <!-- Source -->
            <td class="px-4 py-3">
              <span class="text-sm text-gray-600 dark:text-gray-400">
                {{ account.source || '-' }}
              </span>
            </td>

            <!-- Tags -->
            <td class="px-4 py-3">
              <div class="flex flex-wrap gap-1">
                <span
                  v-for="tag in account.tags"
                  :key="tag.id"
                  class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium"
                  :style="{ backgroundColor: tag.color + '20', color: tag.color }"
                >
                  {{ tag.name }}
                </span>
                <span v-if="account.tags.length === 0" class="text-sm text-gray-400">-</span>
              </div>
            </td>

            <!-- Note -->
            <td class="px-4 py-3">
              <span class="text-sm text-gray-600 dark:text-gray-400 truncate max-w-[200px] block">
                {{ account.note || '-' }}
              </span>
            </td>

            <!-- Actions -->
            <td class="px-4 py-3 text-right">
              <div class="flex items-center justify-end gap-1">
                <button
                  @click="$emit('edit', account)"
                  class="p-1.5 text-gray-400 hover:text-primary-600 dark:hover:text-primary-400 hover:bg-gray-100 dark:hover:bg-gray-700 rounded transition-colors"
                  title="编辑"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                  </svg>
                </button>
                <button
                  @click="$emit('delete', account)"
                  class="p-1.5 text-gray-400 hover:text-rose-600 dark:hover:text-rose-400 hover:bg-gray-100 dark:hover:bg-gray-700 rounded transition-colors"
                  title="删除"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Pagination -->
    <div v-if="accountStore.totalPages > 1" class="px-4 py-3 border-t border-gray-200 dark:border-gray-700 flex items-center justify-between">
      <div class="text-sm text-gray-500 dark:text-gray-400">
        共 {{ accountStore.total }} 条，第 {{ accountStore.page }} / {{ accountStore.totalPages }} 页
      </div>
      <div class="flex items-center gap-2">
        <button
          :disabled="accountStore.page <= 1"
          @click="accountStore.setPage(accountStore.page - 1)"
          class="px-3 py-1 border border-gray-300 dark:border-gray-600 rounded text-sm disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50 dark:hover:bg-gray-700"
        >
          上一页
        </button>
        <button
          :disabled="accountStore.page >= accountStore.totalPages"
          @click="accountStore.setPage(accountStore.page + 1)"
          class="px-3 py-1 border border-gray-300 dark:border-gray-600 rounded text-sm disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50 dark:hover:bg-gray-700"
        >
          下一页
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, inject } from 'vue'
import { useAccountStore } from '@/stores/accounts'
import type { Account } from '@/types'

defineEmits<{
  (e: 'edit', account: Account): void
  (e: 'delete', account: Account): void
  (e: 'copy', text: string, type: string): void
}>()

const accountStore = useAccountStore()
const showToast = inject('showToast') as (msg: string, type?: 'success' | 'error' | 'info') => void

const visiblePasswords = ref<Record<string, string>>({})

async function togglePassword(accountId: string) {
  if (visiblePasswords.value[accountId]) {
    delete visiblePasswords.value[accountId]
  } else {
    try {
      const password = await accountStore.getPassword(accountId)
      if (password) {
        visiblePasswords.value[accountId] = password
      }
    } catch {
      showToast('获取密码失败', 'error')
    }
  }
}

async function copyPassword(accountId: string) {
  try {
    let password = visiblePasswords.value[accountId]
    if (!password) {
      password = await accountStore.getPassword(accountId) || ''
    }
    if (password) {
      await navigator.clipboard.writeText(password)
      showToast('密码已复制，30秒后自动清除', 'success')

      setTimeout(async () => {
        const current = await navigator.clipboard.readText()
        if (current === password) {
          await navigator.clipboard.writeText('')
        }
      }, 30000)
    }
  } catch {
    showToast('复制失败', 'error')
  }
}
</script>
