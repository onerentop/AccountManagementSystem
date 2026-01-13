// Account types
export interface Tag {
  id: string
  name: string
  color: string
  created_at?: string
  account_count?: number
}

export interface Account {
  id: string
  email: string
  note?: string
  sub2api: boolean
  source?: string
  browser?: string
  gpt_membership?: string
  family_group?: string
  recovery_email?: string
  has_password: boolean
  has_totp: boolean
  tags: Tag[]
  created_at: string
  updated_at: string
}

export interface AccountListResponse {
  items: Account[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export interface AccountCreate {
  email: string
  password?: string
  note?: string
  sub2api?: boolean
  source?: string
  browser?: string
  gpt_membership?: string
  family_group?: string
  recovery_email?: string
  totp_secret?: string
  tag_ids?: string[]
}

export interface AccountUpdate extends Partial<AccountCreate> {}

// Auth types
export interface LoginResponse {
  access_token: string
  token_type: string
  expires_in: number
}

export interface SystemStatus {
  is_initialized: boolean
  is_locked: boolean
}

// Import types
export interface ImportResult {
  total: number
  imported: number
  skipped: number
  errors: string[]
}
