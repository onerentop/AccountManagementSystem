<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900">
    <router-view />

    <!-- Toast notifications -->
    <div class="fixed top-4 right-4 z-50 space-y-2">
      <TransitionGroup name="toast">
        <div
          v-for="toast in toasts"
          :key="toast.id"
          :class="[
            'px-4 py-3 rounded-lg shadow-lg flex items-center gap-2 min-w-[300px]',
            toast.type === 'success' ? 'bg-emerald-500 text-white' : '',
            toast.type === 'error' ? 'bg-rose-500 text-white' : '',
            toast.type === 'info' ? 'bg-primary-500 text-white' : '',
          ]"
        >
          <span>{{ toast.message }}</span>
        </div>
      </TransitionGroup>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, provide } from 'vue'

interface Toast {
  id: number
  message: string
  type: 'success' | 'error' | 'info'
}

const toasts = ref<Toast[]>([])
let toastId = 0

function showToast(message: string, type: Toast['type'] = 'info') {
  const id = ++toastId
  toasts.value.push({ id, message, type })
  setTimeout(() => {
    toasts.value = toasts.value.filter(t => t.id !== id)
  }, 3000)
}

provide('showToast', showToast)
</script>
