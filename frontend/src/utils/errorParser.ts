/**
 * Parse API error response to user-friendly Chinese message
 */
export function parseApiError(e: any, defaultMessage = '操作失败，请重试'): string {
  const data = e.response?.data

  // Field name translations
  const fieldNames: Record<string, string> = {
    password: '密码',
    email: '邮箱',
    confirm_password: '确认密码',
    recovery_email: '辅助邮箱',
    totp_secret: '2FA密钥',
    source: '来源',
    note: '备注',
    browser: '登录浏览器',
    gpt_membership: 'GPT会员',
    family_group: '所属家庭',
    custom_fields: '自定义属性',
  }

  // Parse single validation error
  const parseValidationError = (err: any): string => {
    const msg = err.msg || ''
    const field = err.loc?.[err.loc.length - 1] || ''
    const fieldName = fieldNames[field] || field

    // Translate common validation messages
    if (msg.includes('Password must contain')) {
      return '密码必须包含大写字母、小写字母和数字'
    }
    if (msg.includes('at least 8')) {
      return '密码长度至少8位'
    }
    if (msg.includes('Field required')) {
      return `${fieldName}不能为空`
    }
    if (msg.includes('valid email') || msg.includes('@-sign')) {
      return `${fieldName}格式不正确`
    }
    if (msg.includes('String should have at least')) {
      const match = msg.match(/at least (\d+)/)
      const minLen = match ? match[1] : '?'
      return `${fieldName}长度至少${minLen}位`
    }
    if (msg.includes('value_error')) {
      return `${fieldName}格式不正确`
    }

    return fieldName ? `${fieldName}: ${msg}` : msg
  }

  // Handle FastAPI validation errors array (in response.data directly)
  if (Array.isArray(data)) {
    const messages = data.map(parseValidationError)
    return messages.filter(Boolean).join('；')
  }

  // Handle detail string or object
  if (data?.detail) {
    const detail = data.detail

    // Handle detail as array (Pydantic validation errors)
    if (Array.isArray(detail)) {
      const messages = detail.map(parseValidationError)
      return messages.filter(Boolean).join('；')
    }

    // Common error messages translation
    if (typeof detail === 'string') {
      const translations: Record<string, string> = {
        'Invalid password': '密码错误',
        'Not authenticated': '未登录或登录已过期',
        'Account not found': '账户不存在',
        'Email already exists': '邮箱已存在',
        'System already initialized': '系统已初始化',
        'Passwords do not match': '两次输入的密码不一致',
        'Incorrect password': '密码错误',
      }
      return translations[detail] || detail
    }

    return JSON.stringify(detail)
  }

  // Handle network errors
  if (e.code === 'ECONNABORTED') {
    return '请求超时，请检查网络连接'
  }
  if (e.code === 'ERR_NETWORK') {
    return '网络连接失败，请检查后端服务是否启动'
  }

  return defaultMessage
}
