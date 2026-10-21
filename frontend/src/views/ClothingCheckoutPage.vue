<script setup>
import { computed, onMounted, ref } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import { api } from '../api/index.js'
import PageSkeleton from '../components/PageSkeleton.vue'
import ActionButton from '../components/ActionButton.vue'
import { productImageOf } from '../api/productMedia.js'

const route = useRoute()
const router = useRouter()
const product = ref(null)
const loading = ref(true)
const paying = ref(false)
const accepted = ref(false)
const message = ref('')
const paid = ref(false)
const salePrice = computed(() => {
  const contents = product.value?.contents || ''
  const match = contents.match(/판매가\s*[:：]?\s*([\d,]+)\s*원/)
    || contents.match(/가격\s*[:：]?\s*([\d,]+)\s*원/)
    || contents.match(/구매가\s*[:：]?\s*([\d,]+)\s*원/)
  return match ? Number(match[1].replaceAll(',', '')) : null
})
const priceText = computed(() => salePrice.value === null ? '가격 협의' : salePrice.value.toLocaleString('ko-KR') + '원')
const productIcon = computed(() => /가방|백/.test(product.value?.title || '') ? '👜' : /신발|스니커즈/.test(product.value?.title || '') ? '👟' : /바지|팬츠|슬랙스|데님/.test(product.value?.title || '') ? '👖' : /셔츠|니트|상의/.test(product.value?.title || '') ? '👕' : '🧥')
const productImage = computed(() => productImageOf(product.value))

async function verify(paymentId) {
  await api('/payments/clothing/verify', { method: 'POST', body: JSON.stringify({ payment_id: paymentId }) })
  paid.value = true
  message.value = '결제가 확인됐어요. 상품 구매가 완료되었습니다.'
  await router.replace({ path: route.path, query: {} })
}

async function pay() {
  if (!accepted.value || !product.value || paying.value) return
  paying.value = true
  message.value = ''
  try {
    const order = await api('/payments/clothing/orders', { method: 'POST', body: JSON.stringify({ board_idx: product.value.idx }) })
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
      redirectUrl: window.location.origin + route.path,
    })
    if (result?.code) message.value = result.message || '결제가 취소되었거나 완료되지 않았어요.'
    else if (result?.paymentId) await verify(result.paymentId)
  } catch (error) {
    if (error.status === 401) {
      window.location.assign('/login?redirect=' + encodeURIComponent(route.fullPath))
      return
    }
    message.value = error.message || '결제를 시작하지 못했어요. 잠시 후 다시 시도해 주세요.'
  } finally { paying.value = false }
}

onMounted(async () => {
  try {
    product.value = await api('/board/read/' + route.params.idx)
    if (route.query.paymentId) await verify(String(route.query.paymentId))
  } catch (error) {
    message.value = error.message || '상품을 불러오지 못했어요.'
  } finally { loading.value = false }
})
</script>

<template>
  <PageSkeleton v-if="loading" />
  <section v-else class="membership-page doji-checkout-page">
    <RouterLink class="clothing-back" :to="'/posts/' + route.params.idx">← 상품 상세로 돌아가기</RouterLink>
    <div class="membership-hero">
      <div class="membership-copy">
        <p class="panel-label">DOJI · SECOND CHANCE</p>
        <h1>마음에 든 옷이<br /><span>새 주인을 만나요.</span></h1>
        <p>주문 상품과 금액을 확인하고<br />안전하게 결제를 이어가세요.</p>
        <div class="trial-progress"><span class="trial-dot"></span><span>간편하고 안전한 결제</span><span class="trial-separator">—</span><span>PortOne · 토스페이먼츠</span></div>
      </div>
      <div class="membership-ornament" aria-hidden="true"><div class="orbit orbit-one"></div><div class="orbit orbit-two"></div><div class="orbit-core">{{ productIcon }}</div><span class="orbit-star star-one">✳</span><span class="orbit-star star-two">✦</span><span class="orbit-word">GIVE IT<br />A NEW<br />CHAPTER</span></div>
    </div>
    <p v-if="message" class="notice-line" :class="{ 'doji-payment-success': paid }" role="status">{{ message }}</p>
    <div v-if="!product" class="clothing-detail-error" role="alert">{{ message }}</div>
    <template v-else>
      <div class="plan-intro"><div><h2>주문 내용을 확인해 주세요</h2><p>선택하신 상품과 결제 금액이에요.</p></div><span>DOJI SECURE CHECKOUT</span></div>
      <div class="plans-grid doji-checkout-grid">
        <article class="plan-sheet featured doji-order-sheet">
          <div class="plan-head"><div><h3>주문 상품</h3><p>다음 주인을 기다리는 옷</p></div><span class="popular-mark">DOJI</span></div>
          <div class="checkout-product"><div class="checkout-product-art" aria-hidden="true"><img v-if="productImage" class="checkout-product-photo" :src="productImage" alt="" /><span v-else>{{ productIcon }}</span></div><div class="checkout-product-copy"><p>DOJI 옷장</p><h3>{{ product.title }}</h3><span>중고 의류 상품 · 단품</span></div></div>
          <div class="plan-rule"></div><p class="checkout-description">{{ product.contents }}</p>
          <div class="plan-price checkout-price"><strong>{{ priceText }}</strong><span>총 결제 금액</span></div>
        </article>
        <article class="plan-sheet doji-pay-sheet">
          <div class="plan-head"><div><h3>결제 방법</h3><p>원하시는 카드로 결제할 수 있어요.</p></div><span class="saving-mark">CARD</span></div>
          <div class="checkout-method"><span class="checkout-method-icon">▣</span><span><strong>신용·체크카드</strong><small>토스페이먼츠 · PortOne</small></span><span class="checkout-radio"></span></div>
          <label class="checkout-agreement"><input v-model="accepted" type="checkbox" /><span>주문 상품과 결제 금액을 확인했으며, 결제 진행에 동의합니다.</span></label>
          <ActionButton class="doji-pay-button" :disabled="!accepted || paying || paid || !salePrice" @click="pay">{{ paid ? '구매가 완료됐어요' : paying ? '결제 요청 중…' : priceText + ' 결제하기' }}<span v-if="!paid">→</span></ActionButton>
          <p class="checkout-secure-note">결제 승인이 확인된 뒤 주문이 완료됩니다.</p>
        </article>
      </div>
      <div class="billing-note"><span class="note-icon">i</span><p>결제 승인 후에만 주문이 완료돼요. 결제 도중 취소하면 상품 결제가 진행되지 않습니다.</p></div>
    </template>
    <div class="membership-back"><RouterLink :to="'/posts/' + route.params.idx">← 상품 상세로 돌아가기</RouterLink></div>
  </section>
</template>
