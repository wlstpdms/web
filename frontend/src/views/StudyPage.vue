<script setup>
import { computed, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { learningApi } from '../api/index.js'

const lessons = ref([])
const loading = ref(true)
const error = ref('')
const activeLevel = ref('전체')
const levels = ['전체', '초급', '중급']
const levelMap = { beginner: '초급', intermediate: '중급', advanced: '고급' }
const visibleLessons = computed(() => lessons.value.filter((lesson) => activeLevel.value === '전체' || levelMap[lesson.level] === activeLevel.value))

onMounted(async () => {
  try {
    const response = await learningApi.lessons()
    lessons.value = Array.isArray(response) ? response : response?.items || []
  } catch (cause) {
    error.value = cause.message || '레슨을 불러오지 못했어요.'
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <section class="study-catalog-page">
    <div class="study-catalog-hero">
      <div>
        <p class="panel-label">오늘의 영어 연습</p>
        <h1>지금 필요한 말부터<br />하나씩 익혀봐요.</h1>
        <p>짧은 표현을 듣고, 직접 말해보며 내 문장으로 만들어요.</p>
      </div>
      <div class="study-catalog-art" aria-hidden="true"><span>HELLO</span><strong>말</strong><i>✳</i></div>
    </div>

    <div class="study-catalog-toolbar">
      <div><h2>연습할 레슨</h2><p>한 번에 5분이면 충분해요.</p></div>
      <div class="study-level-filters" aria-label="난이도 선택">
        <button v-for="level in levels" :key="level" type="button" :class="{ active: activeLevel === level }" @click="activeLevel = level">{{ level }}</button>
      </div>
    </div>

    <p v-if="loading" class="study-catalog-state" role="status">레슨을 불러오고 있어요…</p>
    <div v-else-if="error" class="study-catalog-state is-error" role="alert">{{ error }} <button type="button" @click="$router.go(0)">다시 시도</button></div>
    <div v-else-if="visibleLessons.length" class="study-lesson-list">
      <article v-for="(lesson, index) in visibleLessons" :key="lesson.id" class="study-lesson-row">
        <span class="study-lesson-mark" :class="`tone-${index % 3}`" aria-hidden="true">{{ ['話', 'Aa', '✳'][index % 3] }}</span>
        <div class="study-lesson-copy">
          <div class="study-lesson-meta"><span>{{ levelMap[lesson.level] || '연습' }}</span><span>{{ lesson.duration_minutes || 5 }}분</span><span v-if="lesson.premium" class="study-premium-tag">PLUS</span></div>
          <h3>{{ lesson.title }}</h3>
          <p>{{ lesson.category || '일상 회화' }} 주제 표현을 익혀요.</p>
        </div>
        <RouterLink v-if="!lesson.premium" class="study-lesson-action" :to="{ path: '/practice', query: { lesson: lesson.id } }">연습하기 <span>→</span></RouterLink>
        <RouterLink v-else class="study-lesson-action is-plus" to="/membership">플랜 보기 <span>→</span></RouterLink>
      </article>
    </div>
    <div v-else class="study-catalog-state">선택한 난이도의 레슨을 준비 중이에요.</div>

    <div class="study-catalog-footer"><RouterLink to="/">← 오늘의 공부 홈</RouterLink><RouterLink to="/groups">친구와 함께 공부하기 <span>→</span></RouterLink></div>
  </section>
</template>
