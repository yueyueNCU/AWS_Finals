<template>
  <div class="container">
    <div v-if="loading" class="loading">載入中...</div>
    <div v-else-if="!exchange" class="error">找不到此交換請求</div>

    <div v-else class="detail-card">
      <div class="header">
        <h1>交換詳情 <small>#{{ exchange.id }}</small></h1>
        <span class="status-badge" :class="exchange.status">
          {{ translateStatus(exchange.status) }}
        </span>
      </div>

      <div class="items-row">
        
        <div class="item-box">
          <h3>對方的物品</h3>
          
          <template v-if="isOwner">
            <div v-if="exchange.offered_item">
              <img :src="exchange.offered_item.cover_image || 'https://via.placeholder.com/150'" class="thumb" />
              <p class="title">{{ exchange.offered_item.title }}</p>
            </div>
            <div v-else class="no-item">
              <p>（純索取 / 無提供物品）</p>
            </div>
          </template>

          <template v-else>
            <div v-if="exchange.target_item">
              <img :src="exchange.target_item.cover_image || 'https://via.placeholder.com/150'" class="thumb" />
              <p class="title">{{ exchange.target_item.title }}</p>
            </div>
          </template>
        </div>

        <div class="arrow">⇄</div>

        <div class="item-box highlight">
          <h3>我的物品</h3>
          
          <template v-if="isOwner">
            <div v-if="exchange.target_item">
              <img :src="exchange.target_item.cover_image || 'https://via.placeholder.com/150'" class="thumb" />
              <p class="title">{{ exchange.target_item.title }}</p>
            </div>
          </template>

          <template v-else>
            <div v-if="exchange.offered_item">
              <img :src="exchange.offered_item.cover_image || 'https://via.placeholder.com/150'" class="thumb" />
              <p class="title">{{ exchange.offered_item.title }}</p>
            </div>
            <div v-else class="no-item">
              <p>（純索取 / 無提供物品）</p>
            </div>
          </template>
        </div>
      </div>

      <div class="message-section">
        <h4>提出者留言：</h4>
        <p class="message-content">{{ exchange.message || '無留言' }}</p>
        <p class="meta">提出者: {{ exchange.requester?.nickname || exchange.requester?.name }} | 時間: {{ formatDate(exchange.created_at) }}</p>
      </div>

      <div v-if="isOwner && exchange.status === 'pending'" class="action-area owner-actions">
        <h3>審核請求</h3>
        <p>請選擇是否接受此交換請求：</p>
        <div class="buttons">
          <button @click="handleReject" class="btn-reject" :disabled="isSubmitting">
            拒絕交換
          </button>
          <button @click="openAcceptModal" class="btn-accept" :disabled="isSubmitting">
            接受交換
          </button>
        </div>
      </div>

      <div v-if="['accepted', 'completed'].includes(exchange.status)" class="deal-info">
        <h3>🎉 交易成立！</h3>
        <div class="info-content">
          <p><strong>面交地點：</strong> {{ exchange.deal_info?.meetup_location?.name || '未指定' }}</p>
          
          <p v-if="getLocationAddress(exchange.deal_info?.meetup_location?.id)">
            <strong>地址參考：</strong> {{ getLocationAddress(exchange.deal_info?.meetup_location?.id) }}
          </p>
          
          <p><strong>聯絡說明：</strong> 請透過 Email 或電話聯繫對方安排時間。</p>
        </div>
      </div>
    </div>

    <div v-if="showAcceptModal" class="modal-overlay" @click.self="showAcceptModal = false">
      <div class="modal-content">
        <h3>確認接受交換</h3>
        <p>請選擇一個面交地點供對方參考：</p>
        
        <div class="form-group">
          <label>面交地點</label>
          <select v-model="selectedLocationId">
            <option disabled value="">請選擇地點...</option>
            <option v-for="loc in locations" :key="loc.id" :value="loc.id">
              {{ loc.name }} ({{ getLocationAddress(loc.id) }})
            </option>
          </select>
        </div>

        <div class="modal-actions">
          <button @click="showAcceptModal = false" class="btn-cancel">取消</button>
          <button @click="handleAccept" class="btn-confirm" :disabled="!selectedLocationId || isSubmitting">
            確認成交
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { exchangesApi } from '@/api';
import { useAuthStore } from '@/stores/auth';

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();

const loading = ref(true);
const exchange = ref(null);
const locations = ref([]);
const showAcceptModal = ref(false);
const selectedLocationId = ref('');
const isSubmitting = ref(false);

// 判斷是否為賣家 (Owner)
const isOwner = computed(() => {
  if (!exchange.value || !authStore.user) return false;
  // 注意：這裡假設後端回傳結構是 exchange.owner.user_id
  return exchange.value.owner?.user_id === authStore.user.id;
});

// 1. 取得詳情
const fetchDetail = async () => {
  loading.value = true;
  try {
    const id = route.params.id;
    const res = await exchangesApi.getExchangeDetail(id);
    exchange.value = res.data;
  } catch (err) {
    console.error(err);
    alert('無法載入詳情');
    router.push('/profile');
  } finally {
    loading.value = false;
  }
};

