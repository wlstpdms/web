import assert from 'node:assert/strict'
import test from 'node:test'
import { apiUrl, apiMediaUrl } from '../src/api/config.js'

test('every backend route uses the configured deployment origin and /api prefix', () => {
  for (const origin of ['http://100.100.100.20:8000', 'http://100.100.100.127:8000']) {
    for (const path of ['/user/signup', '/user/login', '/user/kakao/authorize', '/user/kakao/callback', '/board/images', '/learning/dashboard']) {
      assert.equal(apiUrl(path, `${origin}/api/`), `${origin}/api${path}`)
    }
  }
})

test('same-origin requests retain the development and nginx proxy prefix', () => {
  assert.equal(apiUrl('/user/login', '/api'), '/api/user/login')
  assert.equal(apiUrl('user/signup', '/api/'), '/api/user/signup')
})

test('uploaded media uses the backend origin when direct API access is configured', () => {
  assert.equal(apiMediaUrl('/api/media/products/photo.png', 'http://100.100.100.20:8000/api'),
    'http://100.100.100.20:8000/api/media/products/photo.png')
  assert.equal(apiMediaUrl('/api/media/products/photo.png', '/api'), '/api/media/products/photo.png')
  assert.equal(apiMediaUrl('https://images.example/photo.png', 'http://100.100.100.20:8000/api'),
    'https://images.example/photo.png')
})
