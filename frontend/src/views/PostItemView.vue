<template>
  <div class="post-container">
    <h2>刊登新物品</h2>
    
    <form @submit.prevent="handleSubmit" class="post-form">
      <div class="form-group">
        <label>物品名稱</label>
        <input v-model="form.title" required placeholder="例如：大一微積分課本" />
      </div>

      <div class="form-group">
        <label>分類</label>
        <select v-model="form.category" required>
          <option value="" disabled>請選擇分類</option>
          <option value="TEXTBOOK">教科書</option>
          <option value="3C">3C 周邊</option>
          <option value="DAILY">生活用品</option>
          <option value="OTHER">其他</option>
        </select>
      </div>

      <div class="form-group">
        <label>詳細說明</label>
        <textarea v-model="form.description" required rows="4" placeholder="描述物品狀況、新舊程度..."></textarea>
      </div>

      <div class="form-group">
        <label>上傳照片</label>
        <input type="file" @change="handleFileChange" accept="image/*" required />
        <div v-if="previewUrl" class="image-preview">
          <img :src="previewUrl" alt="Preview" />
        </div>
      </div>

      <button type="submit" :disabled="isSubmitting">
        {{ isSubmitting ? '刊登中...' : '確認刊登' }}
      </button>
    </form>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue';
import { useRouter } from 'vue-router';
import { itemsApi } from '@/api';
import { useAuthStore } from '@/stores/auth';

const router = useRouter();
const authStore = useAuthStore();

// 表單資料
const form = reactive({
  title: '',
  category: '',
  description: '',
  image: null // 存放 File 物件
});

const previewUrl = ref(null);
const isSubmitting = ref(false);

// 處理檔案選擇
const handleFileChange = (event) => {
  const file = event.target.files[0];
  if (file) {
    form.image = file;
    // 建立預覽圖
    previewUrl.value = URL.createObjectURL(file);
  }
};

// 送出表單
const handleSubmit = async () => {
  // 簡單檢查是否有登入
  if (!authStore.isLoggedIn) {
    alert('請先登入才能刊登物品！');
    return;
  }

  isSubmitting.value = true;
  try {
    // 呼叫我們封裝好的 API (會自動轉成 FormData)
    await itemsApi.createItem({
      title: form.title,
      description: form.description,
      category: form.category,
      image: form.image
    });

    alert('刊登成功！');
    router.push('/'); // 回到首頁
  } catch (error) {
    console.error(error);
    alert('刊登失敗，請稍後再試。');
  } finally {
    isSubmitting.value = false;
  }
};
</script>

<style scoped>
.post-container {
  max-width: 600px;
  margin: 0 auto;
  padding: 20px;
}
.post-form {
  display: flex;
  flex-direction: column;
  gap: 15px;
}
.form-group {
  display: flex;
  flex-direction: column;
  gap: 5px;
}
input, select, textarea {
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 4px;
}
button {
  background-color: #4CAF50;
  color: white;
  padding: 10px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
}
button:disabled {
  background-color: #ccc;
}
.image-preview img {
  margin-top: 10px;
  max-width: 200px;
  border-radius: 4px;
}
</style>