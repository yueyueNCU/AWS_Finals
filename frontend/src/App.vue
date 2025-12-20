<template>
  <NavBar />

  <main>
    <RouterView />
  </main>
</template>

<script setup>
import { onMounted } from 'vue';
import { RouterView } from 'vue-router';
import NavBar from './components/NavBar.vue'; // 引入 NavBar
import { useAuthStore } from '@/stores/auth';

const authStore = useAuthStore();

// 每次重新整理網頁時，嘗試從 LocalStorage 把使用者資料抓回來
onMounted(() => {
  authStore.fetchUser();
});
</script>

<style scoped>
main {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}
</style>