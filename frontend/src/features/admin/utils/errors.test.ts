import { describe, expect, it } from 'vitest'

import { ApiError } from '@/shared/api/apiError'

import { adminErrorMessage } from './errors'

describe('adminErrorMessage', () => {
  it('surfaces the first serializer validation message', () => {
    const error = new ApiError('Bad Request', 400, {
      amount: ['The wallet cannot go below zero.'],
    })

    expect(adminErrorMessage(error)).toBe('The wallet cannot go below zero.')
  })

  it('uses the supplied fallback for unknown values', () => {
    expect(adminErrorMessage(null, 'Try again.')).toBe('Try again.')
  })
})
