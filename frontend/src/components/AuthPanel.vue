<script setup>
import PageHeading from './PageHeading.vue'
defineProps({ eyebrow: { type: String, default: 'DOJI · MALANG' }, title: { type: String, required: true }, subtitle: { type: String, required: true }, mark: { type: String, default: '✳' } })
</script>

<template>
  <section class="auth-panel">
    <aside class="auth-aside"><span class="auth-mark" aria-hidden="true">{{ mark }}</span><p>{{ subtitle }}</p><small>{{ eyebrow }}</small></aside>
    <div class="auth-content"><PageHeading class="auth-heading" :eyebrow="eyebrow" :title="title" level="h2" /><slot /></div>
  </section>
</template>

<style scoped>
.auth-panel{display:grid;grid-template-columns:.78fr 1.22fr;max-width:850px;min-height:430px;margin:42px auto 80px;overflow:hidden;border:1px solid var(--brand-line,#deddd3);border-radius:20px;background:var(--brand-paper,#fffefa);box-shadow:0 18px 50px #2336380c}.auth-aside{position:relative;display:flex;flex-direction:column;justify-content:flex-end;min-height:100%;padding:38px;background:linear-gradient(145deg,var(--brand-ink,#293f43),var(--brand-ink-soft,#3d5955));color:white}.auth-mark{position:absolute;top:40px;left:38px;display:grid;place-items:center;width:56px;height:56px;border:1px solid #c8b48780;border-radius:50%;color:var(--brand-accent-soft,#dcc79a);font-size:25px}.auth-aside p{max-width:250px;margin:0 0 30px;font:26px/1.35 Georgia,serif}.auth-aside small{color:var(--brand-accent-soft,#c4b58e);font-size:9px;font-weight:700;letter-spacing:.15em}.auth-content{padding:40px 48px}.auth-heading{margin-bottom:23px}.auth-heading :deep(.page-eyebrow){color:var(--brand-accent,#927b53)}.auth-heading :deep(.page-title){font-size:25px}@media(max-width:700px){.auth-panel{grid-template-columns:1fr;margin:20px auto 85px;border-radius:16px}.auth-aside{min-height:150px;padding:22px}.auth-mark{top:20px;left:auto;right:22px;width:42px;height:42px;font-size:19px}.auth-aside p{max-width:220px;margin:0 0 10px;font-size:20px}.auth-content{padding:25px 22px}.auth-heading :deep(.page-title){font-size:21px}}
</style>
