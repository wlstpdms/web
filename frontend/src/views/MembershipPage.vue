<script setup>
import { onMounted, ref } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import { learningApi } from '../api/index.js'

const plans = ref([
  { id: 'free', name: '무료로 계속', price: '₩0', period: '언제든지', description: '매일 가볍게 공부를 이어가요.', features: ['하루 3회 말하기 연습', '기초 표현과 단어 학습', '나의 연속 학습 기록'], current: true },
  { id: 'premium_monthly', name: '말랑 플러스 월간', price: '₩9,900', period: '/ 월', description: '매달 가볍게 결제하고 모든 학습 기능을 이용해요.', features: ['모든 프리미엄 레슨', '무제한 말하기 연습', '상세 학습 리포트', '광고 없이 학습'], highlighted: true, badge: '인기' },
  { id: 'premium_quarterly', name: '말랑 플러스 3개월', price: '₩26,900', period: '/ 3개월', description: '한 계절 동안 꾸준히 공부하는 분께 추천해요.', features: ['모든 프리미엄 레슨', '무제한 말하기 연습', '상세 학습 리포트', '광고 없이 학습'], saving: '월간보다 약 10% 절약' },
  { id: 'premium_yearly', name: '말랑 플러스 연간', price: '₩79,000', period: '/ 년', description: '한 해의 학습 습관을 꾸준히 이어가요.', features: ['모든 프리미엄 레슨', '무제한 말하기 연습', '상세 학습 리포트', '광고 없이 학습', '연간 학습 요약'], saving: '월간보다 약 33% 절약', badge: '가장 알뜰해요' },
])
const notice = ref('')
const loading = ref(false)
const startingTrial = ref(false)
const trialStarted = ref(false)
const checkingOut = ref('')
const loginRequired = ref(false)
const route = useRoute()
const router = useRouter()

async function confirmPayment(paymentId) {
  await learningApi.verifyCheckout(paymentId)
  notice.value = '결제가 확인되어 플랜이 활성화됐어요.'
  await router.replace({ path: route.path, query: {} })
}

onMounted(async () => {
  loading.value = true
  try {
    const data = await learningApi.plans()
    const rows = Array.isArray(data) ? data : data?.items || data?.plans
    if (rows?.length) plans.value = rows.map((plan) => {
      const isFree = plan.id === 'free'
      const isPremium = plan.id === 'premium_monthly'
      const price = typeof plan.price === 'number' ? new Intl.NumberFormat('ko-KR', { style: 'currency', currency: plan.currency || 'KRW', maximumFractionDigits: 0 }).format(plan.price) : plan.price
      return {
        ...plan,
        price,
        period: plan.interval ? `/ ${{ month: '월', quarter: '3개월', year: '년' }[plan.interval] || plan.interval}` : '언제든지',
        description: plan.description || (isFree ? '매일 가볍게 공부를 이어가요.' : '더 자주, 더 깊게 내 페이스로.'),
        current: isFree,
        highlighted: isPremium,
        features: plan.features || (isFree ? ['하루 3회 말하기 연습', '기초 표현과 단어 학습', '나의 연속 학습 기록'] : ['말하기 연습 무제한', '상황별 학습 코스 전체', '주간 학습 리포트', '친구 모임 무제한 참여']),
      }
    })
  } catch { /* Keep the sample plans available before login. */ }
  finally { loading.value = false }
  if (route.query.paymentId) {
    checkingOut.value = 'returning'
    try { await confirmPayment(String(route.query.paymentId)) }
    catch (error) {
      if (error.status === 401) loginRequired.value = true
      notice.value = error.message || '결제 확인을 완료하지 못했어요. 잠시 후 다시 시도해 주세요.'
    } finally { checkingOut.value = '' }
  }
})

async function choose(plan) {
  if (plan.current) return
  checkingOut.value = plan.id
  loginRequired.value = false
  try {
    const order = await learningApi.checkout(plan.id)
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
    if (result?.code) notice.value = result.message || '결제가 취소되었거나 완료되지 않았어요.'
    else if (result?.paymentId) await confirmPayment(result.paymentId)
  } catch (error) {
    if (error.status === 401) {
      loginRequired.value = true
      notice.value = '플랜을 적용하려면 먼저 로그인해 주세요.'
    } else {
      notice.value = error.message || '결제를 시작하지 못했어요. 잠시 후 다시 시도해 주세요.'
    }
  } finally {
    checkingOut.value = ''
  }
}

