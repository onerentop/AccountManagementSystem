import api from './index'
import type { SystemStatus, LoginResponse } from '@/types'

export const authApi = {
  // Get system status
  getStatus: () => api.get<SystemStatus>('/auth/status'),

  // Setup master password
  setup: (password: string, confirmPassword: string) =>
    api.post('/auth/setup', { password, confirm_password: confirmPassword }),

  // Login
  login: (password: string) =>
    api.post<LoginResponse>('/auth/login', { password }),

  // Logout
  logout: () => api.post('/auth/logout'),

  // Lock application
  lock: () => api.post('/auth/lock'),

  // Change password
  changePassword: (currentPassword: string, newPassword: string, confirmPassword: string) =>
    api.put('/auth/password', {
      current_password: currentPassword,
      new_password: newPassword,
      confirm_password: confirmPassword,
    }),
}
