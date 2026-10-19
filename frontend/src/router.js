import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', redirect: '/posts' },
    { path: '/signup', component: () => import('./views/SignupPage.vue') },
    { path: '/login', component: () => import('./views/LoginPage.vue') },
    { path: '/posts', component: () => import('./views/PostListPage.vue') },
    { path: '/posts/new', component: () => import('./views/PostCreatePage.vue') },
    { path: '/posts/:idx(\\d+)', component: () => import('./views/PostDetailPage.vue') },
    { path: '/:pathMatch(.*)*', redirect: '/posts' },
  ],
})

export default router
