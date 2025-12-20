<!-- 登入回調頁 (處理 Cognito 轉回來的 code) -->
 <template>
  <div class="login-container">
    <h2>正在登入中...</h2>
    <p>請稍候，正在進行身分驗證</p>
  </div>
</template>

<script setup>
import { onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();

onMounted(async () => {
  // 1. 從網址取得 code 參數
  // 網址長這樣: http://localhost:5173/auth/callback?code=xxxx-xxxx
  const code = route.query.code;

  if (code) {
    try {
      // 2. 呼叫 Store 進行登入
      await authStore.login(code);
      
      // 3. 登入成功，跳轉回首頁
      router.push('/');
    } catch (error) {
      alert('登入失敗，請重試');
      router.push('/');
    }
  } else {
    // 沒有 code，代表使用者是直接跑進來這個頁面
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
  height: 100vh; /* 滿版高度 */
  text-align: center;
}
</style>