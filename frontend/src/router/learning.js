import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: () => import('../views/DashboardPage.vue') },
    { path: '/study', component: () => import('../views/StudyPage.vue') },
    { path: '/practice', component: () => import('../views/PracticePage.vue') },
    { path: '/groups', component: () => import('../views/GroupsPage.vue') },
    { path: '/membership', component: () => import('../views/MembershipPage.vue') },
    { path: '/login', component: () => import('../views/LoginPage.vue') },
    { path: '/signup', component: () => import('../views/SignupPage.vue') },
    { path: '/login/kakao/callback', component: () => import('../views/KakaoCallbackPage.vue') },
    { path: '/:pathMatch(.*)*', redirect: '/' },
  ],
  scrollBehavior: () => ({ top: 0 }),
})

export default router
