<template>
  <div class="container">
    <div v-if="loading" class="loading">載入中...</div>
    <div v-else-if="!exchange" class="error">找不到此交換請求</div>

    <div v-else class="detail-card">
      <div class="header">
        <h1>
          交換詳情 <small>#{{ exchange.id.slice(0, 8) }}...</small>
        </h1>
        <span class="status-badge" :class="exchange.status">
          {{ translateStatus(exchange.status) }}
        </span>
      </div>

      <div class="items-row">
        <div class="item-box">
          <h3>對方的物品</h3>
          <template v-if="isOwner">
            <div v-if="exchange.offered_item">
              <img
                :src="exchange.offered_item.cover_image || 'https://via.placeholder.com/150'"
                class="thumb"
              />
              <p class="title">{{ exchange.offered_item.title }}</p>
            </div>
            <div v-else class="no-item"><p>（純索取）</p></div>
          </template>
          <template v-else>
            <div v-if="exchange.target_item">
              <img
                :src="exchange.target_item.cover_image || 'https://via.placeholder.com/150'"
                class="thumb"
              />
              <p class="title">{{ exchange.target_item.title }}</p>
            </div>
          </template>
        </div>

        <div class="arrow">⇄</div>

        <div class="item-box highlight">
          <h3>我的物品</h3>
          <template v-if="isOwner">
            <div v-if="exchange.target_item">
              <img
                :src="exchange.target_item.cover_image || 'https://via.placeholder.com/150'"
                class="thumb"
              />
              <p class="title">{{ exchange.target_item.title }}</p>
            </div>
          </template>
          <template v-else>
            <div v-if="exchange.offered_item">
              <img
                :src="exchange.offered_item.cover_image || 'https://via.placeholder.com/150'"
                class="thumb"
              />
              <p class="title">{{ exchange.offered_item.title }}</p>
            </div>
            <div v-else class="no-item"><p>（純索取）</p></div>
          </template>
        </div>
      </div>

      <div class="message-section">
        <h4>提出者備註：</h4>
        <p class="message-content">{{ exchange.message || "無留言" }}</p>
        <p class="meta">時間: {{ formatDate(exchange.created_at) }}</p>
      </div>

      <div v-if="exchange.status === 'accepted'" class="active-deal-section">
        <div class="deal-header">
          <h3>🤝 交易進行中</h3>
          <p>雙方已接受交換，請透過下方對話框約定時間地點，完成後請點擊「確認完成」。</p>
        </div>

        <div class="deal-location-info">
          <div v-if="exchange.deal_info?.meetup_location" class="location-row">
            <span>
              <strong>預定地點：</strong> {{ exchange.deal_info.meetup_location.name }}
              <small class="text-muted">
                ({{ exchange.deal_info?.meetup_location?.address || "無詳細地址" }})
              </small>
            </span>
            <button
              v-if="authStore.user && !myConfirmed"
              @click="openLocationModal"
              class="btn-edit-loc"
            >
              ✎ 修改
            </button>
          </div>

          <div v-else class="location-row warning-box">
            <span style="color: #f57c00">⚠️ 尚未約定面交地點</span>
            <button
              v-if="authStore.user && !myConfirmed"
              @click="openLocationModal"
              class="btn-edit-loc"
            >
              📍 設定地點
            </button>
          </div>
        </div>

        <div class="confirm-actions">
          <button
            v-if="!myConfirmed"
            @click="handleConfirm"
            class="btn-confirm-deal"
            :disabled="isSubmitting"
          >
            ✅ 確認完成交易
          </button>

          <div v-else class="confirmed-wrapper">
            <div class="confirmed-badge">您已確認，等待對方...</div>
            <button
              @click="handleRevokeConfirm"
              class="btn-revoke-confirm"
              :disabled="isSubmitting"
            >
              ❌ 取消確認
            </button>
          </div>

          <div v-if="partnerConfirmed" class="partner-status">(對方已確認)</div>
        </div>
      </div>

      <ChatBox
        v-if="['accepted', 'completed'].includes(exchange.status) && authStore.user"
        :exchange-id="exchange.id"
        :current-user-id="authStore.user.id"
        :read-only="exchange.status === 'completed'"
      />

      <div class="action-area">
        <div v-if="isOwner && exchange.status === 'pending'" class="owner-actions">
          <h3>審核請求</h3>
          <div class="buttons">
            <button @click="handleReject" class="btn-reject" :disabled="isSubmitting">
              拒絕交換
            </button>
            <button @click="openAcceptModal" class="btn-accept" :disabled="isSubmitting">
              接受交換
            </button>
          </div>
        </div>

        <div v-if="canCancel" class="cancel-section">
          <hr />
          <p class="warning-text" v-if="exchange.status === 'accepted'">
            ⚠️ 若無法達成共識，您可以取消此交易，物品將重新上架。
          </p>
          <button @click="handleCancel" class="btn-cancel-exchange" :disabled="isSubmitting">
            {{ exchange.status === "pending" ? "撤回請求" : "取消交易" }}
          </button>
        </div>
      </div>

      <div v-if="exchange.status === 'completed'" class="deal-info success">
        <h3>🎉 交易圓滿完成！</h3>
        <p>感謝您的使用。</p>
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
              {{ loc.name }} ({{ loc.address || "無詳細地址" }})
            </option>
          </select>
        </div>
        <div class="modal-actions">
          <button @click="showAcceptModal = false" class="btn-cancel">取消</button>
          <button
            @click="handleAccept"
            class="btn-confirm"
            :disabled="!selectedLocationId || isSubmitting"
          >
            確認成交
          </button>
        </div>
      </div>
    </div>
    <div v-if="showLocationModal" class="modal-overlay" @click.self="showLocationModal = false">
      <div class="modal-content">
        <h3>更改面交地點</h3>
        <p>請選擇新的面交地點：</p>

        <div class="form-group">
          <label>面交地點</label>
          <select v-model="newLocationId">
            <option disabled value="">請選擇地點...</option>
            <option v-for="loc in locations" :key="loc.id" :value="loc.id">
              {{ loc.name }} ({{ loc.address || "無詳細地址" }})
            </option>
          </select>
        </div>

        <div class="modal-actions">
          <button @click="showLocationModal = false" class="btn-cancel">取消</button>
          <button
            @click="handleUpdateLocation"
            class="btn-confirm"
            :disabled="!newLocationId || isSubmitting"
          >
            更新地點
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { exchangesApi } from "@/api";
import { useAuthStore } from "@/stores/auth";
import ChatBox from "@/components/ChatBox.vue"; // 引入元件

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();

