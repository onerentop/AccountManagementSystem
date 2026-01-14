<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50" @click.self="$emit('close')">
    <div class="bg-white dark:bg-gray-800 rounded-xl shadow-xl w-full max-w-lg max-h-[90vh] overflow-y-auto">
      <!-- Header -->
      <div class="px-6 py-4 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between">
        <h2 class="text-lg font-semibold text-gray-900 dark:text-white">
          {{ account ? '编辑账户' : '添加账户' }}
        </h2>
        <button
          @click="$emit('close')"
          class="p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <!-- Form -->
      <form @submit.prevent="handleSubmit" class="p-6 space-y-4">
        <!-- Email -->
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            账号邮箱 <span class="text-rose-500">*</span>
          </label>
          <input
            v-model="form.email"
            type="email"
            required
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
            placeholder="example@gmail.com"
          />
        </div>

        <!-- Password -->
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            密码
          </label>
          <div class="relative">
            <input
              v-model="form.password"
              :type="showPassword ? 'text' : 'password'"
              class="w-full px-3 py-2 pr-10 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
              :placeholder="account ? '留空表示不修改' : '输入密码'"
            />
            <button
              type="button"
              @click="showPassword = !showPassword"
              class="absolute right-2 top-1/2 -translate-y-1/2 p-1 text-gray-400 hover:text-gray-600"
            >
              <svg v-if="showPassword" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
              </svg>
              <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
              </svg>
            </button>
          </div>
        </div>

        <!-- Source & GPT -->
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              来源
            </label>
            <input
              v-model="form.source"
              type="text"
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
              placeholder="自建/购买"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              GPT 会员
            </label>
            <input
              v-model="form.gpt_membership"
              type="text"
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
              placeholder="gpt/pro"
            />
          </div>
        </div>

        <!-- Sub2API -->
        <div class="flex items-center gap-2">
          <input
            id="sub2api"
            v-model="form.sub2api"
            type="checkbox"
            class="w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
          />
          <label for="sub2api" class="text-sm text-gray-700 dark:text-gray-300">
            有 sub2api
          </label>
        </div>

        <!-- Tags -->
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            标签
          </label>
          <div class="flex flex-wrap gap-2">
            <button
              v-for="tag in tagStore.tags"
              :key="tag.id"
              type="button"
              @click="toggleTag(tag.id)"
              :class="[
                'px-3 py-1 rounded-full text-sm transition-colors',
                (form.tag_ids || []).includes(tag.id)
                  ? 'text-white'
                  : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
              ]"
              :style="(form.tag_ids || []).includes(tag.id) ? { backgroundColor: tag.color } : {}"
            >
              {{ tag.name }}
            </button>
          </div>
        </div>

        <!-- Note -->
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            备注
          </label>
          <textarea
            v-model="form.note"
            rows="2"
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-700 dark:text-white resize-none"
            placeholder="备注信息..."
          />
        </div>

        <!-- Recovery Email -->
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            辅助邮箱
          </label>
          <input
            v-model="form.recovery_email"
            type="email"
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
            placeholder="recovery@example.com"
          />
        </div>

        <!-- 2FA -->
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            2FA 密钥
          </label>
          <input
            v-model="form.totp_secret"
            type="text"
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-700 dark:text-white font-mono"
            :placeholder="account ? '留空表示不修改' : 'TOTP 密钥'"
          />
        </div>

        <!-- Custom Fields -->
        <div>
          <div class="flex items-center justify-between mb-2">
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">
              自定义属性
            </label>
            <button
              type="button"
              @click="addCustomField"
              class="text-sm text-primary-600 hover:text-primary-700 dark:text-primary-400 flex items-center gap-1"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
              </svg>
              添加属性
            </button>
          </div>
          <div class="space-y-2">
            <div
              v-for="(_, index) in customFieldsList"
              :key="index"
              class="flex items-center gap-2"
            >
              <input
                v-model="customFieldsList[index].key"
                type="text"
                class="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-700 dark:text-white text-sm"
                placeholder="属性名"
              />
              <input
                v-model="customFieldsList[index].value"
                type="text"
                class="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-700 dark:text-white text-sm"
                placeholder="属性值"
              />
              <button
                type="button"
                @click="removeCustomField(index)"
                class="p-2 text-gray-400 hover:text-rose-500 transition-colors"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            <p v-if="customFieldsList.length === 0" class="text-sm text-gray-400 dark:text-gray-500">
              暂无自定义属性
            </p>
          </div>
        </div>

        <!-- Error -->
        <div v-if="error" class="text-rose-500 text-sm">{{ error }}</div>

        <!-- Actions -->
        <div class="flex justify-end gap-3 pt-4">
          <button
            type="button"
            @click="$emit('close')"
            class="px-4 py-2 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
          >
            取消
          </button>
          <button
            type="submit"
            :disabled="loading"
            class="px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg transition-colors disabled:opacity-50"
          >
            {{ loading ? '保存中...' : '保存' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useAccountStore } from '@/stores/accounts'
import { useTagStore } from '@/stores/tags'
import { parseApiError } from '@/utils/errorParser'
import type { Account, AccountCreate, AccountUpdate } from '@/types'

const props = defineProps<{
  account?: Account | null
}>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'saved'): void
}>()

