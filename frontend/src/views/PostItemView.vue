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
          <option v-for="cat in categories" :key="cat.id" :value="cat.id">
            {{ cat.name }}
          </option>
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
import { ref, reactive, onMounted } from 'vue'; // [新增] 引入 onMounted
import { useRouter } from 'vue-router';
import { itemsApi } from '@/api';
import { useAuthStore } from '@/stores/auth';

const router = useRouter();
const authStore = useAuthStore();
const categories = ref([]); // [新增] 用來存放分類清單

// 表單資料
const form = reactive({
  title: '',
  category: '',
  description: '',
  image: null 
});

const previewUrl = ref(null);
const isSubmitting = ref(false);

// [新增] 抓取分類清單
const fetchCategories = async () => {
  try {
    const res = await itemsApi.getCategories();
    categories.value = res.data;
  } catch (error) {
    console.error('無法取得分類:', error);
    alert('無法載入分類選項，請稍後再試');
  }
};

// 處理檔案選擇
const handleFileChange = (event) => {
  const file = event.target.files[0];
  if (file) {
    form.image = file;
    previewUrl.value = URL.createObjectURL(file);
  }
};

// 送出表單
const handleSubmit = async () => {
  if (!authStore.isLoggedIn) {
    alert('請先登入才能刊登物品！');
    return;
  }

  isSubmitting.value = true;
  try {
    await itemsApi.createItem({
      title: form.title,
      description: form.description,
      category: form.category,
      image: form.image
    });

    alert('刊登成功！');
    router.push('/'); 
  } catch (error) {
    console.error(error);
    alert('刊登失敗，請稍後再試。');
  } finally {
    isSubmitting.value = false;
  }
};

// [新增] 畫面載入時抓取分類
onMounted(() => {
  fetchCategories();
});
</script>

<style scoped>
/* 樣式保持不變 */
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