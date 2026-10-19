<script setup>
import { ref } from 'vue'
import { RouterLink, RouterView, useRoute } from 'vue-router'
import PageSkeleton from './components/PageSkeleton.vue'
import router from './router'

const route = useRoute()
const navigating = ref(false)
const routeKey = () => route.fullPath

// Short intentional pause lets the page skeleton communicate each route change.
router.beforeEach(async () => { navigating.value = true })
router.afterEach(() => window.setTimeout(() => { navigating.value = false }, 280))
</script>

<template>
  <div class="page-shell">
    <header class="topbar">
      <RouterLink class="brand" to="/posts" aria-label="모아 홈"><span class="brand-mark">ㅁ</span><span>모아</span></RouterLink>
      <nav class="main-nav" aria-label="주 메뉴">
        <RouterLink to="/posts">게시글</RouterLink>
        <RouterLink to="/posts/new">글쓰기</RouterLink>
      </nav>
      <div class="account-area"><RouterLink class="account-link" to="/login">로그인</RouterLink><RouterLink class="account-button" to="/signup">회원가입</RouterLink></div>
    </header>
    <main>
      <section class="intro">
        <div class="intro-copy"><div class="issue-line"><span class="live-dot"></span> 오늘의 이야기, 여기 모아</div><h1>생각을 꺼내<br />서로에게 건네는 곳.</h1><p>짧은 메모부터 오래 남기고 싶은 이야기까지,<br class="desktop-break" /> 당신의 문장을 기다리고 있어요.</p></div>
        <div class="orbit" aria-hidden="true"><span class="orbit-inner">모아<br /><b>✳</b></span><span class="orbit-note note-one">한 줄의 시작</span><span class="orbit-note note-two">함께 읽기</span></div>
        <div class="intro-foot"><span>작은 게시판</span><span>당신의 이야기를 기록합니다</span><span class="foot-line"></span></div>
      </section>
      <RouterView v-slot="{ Component }"><Transition name="page" mode="out-in"><PageSkeleton v-if="navigating" key="route-skeleton" /><component v-else :is="Component" :key="routeKey()" /></Transition></RouterView>
    </main>
    <footer><RouterLink class="brand footer-brand" to="/posts"><span class="brand-mark">ㅁ</span><span>모아</span></RouterLink><span>마음이 머무는 작은 게시판</span><span>© 2026 MOA</span></footer>
  </div>
</template>
