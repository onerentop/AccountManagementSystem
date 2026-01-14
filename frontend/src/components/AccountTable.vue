<template>
  <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm overflow-hidden">
    <!-- Batch Action Toolbar -->
    <div
      v-if="accountStore.selectedCount > 0"
      class="px-4 py-3 bg-primary-50 dark:bg-primary-900/20 border-b border-primary-200 dark:border-primary-800 flex items-center justify-between"
    >
      <div class="flex items-center gap-3">
        <span class="text-sm font-medium text-primary-700 dark:text-primary-300">
          已选择 {{ accountStore.selectedCount }} 个账户
        </span>
        <button
          @click="accountStore.clearSelection()"
          class="text-sm text-primary-600 hover:text-primary-800 dark:hover:text-primary-200"
        >
          取消选择
        </button>
      </div>
      <div class="flex items-center gap-2">
        <!-- Batch Tag -->
        <button
          @click="showBatchTagModal = true"
          class="px-3 py-1.5 text-sm bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-200 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-600 transition-colors flex items-center gap-1"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
          </svg>
          设置标签
        </button>
        <!-- Batch Export -->
        <button
          @click="handleBatchExport"
          class="px-3 py-1.5 text-sm bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-200 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-600 transition-colors flex items-center gap-1"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
          </svg>
          导出
        </button>
        <!-- Batch Delete -->
        <button
          @click="handleBatchDelete"
          class="px-3 py-1.5 text-sm bg-rose-50 dark:bg-rose-900/20 text-rose-600 dark:text-rose-400 border border-rose-200 dark:border-rose-800 rounded-lg hover:bg-rose-100 dark:hover:bg-rose-900/40 transition-colors flex items-center gap-1"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
          </svg>
          删除
        </button>
      </div>
    </div>

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
      <table class="w-full table-auto">
        <thead class="bg-gray-50 dark:bg-gray-700">
          <tr>
            <!-- Checkbox column -->
            <th class="px-3 py-3 w-10">
              <input
                type="checkbox"
                :checked="accountStore.isAllSelected"
                :indeterminate="accountStore.selectedCount > 0 && !accountStore.isAllSelected"
                @change="accountStore.toggleSelectAll()"
                class="w-4 h-4 text-primary-600 rounded border-gray-300 dark:border-gray-600 focus:ring-primary-500"
              />
            </th>
            <th class="px-3 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider whitespace-nowrap">账号</th>
            <th class="px-3 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider whitespace-nowrap">密码</th>
            <th class="px-3 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider whitespace-nowrap">2FA</th>
            <th class="px-3 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider whitespace-nowrap">辅助邮箱</th>
            <th class="px-3 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider whitespace-nowrap">来源</th>
            <th class="px-3 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider whitespace-nowrap">标签</th>
            <th class="px-3 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider whitespace-nowrap">备注</th>
            <th class="px-3 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider whitespace-nowrap">自定义属性</th>
            <th class="px-3 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider whitespace-nowrap">操作</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-200 dark:divide-gray-700">
          <tr
            v-for="account in accountStore.accounts"
            :key="account.id"
            :class="[
              'hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors',
              accountStore.isSelected(account.id) ? 'bg-primary-50 dark:bg-primary-900/10' : ''
            ]"
          >
            <!-- Checkbox -->
            <td class="px-3 py-2">
              <input
                type="checkbox"
                :checked="accountStore.isSelected(account.id)"
                @change="accountStore.toggleSelect(account.id)"
                class="w-4 h-4 text-primary-600 rounded border-gray-300 dark:border-gray-600 focus:ring-primary-500"
              />
            </td>

            <!-- Email -->
            <td class="px-3 py-2">
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
            <td class="px-3 py-2">
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

            <!-- 2FA -->
            <td class="px-3 py-2">
              <div class="flex items-center gap-2">
                <span class="text-sm text-gray-500 dark:text-gray-400">
                  {{ visibleTotps[account.id] || (account.has_totp ? '••••••••' : '-') }}
                </span>
                <button
                  v-if="account.has_totp"
                  @click="toggleTotp(account.id)"
                  class="p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200"
                  :title="visibleTotps[account.id] ? '隐藏2FA' : '显示2FA'"
                >
                  <svg v-if="visibleTotps[account.id]" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
                  </svg>
                  <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                  </svg>
                </button>
                <button
                  v-if="account.has_totp"
                  @click="copyTotp(account.id)"
                  class="p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200"
                  title="复制2FA"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                  </svg>
                </button>
              </div>
            </td>

            <!-- Recovery Email -->
            <td class="px-3 py-2">
              <div class="flex items-center gap-2">
                <span class="text-sm text-gray-500 dark:text-gray-400 truncate max-w-[150px]">
                  {{ account.recovery_email || '-' }}
                </span>
                <button
                  v-if="account.recovery_email"
                  @click="$emit('copy', account.recovery_email, '辅助邮箱')"
                  class="p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200"
                  title="复制辅助邮箱"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                  </svg>
                </button>
              </div>
            </td>

            <!-- Source -->
            <td class="px-3 py-2">
              <span class="text-sm text-gray-600 dark:text-gray-400">
                {{ account.source || '-' }}
              </span>
            </td>

            <!-- Tags -->
            <td class="px-3 py-2">
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
            <td class="px-3 py-2">
              <span class="text-sm text-gray-600 dark:text-gray-400 truncate max-w-[150px] block">
                {{ account.note || '-' }}
              </span>
            </td>

            <!-- Custom Fields -->
            <td class="px-3 py-2">
              <div class="flex flex-wrap gap-1" v-if="account.custom_fields && Object.keys(account.custom_fields).length > 0">
                <span
                  v-for="(value, key) in account.custom_fields"
                  :key="key"
                  class="inline-flex items-center px-2 py-0.5 rounded text-xs bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300"
                  :title="`${key}: ${value}`"
                >
                  <span class="font-medium">{{ key }}:</span>
                  <span class="ml-1 truncate max-w-[80px]">{{ value }}</span>
                </span>
              </div>
              <span v-else class="text-sm text-gray-400">-</span>
            </td>

            <!-- Actions -->
            <td class="px-3 py-2 text-right">
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
    <div class="px-4 py-3 border-t border-gray-200 dark:border-gray-700 flex items-center justify-between">
      <div class="flex items-center gap-4">
        <span class="text-sm text-gray-500 dark:text-gray-400">
          共 {{ accountStore.total }} 条
        </span>
        <div class="flex items-center gap-2">
          <span class="text-sm text-gray-500 dark:text-gray-400">每页</span>
          <select
            :value="accountStore.pageSize"
            @change="accountStore.setPageSize(Number(($event.target as HTMLSelectElement).value))"
            class="px-2 py-1 border border-gray-300 dark:border-gray-600 rounded text-sm bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-300 focus:ring-2 focus:ring-primary-500"
          >
            <option :value="10">10</option>
            <option :value="20">20</option>
            <option :value="50">50</option>
            <option :value="100">100</option>
          </select>
          <span class="text-sm text-gray-500 dark:text-gray-400">条</span>
        </div>
      </div>
      <div v-if="accountStore.totalPages > 1" class="flex items-center gap-2">
        <span class="text-sm text-gray-500 dark:text-gray-400">
          第 {{ accountStore.page }} / {{ accountStore.totalPages }} 页
        </span>
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

    <!-- Batch Tag Modal -->
    <div
      v-if="showBatchTagModal"
      class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50"
      @click.self="showBatchTagModal = false"
    >
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-xl w-full max-w-md">
        <div class="px-6 py-4 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between">
          <h2 class="text-lg font-semibold text-gray-900 dark:text-white">批量设置标签</h2>
          <button @click="showBatchTagModal = false" class="p-1 text-gray-400 hover:text-gray-600">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <div class="p-6 space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">操作方式</label>
            <div class="space-y-2">
              <label class="flex items-center gap-2">
                <input v-model="batchTagAction" type="radio" value="add" class="text-primary-600" />
                <span class="text-sm text-gray-700 dark:text-gray-300">添加标签（保留原有）</span>
              </label>
              <label class="flex items-center gap-2">
                <input v-model="batchTagAction" type="radio" value="set" class="text-primary-600" />
                <span class="text-sm text-gray-700 dark:text-gray-300">替换标签（覆盖原有）</span>
              </label>
              <label class="flex items-center gap-2">
                <input v-model="batchTagAction" type="radio" value="remove" class="text-primary-600" />
                <span class="text-sm text-gray-700 dark:text-gray-300">移除标签</span>
              </label>
            </div>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">选择标签</label>
            <div class="flex flex-wrap gap-2">
              <button
                v-for="tag in tagStore.tags"
                :key="tag.id"
                @click="toggleBatchTag(tag.id)"
                :class="[
                  'px-3 py-1.5 rounded-full text-sm font-medium transition-all',
                  selectedBatchTags.has(tag.id)
                    ? 'ring-2 ring-offset-2 ring-primary-500'
                    : 'opacity-60 hover:opacity-100'
                ]"
                :style="{ backgroundColor: tag.color + '20', color: tag.color }"
              >
                {{ tag.name }}
              </button>
              <span v-if="tagStore.tags.length === 0" class="text-sm text-gray-400">暂无标签</span>
            </div>
          </div>
          <div class="flex justify-end gap-3 pt-2">
            <button
              @click="showBatchTagModal = false"
              class="px-4 py-2 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg"
            >
              取消
            </button>
            <button
              @click="handleBatchTag"
              :disabled="selectedBatchTags.size === 0 && batchTagAction !== 'set'"
              class="px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg disabled:opacity-50"
            >
              确认
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, inject } from 'vue'
import { useAccountStore } from '@/stores/accounts'
import { useTagStore } from '@/stores/tags'
import { parseApiError } from '@/utils/errorParser'
import type { Account } from '@/types'

