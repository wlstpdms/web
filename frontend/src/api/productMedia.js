const IMAGE_URL = /https?:\/\/[^\s"'<>]+?\.(?:avif|gif|jpe?g|png|webp)(?:\?[^\s"'<>]*)?/i

export function productImageOf(product) {
  const candidates = [product?.image_url, product?.imageUrl, product?.photo_url, product?.photoUrl, product?.thumbnail_url, product?.thumbnail]
  const direct = candidates.find(value => typeof value === 'string' && (/^https?:\/\//i.test(value.trim()) || value.trim().startsWith('/')))
  if (direct) return direct.trim()
  return String(product?.contents || '').match(IMAGE_URL)?.[0] || ''
}
