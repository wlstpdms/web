<script setup>
import { computed, ref } from 'vue'
import { RouterLink, RouterView, useRoute } from 'vue-router'

const route = useRoute()
const credits = ref(3)
const pageName = computed(() => ({ '/': '오늘의 공부', '/study': '레슨 고르기', '/practice': '혼자 연습', '/groups': '같이 공부', '/membership': '멤버십' }[route.path] || '말랑'))
const today = new Intl.DateTimeFormat('ko-KR', { year: 'numeric', month: 'long', day: 'numeric', weekday: 'long' }).format(new Date())
</script>

<template>
  <div class="app-frame">
    <header class="topbar">
      <RouterLink class="wordmark" to="/" aria-label="말랑 홈"><span class="wordmark-symbol">말</span><span>말랑<span class="wordmark-en">MALANG</span></span></RouterLink>
      <nav class="top-nav" aria-label="주요 메뉴">
        <RouterLink to="/">오늘의 공부</RouterLink>
        <RouterLink to="/study">공부하기</RouterLink>
        <RouterLink to="/groups">같이 공부</RouterLink>
        <RouterLink to="/membership">플랜·결제</RouterLink>
      </nav>
      <div class="top-actions"><span class="credit-pill"><span>✦</span> {{ credits }} 크레딧</span><RouterLink class="profile-chip" to="/login"><span class="profile-avatar">M</span><span>로그인</span></RouterLink><RouterLink class="join-chip" to="/signup">무료 가입</RouterLink></div>
    </header>

    <main class="main-content">
      <div class="page-context"><span class="context-dot"></span>{{ pageName }}<span class="context-date">{{ today }}</span></div>
      <RouterView v-slot="{ Component }"><Transition name="page" mode="out-in"><component :is="Component" :key="route.fullPath" @credits-change="credits = $event" /></Transition></RouterView>
    </main>

    <nav class="mobile-nav" aria-label="모바일 메뉴">
      <RouterLink to="/"><span>⌂</span>홈</RouterLink><RouterLink to="/study"><span>◉</span>공부</RouterLink><RouterLink to="/groups"><span>◎</span>모임</RouterLink><RouterLink to="/membership"><span>✦</span>멤버십</RouterLink>
    </nav>
  </div>
</template>
