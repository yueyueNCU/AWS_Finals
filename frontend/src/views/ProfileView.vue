<template>
  <div class="page-container">
    <div class="profile-header-card" v-if="authStore.user">
      <div class="avatar-section">
        <img
          :src="authStore.user.avatar_url || 'https://via.placeholder.com/100'"
          class="avatar"
          alt="User Avatar"
        />
      </div>
      <div class="info-section">
        <h1>{{ authStore.user.name }}</h1>
        <p class="email">{{ authStore.user.email }}</p>
        <div class="stats-row">
          <span class="badge">使用者</span>
        </div>
      </div>
    </div>

    <div class="tabs-container">
      <button
        class="tab-btn"
        :class="{ active: currentTab === 'requester' }"
        @click="currentTab = 'requester'"
      >
        📤 我提出的交換
      </button>
      <button
        class="tab-btn"
        :class="{ active: currentTab === 'owner' }"
        @click="currentTab = 'owner'"
      >
        📥 收到的請求
      </button>
    </div>

    <div class="content-area">
      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
        <p>正在載入交換紀錄...</p>
      </div>

      <div v-else-if="exchanges.length === 0" class="empty-state">
        <span class="icon">📭</span>
        <h3>目前沒有{{ currentTab === "requester" ? "提出的" : "收到的" }}交換紀錄</h3>
        <p v-if="currentTab === 'requester'">
          去 <router-link to="/">首頁</router-link> 逛逛，尋找喜歡的物品吧！
        </p>
        <p v-else>快去 <router-link to="/post">刊登物品</router-link>，讓大家看見你的寶藏！</p>
      </div>

      <div v-else class="exchange-grid">
        <div
          class="exchange-card"
          v-for="ex in exchanges"
          :key="ex.exchange_id"
          @click="viewDetail(ex.exchange_id)"
        >
          <div class="card-top">
            <span class="id-text">#{{ ex.exchange_id.slice(0, 8) }}</span>
            <span class="status-badge" :class="ex.status">
              {{ translateStatus(ex.status) }}
            </span>
          </div>

          <div class="exchange-text-row">
            <div class="item-box">
              <span class="role-hint">
                {{ currentTab === "requester" ? "對方提供" : "對方提供" }}
              </span>
              <h3 class="item-title">
                {{
                  (currentTab === "requester" ? ex.target_item?.title : ex.offered_item?.title) ||
                  "（索取）"
                }}
              </h3>
            </div>

            <div class="arrow-wrapper">
              <span class="arrow-icon">⇄</span>
            </div>

            <div class="item-box my-item">
              <span class="role-hint">我方提供</span>
              <h3 class="item-title">
                {{
                  (currentTab === "requester" ? ex.offered_item?.title : ex.target_item?.title) ||
                  "（索取）"
                }}
              </h3>
            </div>
          </div>

          <div class="card-footer">
            <div class="partner-info">
              <span class="partner-label">交易對象：</span>
              <span class="partner-name">{{ ex.partner?.name || "未知用戶" }}</span>
            </div>

            <div class="actions">
              <button
                v-if="currentTab === 'requester' && ex.status === 'pending'"
                @click.stop="handleCancel(ex.exchange_id)"
                class="btn-outline-danger"
              >
                取消請求
              </button>
              <button class="btn-view">查看詳情</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from "vue";
import { useRouter } from "vue-router";
import { exchangesApi } from "@/api";
import { useAuthStore } from "@/stores/auth";

const router = useRouter();
const authStore = useAuthStore();
const currentTab = ref("requester");
const exchanges = ref([]);
const loading = ref(false);

const translateStatus = (status) => {
  const map = {
    pending: "等待回覆",
    accepted: "交易進行中",
    rejected: "已拒絕",
    completed: "已完成",
    cancelled: "已取消",
  };
  return map[status] || status;
};

const fetchExchanges = async () => {
  if (!authStore.isLoggedIn) return;

  loading.value = true;
  try {
    const role = currentTab.value;
    const response = await exchangesApi.getExchanges(role);
    exchanges.value = response.data;
  } catch (error) {
    console.error(error);
  } finally {
    loading.value = false;
  }
};

const handleCancel = async (exchangeId) => {
  if (!confirm("確定要取消這個交換請求嗎？")) return;
  try {
    await exchangesApi.cancelExchange(exchangeId);
    alert("已成功取消請求");
    fetchExchanges();
  } catch (error) {
    console.error(error);
    alert("取消失敗，請稍後再試");
  }
};

const viewDetail = (id) => {
  router.push(`/exchanges/${id}`);
};

watch(currentTab, () => {
  fetchExchanges();
});

onMounted(() => {
  if (authStore.isLoggedIn) {
    fetchExchanges();
  }
});
</script>

<style scoped>
.page-container {
  max-width: 900px;
  margin: 40px auto;
  padding: 0 20px;
}

/* --- 個人資料卡片 --- */
.profile-header-card {
  background: white;
  border-radius: 20px;
  padding: 30px;
  display: flex;
  align-items: center;
  gap: 30px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.05);
  margin-bottom: 30px;
}

