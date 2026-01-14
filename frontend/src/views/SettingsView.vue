<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900">
    <div class="max-w-2xl mx-auto p-6">
      <h1 class="text-2xl font-bold text-gray-900 dark:text-white mb-6">设置</h1>

      <!-- Change password -->
      <div class="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm">
        <h2 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">修改主密码</h2>

        <form @submit.prevent="handleChangePassword" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              当前密码
            </label>
            <input
              v-model="currentPassword"
              type="password"
              required
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              新密码
            </label>
            <input
              v-model="newPassword"
              type="password"
              required
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              确认新密码
            </label>
            <input
              v-model="confirmPassword"
              type="password"
              required
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
            />
          </div>

          <div v-if="error" class="text-rose-500 text-sm">{{ error }}</div>
          <div v-if="success" class="text-emerald-500 text-sm">{{ success }}</div>

          <button
            type="submit"
            :disabled="loading"
            class="px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg transition-colors disabled:opacity-50"
          >
            {{ loading ? '更新中...' : '更新密码' }}
          </button>
        </form>
      </div>

      <!-- Backup Section -->
      <div class="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm mt-6">
        <h2 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">数据备份</h2>

        <div v-if="backupConfig" class="mb-4 p-3 bg-gray-50 dark:bg-gray-700 rounded-lg text-sm text-gray-600 dark:text-gray-300">
          <p>自动备份: <span class="font-medium">{{ backupConfig.enabled ? '已启用' : '已禁用' }}</span></p>
          <p>备份间隔: <span class="font-medium">{{ backupConfig.interval_hours }} 小时</span></p>
          <p>保留数量: <span class="font-medium">{{ backupConfig.keep_count }} 份</span></p>
          <p>备份格式: <span class="font-medium">{{ backupConfig.format.toUpperCase() }}</span></p>
        </div>

        <button
          @click="handleBackupNow"
          :disabled="backupLoading"
          class="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg transition-colors disabled:opacity-50 mb-4"
        >
          {{ backupLoading ? '备份中...' : '立即备份' }}
        </button>

        <div v-if="backupMessage" class="text-emerald-500 text-sm mb-4">{{ backupMessage }}</div>

        <div v-if="backups.length > 0" class="space-y-2">
          <h3 class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">备份文件列表</h3>
          <div
            v-for="backup in backups"
            :key="backup.filename"
            class="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg"
          >
            <div>
              <p class="text-sm font-medium text-gray-900 dark:text-white">{{ backup.filename }}</p>
              <p class="text-xs text-gray-500 dark:text-gray-400">
                {{ formatSize(backup.size) }} · {{ formatDate(backup.created_at) }}
              </p>
            </div>
            <div class="flex gap-2">
              <button
                @click="handleDownload(backup.filename)"
                class="px-3 py-1 text-sm bg-primary-100 dark:bg-primary-900 text-primary-600 dark:text-primary-400 rounded hover:bg-primary-200 dark:hover:bg-primary-800 transition-colors"
              >
                下载
              </button>
              <button
                @click="handleDeleteBackup(backup.filename)"
                class="px-3 py-1 text-sm bg-rose-100 dark:bg-rose-900 text-rose-600 dark:text-rose-400 rounded hover:bg-rose-200 dark:hover:bg-rose-800 transition-colors"
              >
                删除
              </button>
            </div>
          </div>
        </div>
        <div v-else class="text-sm text-gray-500 dark:text-gray-400">暂无备份文件</div>
      </div>

      <div class="mt-6">
        <router-link
          to="/"
          class="text-primary-600 hover:text-primary-700 text-sm"
        >
          ← 返回首页
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { authApi } from '@/api/auth'
import { backupApi, type BackupFile, type BackupConfig } from '@/api/backup'

// Password change state
const currentPassword = ref('')
const newPassword = ref('')
const confirmPassword = ref('')
const loading = ref(false)
const error = ref('')
const success = ref('')

// Backup state
const backups = ref<BackupFile[]>([])
const backupConfig = ref<BackupConfig | null>(null)
const backupLoading = ref(false)
const backupMessage = ref('')

// Load backups on mount
onMounted(() => {
  loadBackups()
})

async function loadBackups() {
  try {
    const response = await backupApi.list()
    backups.value = response.data.backups
    backupConfig.value = response.data.config
  } catch (e) {
    console.error('Failed to load backups:', e)
  }
}

async function handleBackupNow() {
  backupLoading.value = true
  backupMessage.value = ''

  try {
    const response = await backupApi.backupNow()
    backupMessage.value = response.data.message
    await loadBackups()
  } catch (e: any) {
    backupMessage.value = e.response?.data?.detail || '备份失败'
  } finally {
    backupLoading.value = false
  }
}

async function handleDownload(filename: string) {
  try {
    const response = await backupApi.download(filename)
    const blob = new Blob([response.data])
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = filename
    document.body.appendChild(a)
    a.click()
    window.URL.revokeObjectURL(url)
    document.body.removeChild(a)
  } catch (e) {
    console.error('Download failed:', e)
  }
}

async function handleDeleteBackup(filename: string) {
  if (!confirm('确定要删除备份 ' + filename + ' 吗？')) {
    return
  }

  try {
    await backupApi.delete(filename)
    await loadBackups()
  } catch (e: any) {
    alert(e.response?.data?.detail || '删除失败')
  }
}

function formatSize(bytes: number): string {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleString('zh-CN')
}

async function handleChangePassword() {
  if (newPassword.value !== confirmPassword.value) {
    error.value = '两次输入的密码不一致'
    return
  }

  loading.value = true
  error.value = ''
  success.value = ''

  try {
    await authApi.changePassword(currentPassword.value, newPassword.value, confirmPassword.value)
    success.value = '密码已更新'
    currentPassword.value = ''
    newPassword.value = ''
    confirmPassword.value = ''
  } catch (e: any) {
    error.value = e.response?.data?.detail || '更新失败'
  } finally {
    loading.value = false
  }
}
</script>
