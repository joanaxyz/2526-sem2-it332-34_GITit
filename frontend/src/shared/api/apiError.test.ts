import { describe, expect, it } from 'vitest'

import { apiFieldErrors, ApiError, describeApiError, readApiFieldErrors } from './apiError'

describe('describeApiError', () => {
  it('reads the rejected password rules Django returns as field errors', () => {
    const payload = {
      password: ['This password is too short. It must contain at least 8 characters.', 'This password is too common.'],
    }

    expect(describeApiError(payload, 'Bad Request')).toBe(
      'This password is too short. It must contain at least 8 characters. This password is too common.',
    )
  })

  it('prefers detail over field errors', () => {
    expect(describeApiError({ detail: 'Session expired.', password: ['ignored'] }, 'Bad Request')).toBe('Session expired.')
  })

  it('reads non_field_errors as a whole-request message', () => {
    expect(describeApiError({ non_field_errors: ['Passwords do not match.'] }, 'Bad Request')).toBe('Passwords do not match.')
  })

  it('names each field when several failed', () => {
    const payload = { username: ['Already taken.'], current_password: ['Current password is incorrect.'] }

    expect(describeApiError(payload, 'Bad Request')).toBe(
      'Username: Already taken. Current password: Current password is incorrect.',
    )
  })

  it('falls back when the body carries nothing readable', () => {
    expect(describeApiError({}, 'Bad Request')).toBe('Bad Request')
    expect(describeApiError('<html>oops</html>', 'Bad Request')).toBe('Bad Request')
    expect(describeApiError(null, 'Bad Request')).toBe('Bad Request')
  })
})

describe('readApiFieldErrors', () => {
  it('keys messages by field and skips the non-field keys', () => {
    const payload = { detail: 'nope', non_field_errors: ['nope'], password: ['This password is too common.'] }

    expect(readApiFieldErrors(payload)).toEqual({ password: ['This password is too common.'] })
  })

  it('flattens nested serializer errors', () => {
    expect(readApiFieldErrors({ profile: { display_name: ['Too long.'] } })).toEqual({ profile: ['Too long.'] })
  })

  it('is empty for non-object bodies', () => {
    expect(readApiFieldErrors('Bad Request')).toEqual({})
  })
})

describe('apiFieldErrors', () => {
  it('carries the field errors attached to an ApiError', () => {
    const error = new ApiError('This password is too common.', 400, {}, { password: ['This password is too common.'] })

    expect(apiFieldErrors(error)).toEqual({ password: ['This password is too common.'] })
  })

  it('is empty for anything else', () => {
    expect(apiFieldErrors(new Error('boom'))).toEqual({})
  })
})
