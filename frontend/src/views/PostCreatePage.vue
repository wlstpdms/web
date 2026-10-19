<script setup>
import { ref } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { api } from '../api'
import PageSkeleton from '../components/PageSkeleton.vue'
const router = useRouter()
const title = ref('')
const contents = ref('')
const pending = ref(false)
const error = ref('')
async function submit() {
  error.value = ''
  if (!title.value.trim() || !contents.value.trim()) { error.value = '제목과 내용을 모두 입력해 주세요.'; return }
  pending.value = true
  try {
    const post = await api('/board/register', { method: 'POST', body: JSON.stringify({ title: title.value.trim(), contents: contents.value.trim() }) })
    await router.push(`/posts/${post.idx}`)
  } catch (e) { error.value = e.message }
  finally { pending.value = false }
}
</script>
<template>
  <PageSkeleton v-if="pending" />
  <section v-else class="workspace form-workspace"><aside class="side-rail"><p class="rail-label">새로운 기록</p><p class="rail-description">마음을 담은 한 문장이<br />누군가에게 닿을 수 있어요.</p><RouterLink class="rail-back" to="/posts">← 게시글 목록</RouterLink></aside>
    <div class="content-area"><div class="section-heading"><div><p class="eyebrow">새로운 기록</p><h2>오늘의 이야기를 남겨보세요</h2></div><span class="heading-mark">✳</span></div>
      <form class="write-form" @submit.prevent="submit"><label for="post-title">제목</label><input id="post-title" v-model="title" maxlength="120" required placeholder="이야기의 제목을 적어주세요" /><label for="post-content" class="content-label">내용</label><textarea id="post-content" v-model="contents" rows="8" required placeholder="당신의 생각을 자유롭게 적어보세요."></textarea><p v-if="error" class="form-error" role="alert">{{ error }}</p><div class="form-bottom"><span>{{ contents.length }}자</span><button class="primary-button" type="submit">이야기 등록하기 <span>↗</span></button></div></form>
    </div>
  </section>
</template>
