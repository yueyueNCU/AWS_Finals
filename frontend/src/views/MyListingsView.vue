<template>
  <div class="page-container">
    <div class="header-section">
      <h1>我的物品管理</h1>
      <p class="subtitle">管理您刊登的物品，查看收到的交換請求。</p>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>正在載入您的物品...</p>
    </div>

    <div v-else-if="myItems.length === 0" class="empty-state">
      <span class="empty-icon">📦</span>
      <h3>你還沒有刊登任何物品</h3>
      <p>將閒置的物品放上來，換取你需要的東西吧！</p>
      <router-link to="/post" class="btn-primary">立即刊登物品</router-link>
    </div>

    <div v-else class="listings-container">
      <div v-for="item in myItems" :key="item.id" class="listing-card">
        <div class="info-section">
          <div class="img-wrapper">
            <img :src="item.image_url || 'https://via.placeholder.com/150'" alt="Item" />
          </div>
          <div class="text-content">
            <h3 class="item-title">{{ item.title }}</h3>
            <div class="meta-row">
              <span class="date-tag">{{ formatDate(item.created_at) }}</span>
            </div>
          </div>
        </div>

        <div class="status-section">
          <span class="status-badge" :class="item.status">
            {{ translateStatus(item.status) }}
          </span>
        </div>

        <div class="deal-section">
          <div
            v-if="item.activeExchange"
            class="active-deal-box"
            :class="item.activeExchange.status"
          >
            <span class="deal-icon">🤝</span>
            <div class="deal-info">
              <span class="label">
                {{ item.activeExchange.status === "completed" ? "已成交" : "交易進行中" }}
              </span>
              <span class="partner-name">對象: {{ item.activeExchange.partner_name }}</span>
            </div>
            <router-link :to="`/exchanges/${item.activeExchange.id}`" class="btn-check-deal">
              查看詳情
            </router-link>
          </div>

          <div v-else-if="item.requestCount > 0" class="pending-requests-box">
            <span class="notification-icon">🔔</span>
            <div class="request-info">
              <span class="count">{{ item.requestCount }} 個交換請求</span>
              <span class="hint">等待您的回覆</span>
            </div>
            <router-link to="/profile" class="btn-check-requests"> 前往審核 </router-link>
          </div>

          <div v-else class="no-activity">
            <span class="quiet-text">尚無交換請求</span>
          </div>
        </div>

        <div class="action-section">
          <router-link :to="`/items/${item.id}`" class="btn-view"> 預覽頁面 </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { itemsApi, exchangesApi } from "@/api";
import { useAuthStore } from "@/stores/auth";

const authStore = useAuthStore();
const myItems = ref([]);
const loading = ref(true);

const translateStatus = (status) => {
  const map = { available: "上架中", exchanged: "已交換", reserved: "洽談中", closed: "已關閉" };
  // 後端可能回傳大寫，做個相容
  const key = status?.toLowerCase();
  return map[key] || status;
};

const formatDate = (dateStr) => {
  if (!dateStr) return "";
  return new Date(dateStr).toLocaleDateString();
};

const fetchData = async () => {
  if (!authStore.user) {
    loading.value = false;
    return;
  }

  loading.value = true;
  try {
    // 平行呼叫：我的物品 & 別人對我的請求
    // 注意：getExchanges('owner') 取得的是「別人對我的物品發出的請求」
    const [itemsRes, exchangesRes] = await Promise.all([
      itemsApi.getMyItems ? itemsApi.getMyItems() : itemsApi.getItems(), // 相容處理
      exchangesApi.getExchanges("owner"),
    ]);

    // 若 API 是 getItems (全部)，需手動過濾出自己的
    let items = itemsRes.data;
    if (!itemsApi.getMyItems) {
      items = items.filter((i) => i.owner_id === authStore.user.id);
    }

    const allExchanges = exchangesRes.data;

    // 資料整合
    myItems.value = items.map((item) => {
      // 找出針對此物品的請求
      const relatedExchanges = allExchanges.filter(
        (ex) => ex.target_item?.id === item.id || ex.target_item_id === item.id
      );

      // 找出 Active Deal (Accepted 或 Completed)
      // 注意後端欄位結構，這裡做些防呆
      const activeExchange = relatedExchanges.find((ex) =>
        ["accepted", "completed"].includes(ex.status)
      );

      // 整理 Active Exchange 的顯示資料
      let activeExchangeData = null;
      if (activeExchange) {
        activeExchangeData = {
          id: activeExchange.id,
          status: activeExchange.status,
          // 嘗試抓取對方的名字
          partner_name: activeExchange.requester?.name || activeExchange.requester_name || "對方",
        };
      }

      // 計算 Pending 數量
      const requestCount = relatedExchanges.filter((ex) => ex.status === "pending").length;

      return {
        ...item,
        activeExchange: activeExchangeData,
        requestCount,
      };
    });
  } catch (error) {
    console.error("Data fetch error:", error);
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  fetchData();
});
</script>

<style scoped>
.page-container {
  max-width: 1000px;
  margin: 40px auto;
  padding: 0 20px;
}

