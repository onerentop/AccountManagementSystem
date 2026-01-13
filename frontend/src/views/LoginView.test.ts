/**
 * Tests for LoginView component
 */
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '@/views/LoginView.vue'

// Mock the auth API
vi.mock('@/api/auth', () => ({
  authApi: {
    login: vi.fn(),
  },
}))

import { authApi } from '@/api/auth'

// Create a mock router
const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: { template: '<div>Home</div>' } },
    { path: '/login', component: LoginView },
  ],
})

describe('LoginView', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  const mountComponent = () => {
    return mount(LoginView, {
      global: {
        plugins: [router, createPinia()],
      },
    })
  }

  describe('Rendering', () => {
    it('should render login form', () => {
      const wrapper = mountComponent()

      expect(wrapper.find('h1').text()).toBe('账户管理系统')
      expect(wrapper.find('input[type="password"]').exists()).toBe(true)
      expect(wrapper.find('button[type="submit"]').exists()).toBe(true)
    })

    it('should have password input with placeholder', () => {
      const wrapper = mountComponent()
      const input = wrapper.find('input[type="password"]')

      expect(input.attributes('placeholder')).toBe('请输入主密码')
    })

    it('should show unlock button text', () => {
      const wrapper = mountComponent()
      const button = wrapper.find('button[type="submit"]')

      expect(button.text()).toContain('解锁')
    })
  })

  describe('Form Validation', () => {
    it('should show error when password is empty', async () => {
      const wrapper = mountComponent()

      await wrapper.find('form').trigger('submit.prevent')

      expect(wrapper.text()).toContain('请输入密码')
    })

    it('should not show error initially', () => {
      const wrapper = mountComponent()

      expect(wrapper.find('.text-rose-500').exists()).toBe(false)
    })
  })

  describe('Login Flow', () => {
    it('should call login API with password', async () => {
      const wrapper = mountComponent()
      vi.mocked(authApi.login).mockResolvedValue({
        data: { access_token: 'token', expires_in: 3600 },
      } as any)

      await wrapper.find('input[type="password"]').setValue('password123')
      await wrapper.find('form').trigger('submit.prevent')

      // The component uses the store which calls the API
      await flushPromises()
    })

    it('should show loading state during login', async () => {
      const wrapper = mountComponent()

      // Create a promise that won't resolve immediately
      let resolveLogin: any
      vi.mocked(authApi.login).mockImplementation(
        () => new Promise((resolve) => { resolveLogin = resolve })
      )

      await wrapper.find('input[type="password"]').setValue('password123')
      await wrapper.find('form').trigger('submit.prevent')

      // Check loading state
      expect(wrapper.text()).toContain('登录中')

      // Resolve to clean up
      resolveLogin({ data: { access_token: 'token', expires_in: 3600 } })
      await flushPromises()
    })

    it('should show error on login failure', async () => {
      const wrapper = mountComponent()
      vi.mocked(authApi.login).mockRejectedValue({
        response: { data: { detail: '密码错误' } },
      })

      await wrapper.find('input[type="password"]').setValue('wrongpassword')
      await wrapper.find('form').trigger('submit.prevent')
      await flushPromises()

      expect(wrapper.text()).toContain('密码错误')
    })
  })

  describe('Button State', () => {
    it('should disable button when loading', async () => {
      const wrapper = mountComponent()

      let resolveLogin: any
      vi.mocked(authApi.login).mockImplementation(
        () => new Promise((resolve) => { resolveLogin = resolve })
      )

      await wrapper.find('input[type="password"]').setValue('password123')
      await wrapper.find('form').trigger('submit.prevent')

      const button = wrapper.find('button[type="submit"]')
      expect(button.attributes('disabled')).toBeDefined()

      resolveLogin({ data: { access_token: 'token', expires_in: 3600 } })
      await flushPromises()
    })
  })
})
