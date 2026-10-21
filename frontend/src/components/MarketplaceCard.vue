<script setup>
import { RouterLink } from 'vue-router'
import ActionButton from './ActionButton.vue'
defineProps({ item: { type: Object, required: true }, href: { type: String, required: true }, condition: { type: String, default: '' }, icon: { type: String, default: '✳' }, imageUrl: { type: String, default: '' }, price: { type: String, default: '' }, deal: { type: String, default: '' }, category: { type: String, default: '' }, saved: { type: Boolean, default: false }, background: { type: String, default: 'linear-gradient(145deg,#e8e6d9,#f5f0df)' } })
const emit = defineEmits(['toggle-save'])
</script>

<template>
  <article class="market-card">
    <RouterLink class="market-image-link" :to="href" :aria-label="`${item.title} 상세 보기`">
      <div class="market-image" :style="{ '--market-bg': background }"><img v-if="imageUrl" class="market-photo" :src="imageUrl" :alt="item.title" loading="lazy" @error="$event.currentTarget.remove()" /><span v-if="condition" class="market-condition">{{ condition }}</span><span class="market-art" aria-hidden="true">{{ icon }}</span><span class="market-image-caption">SECOND<br />CHANCE</span></div>
    </RouterLink>
    <button class="market-save" type="button" :aria-label="saved ? '관심 목록에서 제거' : '관심 목록에 저장'" :aria-pressed="saved" @click="emit('toggle-save')">{{ saved ? '♥' : '♡' }}</button>
    <RouterLink class="market-copy" :to="href"><strong class="market-title">{{ item.title }}</strong><span class="market-description">{{ item.description }}</span><strong class="market-price">{{ price }}</strong><span v-if="deal" class="market-deal">{{ deal }}</span><span class="market-meta">{{ category }} · DOJI 셀렉션</span></RouterLink>
    <ActionButton class="market-action" :to="`${href}/checkout`">구매하기 <span aria-hidden="true">→</span></ActionButton>
  </article>
</template>

<style scoped>
.market-card{position:relative;min-width:0;padding:8px 8px 11px;border:1px solid #e4e1d8;border-radius:16px;background:#fffefa;transition:transform .18s,box-shadow .18s}.market-card:hover{transform:translateY(-3px);box-shadow:0 14px 30px #24383b12}.market-image-link{display:block;text-decoration:none}.market-image{position:relative;display:grid;place-items:center;min-height:225px;overflow:hidden;border-radius:10px;background:var(--market-bg)}.market-photo{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}.market-image:after{position:absolute;right:-38px;bottom:-70px;width:190px;height:190px;border:1px solid #ffffff80;border-radius:50%;content:"";pointer-events:none}.market-condition{position:absolute;z-index:1;top:11px;left:11px;padding:6px 9px;border-radius:999px;background:#fffefaeb;color:#52615e;font-size:9px}.market-art{position:relative;z-index:1;font-size:82px;filter:drop-shadow(0 16px 12px #46392b20);transition:transform .2s}.market-photo~.market-art{display:none}.market-card:hover .market-art{transform:translateY(-4px) scale(1.04)}.market-image-caption{position:absolute;right:12px;bottom:11px;color:#788274;font:9px/1.5 Georgia,serif;letter-spacing:.12em;text-align:right}.market-save{position:absolute;z-index:2;top:16px;right:16px;display:grid;place-items:center;width:34px;height:34px;border:1px solid #e8e5dc;border-radius:50%;background:#fffefa;color:#8d7051;font-size:18px;cursor:pointer}.market-save:hover{background:#f3eee2}.market-copy{display:grid;gap:6px;padding:12px 5px 7px;color:inherit;text-decoration:none}.market-title{overflow:hidden;color:#2c4143;font-size:12px;text-overflow:ellipsis;white-space:nowrap}.market-description{min-height:30px;color:#7d8580;font-size:10px;line-height:1.55}.market-price{color:#293e42;font:20px Georgia,serif}.market-deal{color:#927b53;font-size:9px}.market-meta{color:#959a91;font-size:9px}.market-action{display:flex;width:100%;justify-content:space-between;min-height:38px;margin-top:5px;padding:0 12px;border-radius:8px;font-size:11px}.market-action span{color:#d8c293;font-size:17px}@media(max-width:700px){.market-image{min-height:155px}.market-art{font-size:62px}.market-card{padding:6px}.market-copy{gap:5px;padding:9px 3px 6px}.market-title{font-size:10px}.market-description{font-size:9px}}
</style>
