import api from './index'

export interface BackupFile {
  filename: string
  size: number
  created_at: string
}

export interface BackupConfig {
  enabled: boolean
  interval_hours: number
  keep_count: number
  format: string
}

export interface BackupListResponse {
  backups: BackupFile[]
  config: BackupConfig
}

export const backupApi = {
  // 获取备份列表
  list: () => api.get<BackupListResponse>('/backup/list'),

  // 立即备份
  backupNow: () => api.post<{ success: boolean; message: string; filename?: string }>('/backup/now'),

  // 下载备份
  download: (filename: string) => {
    return api.get(`/backup/download/${filename}`, {
      responseType: 'blob',
    })
  },

  // 删除备份
  delete: (filename: string) => api.delete(`/backup/delete/${filename}`),
}