const loading = ref(true);
const exchange = ref(null);
const locations = ref([]);
const showAcceptModal = ref(false);
const selectedLocationId = ref("");
const isSubmitting = ref(false);

const showLocationModal = ref(false);
const newLocationId = ref("");

// 判斷身分
const currentUserId = computed(() => authStore.user?.id);
const isOwner = computed(() => exchange.value?.owner?.user_id === currentUserId.value);
const isRequester = computed(() => exchange.value?.requester?.user_id === currentUserId.value);

// 判斷確認狀態 (依賴後端回傳的新欄位)
const myConfirmed = computed(() => {
  if (!exchange.value) return false;
  if (isOwner.value) return exchange.value.owner_confirmed;
  if (isRequester.value) return exchange.value.requester_confirmed;
  return false;
});

const partnerConfirmed = computed(() => {
  if (!exchange.value) return false;
  if (isOwner.value) return exchange.value.requester_confirmed;
  if (isRequester.value) return exchange.value.owner_confirmed;
  return false;
});

// 判斷是否顯示取消按鈕
const canCancel = computed(() => {
  if (!exchange.value) return false;
  const status = exchange.value.status;

  // Pending: 只有發起者可以撤回 (Owner 只能拒絕)
  if (status === "pending" && isRequester.value) return true;

  // Accepted: 雙方都可以取消
  if (status === "accepted") return true;

  return false;
});

const fetchDetail = async () => {
  loading.value = true;
  try {
    const id = route.params.id;
    const res = await exchangesApi.getExchangeDetail(id);
    exchange.value = res.data;
  } catch (err) {
    console.error(err);
    alert("無法載入詳情");
    router.push("/profile");
  } finally {
    loading.value = false;
  }
};

