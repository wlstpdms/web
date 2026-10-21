<script setup>
import { RouterLink } from 'vue-router'

defineProps({
  to: { type: String, default: '' },
  type: { type: String, default: 'button' },
  variant: { type: String, default: 'primary' },
  disabled: { type: Boolean, default: false },
})
</script>

<template>
  <component :is="to ? RouterLink : 'button'" :to="to || undefined" :type="to ? undefined : type" :disabled="!to && disabled" :aria-disabled="to && disabled ? 'true' : undefined" class="action-button" :class="[`is-${variant}`, { 'is-disabled': disabled }]" :tabindex="to && disabled ? -1 : undefined" @click="to && disabled ? $event.preventDefault() : undefined">
    <slot />
  </component>
</template>

<style scoped>
.action-button{display:inline-flex;align-items:center;justify-content:center;gap:10px;min-height:43px;padding:0 17px;border:1px solid transparent;border-radius:10px;background:var(--brand-ink,#30494b);color:#fff;text-decoration:none;font:inherit;font-size:12px;font-weight:700;cursor:pointer;transition:background .16s,border-color .16s,transform .16s}.action-button:hover:not(:disabled):not(.is-disabled){transform:translateY(-1px);background:var(--brand-ink-hover,#20383b)}.action-button:focus-visible{outline:3px solid var(--brand-accent,#a48a5e);outline-offset:3px}.action-button.is-secondary{border-color:var(--brand-line,#deddd3);background:var(--brand-paper,#fffefa);color:var(--brand-ink,#30494b)}.action-button.is-secondary:hover:not(:disabled):not(.is-disabled){background:var(--brand-paper-muted,#f2f0e8)}.action-button.is-social{border-color:#e6dfc4;background:#f3efd9;color:#514b3c}.action-button.is-social:hover:not(:disabled):not(.is-disabled){background:#ece5c9}.action-button:disabled,.action-button.is-disabled{cursor:not-allowed;opacity:.55}
</style>
