// 管理登入狀態

import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { authApi } from '@/api'; // 引用我們上一步寫好的 API

export const useAuthStore = defineStore('auth', () => {
  // --- State (資料) ---
  const token = ref(localStorage.getItem('access_token') || '');
  const user = ref(null);

  // --- Getters (計算屬性) ---
  const isLoggedIn = computed(() => !!token.value);

  // --- Actions (動作) ---
  
  // 1. 處理登入 (拿 code 換 token)
  const login = async (code) => {
    try {
      const response = await authApi.login(code);
      // 假設後端回傳格式: { access_token: "...", ...user_info }
      const { access_token, ...userData } = response.data;
      
      // 存到狀態與 LocalStorage
      token.value = access_token;
      user.value = userData;
      localStorage.setItem('access_token', access_token);
      
      return true; // 登入成功
    } catch (error) {
      console.error('Login failed:', error);
      throw error;
    }
  };

  // 2. 登出
  const logout = () => {
    token.value = '';
    user.value = null;
    localStorage.removeItem('access_token');
    // 可以選擇重新整理頁面或跳轉
    window.location.href = '/'; 
  };

  // 3. 初始化 (F5 重新整理後，試著把使用者資料抓回來)
  const fetchUser = async () => {
    if (!token.value) return;
    try {
      const response = await authApi.getMe();
      user.value = response.data;
    } catch (error) {
      // Token 可能過期了，強制登出
      logout();
    }
  };

  return { token, user, isLoggedIn, login, logout, fetchUser };
});