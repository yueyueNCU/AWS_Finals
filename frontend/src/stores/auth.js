// 管理登入狀態

import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { authApi } from '@/api'; // 引用我們上一步寫好的 API

export const useAuthStore = defineStore('auth', () => {
  // 這裡建議預設值給 null，比較好判斷
  const token = ref(localStorage.getItem('access_token') || '');
  const user = ref(JSON.parse(localStorage.getItem('user_info') || 'null')); // 多存一個 user_info 到 localStorage 避免重整後名字消失

  const isLoggedIn = computed(() => !!token.value);

  const login = async (code) => {
    try {
      // 呼叫後端
      const response = await authApi.login(code);
      
      // 根據你提供的資料結構:
      // { "id": "...", "name": "陳揚盛", "access_token": "...", ... }
      const { access_token, ...userData } = response.data;
      
      // 更新狀態
      token.value = access_token;
      user.value = userData; // 這裡面會有 name, email, avatar_url
      
      // 存入 LocalStorage (讓 F5 重新整理後還記得)
      localStorage.setItem('access_token', access_token);
      localStorage.setItem('user_info', JSON.stringify(userData)); // 新增這一行
      
      return true;
    } catch (error) {
      console.error('Login failed:', error);
      throw error;
    }
  };

  const logout = () => {
    token.value = '';
    user.value = null;
    localStorage.removeItem('access_token');
    localStorage.removeItem('user_info'); // 記得一併清除
    window.location.href = '/'; 
  };
  
  // fetchUser 可以保留，用來驗證 Token 有效性並更新最新資料
  const fetchUser = async () => {
    if (!token.value) return;
    try {
      const response = await authApi.getMe();
      user.value = response.data; // 更新 user 資料
      localStorage.setItem('user_info', JSON.stringify(response.data)); // 同步更新 storage
    } catch (error) {
      logout();
    }
  };

  return { token, user, isLoggedIn, login, logout, fetchUser };
});