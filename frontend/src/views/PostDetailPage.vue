<script setup>
import { computed, onMounted, ref } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import { api } from '../api/index.js'
import PageSkeleton from '../components/PageSkeleton.vue'
import DetailPanel from '../components/DetailPanel.vue'
import ActionButton from '../components/ActionButton.vue'
import PageHeading from '../components/PageHeading.vue'
import { productImageOf } from '../api/productMedia.js'

const route = useRoute()
const router = useRouter()
const post = ref(null)
const loading = ref(true)
const pending = ref(false)
const message = ref('')
const messageKind = ref('info')
const salePrice = computed(() => {
  const contents = post.value?.contents || ''
  const match = contents.match(/판매가\s*[:：]?\s*([\d,]+)\s*원/)
    || contents.match(/가격\s*[:：]?\s*([\d,]+)\s*원/)
    || contents.match(/구매가\s*[:：]?\s*([\d,]+)\s*원/)
  return match ? Number(match[1].replaceAll(',', '')) : null
})
const formattedPrice = computed(() => salePrice.value === null ? '가격 문의' : `${salePrice.value.toLocaleString('ko-KR')}원`)
const productImage = computed(() => productImageOf(post.value))

function showMessage(text, kind = 'info') {
  message.value = text
  messageKind.value = kind
}

async function confirmPayment(paymentId) {
  await api('/payments/clothing/verify', { method: 'POST', body: JSON.stringify({ payment_id: paymentId }) })
  showMessage('결제가 확인됐어요. 주문이 완료되었습니다.', 'success')
  await router.replace({ path: route.path, query: {} })
}

async function buy() {
  if (!post.value || pending.value) return
  if (!salePrice.value) { showMessage('판매 가격이 등록되지 않은 상품이에요.', 'error'); return }
  pending.value = true
  message.value = ''
  try {
    const order = await api('/payments/clothing/orders', { method: 'POST', body: JSON.stringify({ board_idx: post.value.idx }) })
    const PortOne = await import('@portone/browser-sdk/v2')
    const result = await PortOne.requestPayment({
      storeId: order.store_id,
      channelKey: order.channel_key,
      paymentId: order.payment_id,
      orderName: order.order_name,
      totalAmount: order.amount,
      currency: order.currency,
      payMethod: 'CARD',
      locale: 'KO_KR',
      redirectUrl: `${window.location.origin}${route.path}`,
    })
    if (result?.code) { showMessage(result.message || '결제가 취소되었거나 완료되지 않았어요.', 'error'); return }
    if (result?.paymentId) await confirmPayment(result.paymentId)
  } catch (error) {
    if (error.status === 401) {
      window.location.assign(`/login?redirect=${encodeURIComponent(route.fullPath)}`)
      return
    }
    showMessage(error.message || '결제 요청을 완료하지 못했어요.', 'error')
  } finally { pending.value = false }
}

onMounted(async () => {
  try {
    post.value = await api(`/board/read/${route.params.idx}`)
    if (route.query.paymentId) {
      pending.value = true
      await confirmPayment(String(route.query.paymentId))
    }
  } catch (error) { showMessage(error.message || '상품을 불러오지 못했어요.', 'error') }
  finally { pending.value = false; loading.value = false }
})
</script>

<template>
  <PageSkeleton v-if="loading" />
  <section v-else class="clothing-detail-page">
    <RouterLink class="clothing-back" to="/posts">← DOJI 옷장으로 돌아가기</RouterLink>
    <div v-if="!post" class="clothing-detail-error" role="alert">{{ message }}</div>
    <DetailPanel v-else>
      <template #visual>
      <div class="clothing-product-art">
        <img v-if="productImage" class="clothing-product-photo" :src="productImage" :alt="post.title" @error="$event.currentTarget.remove()" />
        <span class="clothing-art-spark">✳</span>
        <span v-if="!productImage" class="clothing-art-emoji">{{ /가방|백/.test(post.title) ? '👜' : /신발|스니커즈/.test(post.title) ? '👟' : /바지|팬츠|슬랙스|데님/.test(post.title) ? '👖' : /셔츠|니트|상의/.test(post.title) ? '👕' : /귀걸이|머플러|스카프/.test(post.title) ? '🧣' : '🧥' }}</span>
        <span class="clothing-art-note">SECOND<br />CHANCE</span>
      </div>
      </template>
      <div class="clothing-product-info">
        <PageHeading eyebrow="다음 주인을 기다리는 옷" :title="post.title" level="h1">
          <span class="clothing-detail-price">{{ formattedPrice }}</span>
        </PageHeading>
        <div class="clothing-detail-rule"></div>
        <p class="clothing-detail-copy">{{ post.contents }}</p>
        <p v-if="message" class="clothing-payment-message" :class="`is-${messageKind}`" role="status">{{ message }}</p>
        <ActionButton v-if="salePrice" :to="`/posts/${post.idx}/checkout`" class="clothing-buy-button">구매하기<span aria-hidden="true">→</span></ActionButton>
        <ActionButton v-else class="clothing-buy-button" disabled>판매 가격 확인이 필요해요</ActionButton>
        <p class="clothing-secure-note">PortOne · Toss Payments 안전 결제</p>
      </div>
    </DetailPanel>
  </section>
</template>

<style scoped>
.clothing-product-photo{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}.clothing-art-spark,.clothing-art-note{z-index:1}.clothing-art-spark{padding:4px 8px;border-radius:20px;background:#fffefaad}.clothing-art-note{padding:6px 9px;border-radius:6px;background:#fffefaad}
</style>
