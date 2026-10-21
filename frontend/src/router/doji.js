import { createRouter, createWebHashHistory } from 'vue-router'

const router = createRouter({
  // DOJI is served from its own Vite entry (doji.html) alongside Malang.
  // Hash routing keeps its URLs isolated from the learning app's history routes.
  history: createWebHashHistory('/doji.html'),
  routes: [
    { path: '/posts', component: () => import('../views/PostListPage.vue') },
    { path: '/posts/new', component: () => import('../views/PostCreatePage.vue') },
    { path: '/posts/:idx/checkout', component: () => import('../views/ClothingCheckoutPage.vue') },
    { path: '/posts/:idx', component: () => import('../views/PostDetailPage.vue'), props: true },
    { path: '/:pathMatch(.*)*', redirect: '/posts' },
  ],
  scrollBehavior: () => ({ top: 0 }),
})

export default router
