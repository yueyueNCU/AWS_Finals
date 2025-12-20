<template>
  <div class="login-container">
    <h2>正在登入中...</h2>
    <p>請稍候，正在進行身分驗證</p>
  </div>
</template>

<script>
// 【關鍵修正】
// 將變數宣告在 script setup 之外，使其成為該模組的全域變數。
// 即使 Component 被重新建立，這個變數依然會保持 true，防止二次執行。
let isLoginProcessing = false;
</script>

<script setup>
import { onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();

onMounted(async () => {
  const code = route.query.code;

  // 1. 檢查是否正在處理中 (鎖定)
  if (isLoginProcessing) {
    console.warn('Login is already processing, skipping double call.');
    return; 
  }

  if (code) {
    isLoginProcessing = true; // 上鎖

    try {
      // 2. 呼叫 Store 進行登入
      await authStore.login(code);
      
      // 3. 登入成功
      router.push('/');
    } catch (error) {
      console.error('Login error:', error);
      
      // 【進階防護】
      // 如果後端回傳 400/500，但 LocalStorage 其實已經有 Token 了 (可能是第一次請求成功，第二次失敗)
      // 我們可以視為成功，直接跳轉，不要報錯
      if (localStorage.getItem('access_token')) {
         console.warn('Token exists despite error, redirecting to home.');
         router.push('/');
      } else {
         alert('登入失敗，請重試');
         router.push('/');
      }
    } finally {
      // 這裡故意 "不" 把 isLoginProcessing 設回 false
      // 因為 code 是一次性的，失敗或成功後都不該再用同一個 code 試圖登入
      // 等到使用者離開頁面或重新整理，模組重新載入時自然會重置
    }
  } else {
    router.push('/');
  }
});
</script>

<style scoped>
.login-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100vh;
  text-align: center;
}
</style>