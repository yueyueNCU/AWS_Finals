import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import LoginView from '../views/LoginView.vue'
import PostItemView from '../views/PostItemView.vue'
import ItemDetailView from '../views/ItemDetailView.vue'
import ProfileView from '../views/ProfileView.vue'
import ExchangeDetailView from '../views/ExchangeDetailView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView
    },
    {
      path: '/callback',
      name: 'login-callback',
      component: LoginView
    },
    {
      path: '/post',
      name: 'post-item',
      component: PostItemView
    },
    {
      path: '/items/:id',
      name: 'item-detail',
      component: ItemDetailView
    },
    {
      path: '/profile',
      name: 'profile',
      component: ProfileView
    },
    // [新增] 交換詳情頁路由
    {
      path: '/exchanges/:id',
      name: 'exchange-detail',
      component: ExchangeDetailView
    }
  ]
})

export default router