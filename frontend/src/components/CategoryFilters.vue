<script setup>
defineProps({ categories: { type: Array, required: true }, modelValue: { type: String, required: true } })
const emit = defineEmits(['update:modelValue'])
</script>

<template>
  <nav class="category-filters" aria-label="카테고리">
    <button v-for="category in categories" :key="category.name" type="button" :aria-pressed="modelValue === category.name" :class="{ active: modelValue === category.name }" @click="emit('update:modelValue', category.name)">
      <span aria-hidden="true">{{ category.icon }}</span>{{ category.name }}
    </button>
  </nav>
</template>

<style scoped>
.category-filters{display:flex;justify-content:center;gap:8px;margin:0 auto 30px;overflow-x:auto;padding:2px 1px 8px;scrollbar-width:thin}.category-filters button{display:flex;align-items:center;gap:7px;flex:none;padding:9px 14px;border:1px solid var(--brand-line,#dfddd4);border-radius:999px;background:var(--brand-paper-muted,#fbfaf6);color:var(--brand-muted-strong,#626d69);font:inherit;font-size:11px;white-space:nowrap;cursor:pointer;transition:background .15s,border-color .15s,color .15s}.category-filters button:hover{border-color:var(--brand-accent,#9d8965);color:var(--brand-ink,#334a4b)}.category-filters button.active{border-color:var(--brand-ink,#344f50);background:var(--brand-ink,#344f50);color:#fff}.category-filters button span{font-size:14px}@media(max-width:620px){.category-filters{justify-content:flex-start;margin-bottom:22px}}
</style>
