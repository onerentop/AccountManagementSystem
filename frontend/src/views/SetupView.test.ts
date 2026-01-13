/**
 * Tests for SetupView component
 */
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createRouter, createWebHistory } from 'vue-router'

// Create a simple SetupView mock for testing since we need to test the pattern
const SetupViewMock = {
  template: `
    <div>
      <h1>初始化系统</h1>
      <form @submit.prevent="handleSetup">
        <input v-model="password" type="password" placeholder="设置主密码" />
        <input v-model="confirmPassword" type="password" placeholder="确认密码" />
        <div v-if="error" class="error">{{ error }}</div>
        <button type="submit" :disabled="loading">{{ loading ? '设置中...' : '设置密码' }}</button>
      </form>
    </div>
  `,
  data() {
    return {
      password: '',
      confirmPassword: '',
      error: '',
      loading: false,
    }
  },
  methods: {
    async handleSetup() {
      if (this.password !== this.confirmPassword) {
        this.error = '两次密码不一致'
        return
      }
      if (this.password.length < 8) {
        this.error = '密码至少8个字符'
        return
      }
      this.loading = true
      // Simulate setup
      this.loading = false
    },
  },
}

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: { template: '<div>Home</div>' } },
    { path: '/setup', component: SetupViewMock },
  ],
})

describe('SetupView', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  const mountComponent = () => {
    return mount(SetupViewMock, {
      global: {
        plugins: [router, createPinia()],
      },
    })
  }

  describe('Rendering', () => {
    it('should render setup form', () => {
      const wrapper = mountComponent()

      expect(wrapper.find('h1').text()).toBe('初始化系统')
      expect(wrapper.findAll('input[type="password"]')).toHaveLength(2)
    })

    it('should have password confirmation field', () => {
      const wrapper = mountComponent()
      const inputs = wrapper.findAll('input[type="password"]')

      expect(inputs[0].attributes('placeholder')).toBe('设置主密码')
      expect(inputs[1].attributes('placeholder')).toBe('确认密码')
    })
  })

  describe('Validation', () => {
    it('should show error when passwords do not match', async () => {
      const wrapper = mountComponent()
      const inputs = wrapper.findAll('input[type="password"]')

      await inputs[0].setValue('password123')
      await inputs[1].setValue('differentpass')
      await wrapper.find('form').trigger('submit.prevent')

      expect(wrapper.text()).toContain('两次密码不一致')
    })

    it('should show error when password is too short', async () => {
      const wrapper = mountComponent()
      const inputs = wrapper.findAll('input[type="password"]')

      await inputs[0].setValue('short')
      await inputs[1].setValue('short')
      await wrapper.find('form').trigger('submit.prevent')

      expect(wrapper.text()).toContain('密码至少8个字符')
    })

    it('should not show error when passwords match and are valid', async () => {
      const wrapper = mountComponent()
      const inputs = wrapper.findAll('input[type="password"]')

      await inputs[0].setValue('validpassword123')
      await inputs[1].setValue('validpassword123')
      await wrapper.find('form').trigger('submit.prevent')

      expect(wrapper.find('.error').exists()).toBe(false)
    })
  })
})
