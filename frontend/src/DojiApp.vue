<template>
  <div class="doji-shell">
    <DojiHeader />
    <main class="doji-main"><RouterView /></main>
  </div>
</template>

<script setup>
import { RouterView } from 'vue-router'
import DojiHeader from './components/DojiHeader.vue'
</script>
