<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900">
    <!-- Header -->
    <header class="bg-white dark:bg-gray-800 shadow-sm sticky top-0 z-40">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between h-16">
          <!-- Logo -->
          <div class="flex items-center gap-3">
            <div class="w-8 h-8 bg-primary-500 rounded-lg flex items-center justify-center">
              <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z" />
              </svg>
            </div>
            <h1 class="text-lg font-semibold text-gray-900 dark:text-white">账户管理</h1>
          </div>

          <!-- Search -->
          <div class="flex-1 max-w-xl mx-8">
            <div class="relative">
              <input
                v-model="searchQuery"
                type="text"
                placeholder="搜索账号、备注..."
                class="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                @input="debouncedSearch"
              />
              <svg class="absolute left-3 top-2.5 w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
          </div>

          <!-- Actions -->
          <div class="flex items-center gap-2">
            <button
              @click="showImportModal = true"
              class="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
              title="导入"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
              </svg>
            </button>
            <button
              @click="showAddModal = true"
              class="flex items-center gap-2 px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg transition-colors"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
              </svg>
              <span>添加账户</span>
            </button>
            <button
              @click="handleLock"
              class="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
              title="锁定"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </header>

    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
      <div class="flex gap-6">
        <!-- Sidebar -->
        <aside class="w-60 flex-shrink-0">
          <!-- Stats -->
          <div class="bg-white dark:bg-gray-800 rounded-xl p-4 shadow-sm mb-4">
            <h3 class="text-sm font-medium text-gray-500 dark:text-gray-400 mb-3">账户统计</h3>
            <div class="text-3xl font-bold text-gray-900 dark:text-white">{{ accountStore.stats?.total || 0 }}</div>
            <div class="text-sm text-gray-500 dark:text-gray-400">总账户数</div>
          </div>

          <!-- Tags -->
          <div class="bg-white dark:bg-gray-800 rounded-xl p-4 shadow-sm">
            <div class="flex items-center justify-between mb-3">
              <h3 class="text-sm font-medium text-gray-500 dark:text-gray-400">标签</h3>
              <button
                @click="showTagModal = true"
                class="p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                </svg>
              </button>
            </div>
            <div class="space-y-1">
              <button
                @click="filterByTag(null)"
                :class="[
                  'w-full flex items-center justify-between px-3 py-2 rounded-lg text-sm transition-colors',
                  !selectedTagId ? 'bg-primary-100 dark:bg-primary-900 text-primary-700 dark:text-primary-300' : 'hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300'
                ]"
              >
                <span>全部</span>
                <span class="text-gray-400">{{ accountStore.stats?.total || 0 }}</span>
              </button>
              <button
                v-for="tag in tagStore.tags"
                :key="tag.id"
                @click="filterByTag(tag.id)"
                :class="[
                  'w-full flex items-center justify-between px-3 py-2 rounded-lg text-sm transition-colors',
                  selectedTagId === tag.id ? 'bg-primary-100 dark:bg-primary-900 text-primary-700 dark:text-primary-300' : 'hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300'
                ]"
              >
                <div class="flex items-center gap-2">
                  <span class="w-2 h-2 rounded-full" :style="{ backgroundColor: tag.color }"></span>
                  <span>{{ tag.name }}</span>
                </div>
                <span class="text-gray-400">{{ tag.account_count }}</span>
              </button>
            </div>
          </div>
        </aside>

        <!-- Main content -->
        <main class="flex-1 min-w-0">
          <AccountTable
            @edit="handleEdit"
            @delete="handleDelete"
            @copy="handleCopy"
          />
        </main>
      </div>
    </div>

    <!-- Add/Edit Modal -->
    <AccountModal
      v-if="showAddModal || editingAccount"
      :account="editingAccount"
      @close="closeModal"
      @saved="handleSaved"
    />

    <!-- Import Modal -->
    <ImportModal
      v-if="showImportModal"
      @close="showImportModal = false"
      @imported="handleImported"
    />

    <!-- Tag Modal -->
    <TagModal
      v-if="showTagModal"
      @close="showTagModal = false"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, inject } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useAccountStore } from '@/stores/accounts'
import { useTagStore } from '@/stores/tags'
import type { Account } from '@/types'
import AccountTable from '@/components/AccountTable.vue'
import AccountModal from '@/components/AccountModal.vue'
import ImportModal from '@/components/ImportModal.vue'
import TagModal from '@/components/TagModal.vue'

const router = useRouter()
const authStore = useAuthStore()
const accountStore = useAccountStore()
const tagStore = useTagStore()
const showToast = inject('showToast') as (msg: string, type?: 'success' | 'error' | 'info') => void

const searchQuery = ref('')
const selectedTagId = ref<string | null>(null)
const showAddModal = ref(false)
const showImportModal = ref(false)
const showTagModal = ref(false)
const editingAccount = ref<Account | null>(null)

let searchTimeout: ReturnType<typeof setTimeout>

onMounted(async () => {
  await Promise.all([
    accountStore.fetchAccounts(),
    accountStore.fetchStats(),
    tagStore.fetchTags(),
  ])
})

function debouncedSearch() {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    accountStore.fetchAccounts({ search: searchQuery.value || undefined })
  }, 300)
}

function filterByTag(tagId: string | null) {
  selectedTagId.value = tagId
  accountStore.fetchAccounts({ tag_ids: tagId ? [tagId] : undefined })
}

function handleEdit(account: Account) {
  editingAccount.value = account
}

async function handleDelete(account: Account) {
  if (confirm(`确定要删除账户 ${account.email} 吗？`)) {
    try {
      await accountStore.deleteAccount(account.id)
      showToast('删除成功', 'success')
    } catch {
      showToast('删除失败', 'error')
    }
  }
}

async function handleCopy(text: string, type: string) {
  try {
    await navigator.clipboard.writeText(text)
    showToast(`${type}已复制`, 'success')

    // Clear clipboard after 30 seconds
    setTimeout(async () => {
      const current = await navigator.clipboard.readText()
      if (current === text) {
        await navigator.clipboard.writeText('')
      }
    }, 30000)
  } catch {
    showToast('复制失败', 'error')
  }
}

function closeModal() {
  showAddModal.value = false
  editingAccount.value = null
}

function handleSaved() {
  closeModal()
  accountStore.fetchAccounts()
  accountStore.fetchStats()
  showToast('保存成功', 'success')
}

function handleImported() {
  showImportModal.value = false
  accountStore.fetchAccounts()
  accountStore.fetchStats()
  showToast('导入成功', 'success')
}

async function handleLock() {
  await authStore.lock()
  router.push('/login')
}
</script>
