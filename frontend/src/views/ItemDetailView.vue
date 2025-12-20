<template>
  <div class="detail-container" v-if="item">
    <div class="image-section">
      <img :src="item.image_url || 'https://via.placeholder.com/400'" alt="Item Image" />
    </div>

    <div class="info-section">
      <div class="header">
        <span class="category-tag">{{ item.category }}</span>
        <span class="date">{{ new Date(item.created_at).toLocaleDateString() }}</span>
      </div>
      
      <h1>{{ item.title }}</h1>
      
      <div class="owner-info">
        <span class="label">刊登者：</span>
        <span>{{ item.owner_id }}</span>
      </div>

      <div class="description">
        <h3>物品描述</h3>
        <p>{{ item.description }}</p>
      </div>

      <div class="action-area">
        <div v-if="isOwner">
          <button class="btn-disabled" disabled>這是你的物品</button>
        </div>
        
        <div v-else>
          <button @click="showExchangeModal = true" class="btn-exchange">
            提出交換請求
          </button>
        </div>
      </div>
    </div>

    <div v-if="showExchangeModal" class="modal-overlay" @click.self="showExchangeModal = false">
      <div class="modal-content">
        <h3>向刊登者提出交換</h3>
        
        <div class="form-group">
          <label>留言訊息 (必填)</label>
          <textarea v-model="exchangeMessage" placeholder="你好，我想用微積分課本跟你交換..." rows="4"></textarea>
        </div>

        <div class="form-group">
          <label>提供交換的物品 ID (選填)</label>
          <input v-model="offeredItemId" placeholder="如果你有刊登物品，可填入 ID" />
          <small>未來這裡會改成下拉選單選擇你的物品</small>
        </div>

        <div class="modal-actions">
          <button @click="showExchangeModal = false" class="btn-cancel">取消</button>
          <button @click="submitExchange" class="btn-confirm" :disabled="isSubmitting">
            {{ isSubmitting ? '傳送中...' : '確認送出' }}
          </button>
        </div>
      </div>
    </div>
  </div>

  <div v-else class="loading">
    載入中...
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { itemsApi, exchangesApi } from '@/api';
import { useAuthStore } from '@/stores/auth';

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();

const item = ref(null);
const showExchangeModal = ref(false);
const exchangeMessage = ref('');
const offeredItemId = ref('');
const isSubmitting = ref(false);

// 判斷是否為自己的物品
const isOwner = computed(() => {
  if (!authStore.user || !item.value) return false;
  return authStore.user.id === item.value.owner_id;
});

// 1. 載入物品詳情
const fetchItemDetail = async () => {
  try {
    const id = route.params.id; // 從網址 /items/:id 拿到 id
    const response = await itemsApi.getItem(id);
    item.value = response.data;
  } catch (error) {
    console.error(error);
    alert('物品不存在或發生錯誤');
    router.push('/');
  }
};

// 2. 送出交換請求
const submitExchange = async () => {
  if (!authStore.isLoggedIn) {
    alert('請先登入！');
    showExchangeModal.value = false;
    return;
  }
  
  if (!exchangeMessage.value) {
    alert('請輸入訊息');
    return;
  }

  isSubmitting.value = true;
  try {
    await exchangesApi.createExchange(item.value.id, {
      offered_item_id: offeredItemId.value || null,
      message: exchangeMessage.value
    });
    
    alert('交換請求已送出！請至「我的帳戶」查看狀態。');
    showExchangeModal.value = false;
    router.push('/profile'); // 跳轉到個人頁面查看紀錄
  } catch (error) {
    console.error(error);
    alert('送出失敗，請稍後再試');
  } finally {
    isSubmitting.value = false;
  }
};

onMounted(() => {
  fetchItemDetail();
});
</script>

<style scoped>
.detail-container {
  display: flex;
  gap: 40px;
  padding: 40px 0;
  flex-wrap: wrap;
}
.image-section {
  flex: 1;
  min-width: 300px;
}
.image-section img {
  width: 100%;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}
.info-section {
  flex: 1;
  min-width: 300px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}
.category-tag {
  background: #e0f2f1;
  color: #00695c;
  padding: 4px 12px;
  border-radius: 16px;
  font-size: 0.9rem;
  margin-right: 10px;
}
.date {
  color: #888;
  font-size: 0.9rem;
}
.owner-info {
  background: #f9f9f9;
  padding: 10px;
  border-radius: 4px;
}
.description {
  line-height: 1.6;
  color: #333;
}
.btn-exchange {
  background-color: #ff9800;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 4px;
  font-size: 1.1rem;
  cursor: pointer;
  width: 100%;
}
.btn-exchange:hover {
  background-color: #f57c00;
}
.btn-disabled {
  background-color: #ccc;
  color: #666;
  border: none;
  padding: 12px 24px;
  border-radius: 4px;
  width: 100%;
  cursor: not-allowed;
}

/* Modal 樣式 */
.modal-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}
.modal-content {
  background: white;
  padding: 30px;
  border-radius: 8px;
  width: 90%;
  max-width: 500px;
}
.form-group {
  margin-bottom: 15px;
}
.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
}
.form-group textarea, .form-group input {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}
.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
}
.btn-cancel {
  background: #ddd;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
}
.btn-confirm {
  background: #4CAF50;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
}
</style>