defineEmits<{
  (e: 'edit', account: Account): void
  (e: 'delete', account: Account): void
  (e: 'copy', text: string, type: string): void
}>()

const accountStore = useAccountStore()
const tagStore = useTagStore()
const showToast = inject('showToast') as (msg: string, type?: 'success' | 'error' | 'info') => void

const visiblePasswords = ref<Record<string, string>>({})
const visibleTotps = ref<Record<string, string>>({})
const showBatchTagModal = ref(false)
const batchTagAction = ref<'add' | 'remove' | 'set'>('add')
const selectedBatchTags = ref<Set<string>>(new Set())

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

async function toggleTotp(accountId: string) {
  if (visibleTotps.value[accountId]) {
    delete visibleTotps.value[accountId]
  } else {
    try {
      const totp = await accountStore.getTotp(accountId)
      if (totp) {
        visibleTotps.value[accountId] = totp
      }
    } catch {
      showToast('获取2FA失败', 'error')
    }
  }
}

async function copyTotp(accountId: string) {
  try {
    let totp = visibleTotps.value[accountId]
    if (!totp) {
      totp = await accountStore.getTotp(accountId) || ''
    }
    if (totp) {
      await navigator.clipboard.writeText(totp)
      showToast('2FA已复制，30秒后自动清除', 'success')

      setTimeout(async () => {
        const current = await navigator.clipboard.readText()
        if (current === totp) {
          await navigator.clipboard.writeText('')
        }
      }, 30000)
    }
  } catch {
    showToast('复制失败', 'error')
  }
}

