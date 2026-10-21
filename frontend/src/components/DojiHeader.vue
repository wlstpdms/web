<script setup>
import { RouterLink } from 'vue-router'
</script>

<template>
  <header class="doji-topbar">
      <RouterLink class="doji-wordmark" to="/posts" aria-label="DOJI 홈"><strong>DOJI</strong><span>옷의 다음 장면</span></RouterLink>
      <nav class="doji-nav" aria-label="DOJI 메뉴"><RouterLink to="/posts">옷 둘러보기</RouterLink><RouterLink to="/posts/new">상품 올리기</RouterLink></nav>
      <RouterLink class="doji-account" to="/login">로그인</RouterLink>
  </header>
  <nav class="doji-mobile-nav" aria-label="DOJI 모바일 메뉴"><RouterLink to="/posts">옷 둘러보기</RouterLink><RouterLink to="/posts/new">상품 올리기</RouterLink></nav>
</template>
