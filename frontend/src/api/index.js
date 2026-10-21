import { apiUrl } from './config.js'

export { apiBaseUrl } from './config.js'

export async function api(path, options = {}) {
  const response = await fetch(apiUrl(path), {
    ...options,
    credentials: 'include',
    headers: { ...(options.body ? { 'Content-Type': 'application/json' } : {}), ...options.headers },
  })
  const data = await response.json().catch(() => null)
  if (!response.ok) {
    const detail = data?.detail
    const message = typeof detail === 'string' ? detail : detail?.message
    const error = new Error(message || '요청을 처리하지 못했어요. 잠시 후 다시 시도해 주세요.')
    error.status = response.status
    error.code = typeof detail === 'object' ? detail?.code : undefined
    throw error
  }
  return data
}

export async function uploadProductImage(file) {
  const response = await fetch(apiUrl('/board/images'), {
    method: 'POST',
    credentials: 'include',
    headers: { 'Content-Type': file.type },
    body: file,
  })
  const data = await response.json().catch(() => null)
  if (!response.ok) throw new Error(typeof data?.detail === 'string' ? data.detail : '상품 사진을 올리지 못했어요.')
  return data.image_url
}

export const learningApi = {
  dashboard: () => api('/learning/dashboard'),
  lessons: () => api('/learning/lessons'),
  lesson: (id) => api(`/learning/lessons/${encodeURIComponent(id)}`),
  completeLesson: (id) => api(`/learning/lessons/${encodeURIComponent(id)}/complete`, { method: 'POST' }),
  groups: () => api('/study-groups'),
  createGroup: (name) => api('/study-groups', { method: 'POST', body: JSON.stringify({ name }) }),
  joinGroup: (join_code) => api('/language/groups/join', { method: 'POST', body: JSON.stringify({ join_code }) }),
  plans: () => api('/billing/plans'),
  startTrial: () => api('/language/trial', { method: 'POST' }),
  checkout: (planId) => api('/billing/checkout', { method: 'POST', body: JSON.stringify({ plan_id: planId }) }),
  verifyCheckout: (paymentId) => api('/billing/verify', { method: 'POST', body: JSON.stringify({ payment_id: paymentId }) }),
  rewardAd: () => api('/rewards/ad-credit', { method: 'POST' }),
}
