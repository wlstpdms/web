<script setup>
import { computed, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { api } from '../api/index.js'
import ExploreSearch from '../components/ExploreSearch.vue'
import CategoryFilters from '../components/CategoryFilters.vue'
import MarketplaceCard from '../components/MarketplaceCard.vue'
import ActionButton from '../components/ActionButton.vue'
import PageHeading from '../components/PageHeading.vue'
import { productImageOf } from '../api/productMedia.js'

const posts = ref([])
const loading = ref(true)
const error = ref('')
const query = ref('')
const activeCategory = ref('전체')
const favorites = ref(new Set())

const categories = [
  { name: '전체', icon: '✳' }, { name: '아우터', icon: '🧥' }, { name: '상의', icon: '👕' },
  { name: '하의', icon: '👖' }, { name: '가방', icon: '👜' }, { name: '신발', icon: '👟' }, { name: '잡화', icon: '🧣' },
]
const categoryWords = {
  아우터: ['아우터', '코트', '자켓', '재킷', '패딩', '점퍼', '가디건', '트렌치'],
  상의: ['상의', '셔츠', '티셔츠', '니트', '맨투맨', '블라우스', '후드'],
  하의: ['하의', '바지', '팬츠', '청바지', '데님', '스커트', '슬랙스'],
  가방: ['가방', '백팩', '숄더백', '크로스백', '토트백'],
  신발: ['신발', '운동화', '스니커즈', '부츠', '구두', '샌들'],
  잡화: ['잡화', '모자', '벨트', '머플러', '스카프', '지갑', '시계'],
}
const categoryOf = (post) => {
  const text = `${post.title} ${post.contents}`.toLowerCase()
  return Object.entries(categoryWords).find(([, words]) => words.some(word => text.includes(word)))?.[0] || '기타'
}
const visiblePosts = computed(() => [...posts.value].reverse().filter(post => {
  const text = `${post.title} ${post.contents}`.toLowerCase()
  return (!query.value.trim() || text.includes(query.value.trim().toLowerCase())) &&
    (activeCategory.value === '전체' || categoryOf(post) === activeCategory.value)
}))
const priceOf = (post) => {
  const explicit = post.contents.match(/판매가\s*[:：]?\s*([\d,]+)\s*원/)
    || post.contents.match(/가격\s*[:：]?\s*([\d,]+)\s*원/)
    || post.contents.match(/구매가\s*[:：]?\s*([\d,]+)\s*원/)
  const amounts = [...post.contents.matchAll(/([\d,]+)\s*원/g)]
  const match = explicit || amounts.at(-1)
  return match ? `${match[1]}원` : '가격 협의'
}
const dealLabel = (post) => {
  const original = post.contents.match(/(?:정가|새상품가|구매가)\s*[:：]?\s*([\d,]+)\s*원/)
  const sale = post.contents.match(/판매가\s*[:：]?\s*([\d,]+)\s*원/)
    || post.contents.match(/가격\s*[:：]?\s*([\d,]+)\s*원/)
    || post.contents.match(/구매가\s*[:：]?\s*([\d,]+)\s*원/)
  if (!original || !sale) return ''
  const originalPrice = Number(original[1].replaceAll(',', ''))
  const salePrice = Number(sale[1].replaceAll(',', ''))
  if (!originalPrice || salePrice >= originalPrice) return ''
  return `정가보다 ${Math.round((1 - salePrice / originalPrice) * 100)}% 낮아요`
}
const conditionOf = (post) => {
  const text = post.contents
  if (/미개봉|새상품|새 제품/.test(text)) return '미개봉'
  if (/거의 새|사용감 없/.test(text)) return '상태 좋음'
  return '중고'
}
const artOf = (post) => {
  const category = categoryOf(post)
  const icons = { 아우터: '🧥', 상의: '👕', 하의: '👖', 가방: '👜', 신발: '👟', 잡화: '🧣', 기타: '🧶' }
  return icons[category]
}
const backgrounds = ['linear-gradient(145deg,#eddbc5,#f8eddb)', 'linear-gradient(145deg,#e6e3ce,#f3edcf)', 'linear-gradient(145deg,#f0d9cc,#f7e8dc)', 'linear-gradient(145deg,#d9e0d4,#edf0e4)', 'linear-gradient(145deg,#e9dce5,#f4ebf1)']
function toggleFavorite(idx) {
  const next = new Set(favorites.value)
  next.has(idx) ? next.delete(idx) : next.add(idx)
  favorites.value = next
}

onMounted(async () => {
  try { posts.value = await api('/board/list') }
  catch (e) { error.value = e.message }
  finally { loading.value = false }
})
</script>

<template>
  <section class="browse-page premium-browse" aria-label="중고 상품 둘러보기">
    <ExploreSearch v-model="query" placeholder="코트, 니트, 가방을 찾아보세요" label="옷 검색" />
    <CategoryFilters v-model="activeCategory" :categories="categories" />

    <PageHeading eyebrow="DOJI · 다시 입는 취향" title="다음 계절의 단골" description="새 옷 같은 취향을, 부담 덜한 가격으로 찾아보세요.">
      <ActionButton to="/posts/new" class="browse-create">내 옷 나누기 <span>＋</span></ActionButton>
    </PageHeading>
    <div class="listing-toolbar"><strong>{{ activeCategory === '전체' ? '오늘의 옷장' : activeCategory }}</strong><span>{{ visiblePosts.length }}벌의 옷</span></div>

    <div v-if="loading" class="loading-grid" aria-label="매물을 불러오는 중" aria-busy="true"><div v-for="n in 8" :key="n" class="loading-card"></div></div>
    <div v-else-if="error" class="empty-state error-state"><span class="empty-mark">!</span><h3>매물을 불러오지 못했어요</h3><p>{{ error }}</p><button class="text-button" @click="$router.go(0)">다시 불러오기 <span>↻</span></button></div>
    <div v-else-if="visiblePosts.length" class="listing-grid">
      <MarketplaceCard v-for="(post, index) in visiblePosts" :key="post.idx" :item="{ title: post.title, description: post.contents.slice(0, 58) + (post.contents.length > 58 ? '…' : '') }" :href="`/posts/${post.idx}`" :condition="conditionOf(post)" :icon="artOf(post)" :image-url="productImageOf(post)" :price="priceOf(post)" :deal="dealLabel(post)" :category="categoryOf(post)" :saved="favorites.has(post.idx)" :background="backgrounds[index % backgrounds.length]" @toggle-save="toggleFavorite(post.idx)" />
    </div>
    <div v-else class="empty-state"><span class="empty-mark">✳</span><h3>{{ query || activeCategory !== '전체' ? '조건에 맞는 매물이 없어요' : '아직 올라온 물건이 없어요' }}</h3><p>{{ query || activeCategory !== '전체' ? '검색어나 카테고리를 바꿔 다시 찾아보세요.' : '첫 번째 물건을 올리고 새로운 주인을 만나보세요.' }}</p><RouterLink v-if="!query && activeCategory === '전체'" class="text-button" to="/posts/new">첫 상품 등록하기 <span>↗</span></RouterLink><button v-else class="text-button" @click="query = ''; activeCategory = '전체'">전체 매물 보기 <span>↗</span></button></div>
  </section>
</template>
