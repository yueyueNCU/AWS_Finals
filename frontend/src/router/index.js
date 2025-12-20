import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import LoginView from '../views/LoginView.vue' // 引入剛寫好的元件

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView
    },
    {
      // 這是 Cognito 設定的 Callback URL 路徑
      path: '/auth/callback',
      name: 'login-callback',
      component: LoginView
    },
    // ... 其他頁面之後再加
  ]
})

export default router