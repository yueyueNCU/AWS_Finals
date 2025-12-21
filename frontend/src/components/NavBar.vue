<template>
  <nav class="navbar">
    <div class="logo">
      <RouterLink to="/">中央以物易物</RouterLink>
    </div>

    <div class="links">
      <RouterLink to="/">首頁</RouterLink>
      <RouterLink to="/post">我要刊登</RouterLink>
      
      <RouterLink v-if="authStore.isLoggedIn" to="/my-items">我的物品</RouterLink>
      
      <div v-if="authStore.isLoggedIn" class="user-menu">
        <RouterLink to="/profile">
          <span class="user-name">你好，{{ authStore.user?.name || '同學' }}</span>
        </RouterLink>
        <button @click="authStore.logout" class="btn-logout">登出</button>
      </div>

      <div v-else>
        <button @click="handleLogin" class="btn-login">NCU Gmail 登入</button>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { RouterLink } from 'vue-router';
import { useAuthStore } from '@/stores/auth';

const authStore = useAuthStore();

// (handleLogin 函式保持不變...)
const handleLogin = () => {
  const cognitoDomain = 'https://ap-southeast-2tcte1x780.auth.ap-southeast-2.amazoncognito.com'; 
  const clientId = '3e01cbi503u29lb0jpm62ospm4' ; 
  const baseUrl = import.meta.env.VITE_APP_BASE_URL;
  const redirectUri = encodeURIComponent(`${baseUrl}/callback/`);
  const loginUrl = `${cognitoDomain}/login?client_id=${clientId}&response_type=code&scope=email+openid+profile&redirect_uri=${redirectUri}`;
  window.location.href = loginUrl;
};
</script>

<style scoped>
/* (樣式保持不變) */
.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 2rem;
  background-color: #ffffff;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
.logo a {
  font-size: 1.5rem;
  font-weight: bold;
  color: #2c3e50;
  text-decoration: none;
}
.links {
  display: flex;
  align-items: center;
  gap: 20px;
}
.links a {
  text-decoration: none;
  color: #666;
  font-weight: 500;
}
.links a.router-link-active {
  color: #42b983;
}
.btn-login {
  background-color: #42b983;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
}
.btn-logout {
  background-color: #e74c3c;
  color: white;
  border: none;
  padding: 6px 12px;
  border-radius: 4px;
  cursor: pointer;
  margin-left: 10px;
}
.user-menu {
  display: flex;
  align-items: center;
}
</style>