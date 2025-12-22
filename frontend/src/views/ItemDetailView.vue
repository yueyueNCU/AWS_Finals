<template>
  <div class="page-container">
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>正在讀取物品詳情...</p>
    </div>

    <div v-else-if="!item" class="error-state">
      <span class="icon">🔍</span>
      <h3>找不到這個物品</h3>
      <button @click="router.push('/')" class="btn-back">回首頁</button>
    </div>

    <div v-else class="detail-card">
      <div class="image-column">
        <div class="image-wrapper">
          <img
            :src="item.image_url || 'https://via.placeholder.com/600x400?text=No+Image'"
            alt="Item Image"
            @error="handleImageError"
          />
          <div v-if="item.status && item.status !== 'available'" class="status-overlay">
            {{ getStatusText(item.status) }}
          </div>
        </div>
      </div>

      <div class="info-column">
        <div class="info-header">
          <div class="meta-row">
            <span class="category-tag">🏷️ {{ categoryName }}</span>
            <span class="date-tag">{{ formatDate(item.created_at) }}</span>
          </div>
          <h1 class="item-title">{{ item.title }}</h1>
        </div>

        <div class="owner-block">
          <div class="avatar-placeholder">
            {{ getOwnerInitial(item.owner?.name || item.owner_name) }}
          </div>
          <div class="owner-text">
            <span class="label">刊登者</span>
            <span class="name">{{ item.owner?.name || item.owner_name || "未知使用者" }}</span>
          </div>
        </div>

        <div class="description-box">
          <h3>📝 物品描述</h3>
          <p>{{ item.description || "這個物品沒有詳細描述。" }}</p>
        </div>

        <div class="action-footer">
          <div v-if="isOwner" class="owner-actions">
            <button class="btn-disabled" disabled>👤 這是您刊登的物品</button>
          </div>

          <div v-else class="guest-actions">
            <button @click="openExchangeModal" class="btn-exchange">提出交換請求</button>
          </div>
        </div>
      </div>
    </div>

    <Transition name="fade">
      <div v-if="showExchangeModal" class="modal-overlay" @click.self="closeModal">
        <div class="modal-card">
          <div class="modal-header">
            <h3>發送交換請求</h3>
            <button class="btn-close" @click="closeModal">✕</button>
          </div>

          <div class="modal-body">
            <div class="form-group">
              <label>選擇你的物品 (用於交換)</label>
              <div class="select-wrapper">
                <select v-model="offeredItemId" class="styled-input styled-select">
                  <option value="">索取</option>
                  <option v-for="myItem in myItems" :key="myItem.id" :value="myItem.id">
                    {{ myItem.title }}
                  </option>
                </select>
                <span class="select-arrow">▼</span>
              </div>
              <small v-if="myItems.length === 0" class="hint-text">
                💡 你目前沒有上架的物品，建議先<router-link to="/post">刊登物品</router-link
                >增加交換成功率！
              </small>
            </div>

            <div class="form-group">
              <label>留言訊息 <span class="required">*</span></label>
              <textarea
                v-model="exchangeMessage"
                placeholder="你好，我對這個物品很有興趣，方便約時間交換嗎？..."
                rows="5"
                class="styled-input"
              ></textarea>
            </div>
          </div>

          <div class="modal-footer">
            <button @click="closeModal" class="btn-cancel">取消</button>
            <button @click="submitExchange" class="btn-confirm" :disabled="isSubmitting">
              {{ isSubmitting ? "傳送中..." : "確認送出" }}
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { itemsApi, exchangesApi } from "@/api";
import { useAuthStore } from "@/stores/auth";

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();

const item = ref(null);
const categories = ref([]);
const myItems = ref([]);
const showExchangeModal = ref(false);
const exchangeMessage = ref("");
const offeredItemId = ref("");
const isSubmitting = ref(false);
const loading = ref(true);

const isOwner = computed(() => {
  if (!authStore.user || !item.value) return false;
  const itemOwnerId = item.value.owner?.user_id || item.value.owner_id;
  return authStore.user.id === itemOwnerId;
});

const categoryName = computed(() => {
  if (!item.value || !categories.value.length) return "載入中...";
  const cat = categories.value.find(
    (c) => c.id === item.value.category_id || c.id === item.value.category
  );
  return cat ? cat.name : "一般物品";
});

