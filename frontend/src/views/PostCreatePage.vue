<script setup>
import { onBeforeUnmount, ref } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { api, uploadProductImage } from '../api/index.js'
import PageSkeleton from '../components/PageSkeleton.vue'
import ActionButton from '../components/ActionButton.vue'
import PageHeading from '../components/PageHeading.vue'
const router = useRouter()
const title = ref('')
const contents = ref('')
const imageFile = ref(null)
const imagePreview = ref('')
const pending = ref(false)
const error = ref('')
function selectImage(event) {
  const file = event.target.files?.[0]
  error.value = ''
  if (!file) return
  if (!['image/jpeg', 'image/png', 'image/webp'].includes(file.type) || file.size > 8 * 1024 * 1024) {
    error.value = 'JPG, PNG, WEBP 형식의 8MB 이하 사진을 선택해 주세요.'
    event.target.value = ''
    return
  }
  if (imagePreview.value) URL.revokeObjectURL(imagePreview.value)
  imageFile.value = file
  imagePreview.value = URL.createObjectURL(file)
}
onBeforeUnmount(() => { if (imagePreview.value) URL.revokeObjectURL(imagePreview.value) })
async function submit() {
  error.value = ''
  if (!title.value.trim() || !contents.value.trim()) { error.value = '제목과 내용을 모두 입력해 주세요.'; return }
  pending.value = true
  try {
    const image_url = imageFile.value ? await uploadProductImage(imageFile.value) : null
    const post = await api('/board/register', { method: 'POST', body: JSON.stringify({ title: title.value.trim(), contents: contents.value.trim(), image_url }) })
    await router.push(`/posts/${post.idx}`)
  } catch (e) { error.value = e.message }
  finally { pending.value = false }
}
</script>
<template>
  <PageSkeleton v-if="pending" />
  <section v-else class="workspace form-workspace"><aside class="side-rail"><p class="rail-label">DOJI</p><p class="rail-description">잘 입은 옷이 새 주인을 만나<br />다음 계절에도 사랑받도록.</p><RouterLink class="rail-back" to="/posts">← 옷 둘러보기</RouterLink></aside>
    <div class="content-area"><PageHeading eyebrow="옷장 나누기" title="다음 주인을 기다리는 옷" />
      <form class="write-form" @submit.prevent="submit"><label for="post-image">상품 사진 <small>선택 · JPG, PNG, WEBP · 8MB 이하</small></label><input id="post-image" type="file" accept="image/jpeg,image/png,image/webp" @change="selectImage" /><img v-if="imagePreview" class="post-image-preview" :src="imagePreview" alt="등록할 상품 미리보기" /><label for="post-title">옷 이름</label><input id="post-title" v-model="title" maxlength="120" required placeholder="예: 포근한 브라운 울 코트" /><label for="post-content" class="content-label">옷 소개와 가격</label><textarea id="post-content" v-model="contents" rows="8" required placeholder="브랜드, 사이즈, 상태와 판매 가격을 적어주세요.\n예: M 사이즈 · 두 번 착용 · 35,000원"></textarea><p v-if="error" class="form-error" role="alert">{{ error }}</p><div class="form-bottom"><span>{{ contents.length }}자</span><ActionButton type="submit">옷 등록하기 <span>↗</span></ActionButton></div></form>
    </div>
  </section>
</template>
