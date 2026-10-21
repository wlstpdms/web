<script setup>
defineProps({ modelValue: { type: String, default: '' }, placeholder: { type: String, default: '무엇을 찾으시나요?' }, label: { type: String, default: '검색' } })
const emit = defineEmits(['update:modelValue', 'submit'])
</script>

<template>
  <form class="explore-search" role="search" @submit.prevent="emit('submit')">
    <span class="search-mark" aria-hidden="true">⌕</span>
    <input :value="modelValue" type="search" :placeholder="placeholder" :aria-label="label" @input="emit('update:modelValue', $event.target.value)" />
    <button type="submit" :aria-label="label">검색 <span aria-hidden="true">→</span></button>
  </form>
</template>

<style scoped>
.explore-search{display:flex;align-items:center;gap:12px;width:min(100%,620px);min-height:54px;margin:0 auto 22px;padding:5px 6px 5px 17px;border:1px solid #d9d7ce;border-radius:999px;background:#fffefa;box-shadow:0 7px 24px #202c2b0b}.search-mark{color:#9a8057;font-size:22px}.explore-search input{flex:1;min-width:0;border:0;outline:0;background:transparent;color:#263a3f;font:inherit;font-size:13px}.explore-search button{display:flex;align-items:center;gap:10px;min-height:42px;padding:0 17px;border:0;border-radius:999px;background:#294349;color:#fff;font:inherit;font-size:11px;font-weight:700;cursor:pointer}.explore-search button span{color:#d8c293;font-size:17px}.explore-search button:hover{background:#1e343a}
</style>
