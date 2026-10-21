<script setup>
import { computed, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { useRoute } from 'vue-router'
import { learningApi } from '../api/index.js'

const emit = defineEmits(['credits-change'])
const route = useRoute()
const index = ref(0)
const flipped = ref(false)
const completed = ref(false)
const saving = ref(false)
const message = ref('')
const lesson = ref({ id: 'daily-small-talk', title: '카페에서 주문하기', subtitle: '상황에 맞게 한 문장 말해봐요', phrases: [
  { ko: '아이스 아메리카노 한 잔 주세요.', en: 'Can I get an iced Americano?', hint: 'Can I get…? 으로 주문을 시작해요.' },
  { ko: '사이즈는 미디엄으로 할게요.', en: 'I’ll have a medium, please.', hint: 'I’ll have… 는 선택을 말할 때 써요.' },
  { ko: '여기서 마실게요.', en: 'For here, please.', hint: '짧고 자연스럽게, For here.' },
  { ko: '카드로 결제할게요.', en: 'I’ll pay by card.', hint: 'pay by card 는 카드로 결제한다는 뜻이에요.' },
  { ko: '감사합니다. 좋은 하루 보내세요!', en: 'Thanks. Have a nice day!', hint: '마지막 인사도 자신 있게 말해봐요.' },
] })
const current = computed(() => lesson.value.phrases[index.value])
const progress = computed(() => (index.value / lesson.value.phrases.length) * 100)

onMounted(async () => {
  try {
    const catalog = await learningApi.lessons()
    const rows = Array.isArray(catalog) ? catalog : catalog?.items
    const selected = rows?.find((item) => String(item.id) === String(route.query.lesson)) || rows?.[0]
    if (selected?.id != null) {
      lesson.value = { ...lesson.value, id: selected.id, title: selected.title || selected.name || lesson.value.title }
      try {
        const data = await learningApi.lesson(selected.id)
        const steps = data?.steps || data?.items || data?.phrases
        if (steps?.length) lesson.value = { ...lesson.value, ...data, phrases: steps.map((step) => ({ ko: step.prompt_ko || step.ko || step.prompt || '', en: step.answer_en || step.en || step.answer || '', hint: step.explanation_ko || step.hint || '' })) }
      } catch { /* Lesson details may require login; keep the sample phrase set. */ }
    }
  } catch { /* The built-in sample keeps logged-out practice available. */ }
})

function nextPhrase() {
  if (index.value < lesson.value.phrases.length - 1) { index.value += 1; flipped.value = false }
  else finish()
}
async function finish() {
  saving.value = true
  try {
    const result = await learningApi.completeLesson(lesson.value.id)
    if (result?.credits != null) emit('credits-change', result.credits)
    message.value = `${result?.xp_earned ?? 30} XP를 모았어요.`
  } catch { message.value = '오늘의 연습을 마쳤어요. XP는 체험용으로 표시됩니다.' }
  completed.value = true
  saving.value = false
}
</script>

<template>
  <section class="practice-page">
    <RouterLink class="back-link" to="/">← 오늘의 공부</RouterLink>
    <div class="practice-heading"><div><p class="panel-label">SPEAKING · 5 MIN</p><h1>{{ lesson.title }}</h1><p>{{ lesson.subtitle }}</p></div><span class="practice-counter">{{ String(Math.min(index + 1, lesson.phrases.length)).padStart(2, '0') }} <i>/ {{ String(lesson.phrases.length).padStart(2, '0') }}</i></span></div>
    <div class="practice-progress"><span :style="{ width: completed ? '100%' : `${progress}%` }"></span></div>
    <RouterLink class="practice-plan-link" to="/membership"><span>더 많은 레슨과 학습 혜택을 만나보세요</span><strong>플랜·결제 옵션 보기 <b>→</b></strong></RouterLink>
    <div v-if="!completed" class="phrase-stage">
      <div class="phrase-label"><span class="phrase-dot"></span> 한국어 문장을 영어로 말해보세요</div>
      <button class="phrase-card" type="button" :class="{ revealed: flipped }" @click="flipped = !flipped" @keydown.enter="flipped = !flipped">
        <span class="phrase-count">TODAY’S PHRASE {{ String(index + 1).padStart(2, '0') }}</span>
        <span class="phrase-ko">{{ current.ko }}</span>
        <span v-if="flipped" class="phrase-en">{{ current.en }}</span>
        <span class="phrase-hint">{{ flipped ? current.hint : '답 확인하기 · 눌러서 뒤집기' }}</span>
        <span class="phrase-card-mark" aria-hidden="true">{{ flipped ? '↻' : 'Aa' }}</span>
      </button>
      <div class="practice-actions"><button class="quiet-button" type="button" @click="flipped = !flipped">{{ flipped ? '한국어 다시 보기' : '정답 보기' }}</button><button class="start-button" type="button" @click="nextPhrase">{{ index === lesson.phrases.length - 1 ? '오늘 연습 마치기' : '다음 문장' }} <span>→</span></button></div>
      <p class="practice-guidance">소리 내서 한 번 말해보고, 내 속도로 다음 문장으로 넘어가요.</p>
    </div>
    <div v-else class="completion-stage"><div class="completion-spark">✳</div><p class="panel-label">PRACTICE COMPLETE</p><h2>오늘의 한 문장,<br />잘 해냈어요.</h2><p>{{ message }}</p><div class="completion-xp"><strong>+30</strong><span>XP</span></div><RouterLink to="/" class="start-button">오늘의 공부로 돌아가기 <span>↗</span></RouterLink></div>
    <p v-if="saving" class="notice-line" role="status">학습을 마무리하고 있어요…</p>
  </section>
</template>