const initData = async () => {
  loading.value = true;
  try {
    const [itemRes, catRes] = await Promise.all([
      itemsApi.getItem(route.params.id),
      itemsApi.getCategories(),
    ]);
    item.value = itemRes.data;
    categories.value = catRes.data;
  } catch (error) {
    console.error("Error loading data:", error);
  } finally {
    loading.value = false;
  }
};

const fetchMyItems = async () => {
  if (!authStore.isLoggedIn) return;
  try {
    let res;
    if (itemsApi.getMyItems) {
      res = await itemsApi.getMyItems();
    } else {
      res = await itemsApi.getItems();
      res.data = res.data.filter((i) => i.owner_id === authStore.user.id);
    }
    myItems.value = res.data;
  } catch (err) {
    console.error("Fetch my items error:", err);
  }
};

const openExchangeModal = () => {
  if (!authStore.isLoggedIn) {
    alert("請先登入才能提出交換！");
    return;
  }
  fetchMyItems();
  showExchangeModal.value = true;
};

const closeModal = () => {
  showExchangeModal.value = false;
  exchangeMessage.value = "";
  offeredItemId.value = "";
};

const submitExchange = async () => {
  if (!exchangeMessage.value.trim()) {
    alert("請輸入留言訊息");
    return;
  }

  isSubmitting.value = true;
  try {
    await exchangesApi.createExchange(item.value.id, {
      offered_item_id: offeredItemId.value || null,
      message: exchangeMessage.value,
    });

    alert("交換請求已送出！請至「我的帳戶」查看狀態。");
    closeModal();
    router.push("/profile");
  } catch (error) {
    console.error(error);
    const errorMsg = error.response?.data?.detail || "送出失敗，請稍後再試";
    alert(errorMsg);
  } finally {
    isSubmitting.value = false;
  }
};

const formatDate = (dateStr) => {
  if (!dateStr) return "";
  return new Date(dateStr).toLocaleDateString();
};

const getStatusText = (status) => {
  const map = { exchanged: "已交換", reserved: "洽談中", closed: "已結案" };
  return map[status] || status;
};

const getOwnerInitial = (name) => {
  return name ? name.charAt(0).toUpperCase() : "?";
};

const handleImageError = (e) => {
  e.target.src = "https://via.placeholder.com/600x400?text=Image+Error";
};

onMounted(() => {
  initData();
});
</script>

<style scoped>
.page-container {
  max-width: 1000px;
  margin: 40px auto;
  padding: 0 20px;
}

/* Loading & Error */
.loading-state,
.error-state {
  text-align: center;
  padding: 80px 0;
  color: #64748b;
}
.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #e2e8f0;
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
.error-state .icon {
  font-size: 3rem;
  display: block;
  margin-bottom: 10px;
}
.btn-back {
  margin-top: 15px;
  padding: 8px 16px;
  background: #fff;
  border: 1px solid #ddd;
  border-radius: 6px;
  cursor: pointer;
}

/* Detail Card */
.detail-card {
  display: flex;
  background: white;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.08);
  min-height: 500px;
}

/* Image Column */
.image-column {
  flex: 1.2;
  background-color: #f8fafc;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.image-wrapper {
  width: 100%;
  height: 100%;
  position: relative;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.image-wrapper img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  max-height: 500px;
  background: #f1f5f9;
}

.status-overlay {
  position: absolute;
  top: 15px;
  right: 15px;
  background: rgba(0, 0, 0, 0.8);
  color: white;
  padding: 6px 12px;
  border-radius: 20px;
  font-weight: bold;
}

/* Info Column */
.info-column {
  flex: 1;
  padding: 40px;
  display: flex;
  flex-direction: column;
}

.info-header {
  margin-bottom: 25px;
  border-bottom: 1px solid #f1f5f9;
  padding-bottom: 20px;
}

.meta-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  font-size: 0.9rem;
}

.category-tag {
  background: #ecfdf5;
  color: #059669;
  padding: 4px 10px;
  border-radius: 6px;
  font-weight: 600;
}
.date-tag {
  color: #94a3b8;
}

.item-title {
  font-size: 1.8rem;
  color: #1e293b;
  margin: 0;
  line-height: 1.3;
}