const openAcceptModal = async () => {
  try {
    const res = await exchangesApi.getLocations();
    locations.value = res.data;
    showAcceptModal.value = true;
  } catch (err) {
    console.error(err);
    alert("無法載入地點清單");
  }
};

const handleAccept = async () => {
  if (!selectedLocationId.value) {
    alert("請選擇一個地點！");
    return;
  }

  if (!confirm("確定要接受此交換請求嗎？")) return;

  isSubmitting.value = true;
  try {
    // 將選中的地點 ID 傳給後端
    await exchangesApi.updateExchangeStatus(exchange.value.id, {
      action: "accept",
      meetup_location_id: selectedLocationId.value,
    });

    alert("已接受交易！");
    showAcceptModal.value = false;

    // 重新獲取資料以更新畫面狀態
    await fetchDetail();
  } catch (err) {
    console.error(err);
    alert("操作失敗，請稍後再試");
  } finally {
    isSubmitting.value = false;
  }
};

const handleReject = async () => {
  if (!confirm("確定要拒絕此交換請求嗎？")) return;
  performAction(() => exchangesApi.updateExchangeStatus(exchange.value.id, { action: "reject" }));
};

// 確認交易邏輯
const handleConfirm = async () => {
  if (!confirm("您確認已經完成交換了嗎？")) return;
  performAction(async () => {
    await exchangesApi.confirmExchange(exchange.value.id, { action: "confirm" });
    alert("您已確認完成！若對方也確認後，交易將自動結束。");
    fetchDetail();
  });
};

// 取消確認邏輯
const handleRevokeConfirm = async () => {
  if (!confirm("要取消「確認完成」狀態嗎？")) return;
  performAction(async () => {
    await exchangesApi.confirmExchange(exchange.value.id, { action: "revoke" });
    alert("已取消確認狀態。");
    fetchDetail();
  });
};

// 取消交易邏輯
const handleCancel = async () => {
  const msg =
    exchange.value.status === "accepted"
      ? "交易正在進行中，確定要取消嗎？物品將會重新變為可交易狀態。"
      : "確定要撤回此請求嗎？";

  if (!confirm(msg)) return;
  performAction(async () => {
    await exchangesApi.cancelExchange(exchange.value.id);
    alert("已取消交易");
    fetchDetail(); // 或導回列表 router.push('/exchanges?role=...')
  });
};

// 輔助函式: 統一處理 try-catch
const performAction = async (actionFn) => {
  isSubmitting.value = true;
  try {
    await actionFn();
    fetchDetail();
  } catch (err) {
    console.error(err);
    alert(err.response?.data?.detail || "操作失敗");
  } finally {
    isSubmitting.value = false;
  }
};

// 開啟修改地點視窗
const openLocationModal = async () => {
  // 如果還沒載入過地點，先載入
  if (locations.value.length === 0) {
    try {
      const res = await exchangesApi.getLocations();
      locations.value = res.data;
    } catch (err) {
      alert("無法載入地點清單");
      return;
    }
  }

  // 預設選中目前的地點
  if (exchange.value.deal_info?.meetup_location?.id) {
    newLocationId.value = exchange.value.deal_info.meetup_location.id;
  }

  showLocationModal.value = true;
};

// 執行更新地點
const handleUpdateLocation = async () => {
  if (!newLocationId.value) return;

  // 避免重複選擇
  if (exchange.value.deal_info?.meetup_location?.id === newLocationId.value) {
    showLocationModal.value = false;
    return;
  }

  isSubmitting.value = true;
  try {
    await exchangesApi.updateLocation(exchange.value.id, newLocationId.value);
    alert("地點已更新！");
    showLocationModal.value = false;
    fetchDetail(); // 重新整理畫面
  } catch (err) {
    console.error(err);
    alert("更新失敗");
  } finally {
    isSubmitting.value = false;
  }
};

const translateStatus = (status) => {
  const map = {
    pending: "等待中",
    accepted: "交易中",
    rejected: "已拒絕",
    completed: "已完成",
    cancelled: "已取消",
  };
  return map[status] || status;
};

const formatDate = (dateStr) => {
  if (!dateStr) return "";
  return new Date(dateStr).toLocaleString();
};

onMounted(() => {
  fetchDetail();
});
</script>

