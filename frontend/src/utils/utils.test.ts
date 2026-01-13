/**
 * Utility tests
 */
import { describe, it, expect } from 'vitest'

describe('Utility Functions', () => {
  describe('Email Validation Pattern', () => {
    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

    it('should validate correct email formats', () => {
      expect(emailPattern.test('test@example.com')).toBe(true)
      expect(emailPattern.test('user.name@domain.org')).toBe(true)
      expect(emailPattern.test('user+tag@example.co.uk')).toBe(true)
    })

    it('should reject invalid email formats', () => {
      expect(emailPattern.test('invalid')).toBe(false)
      expect(emailPattern.test('invalid@')).toBe(false)
      expect(emailPattern.test('@domain.com')).toBe(false)
      expect(emailPattern.test('user@domain')).toBe(false)
    })
  })

  describe('Color Format Validation', () => {
    const hexColorPattern = /^#[0-9A-Fa-f]{6}$/

    it('should validate correct hex color formats', () => {
      expect(hexColorPattern.test('#ff5733')).toBe(true)
      expect(hexColorPattern.test('#FF5733')).toBe(true)
      expect(hexColorPattern.test('#000000')).toBe(true)
      expect(hexColorPattern.test('#ffffff')).toBe(true)
    })

    it('should reject invalid hex color formats', () => {
      expect(hexColorPattern.test('ff5733')).toBe(false)
      expect(hexColorPattern.test('#fff')).toBe(false)
      expect(hexColorPattern.test('#gggggg')).toBe(false)
      expect(hexColorPattern.test('#ff573')).toBe(false)
    })
  })

  describe('Pagination Calculation', () => {
    const calculateTotalPages = (total: number, pageSize: number) => {
      return Math.ceil(total / pageSize) || 1
    }

    it('should calculate correct total pages', () => {
      expect(calculateTotalPages(100, 10)).toBe(10)
      expect(calculateTotalPages(101, 10)).toBe(11)
      expect(calculateTotalPages(0, 10)).toBe(1)
      expect(calculateTotalPages(5, 10)).toBe(1)
    })
  })

  describe('Date Formatting', () => {
    const formatDate = (dateStr: string) => {
      const date = new Date(dateStr)
      return date.toLocaleDateString('zh-CN')
    }

    it('should format dates correctly', () => {
      const result = formatDate('2024-01-15T10:30:00Z')
      expect(result).toMatch(/2024/)
    })
  })

  describe('Search Query Normalization', () => {
    const normalizeSearch = (query: string) => {
      return query.trim().toLowerCase()
    }

    it('should normalize search queries', () => {
      expect(normalizeSearch('  Test  ')).toBe('test')
      expect(normalizeSearch('UPPERCASE')).toBe('uppercase')
      expect(normalizeSearch('  Mixed Case  ')).toBe('mixed case')
    })
  })
})
