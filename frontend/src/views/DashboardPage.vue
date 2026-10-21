<script setup>
import { onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { learningApi } from '../api/index.js'

const emit = defineEmits(['credits-change'])
const syncing = ref(true)
const notice = ref('')
const dashboard = ref({
  user: { display_name: '지민', level: '초급 2' },
  progress: { streak_days: 4, xp: 680, weekly: [{ day: '월', xp: 24 }, { day: '화', xp: 36 }, { day: '수', xp: 18 }, { day: '목', xp: 42 }, { day: '금', xp: 0 }, { day: '토', xp: 0 }, { day: '일', xp: 0 }] },
  next_lesson: { id: 'daily-small-talk', title: '카페에서 주문하기', subtitle: '오늘의 표현 5개 · 듣고 따라 말하기', duration_minutes: 5, xp_reward: 30 },
  groups: [{ id: 'lunch-club', name: '점심 영어 한 입', members: 6, activity: '오늘의 질문에 4명이 답했어요' }],
  credits: { available: 3, daily_limit: 5 }, subscription: { plan: 'free', trial_days_left: 7 },
})

function weekdayLabel(value) {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(String(value))) return value
  const [year, month, day] = value.split('-').map(Number)
  return new Intl.DateTimeFormat('ko-KR', { weekday: 'short' }).format(new Date(year, month - 1, day))
}

onMounted(async () => {
  try {
    const data = await learningApi.dashboard()
    if (data) {
      dashboard.value = { ...dashboard.value, ...data }
      if (data.progress) dashboard.value.progress = { ...dashboard.value.progress, ...data.progress,
        weekly: data.progress.weekly?.map((day) => ({ ...day, day: weekdayLabel(day.day) })) ?? dashboard.value.progress.weekly }
    }
    if (dashboard.value.credits?.available != null) emit('credits-change', dashboard.value.credits.available)
  } catch {
    notice.value = '지금은 체험 화면으로 보고 있어요. 로그인 후 학습 기록이 저장됩니다.'
  } finally { syncing.value = false }
})

async function earnCredits() {
  notice.value = '체험용 광고를 확인했어요. 크레딧 적립은 시뮬레이션이에요.'
  try {
    const result = await learningApi.rewardAd()
    if (result?.available != null) emit('credits-change', result.available)
  } catch { emit('credits-change', Math.min((dashboard.value.credits?.available ?? 3) + 1, 5)) }
}
</script>

<template>
  <section class="dashboard-page">
    <div class="welcome-row">
      <div><p class="date-kicker">TUESDAY · YOUR STUDY NOTE</p><h1>지민 님, 오늘도<br class="small-only" /> 영어 한 문장 해볼까요?</h1><p class="welcome-sub">짧게라도 매일 말하면, 어느새 내 표현이 돼요.</p></div>
      <div class="streak-stamp" aria-label="연속 학습 4일"><span class="stamp-sun">✳</span><strong>{{ dashboard.progress.streak_days }}일</strong><small>연속 공부 중</small></div>
    </div>

    <p v-if="notice" class="notice-line" role="status">{{ notice }}</p>

    <div class="study-layout">
      <section class="today-lesson" aria-labelledby="lesson-title">
        <div class="lesson-topline"><span class="lesson-tag"><span></span> 오늘의 5분 연습</span><span class="lesson-index">{{ syncing ? '불러오는 중' : 'OCT 20 / TUE' }}</span></div>
        <div class="lesson-content">
          <div class="lesson-copy"><p class="lesson-level">{{ dashboard.user.level }} · 말하기</p><h2 id="lesson-title">{{ dashboard.next_lesson.title }}</h2><p>{{ dashboard.next_lesson.subtitle }}</p><div class="lesson-meta"><span>◷ {{ dashboard.next_lesson.duration_minutes }}분</span><span>✦ 완료하면 {{ dashboard.next_lesson.xp_reward }} XP</span></div><RouterLink class="start-button" :to="{ path: '/practice', query: { lesson: dashboard.next_lesson.id } }">연습 시작하기 <span>↗</span></RouterLink></div>
          <div class="lesson-visual" aria-hidden="true"><div class="speech s-one">Can I get<br />a latte?</div><div class="speech s-two">따뜻한 라테<br />한 잔 주세요</div><div class="cup"><i></i><b></b></div><span class="visual-spark">✳</span><span class="visual-label">SAY IT<br />YOUR WAY</span></div>
        </div>
        <div class="lesson-bottom"><span>오늘 한 문장, 내일은 더 자연스럽게</span><span class="bottom-rule"></span><span>01 — 05</span></div>
      </section>

      <aside class="progress-column">
        <section class="xp-panel">
          <div class="panel-heading"><div><p class="panel-label">MY JOURNEY</p><h2>배움의 리듬</h2></div><span class="level-chip">{{ dashboard.user.level }}</span></div>
          <div class="xp-number"><strong>{{ dashboard.progress.xp.toLocaleString() }}</strong><span>XP</span></div>
          <div class="xp-track"><span :style="{ width: `${Math.min((dashboard.progress.xp % 1000) / 10, 100)}%` }"></span></div>
          <div class="xp-caption"><span>다음 레벨까지</span><strong>{{ 1000 - dashboard.progress.xp % 1000 }} XP</strong></div>
          <div class="week-chart" aria-label="이번 주 학습 기록">
            <div v-for="(day, index) in dashboard.progress.weekly" :key="day.day" class="week-day"><div class="bar-track"><span :style="{ height: `${Math.max(day.xp ? Math.min(day.xp * 1.8, 100) : 5, 5)}%` }" :class="{ today: index === 1, done: day.xp > 0 }"></span></div><small>{{ day.day }}</small></div>
          </div>
        </section>

        <section class="credit-panel">
          <div class="credit-icon">✳</div><div class="credit-copy"><strong>연습 크레딧 {{ dashboard.credits.available }}개</strong><span>오늘 {{ dashboard.credits.daily_limit }}개까지 무료</span></div><button class="earn-button" type="button" @click="earnCredits">+1 받기</button>
          <p>광고와 크레딧 적립은 화면 체험용으로 시뮬레이션돼요.</p>
        </section>
      </aside>
    </div>

    <div class="dashboard-study-link"><div><strong>다른 주제도 공부해볼까요?</strong><span>카페·일상 회화부터 업무 영어까지 골라서 연습할 수 있어요.</span></div><RouterLink to="/study">레슨 둘러보기 <b>→</b></RouterLink></div>

    <section class="lower-row">
      <div class="group-teaser"><div class="group-doodle" aria-hidden="true"><span>안녕!</span><i>↗</i></div><div class="group-teaser-copy"><p class="panel-label">STUDY TOGETHER</p><h2>혼자 하면 작심삼일,<br />같이 하면 오늘도 한 걸음.</h2><p>친구들과 짧은 영어 질문을 주고받아요.</p><RouterLink to="/groups" class="under-link">공부 모임 둘러보기 <span>→</span></RouterLink></div></div>
      <div class="trial-note"><span class="trial-mark">M</span><div><p class="panel-label">말랑 플러스</p><h3>첫 7일은 가볍게 시작해요</h3><p>무제한 연습과 나만의 학습 리포트를 만나보세요.</p><RouterLink to="/membership" class="under-link">플랜 알아보기 <span>→</span></RouterLink></div></div>
    </section>
    <footer class="dashboard-footer"><span>오늘의 한 문장, 내일의 나를 만들어요.</span><span>LANGUAGE IS A DAILY PRACTICE</span></footer>
  </section>
</template>