.avatar {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  object-fit: cover;
  border: 4px solid #f0fdf4;
}

.info-section h1 {
  margin: 0 0 5px 0;
  color: #2c3e50;
  font-size: 1.8rem;
}

.info-section .email {
  color: #64748b;
  margin: 0 0 15px 0;
}

.badge {
  background: #ecfdf5;
  color: #059669;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 600;
}

/* --- 頁籤 --- */
.tabs-container {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  border-bottom: 2px solid #f1f5f9;
  padding-bottom: 10px;
}

.tab-btn {
  background: none;
  border: none;
  padding: 10px 20px;
  font-size: 1rem;
  color: #94a3b8;
  cursor: pointer;
  font-weight: 600;
  border-radius: 8px;
  transition: all 0.2s;
}

.tab-btn:hover {
  color: #42b983;
  background: #f0fdf4;
}

.tab-btn.active {
  color: #42b983;
  background: white;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
}

/* --- 列表區 --- */
.loading-state,
.empty-state {
  text-align: center;
  padding: 60px 0;
  color: #64748b;
  background: white;
  border-radius: 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03);
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

.empty-state .icon {
  font-size: 3rem;
  display: block;
  margin-bottom: 15px;
}
.empty-state a {
  color: #42b983;
  font-weight: bold;
  text-decoration: none;
}

/* Grid Layout */
.exchange-grid {
  display: grid;
  gap: 20px;
}

/* 交換卡片 (Card UI) */
.exchange-card {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.03);
  border: 1px solid #f1f5f9;
  transition: all 0.3s ease;
  cursor: pointer;
  display: flex;
  flex-direction: column;
}

.exchange-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.08);
  border-color: #42b983;
}

/* Card Top */
.card-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 1px solid #f8fafc;
}

.id-text {
  font-family: monospace;
  color: #cbd5e1;
  font-size: 0.9rem;
}

.status-badge {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: bold;
}
.status-badge.pending {
  background: #fff7ed;
  color: #ea580c;
}
.status-badge.accepted {
  background: #eff6ff;
  color: #2563eb;
}
.status-badge.completed {
  background: #ecfdf5;
  color: #059669;
}
.status-badge.rejected,
.status-badge.cancelled {
  background: #fef2f2;
  color: #dc2626;
}

/* Content Row (Text Only) */
.exchange-text-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
  padding: 0 10px;
}

.item-box {
  flex: 1;
  display: flex;
  flex-direction: row; /* 改成水平排列 */
  align-items: center; /* 垂直置中對齊 */
  gap: 10px; /* 標籤與標題之間的距離 */
}

/* 讓右邊 (我方) 的內容靠右對齊 */
.item-box.my-item {
  justify-content: flex-end; /* 內容靠右 */
}

.role-hint {
  font-size: 0.8rem;
  color: #94a3b8;
  background: #f1f5f9;
  padding: 4px 8px; /*稍微增加高度讓它跟標題比較搭*/
  border-radius: 4px;
  white-space: nowrap; /* 防止標籤換行 */
}

.item-title {
  font-size: 1.1rem;
  color: #334155;
  font-weight: 700;
  margin: 0;
  line-height: 1.4;
}

.arrow-wrapper {
  padding: 0 20px;
  color: #cbd5e0;
  font-size: 1.5rem;
}

/* Footer */
.card-footer {
  margin-top: auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 15px;
  border-top: 1px solid #f8fafc;
}

.partner-info {
  font-size: 0.9rem;
  color: #64748b;
}
.partner-label {
  color: #94a3b8;
}
.partner-name {
  font-weight: 600;
  color: #475569;
}

.actions {
  display: flex;
  gap: 10px;
}

.btn-view {
  background: #42b983;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 8px;
  font-size: 0.9rem;
  cursor: pointer;
  transition: 0.2s;
  font-weight: 500;
}
.btn-view:hover {
  background: #3aa876;
}

.btn-outline-danger {
  background: white;
  border: 1px solid #fca5a5;
  color: #ef4444;
  padding: 8px 16px;
  border-radius: 8px;
  font-size: 0.9rem;
  cursor: pointer;
  transition: 0.2s;
}
.btn-outline-danger:hover {
  background: #fef2f2;
}

/* RWD */
@media (max-width: 600px) {
  .profile-header-card {
    flex-direction: column;
    text-align: center;
    padding: 20px;
  }

  .exchange-text-row {
    flex-direction: column;
    gap: 15px;
    text-align: center;
  }

  .item-box,
  .item-box.my-item {
    text-align: center;
    align-items: center;
    width: 100%;
  }

  .arrow-wrapper {
    transform: rotate(90deg); /* 轉成垂直箭頭 */
  }

  .card-footer {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }

  .actions {
    width: 100%;
    justify-content: space-between;
  }
  .btn-view,
  .btn-outline-danger {
    flex: 1;
  }
}
</style>
