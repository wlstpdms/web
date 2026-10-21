<script setup>
import { onMounted, ref } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import { api } from '../api/index.js'
import PageSkeleton from '../components/PageSkeleton.vue'

const route = useRoute()
const router = useRouter()
const error = ref('')

onMounted(async () => {
  const { code, state, error: kakaoError } = route.query
  if (kakaoError) {
    error.value = '카카오 로그인이 취소되었거나 완료되지 않았습니다.'
    return
  }
  if (typeof code !== 'string' || typeof state !== 'string') {
    error.value = '카카오 로그인 응답을 확인할 수 없습니다. 다시 시도해 주세요.'
    return
  }

  try {
    await api('/user/kakao/callback', {
      method: 'POST',
      body: JSON.stringify({ code, state }),
    })
    await router.replace('/')
  } catch (e) {
    error.value = e.message
  }
})
</script>

<template>
  <PageSkeleton v-if="!error" />
  <section v-else class="workspace form-workspace">
    <div class="content-area kakao-callback-error">
      <div class="section-heading"><div><p class="eyebrow">카카오 로그인</p><h2>로그인할 수 없어요</h2></div></div>
      <p class="form-error" role="alert">{{ error }}</p>
      <RouterLink class="primary-button kakao-back-link" to="/login">로그인 화면으로 돌아가기 <span>→</span></RouterLink>
    </div>
  </section>
</template>