.header-section {
  margin-bottom: 30px;
}
.header-section h1 {
  color: #2c3e50;
  margin: 0 0 10px 0;
  font-size: 1.8rem;
}
.subtitle {
  color: #64748b;
  margin: 0;
}

/* Loading & Empty */
.loading-state,
.empty-state {
  text-align: center;
  padding: 60px 0;
  color: #64748b;
}
.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #eee;
  border-top-color: #42b983;
  border-radius: 50%;
  margin: 0 auto 20px;
  animation: spin 1s linear infinite;
}
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.empty-state {
  background: white;
  border-radius: 16px;
  padding: 60px 20px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
}
.empty-icon {
  font-size: 4rem;
  margin-bottom: 20px;
  display: block;
  opacity: 0.6;
}
.empty-state h3 {
  color: #2c3e50;
  margin-bottom: 10px;
}
.btn-primary {
  display: inline-block;
  margin-top: 20px;
  background: #42b983;
  color: white;
  padding: 10px 24px;
  border-radius: 8px;
  text-decoration: none;
  font-weight: bold;
  transition: 0.2s;
}
.btn-primary:hover {
  background: #3aa876;
  transform: translateY(-2px);
}

/* --- 列表容器 --- */
.listings-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* 單張卡片 (Row Layout) */
.listing-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  border: 1px solid #f1f5f9;
  transition: all 0.3s ease;
}

.listing-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.08);
  border-color: #42b983;
}

/* 1. 圖片與標題 */
.info-section {
  flex: 2;
  display: flex;
  align-items: center;
  gap: 15px;
  min-width: 250px;
}

.img-wrapper {
  width: 70px;
  height: 70px;
  border-radius: 8px;
  overflow: hidden;
  flex-shrink: 0;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
}
.img-wrapper img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.text-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.item-title {
  margin: 0;
  font-size: 1.1rem;
  color: #334155;
  font-weight: 600;
}
.meta-row {
  font-size: 0.85rem;
  color: #94a3b8;
}

/* 2. 狀態標籤 */
.status-section {
  flex: 1;
  display: flex;
  justify-content: center;
}
.status-badge {
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: bold;
  white-space: nowrap;
}
.status-badge.available {
  background: #f0fdf4;
  color: #166534;
} /* 上架中 - 綠 */
.status-badge.reserved {
  background: #eff6ff;
  color: #1e40af;
} /* 洽談中 - 藍 */
.status-badge.exchanged,
.status-badge.closed {
  background: #f1f5f9;
  color: #475569;
} /* 結束 - 灰 */

/* 3. 交易動態 (中間區塊) */
.deal-section {
  flex: 2;
  display: flex;
  justify-content: center;
}

/* 樣式 A: 進行中/完成的交易 */
.active-deal-box {
  background: #eff6ff;
  border: 1px solid #bfdbfe;
  padding: 8px 15px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  justify-content: space-between;
}
.active-deal-box.completed {
  background: #f0fdf4;
  border-color: #bbf7d0;
}

.deal-info {
  display: flex;
  flex-direction: column;
  font-size: 0.85rem;
}
.deal-info .label {
  font-weight: bold;
  color: #1e40af;
}
.active-deal-box.completed .label {
  color: #166534;
}
.partner-name {
  color: #64748b;
}

.btn-check-deal {
  font-size: 0.85rem;
  color: #2563eb;
  text-decoration: none;
  font-weight: 600;
}
.btn-check-deal:hover {
  text-decoration: underline;
}

/* 樣式 B: 待審核請求 */
.pending-requests-box {
  background: #fff7ed;
  border: 1px solid #fed7aa;
  padding: 8px 15px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  justify-content: space-between;
}
.notification-icon {
  color: #f97316;
}
.request-info {
  display: flex;
  flex-direction: column;
  font-size: 0.85rem;
}
.request-info .count {
  font-weight: bold;
  color: #c2410c;
}
.request-info .hint {
  color: #fdba74;
}

.btn-check-requests {
  font-size: 0.85rem;
  color: #ea580c;
  text-decoration: none;
  font-weight: 600;
  background: white;
  padding: 4px 8px;
  border-radius: 4px;
  border: 1px solid #fed7aa;
}
.btn-check-requests:hover {
  background: #fffaf0;
}

/* 樣式 C: 無動靜 */
.no-activity {
  color: #cbd5e0;
  font-size: 0.9rem;
  font-style: italic;
}

/* 4. 操作區 */
.action-section {
  flex: 0.8;
  display: flex;
  justify-content: flex-end;
}
.btn-view {
  padding: 8px 16px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  color: #64748b;
  text-decoration: none;
  font-size: 0.9rem;
  transition: 0.2s;
  background: white;
  white-space: nowrap;
}
.btn-view:hover {
  border-color: #42b983;
  color: #42b983;
  background: #f0fdf4;
}

/* RWD */
@media (max-width: 768px) {
  .listing-card {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }
  .info-section,
  .status-section,
  .deal-section,
  .action-section {
    width: 100%;
    justify-content: flex-start;
  }
  .status-section {
    justify-content: flex-start;
  }
  .action-section {
    justify-content: stretch;
  }
  .btn-view {
    width: 100%;
    text-align: center;
  }
}
</style>
