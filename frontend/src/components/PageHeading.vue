<script setup>
defineProps({ eyebrow: { type: String, default: '' }, title: { type: String, required: true }, description: { type: String, default: '' }, level: { type: String, default: 'h2' } })
</script>

<template>
  <header class="page-heading">
    <div><p v-if="eyebrow" class="page-eyebrow">{{ eyebrow }}</p><component :is="level" class="page-title">{{ title }}</component><p v-if="description" class="page-description">{{ description }}</p></div>
    <div v-if="$slots.default" class="page-heading-action"><slot /></div>
  </header>
</template>

<style scoped>
.page-heading{display:flex;align-items:center;justify-content:space-between;gap:18px;margin:0 0 20px}.page-eyebrow{margin:0 0 7px;color:var(--brand-accent,#927b53);font-size:9px;font-weight:700;letter-spacing:.14em;text-transform:uppercase}.page-title{margin:0;color:var(--brand-ink,#293e42);font-size:25px;line-height:1.35;letter-spacing:-.045em;font-weight:650}.page-description{margin:6px 0 0;color:var(--brand-muted,#7d8580);font-size:11px;line-height:1.65}.page-heading-action{flex:none}@media(max-width:620px){.page-heading{align-items:flex-start;gap:12px}.page-title{font-size:21px}.page-description{max-width:230px;font-size:10px}}
</style>
