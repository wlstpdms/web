<script setup>
import { computed, ref } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import { api } from '../api'
import PageSkeleton from '../components/PageSkeleton.vue'
const route = useRoute()
const router = useRouter()
const email = ref('')
const password = ref('')
const pending = ref(false)
const error = ref('')
const created = computed(() => route.query.created === '1')
async function submit() {
  error.value = ''
  if (!email.value.trim() || !password.value) { error.value = '이메일과 비밀번호를 입력해 주세요.'; return }
  pending.value = true
  try {
    const result = await api('/user/login', { method: 'POST', body: JSON.stringify({ email: email.value.trim(), password: password.value }) })
    if (!result) { error.value = '이메일 또는 비밀번호를 확인해 주세요.'; return }
    await router.push('/posts')
  } catch (e) { error.value = e.message }
  finally { pending.value = false }
}
</script>
<template>
  <PageSkeleton v-if="pending" />
  <section v-else class="workspace form-workspace"><aside class="side-rail"><p class="rail-label">다시 만나 반가워요</p><p class="rail-description">로그인하고 이어서<br />이야기를 나눠보세요.</p></aside>
    <div class="content-area"><div class="section-heading"><div><p class="eyebrow">내 계정</p><h2>다시 만나 반가워요</h2></div><span class="heading-mark">✳</span></div>
      <p v-if="created" class="form-success" role="status">가입이 완료됐어요. 로그인해 주세요.</p>
      <form class="auth-form" @submit.prevent="submit"><label for="login-email">이메일</label><input id="login-email" v-model="email" type="email" autocomplete="email" required placeholder="name@example.com" /><label for="login-password">비밀번호</label><input id="login-password" v-model="password" type="password" autocomplete="current-password" required placeholder="비밀번호" /><p v-if="error" class="form-error" role="alert">{{ error }}</p><button class="primary-button" type="submit">로그인 <span>↗</span></button></form>
      <p class="switch-auth">아직 계정이 없나요? <RouterLink to="/signup">회원가입</RouterLink></p>
    </div>
  </section>
</template>
