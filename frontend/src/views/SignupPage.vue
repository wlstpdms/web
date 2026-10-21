<script setup>
import { ref } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { api } from '../api/index.js'
import { startKakaoAuth } from '../api/kakao.js'
import PageSkeleton from '../components/PageSkeleton.vue'
import AuthPanel from '../components/AuthPanel.vue'
import ActionButton from '../components/ActionButton.vue'

const router = useRouter()
const name = ref('')
const email = ref('')
const password = ref('')
const pending = ref(false)
const error = ref('')

async function signupWithKakao() {
  error.value = ''
  pending.value = true
  try {
    await startKakaoAuth()
  } catch (e) {
    error.value = e.message
    pending.value = false
  }
}

async function submit() {
  error.value = ''
  if (!name.value.trim() || !email.value.trim() || !password.value) {
    error.value = '모든 항목을 입력해 주세요.'
    return
  }
  pending.value = true
  try {
    await api('/user/signup', {
      method: 'POST',
      body: JSON.stringify({ name: name.value.trim(), email: email.value.trim(), password: password.value }),
    })
    await router.push('/login?created=1')
  } catch (e) {
    error.value = e.message
  } finally {
    pending.value = false
  }
}
</script>

<template>
  <PageSkeleton v-if="pending" />
  <AuthPanel v-else eyebrow="오늘부터 한 문장" title="말랑에 오신 걸 환영해요" subtitle="계정을 만들고 매일의 영어 연습을 기록해 보세요.">
      <form class="auth-form" @submit.prevent="submit">
        <label for="signup-name">이름</label>
        <input id="signup-name" v-model="name" autocomplete="name" required placeholder="이름" />
        <label for="signup-email">이메일</label>
        <input id="signup-email" v-model="email" type="email" autocomplete="email" required placeholder="name@example.com" />
        <label for="signup-password">비밀번호</label>
        <input id="signup-password" v-model="password" type="password" autocomplete="new-password" required placeholder="비밀번호" />
        <p v-if="error" class="form-error" role="alert">{{ error }}</p>
        <ActionButton type="submit">가입하기 <span>→</span></ActionButton>
      </form>
      <div class="login-divider"><span>또는</span></div>
      <ActionButton variant="social" @click="signupWithKakao">
        <span class="kakao-login-icon" aria-hidden="true">K</span>
        카카오 닉네임으로 가입하기
      </ActionButton>
      <p class="switch-auth">이미 계정이 있나요? <RouterLink to="/login">로그인</RouterLink></p>
  </AuthPanel>
</template>
