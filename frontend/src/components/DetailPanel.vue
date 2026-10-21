<template>
  <article class="detail-panel"><div class="detail-visual"><slot name="visual" /></div><div class="detail-content"><slot /></div></article>
</template>

<style scoped>
.detail-panel{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);min-height:470px;overflow:hidden;border:1px solid var(--brand-line,#dfddd4);border-radius:18px;background:var(--brand-paper,#fffefa);box-shadow:0 18px 45px #263a3f0d}.detail-visual{position:relative;display:grid;place-items:center;overflow:hidden;background:linear-gradient(145deg,#e4e6d9,#f4efdf)}.detail-visual:after{position:absolute;right:-65px;bottom:-95px;width:260px;height:260px;border:1px solid #fff9;border-radius:50%;content:""}.detail-content{align-self:center;padding:0}@media(max-width:700px){.detail-panel{grid-template-columns:1fr}.detail-visual{min-height:260px}}
</style>
