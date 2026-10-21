<script setup>
import { computed, ref } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import { api } from '../api/index.js'
import { startKakaoAuth } from '../api/kakao.js'
import PageSkeleton from '../components/PageSkeleton.vue'
import AuthPanel from '../components/AuthPanel.vue'
import ActionButton from '../components/ActionButton.vue'

const route = useRoute()
const router = useRouter()
const email = ref('')
const password = ref('')
const pending = ref(false)
const kakaoError = ref('')
const error = ref(String(route.query.socialError || ''))
const created = computed(() => route.query.created === '1')

async function submit() {
  error.value = ''
  if (!email.value.trim() || !password.value) {
    error.value = '이메일과 비밀번호를 입력해 주세요.'
    return
  }
  pending.value = true
  try {
    await api('/user/login', {
      method: 'POST',
      body: JSON.stringify({ email: email.value.trim(), password: password.value }),
    })
    const requestedPath = typeof route.query.redirect === 'string' ? route.query.redirect : '/'
    const nextPath = requestedPath.startsWith('/') && !requestedPath.startsWith('//') ? requestedPath : '/'
    if (nextPath.startsWith('/posts')) window.location.assign(nextPath)
    else await router.push(nextPath)
  } catch (e) {
    error.value = e.message
  } finally {
    pending.value = false
  }
}

async function loginWithKakao() {
  kakaoError.value = ''
  pending.value = true
  try {
    await startKakaoAuth()
  } catch (e) {
    kakaoError.value = e.message || '카카오 로그인 페이지를 열지 못했습니다.'
    pending.value = false
  }
}
</script>

<template>
  <PageSkeleton v-if="pending" />
  <AuthPanel v-else eyebrow="내 계정" title="다시 만나 반가워요" subtitle="오늘의 영어 연습을 이어가고, 작은 성취를 쌓아 보세요.">
      <p v-if="created" class="form-success" role="status">가입이 완료됐어요. 로그인해 주세요.</p>
      <form class="auth-form" @submit.prevent="submit">
        <label for="login-email">이메일</label>
        <input id="login-email" v-model="email" type="email" autocomplete="email" required placeholder="name@example.com" />
        <label for="login-password">비밀번호</label>
        <input id="login-password" v-model="password" type="password" autocomplete="current-password" required placeholder="비밀번호" />
        <p v-if="error" class="form-error" role="alert">{{ error }}</p>
        <ActionButton type="submit">로그인 <span>→</span></ActionButton>
      </form>
      <div class="login-divider"><span>또는</span></div>
      <ActionButton variant="social" @click="loginWithKakao">
        <span class="kakao-login-icon" aria-hidden="true">K</span>
        카카오로 시작하기
      </ActionButton>
      <p v-if="kakaoError" class="form-error kakao-login-error" role="alert">{{ kakaoError }}</p>
      <p class="switch-auth">아직 계정이 없나요? <RouterLink to="/signup">회원가입</RouterLink></p>
  </AuthPanel>
</template>
