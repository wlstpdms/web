import { createApp } from 'vue'
import DojiApp from './DojiApp.vue'
import router from './router/doji.js'
import './asset/style.css'
import './asset/doji.css'

createApp(DojiApp).use(router).mount('#app')
