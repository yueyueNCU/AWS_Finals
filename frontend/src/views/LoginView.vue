<template>
  <div class="page-container">
    <div class="login-card">
      <div class="spinner"></div>
      <h2>正在登入中...</h2>
      <p class="subtitle">正在驗證您的身分，請稍候片刻。</p>
      <p class="hint">驗證完成後將自動跳轉至首頁</p>
    </div>
  </div>
</template>

<script>
// 【關鍵修正】保持不變
// 將變數宣告在 script setup 之外，使其成為該模組的全域變數。
// 即使 Component 被重新建立，這個變數依然會保持 true，防止二次執行。
let isLoginProcessing = false;
</script>

<script setup>
import { onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useAuthStore } from "@/stores/auth";

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();

onMounted(async () => {
  const code = route.query.code;

  // 1. 檢查是否正在處理中 (鎖定)
  if (isLoginProcessing) {
    console.warn("Login is already processing, skipping double call.");
    return;
  }

  if (code) {
    isLoginProcessing = true; // 上鎖

    try {
      // 2. 呼叫 Store 進行登入
      await authStore.login(code);

      // 3. 登入成功
      router.push("/");
    } catch (error) {
      console.error("Login error:", error);

      // 【進階防護】
      // 如果後端回傳 400/500，但 LocalStorage 其實已經有 Token 了 (可能是第一次請求成功，第二次失敗)
      if (localStorage.getItem("access_token")) {
        console.warn("Token exists despite error, redirecting to home.");
        router.push("/");
      } else {
        alert("登入失敗，請重試");
        router.push("/");
      }
    } finally {
      // 這裡故意 "不" 把 isLoginProcessing 設回 false
      // 因為 code 是一次性的，失敗或成功後都不該再用同一個 code 試圖登入
    }
  } else {
    router.push("/");
  }
});
</script>

<style scoped>
.page-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 80vh; /* 讓卡片垂直置中 */
  padding: 20px;
  background-color: #f8fafc; /* 淺灰背景，突顯卡片 */
}

.login-card {
  background: white;
  padding: 50px 40px;
  border-radius: 20px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.08);
  text-align: center;
  max-width: 400px;
  width: 100%;
  border: 1px solid #f1f5f9;
  display: flex;
  flex-direction: column;
  align-items: center;
  animation: slideUp 0.5s ease-out;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Spinner 動畫 */
.spinner {
  width: 50px;
  height: 50px;
  border: 4px solid #e2e8f0;
  border-top-color: #42b983; /* 主色調 */
  border-radius: 50%;
  margin-bottom: 25px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

h2 {
  color: #2c3e50;
  margin: 0 0 10px 0;
  font-size: 1.5rem;
}

.subtitle {
  color: #64748b;
  font-size: 1.05rem;
  margin: 0 0 20px 0;
}

.hint {
  color: #94a3b8;
  font-size: 0.85rem;
  margin: 0;
}
</style>