<style scoped>
/* 包含原有的 CSS */
.container {
  padding: 40px;
  max-width: 800px;
  margin: 0 auto;
}
.detail-card {
  border: 1px solid #ddd;
  padding: 30px;
  border-radius: 8px;
  background: #fff;
}
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}
.status-badge {
  padding: 6px 12px;
  border-radius: 20px;
  font-weight: bold;
  font-size: 0.9rem;
}
.status-badge.pending {
  background: #fff3e0;
  color: #ef6c00;
}
.status-badge.accepted {
  background: #e3f2fd;
  color: #1976d2;
} /* 改藍色系表示進行中 */
.status-badge.rejected,
.status-badge.cancelled {
  background: #ffebee;
  color: #c62828;
}
.status-badge.completed {
  background: #e8f5e9;
  color: #2e7d32;
}

/* ... Items Row CSS (省略) ... */
.items-row {
  display: flex;
  align-items: center;
  justify-content: space-around;
  margin-bottom: 30px;
  flex-wrap: wrap;
  gap: 20px;
}
.item-box {
  text-align: center;
  flex: 1;
  min-width: 200px;
  padding: 15px;
  border: 1px solid #eee;
  border-radius: 8px;
}
.item-box.highlight {
  border-color: #4caf50;
  background: #f9fff9;
}
.arrow {
  font-size: 2rem;
  color: #999;
}
.thumb {
  width: 100px;
  height: 100px;
  object-fit: cover;
  border-radius: 4px;
  margin-bottom: 10px;
}
.title {
  font-weight: bold;
}

.message-section {
  background: #f5f5f5;
  padding: 15px;
  border-radius: 4px;
  margin-bottom: 20px;
}

/* 新增樣式 */
.active-deal-section {
  background: #e3f2fd;
  border: 1px solid #bbdefb;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
}
.deal-header h3 {
  color: #1565c0;
  margin-top: 0;
}
.confirm-actions {
  margin-top: 15px;
  display: flex;
  align-items: center;
  gap: 15px;
}
.btn-confirm-deal {
  background: #2196f3;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
}
.btn-confirm-deal:hover {
  background: #1976d2;
}
.confirmed-badge {
  color: #2e7d32;
  font-weight: bold;
  background: #e8f5e9;
  padding: 8px 15px;
  border-radius: 20px;
}
.partner-status {
  color: #666;
  font-size: 0.9rem;
}

.cancel-section {
  margin-top: 30px;
  text-align: center;
}
.btn-cancel-exchange {
  background: transparent;
  border: 1px solid #999;
  color: #666;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
}
.btn-cancel-exchange:hover {
  background: #f5f5f5;
  color: #333;
}
.warning-text {
  color: #f57c00;
  font-size: 0.9rem;
  margin-bottom: 10px;
}

.action-area {
  margin-top: 30px;
}
.buttons {
  display: flex;
  gap: 20px;
  justify-content: center;
}
.btn-reject {
  background: #ff5252;
  color: white;
  border: none;
  padding: 10px 30px;
  border-radius: 4px;
  cursor: pointer;
}
.btn-accept {
  background: #4caf50;
  color: white;
  border: none;
  padding: 10px 30px;
  border-radius: 4px;
  cursor: pointer;
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
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
  max-width: 400px;
}
.form-group select {
  width: 100%;
  padding: 10px;
  margin-top: 5px;
  border: 1px solid #ccc;
  border-radius: 4px;
}
.modal-actions {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
.btn-cancel {
  background: #ccc;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
}
.btn-confirm {
  background: #4caf50;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
}
.location-row {
  display: flex;
  align-items: center;
  gap: 10px;
}

.btn-edit-loc {
  background: transparent;
  border: 1px solid #aaa;
  color: #666;
  border-radius: 4px;
  padding: 2px 8px;
  font-size: 0.8rem;
  cursor: pointer;
}
.btn-edit-loc:hover {
  background: #eee;
  color: #333;
}
.text-muted {
  color: #888;
  font-size: 0.9em;
}
.confirmed-wrapper {
  display: flex;
  align-items: center;
  gap: 10px;
}
.btn-revoke-confirm {
  background: transparent;
  border: 1px solid #ff5252;
  color: #ff5252;
  padding: 6px 12px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
}
.btn-revoke-confirm:hover {
  background: #ffebee;
}
</style>
