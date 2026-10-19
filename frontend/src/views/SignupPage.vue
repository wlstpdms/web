<script setup>
import { ref } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { api } from '../api'
import PageSkeleton from '../components/PageSkeleton.vue'
const router = useRouter()
const name = ref('')
const email = ref('')
const password = ref('')
const pending = ref(false)
const error = ref('')
async function submit() {
  error.value = ''
  if (!name.value.trim() || !email.value.trim() || !password.value) { error.value = '모든 항목을 입력해 주세요.'; return }
  pending.value = true
  try {
    await api('/user/signup', { method: 'POST', body: JSON.stringify({ name: name.value.trim(), email: email.value.trim(), password: password.value }) })
    await router.push('/login?created=1')
  } catch (e) { error.value = e.message }
  finally { pending.value = false }
}
</script>
<template>
  <PageSkeleton v-if="pending" />
  <section v-else class="workspace form-workspace"><aside class="side-rail"><p class="rail-label">모아 시작하기</p><p class="rail-description">이메일로 계정을 만들고<br />당신의 이야기를 남겨보세요.</p></aside>
    <div class="content-area"><div class="section-heading"><div><p class="eyebrow">함께 쓰기</p><h2>모아에 오신 걸 환영해요</h2></div><span class="heading-mark">✳</span></div>
      <form class="auth-form" @submit.prevent="submit"><label for="signup-name">이름</label><input id="signup-name" v-model="name" autocomplete="name" required placeholder="이름" /><label for="signup-email">이메일</label><input id="signup-email" v-model="email" type="email" autocomplete="email" required placeholder="name@example.com" /><label for="signup-password">비밀번호</label><input id="signup-password" v-model="password" type="password" autocomplete="new-password" required placeholder="비밀번호" /><p v-if="error" class="form-error" role="alert">{{ error }}</p><button class="primary-button" type="submit">가입하기 <span>↗</span></button></form>
      <p class="switch-auth">이미 계정이 있나요? <RouterLink to="/login">로그인</RouterLink></p>
    </div>
  </section>
</template>