function toggleBatchTag(tagId: string) {
  if (selectedBatchTags.value.has(tagId)) {
    selectedBatchTags.value.delete(tagId)
  } else {
    selectedBatchTags.value.add(tagId)
  }
  selectedBatchTags.value = new Set(selectedBatchTags.value)
}

async function handleBatchTag() {
  try {
    const tagIds = Array.from(selectedBatchTags.value)
    const result = await accountStore.batchUpdateTags(tagIds, batchTagAction.value)
    showToast(`成功更新 ${result.updated} 个账户`, 'success')
    showBatchTagModal.value = false
    selectedBatchTags.value = new Set()
    // Refresh tag counts and stats
    await Promise.all([tagStore.fetchTags(), accountStore.fetchStats()])
  } catch (e) {
    showToast(parseApiError(e, '批量更新标签失败'), 'error')
  }
}

async function handleBatchDelete() {
  const count = accountStore.selectedCount
  if (!confirm(`确定要删除选中的 ${count} 个账户吗？`)) return

  try {
    const result = await accountStore.batchDelete()
    showToast(`成功删除 ${result.deleted} 个账户`, 'success')
    // Refresh tag counts and stats
    await Promise.all([tagStore.fetchTags(), accountStore.fetchStats()])
  } catch (e) {
    showToast(parseApiError(e, '批量删除失败'), 'error')
  }
}

async function handleBatchExport() {
  try {
    await accountStore.exportAccounts('excel', true)
    showToast('导出成功', 'success')
  } catch (e) {
    showToast(parseApiError(e, '导出失败'), 'error')
  }
}
</script>
