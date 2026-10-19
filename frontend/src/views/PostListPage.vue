<script setup>
import { onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { api } from '../api'
const posts = ref([])
const loading = ref(true)
const error = ref('')
onMounted(async () => {
  try { posts.value = await api('/board/list') }
  catch (e) { error.value = e.message }
  finally { loading.value = false }
})
</script>
<template>
  <section class="workspace"><aside class="side-rail"><p class="rail-label">공간</p><RouterLink class="rail-item active" to="/posts">▤ 게시글 목록</RouterLink><RouterLink class="rail-item" to="/posts/new">＋ 새 글 쓰기</RouterLink><div class="rail-note"><span class="note-icon">↗</span><p>마음을 담은 한 문장이<br />누군가에게 닿을 수 있어요.</p></div></aside>
    <div class="content-area"><div class="section-heading"><div><p class="eyebrow">모아 둔 이야기</p><h2>모두의 이야기</h2></div><RouterLink class="primary-button link-button" to="/posts/new">글쓰기 <span>↗</span></RouterLink></div>
      <div v-if="loading" class="post-list" aria-label="게시글 목록을 불러오는 중" aria-busy="true"><div v-for="n in 4" :key="n" class="post-skeleton"><span class="skeleton-circle"></span><span class="skeleton-post-copy"><i></i><i></i></span></div></div>
      <div v-else-if="error" class="empty-state"><span class="empty-mark">!</span><h3>게시글을 불러오지 못했어요</h3><p>{{ error }}</p><button class="text-button" @click="$router.go(0)">다시 불러오기 ↗</button></div>
      <div v-else-if="posts.length" class="post-list"><RouterLink v-for="post in [...posts].reverse()" :key="post.idx" class="post-row" :to="`/posts/${post.idx}`"><span class="post-number">{{ String(post.idx).padStart(2, '0') }}</span><span class="post-info"><strong>{{ post.title }}</strong><small>{{ post.contents.slice(0, 100) }}{{ post.contents.length > 100 ? '…' : '' }}</small></span><span class="row-arrow">↗</span></RouterLink></div>
      <div v-else class="empty-state"><span class="empty-mark">✳</span><h3>아직 게시글이 없어요</h3><p>첫 번째 이야기를 남겨 이곳을 채워보세요.</p><RouterLink class="text-button" to="/posts/new">첫 글 쓰기 ↗</RouterLink></div>
    </div>
  </section>
</template>
