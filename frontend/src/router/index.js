import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import LoginView from '../views/LoginView.vue'
import PostItemView from '../views/PostItemView.vue'     // 新增引入
import ItemDetailView from '../views/ItemDetailView.vue' // 新增引入
import ProfileView from '../views/ProfileView.vue'       // 新增引入

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView
    },
    {
      path: '/auth/callback',
      name: 'login-callback',
      component: LoginView
    },
    {
      path: '/post',
      name: 'post-item',
      component: PostItemView
    },
    {
      path: '/items/:id', // :id 代表動態參數
      name: 'item-detail',
      component: ItemDetailView
    },
    {
      path: '/profile',
      name: 'profile',
      component: ProfileView
    }
  ]
})

export default router