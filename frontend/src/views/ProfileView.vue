<template>
  <div class="profile-container">
    <div class="user-header" v-if="authStore.user">
      <img :src="authStore.user.avatar_url || 'https://via.placeholder.com/100'" class="avatar" />
      <div class="user-info">
        <h2>{{ authStore.user.name }}</h2>
        <p>{{ authStore.user.email }}</p>
      </div>
    </div>

    <div class="tabs">
      <button 
        :class="{ active: currentTab === 'requester' }" 
        @click="currentTab = 'requester'"
      >
        我提出的交換
      </button>
      <button 
        :class="{ active: currentTab === 'owner' }" 
        @click="currentTab = 'owner'"
      >
        別人向我提出的請求
      </button>
    </div>

    <div class="exchange-list">
      <div v-if="loading">載入中...</div>
      
      <div v-else-if="exchanges.length === 0" class="empty-state">
        目前沒有{{ currentTab === 'requester' ? '提出的' : '收到的' }}交換紀錄。
      </div>

      <div v-else class="exchange-card" v-for="ex in exchanges" :key="ex.exchange_id">
        <div class="card-header">
          <span class="status-badge" :class="ex.status">{{ translateStatus(ex.status) }}</span>
          <span class="date">交換 ID: {{ ex.exchange_id }}</span>
        </div>
        
        <div class="card-body">
          <div class="item-pair">
            <div class="item">
              <small>對方的物品</small>
              <h4>
                {{ 
                  (currentTab === 'requester' 
                    ? ex.target_item?.title 
                    : ex.offered_item?.title) || '（無/純索取）' 
                }}
              </h4>
            </div>

            <div class="arrow">⇄</div>

            <div class="item">
              <small>我的物品</small>
              <h4>
                {{ 
                  (currentTab === 'requester' 
                    ? ex.offered_item?.title 
                    : ex.target_item?.title) || '（無/純索取）' 
                }}
              </h4>
            </div>
          </div>
          
          <div class="partner-info">
            交易對象: {{ ex.partner?.name || '未知用戶' }}
          </div>
        </div>

        <div class="card-actions">
          <button 
            v-if="currentTab === 'requester' && ex.status === 'pending'"
            @click.stop="handleCancel(ex.exchange_id)" 
            class="btn-cancel"
          >
            取消請求
          </button>

          <button @click="viewDetail(ex.exchange_id)">查看對話與詳情</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue';
import { useRouter } from 'vue-router'; // 修正引入
import { exchangesApi } from '@/api';
import { useAuthStore } from '@/stores/auth';

const router = useRouter(); // 確保這裡正確使用
const authStore = useAuthStore();
const currentTab = ref('requester'); // 'requester' or 'owner'
const exchanges = ref([]);
const loading = ref(false);

// 狀態翻譯
const translateStatus = (status) => {
  const map = {
    pending: '等待回覆',
    accepted: '已接受',
    rejected: '已拒絕',
    completed: '已完成',
    cancelled: '已取消'
  };
  return map[status] || status;
};

// 抓取交換列表
const fetchExchanges = async () => {
  // 如果沒登入，就不抓資料 (或導向首頁)
  if (!authStore.isLoggedIn) return;

  loading.value = true;
  try {
    // 根據 Tab 決定 role 參數
    const role = currentTab.value; 
    const response = await exchangesApi.getExchanges(role);
    exchanges.value = response.data;
  } catch (error) {
    console.error(error);
  } finally {
    loading.value = false;
  }
};

// 處理取消請求
const handleCancel = async (exchangeId) => {
  // 1. 跳出 Confirm 視窗
  const isConfirmed = confirm('確定要取消這個交換請求嗎？');
  
  if (!isConfirmed) return;

  try {
    // 2. 呼叫 API
    await exchangesApi.cancelExchange(exchangeId);
    
    // 3. 成功提示
    alert('已成功取消請求');
    
    // 4. 重新整理列表 (假設你的讀取函式叫 fetchExchanges)
    fetchExchanges(); 
    
  } catch (error) {
    console.error(error);
    alert('取消失敗，請稍後再試');
  }
};
// 當 Tab 改變時，重新抓資料
watch(currentTab, () => {
  fetchExchanges();
});

// 進入詳情 (如果未來有做 ExchangeDetailView 的話)
const viewDetail = (id) => {
  router.push(`/exchanges/${id}`);
};

onMounted(() => {
  if (!authStore.isLoggedIn) {
    // 沒登入就導回首頁，避免報錯
    // router.push('/'); 
  } else {
    fetchExchanges();
  }
});
</script>

<style scoped>
.profile-container {
  max-width: 800px;
  margin: 0 auto;
}
.user-header {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 30px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
}
.avatar {
  width: 80px;
  height: 80px;
  border-radius: 50%;
}
.tabs {
  display: flex;
  border-bottom: 1px solid #ddd;
  margin-bottom: 20px;
}
.tabs button {
  padding: 10px 20px;
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1rem;
  color: #666;
  border-bottom: 3px solid transparent;
}
.tabs button.active {
  color: #4CAF50;
  border-bottom: 3px solid #4CAF50;
  font-weight: bold;
}
.exchange-card {
  border: 1px solid #eee;
  border-radius: 8px;
  padding: 15px;
  margin-bottom: 15px;
  background: white;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}
.card-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
  font-size: 0.9rem;
}
.status-badge {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 0.8rem;
  background: #eee;
}
.status-badge.pending { background: #fff3cd; color: #856404; }
.status-badge.accepted { background: #d4edda; color: #155724; }
.status-badge.rejected { background: #f8d7da; color: #721c24; }

.card-body {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.item-pair {
  display: flex;
  align-items: center;
  gap: 15px;
}
.arrow {
  font-size: 1.2rem;
  color: #999;
}
.card-actions {
  margin-top: 15px;
  text-align: right;
}
.card-actions button {
  background: #007bff;
  color: white;
  border: none;
  padding: 5px 10px;
  border-radius: 4px;
  cursor: pointer;
}
.btn-cancel {
  background-color: #ff5252;
  color: white;
  margin-right: 10px; /* 與右邊的按鈕保持距離 */
}
.btn-cancel:hover {
  background-color: #d32f2f;
}
</style>