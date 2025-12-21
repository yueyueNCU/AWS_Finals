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
          <label>提供交換的物品 (選填)</label>
          <select v-model="offeredItemId">
            <option value="">(無) 純索取 / 私下協調</option>
            <option v-for="myItem in myItems" :key="myItem.id" :value="myItem.id">
              {{ myItem.title }}
            </option>
          </select>
          <small v-if="myItems.length === 0">你目前沒有上架的物品可供交換</small>
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
import { itemsApi, exchangesApi } from '@/api'; // 確保這裡有正確引入 itemsApi
import { useAuthStore } from '@/stores/auth';

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();

const item = ref(null);
// [新增] 存放我自己的物品列表
const myItems = ref([]);

const showExchangeModal = ref(false);
const exchangeMessage = ref('');
const offeredItemId = ref(''); // 這裡會綁定 select 的值 (預設為空字串)
const isSubmitting = ref(false);

const isOwner = computed(() => {
  if (!authStore.user || !item.value) return false;
  return authStore.user.id === item.value.owner_id;
});

// 1. 載入當前物品詳情
const fetchItemDetail = async () => {
  try {
    const id = route.params.id; 
    const response = await itemsApi.getItem(id);
    item.value = response.data;
  } catch (error) {
    console.error(error);
    alert('物品不存在或發生錯誤');
    router.push('/');
  }
};

// [新增] 2. 載入我的物品清單 (用於下拉選單)
// src/views/ItemDetailView.vue

const fetchMyItems = async () => {
  // 如果沒登入就不抓
  if (!authStore.isLoggedIn) return;
  
  try {
    // 1. 呼叫 API 取得物品列表
    // 雖然我們傳了 owner_id，但後端似乎會忽略它並回傳全部物品，所以在下一步前端過濾
    const res = await itemsApi.getItems(); 
    
    // 2. 在前端進行過濾：只保留 owner_id 等於目前使用者 ID 的物品
    const allItems = res.data;
    myItems.value = allItems.filter(item => item.owner_id === authStore.user.id);

  } catch (err) {
    console.error('Fetch my items error:', err);
  }
};

// 3. 送出交換請求
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
      offered_item_id: offeredItemId.value || null, // 若為空字串則轉為 null
      message: exchangeMessage.value
    });
    
    alert('交換請求已送出！請至「我的帳戶」查看狀態。');
    showExchangeModal.value = false;
    router.push('/profile'); 
  } catch (error) {
    console.error(error);
    // [修改] 顯示後端回傳的詳細錯誤訊息 (例如：重複請求)
    const errorMsg = error.response?.data?.detail || '送出失敗，請稍後再試';
    alert(errorMsg);
  } finally {
    isSubmitting.value = false;
  }
};

onMounted(() => {
  fetchItemDetail();
  fetchMyItems(); // [新增] 載入頁面時順便抓取我的物品
});
</script>

<style scoped>
/* (原有的樣式保持不變，新增 select 的樣式) */
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
/* [修改] 增加 select 樣式 */
.form-group textarea, .form-group input, .form-group select {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background-color: #fff;
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