// 2. 開啟接受視窗 (並載入地點)
const openAcceptModal = async () => {
  try {
    const res = await exchangesApi.getLocations();
    locations.value = res.data;
    showAcceptModal.value = true;
  } catch (err) {
    console.error(err);
    alert('無法載入地點清單');
  }
};

// 3. 執行接受 (Accept)
const handleAccept = async () => {
  if (!selectedLocationId.value) return;
  isSubmitting.value = true;
  try {
    // 修改前: await exchangesApi.updateExchangeStatus(exchange.value.exchange_id, {
    
    // 修改後: 改用 exchange.value.id
    await exchangesApi.updateExchangeStatus(exchange.value.id, {
      action: 'accept',
      meetup_location_id: selectedLocationId.value
    });
    alert('已接受交易！');
    showAcceptModal.value = false;
    fetchDetail(); 
  } catch (err) {
    console.error(err);
    alert('操作失敗');
  } finally {
    isSubmitting.value = false;
  }
};

// 4. 執行拒絕 (Reject)
const handleReject = async () => {
  if (!confirm('確定要拒絕此交換請求嗎？此操作無法復原。')) return;
  
  isSubmitting.value = true;
  try {
    // 修改前: await exchangesApi.updateExchangeStatus(exchange.value.exchange_id, {
    
    // 修改後: 改用 exchange.value.id
    await exchangesApi.updateExchangeStatus(exchange.value.id, {
      action: 'reject'
    });
    alert('已拒絕請求');
    fetchDetail();
  } catch (err) {
    console.error(err);
    alert('操作失敗');
  } finally {
    isSubmitting.value = false;
  }
};

// 後端沒有提供詳細地址，這裡直接用 map
const getLocationAddress = (id) => {
  const addressMap = {
    1: '校門口圓環旁',
    2: '男九舍 B1 全家便利商店',
    3: '依仁堂籃球場入口'
  };
  return addressMap[id] || '';
};

// 工具函式
const translateStatus = (status) => {
  const map = { pending: '等待中', accepted: '已接受', rejected: '已拒絕', completed: '已完成' };
  return map[status] || status;
};

const formatDate = (dateStr) => {
  return new Date(dateStr).toLocaleString();
};

onMounted(() => {
  fetchDetail();
});
</script>

<style scoped>
.container { padding: 40px; max-width: 800px; margin: 0 auto; }
.detail-card { border: 1px solid #ddd; padding: 30px; border-radius: 8px; background: #fff; }

.header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; }
.status-badge { padding: 6px 12px; border-radius: 20px; font-weight: bold; font-size: 0.9rem; }
.status-badge.pending { background: #fff3e0; color: #ef6c00; }
.status-badge.accepted { background: #e8f5e9; color: #2e7d32; }
.status-badge.rejected { background: #ffebee; color: #c62828; }

.items-row { display: flex; align-items: center; justify-content: space-around; margin-bottom: 30px; flex-wrap: wrap; gap: 20px;}
.item-box { text-align: center; flex: 1; min-width: 200px; padding: 15px; border: 1px solid #eee; border-radius: 8px; }
.item-box.highlight { border-color: #4CAF50; background: #f9fff9; }
.arrow { font-size: 2rem; color: #999; }
.thumb { width: 100px; height: 100px; object-fit: cover; border-radius: 4px; margin-bottom: 10px; }
.title { font-weight: bold; }

.message-section { background: #f5f5f5; padding: 15px; border-radius: 4px; margin-bottom: 30px; }
.message-content { font-size: 1.1rem; margin: 10px 0; white-space: pre-wrap; }
.meta { color: #888; font-size: 0.85rem; }

.action-area { border-top: 2px dashed #ddd; padding-top: 20px; text-align: center; }
.buttons { margin-top: 15px; display: flex; gap: 20px; justify-content: center; }
.btn-reject { background: #ff5252; color: white; border: none; padding: 10px 30px; border-radius: 4px; cursor: pointer; }
.btn-accept { background: #4CAF50; color: white; border: none; padding: 10px 30px; border-radius: 4px; cursor: pointer; }
.btn-reject:hover { background: #d32f2f; }
.btn-accept:hover { background: #388E3C; }
.btn-reject:disabled, .btn-accept:disabled { opacity: 0.6; cursor: not-allowed; }

.deal-info { background: #e8f5e9; border: 1px solid #c8e6c9; padding: 20px; border-radius: 8px; margin-top: 20px; }
.deal-info h3 { color: #2e7d32; margin-bottom: 10px; }

/* Modal Styles */
.modal-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.5); display: flex; justify-content: center; align-items: center; z-index: 1000; }
.modal-content { background: white; padding: 30px; border-radius: 8px; width: 90%; max-width: 400px; }
.form-group select { width: 100%; padding: 10px; margin-top: 5px; border: 1px solid #ccc; border-radius: 4px; }
.modal-actions { margin-top: 20px; display: flex; justify-content: flex-end; gap: 10px; }
.btn-cancel { background: #ccc; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer; }
.btn-confirm { background: #4CAF50; color: white; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer; }
.btn-confirm:disabled { background: #81c784; cursor: not-allowed; }
</style>