/* Owner Block */
.owner-block {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 25px;
}

.avatar-placeholder {
  width: 42px;
  height: 42px;
  background: linear-gradient(135deg, #42b983, #3aa876);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 1.2rem;
}

.owner-text {
  display: flex;
  flex-direction: column;
}
.owner-text .label {
  font-size: 0.75rem;
  color: #94a3b8;
}
.owner-text .name {
  font-weight: 600;
  color: #334155;
}

/* Description */
.description-box {
  background-color: #f8fafc;
  padding: 20px;
  border-radius: 12px;
  flex-grow: 1;
  margin-bottom: 30px;
}

.description-box h3 {
  margin: 0 0 10px 0;
  font-size: 1rem;
  color: #475569;
}
.description-box p {
  color: #334155;
  line-height: 1.6;
  white-space: pre-line;
  margin: 0;
}

/* Action Footer */
.action-footer {
  margin-top: auto;
}
.btn-exchange {
  width: 100%;
  padding: 14px;
  background: #42b983;
  color: white;
  border: none;
  border-radius: 10px;
  font-size: 1.1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 4px 12px rgba(66, 185, 131, 0.3);
}
.btn-exchange:hover {
  background: #3aa876;
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(66, 185, 131, 0.4);
}

.owner-actions {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.btn-disabled {
  width: 100%;
  padding: 12px;
  background: #f1f5f9;
  color: #94a3b8;
  border: 1px dashed #cbd5e0;
  border-radius: 8px;
  cursor: default;
}
.btn-edit {
  width: 100%;
  padding: 10px;
  background: transparent;
  border: 1px solid #42b983;
  color: #42b983;
  border-radius: 8px;
  cursor: pointer;
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(4px);
  z-index: 999;
  display: flex;
  justify-content: center;
  align-items: center;
}

.modal-card {
  background: white;
  width: 90%;
  max-width: 500px;
  border-radius: 16px;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.2);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  animation: slideUp 0.3s ease-out;
}

@keyframes slideUp {
  from {
    transform: translateY(20px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

.modal-header {
  padding: 20px;
  border-bottom: 1px solid #f1f5f9;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.modal-header h3 {
  margin: 0;
  color: #1e293b;
}
.btn-close {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #94a3b8;
}

.modal-body {
  padding: 25px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group label {
  display: block;
  font-weight: 600;
  margin-bottom: 8px;
  color: #475569;
  font-size: 0.9rem;
}
.required {
  color: #ef4444;
}

.styled-input {
  width: 100%;
  padding: 12px;
  border: 1px solid #cbd5e0;
  border-radius: 8px;
  font-size: 1rem;
  background: #f8fafc;
  transition: 0.3s;
  box-sizing: border-box;
}
.styled-input:focus {
  background: white;
  border-color: #42b983;
  outline: none;
  box-shadow: 0 0 0 3px rgba(66, 185, 131, 0.1);
}

.select-wrapper {
  position: relative;
}
.styled-select {
  appearance: none;
  cursor: pointer;
}
.select-arrow {
  position: absolute;
  right: 15px;
  top: 50%;
  transform: translateY(-50%);
  color: #94a3b8;
  pointer-events: none;
}
.hint-text {
  color: #94a3b8;
  font-size: 0.85rem;
  margin-top: 5px;
  display: block;
}
.hint-text a {
  color: #42b983;
  text-decoration: none;
}

.modal-footer {
  padding: 15px 25px 25px;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
.btn-cancel {
  padding: 10px 20px;
  border: 1px solid #cbd5e0;
  background: white;
  border-radius: 8px;
  color: #64748b;
  cursor: pointer;
}
.btn-confirm {
  padding: 10px 24px;
  background: #42b983;
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
}
.btn-confirm:hover {
  background: #3aa876;
}

/* RWD */
@media (max-width: 768px) {
  .detail-card {
    flex-direction: column;
    min-height: auto;
  }
  .image-column {
    padding: 0;
    height: 300px;
  }
  .image-wrapper {
    border-radius: 0;
    box-shadow: none;
  }
  .info-column {
    padding: 25px;
  }
  .item-title {
    font-size: 1.5rem;
  }
}

/* Transition */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