async function startTrial() {
  startingTrial.value = true
  loginRequired.value = false
  try {
    const result = await learningApi.startTrial()
    trialStarted.value = true
    notice.value = result?.message || '7일 무료 체험이 시작됐어요. 이 과정에서 실제 결제는 진행되지 않습니다.'
  } catch (error) {
    if (error.status === 401) {
      loginRequired.value = true
      notice.value = '무료 체험을 시작하려면 먼저 로그인해 주세요.'
    } else if (error.status === 409) {
      trialStarted.value = true
      notice.value = '무료 체험이 이미 진행 중이거나 사용된 계정입니다.'
    } else {
      notice.value = error.message || '무료 체험을 시작하지 못했어요. 잠시 후 다시 시도해 주세요.'
    }
  } finally { startingTrial.value = false }
}
</script>

<template>
  <section class="membership-page">
    <div class="membership-hero"><div class="membership-copy"><p class="panel-label">A SMALL STEP, EVERY DAY</p><h1>영어 공부가<br /><span>내 일상이 되도록.</span></h1><p>7일 동안 플러스를 무료로 경험해보세요.<br />체험 기간에는 결제되지 않아요.</p><div class="trial-progress"><span class="trial-dot"></span><span>무료 체험 {{ loading ? '확인 중' : '7일 제공' }}</span><span class="trial-separator">—</span><span>지금 시작해도 안심하세요</span></div><button class="trial-start-button" type="button" :disabled="startingTrial || trialStarted" @click="startTrial">{{ startingTrial ? '시작하는 중…' : trialStarted ? '체험이 시작됐어요' : '7일 무료 체험 시작하기' }}<span>&rarr;</span></button></div><div class="membership-ornament" aria-hidden="true"><div class="orbit orbit-one"></div><div class="orbit orbit-two"></div><div class="orbit-core">말</div><span class="orbit-star star-one">✳</span><span class="orbit-star star-two">✦</span><span class="orbit-word">GROW<br />AT YOUR<br />OWN PACE</span></div></div>
    <p v-if="notice" class="notice-line" role="status">{{ notice }} <RouterLink v-if="loginRequired" to="/login?redirect=/membership">로그인하기</RouterLink></p>
    <div class="plan-intro"><div><h2>나에게 맞는 속도로</h2><p>필요한 만큼 공부하고, 언제든 바꿀 수 있어요.</p></div><span>모든 플랜은 부가세 포함</span></div>
    <div class="plans-grid">
      <article v-for="plan in plans" :key="plan.id" class="plan-sheet" :class="{ featured: plan.highlighted, current: plan.current }">
        <div class="plan-head"><div><h3>{{ plan.name }}</h3><p>{{ plan.description }}</p></div><span v-if="plan.highlighted" class="popular-mark">{{ plan.badge || '추천' }}</span><span v-else-if="plan.saving" class="saving-mark">{{ plan.saving }}</span><span v-else-if="plan.current" class="current-mark">현재 플랜</span></div>
        <div class="plan-price"><strong>{{ plan.price }}</strong><span>{{ plan.period }}</span></div>
        <button class="plan-button" :class="{ dark: plan.highlighted }" type="button" :disabled="plan.current || Boolean(checkingOut)" @click="choose(plan)">{{ plan.current ? '이용 중인 플랜' : checkingOut === plan.id ? '결제 준비 중…' : '결제하고 시작하기' }} <span v-if="!plan.current">→</span></button>
        <div class="plan-rule"></div><p class="benefits-label">이 플랜에 포함돼요</p><ul><li v-for="feature in plan.features" :key="feature"><span>✓</span>{{ feature }}</li></ul>
      </article>
    </div>
    <div class="billing-note"><span class="note-icon">i</span><p>PortOne과 토스페이먼츠 안전 결제를 이용해요. 결제가 승인된 뒤에만 플랜이 활성화됩니다. 무료 체험은 결제 없이 시작할 수 있어요.</p></div>
    <div class="membership-back"><RouterLink to="/">← 오늘의 공부로 돌아가기</RouterLink></div>
  </section>
</template>