const accountStore = useAccountStore()
const tagStore = useTagStore()

const loading = ref(false)
const error = ref('')
const showPassword = ref(false)
const customFieldsList = ref<Array<{ key: string; value: string }>>([])

const form = reactive<AccountCreate>({
  email: '',
  password: '',
  note: '',
  sub2api: false,
  source: '',
  browser: '',
  gpt_membership: '',
  family_group: '',
  recovery_email: '',
  totp_secret: '',
  tag_ids: [],
  custom_fields: {},
})

onMounted(() => {
  if (props.account) {
    form.email = props.account.email
    form.note = props.account.note || ''
    form.sub2api = props.account.sub2api
    form.source = props.account.source || ''
    form.browser = props.account.browser || ''
    form.gpt_membership = props.account.gpt_membership || ''
    form.family_group = props.account.family_group || ''
    form.recovery_email = props.account.recovery_email || ''
    form.tag_ids = props.account.tags.map(t => t.id)
    // Initialize custom fields
    if (props.account.custom_fields) {
      customFieldsList.value = Object.entries(props.account.custom_fields).map(([key, value]) => ({ key, value }))
    }
  }
})

function toggleTag(tagId: string) {
  const index = form.tag_ids!.indexOf(tagId)
  if (index >= 0) {
    form.tag_ids!.splice(index, 1)
  } else {
    form.tag_ids!.push(tagId)
  }
}

function addCustomField() {
  customFieldsList.value.push({ key: '', value: '' })
}

function removeCustomField(index: number) {
  customFieldsList.value.splice(index, 1)
}

function buildCustomFields(): Record<string, string> {
  const result: Record<string, string> = {}
  for (const field of customFieldsList.value) {
    if (field.key.trim()) {
      result[field.key.trim()] = field.value
    }
  }
  return result
}

async function handleSubmit() {
  loading.value = true
  error.value = ''

  try {
    // Build custom fields from list
    const customFields = buildCustomFields()

    // Clean up empty strings to avoid validation errors
    const cleanData = (data: Record<string, any>) => {
      const cleaned: Record<string, any> = {}
      for (const [key, value] of Object.entries(data)) {
        if (value === '' || value === undefined) {
          continue // Skip empty strings and undefined
        }
        cleaned[key] = value
      }
      return cleaned
    }

    if (props.account) {
      // Update
      const updateData: AccountUpdate = cleanData({ ...form, custom_fields: customFields }) as AccountUpdate
      if (!updateData.password) {
        delete updateData.password
      }
      if (!updateData.totp_secret) {
        delete updateData.totp_secret
      }
      await accountStore.updateAccount(props.account.id, updateData)
    } else {
      // Create
      await accountStore.createAccount(cleanData({ ...form, custom_fields: customFields }) as AccountCreate)
    }
    emit('saved')
  } catch (e: any) {
    error.value = parseApiError(e, '保存失败')
  } finally {
    loading.value = false
  }
}
</script>
