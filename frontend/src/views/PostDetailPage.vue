<script setup>
import { onMounted, ref } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import { api } from '../api'
import PageSkeleton from '../components/PageSkeleton.vue'
const route = useRoute()
const post = ref(null)
const loading = ref(true)
const error = ref('')
onMounted(async () => {
  try {
    post.value = await api(`/board/read/${route.params.idx}`)
    if (!post.value) error.value = '해당 번호의 게시글을 찾을 수 없습니다.'
  } catch (e) { error.value = e.message }
  finally { loading.value = false }
})
</script>
<template>
  <PageSkeleton v-if="loading" />
  <section v-else class="workspace"><aside class="side-rail"><p class="rail-label">이야기</p><RouterLink class="rail-item" to="/posts">← 게시글 목록</RouterLink><RouterLink class="rail-item" to="/posts/new">＋ 새 글 쓰기</RouterLink></aside>
    <div class="content-area"><div v-if="error" class="empty-state detail-error"><span class="empty-mark">!</span><h3>게시글을 찾을 수 없어요</h3><p>{{ error }}</p><RouterLink class="text-button" to="/posts">목록으로 돌아가기 ↗</RouterLink></div>
      <article v-else class="detail-article"><div class="detail-top"><p class="eyebrow">게시글 {{ String(post.idx).padStart(2, '0') }}</p><RouterLink class="detail-back" to="/posts">목록으로 돌아가기 ↗</RouterLink></div><h2>{{ post.title }}</h2><div class="detail-rule"></div><p class="detail-content">{{ post.contents }}</p></article>
    </div>
  </section>
</template>
