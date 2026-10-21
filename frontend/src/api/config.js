// Vite replaces this value at build time. Development defaults to its /api proxy.
export const apiBaseUrl = (import.meta.env?.VITE_API_BASE_URL?.trim() || '/api').replace(/\/+$/, '')

export function apiUrl(path, baseUrl = apiBaseUrl) {
  return `${baseUrl.replace(/\/+$/, '')}/${path.replace(/^\/+/, '')}`
}

export function apiMediaUrl(path, baseUrl = apiBaseUrl) {
  // Uploaded files are returned by FastAPI as /api/media/... paths.
  if (path.startsWith('/api/media/') && /^https?:\/\//i.test(baseUrl)) {
    return new URL(path, baseUrl).href
  }
  return path
}
