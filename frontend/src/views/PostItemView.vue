<template>
  <div class="post-container">
    <div class="post-card">
      <div class="card-header">
        <h2>📦 刊登新物品</h2>
        <p class="subtitle">填寫以下資訊，讓其他同學看見你的物品！</p>
      </div>

      <form @submit.prevent="handleSubmit" class="post-form">
        <div class="form-group upload-group">
          <label>物品照片</label>
          <div
            class="image-upload-area"
            :class="{ 'has-image': previewUrl, 'is-dragging': isDragging }"
            @dragover.prevent="isDragging = true"
            @dragleave.prevent="isDragging = false"
            @drop.prevent="handleDrop"
            @click="triggerFileInput"
          >
            <input
              type="file"
              ref="fileInput"
              @change="handleFileChange"
              accept="image/*"
              class="hidden-input"
            />

            <div v-if="!previewUrl" class="upload-placeholder">
              <span class="icon">📷</span>
              <p>點擊或拖曳上傳照片</p>
            </div>

            <div v-else class="preview-container">
              <img :src="previewUrl" alt="Preview" />
              <button type="button" class="btn-remove" @click.stop="removeImage">✕ 移除</button>
            </div>
          </div>
        </div>

        <div class="form-row highlight-row">
          <div class="form-group flex-2">
            <label for="title">物品名稱 <span class="required">*</span></label>
            <div class="input-wrapper">
              <span class="input-icon">✎</span>
              <input
                id="title"
                v-model="form.title"
                required
                placeholder="例如：大一微積分課本"
                class="styled-input"
              />
            </div>
          </div>

          <div class="form-group flex-1">
            <label for="category">分類 <span class="required">*</span></label>
            <div class="input-wrapper select-wrapper">
              <span class="input-icon">🏷️</span>
              <select
                id="category"
                v-model="form.category"
                required
                class="styled-input styled-select"
                :class="{ 'placeholder-selected': !form.category }"
              >
                <option value="" disabled>請選擇分類</option>
                <option v-for="cat in categories" :key="cat.id" :value="cat.id">
                  {{ cat.name }}
                </option>
              </select>
              <span class="select-arrow">▼</span>
            </div>
          </div>
        </div>

        <div class="form-group">
          <label for="description">詳細說明 <span class="required">*</span></label>
          <textarea
            id="description"
            v-model="form.description"
            required
            rows="5"
            placeholder="描述物品狀況、新舊程度、交換意願等..."
            class="styled-input textarea-input"
          ></textarea>
        </div>

        <div v-if="errorMessage" class="error-alert">
          {{ errorMessage }}
        </div>

        <div class="form-actions">
          <button type="button" class="btn-cancel" @click="handleCancel">取消</button>
          <button type="submit" class="btn-submit" :disabled="isSubmitting">
            {{ isSubmitting ? "處理中..." : "確認刊登" }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from "vue";
import { useRouter } from "vue-router";
import { itemsApi } from "@/api";
import { useAuthStore } from "@/stores/auth";

const router = useRouter();
const authStore = useAuthStore();
const categories = ref([]);
const fileInput = ref(null);

const form = reactive({
  title: "",
  category: "",
  description: "",
  image: null,
});

const previewUrl = ref(null);
const isSubmitting = ref(false);
const isDragging = ref(false);
const errorMessage = ref("");

const fetchCategories = async () => {
  try {
    const res = await itemsApi.getCategories();
    categories.value = res.data;
  } catch (error) {
    console.error("無法取得分類:", error);
  }
};

const triggerFileInput = () => fileInput.value.click();

const handleFile = (file) => {
  if (!file || !file.type.startsWith("image/")) return;
  form.image = file;
  previewUrl.value = URL.createObjectURL(file);
  errorMessage.value = "";
};

const handleFileChange = (e) => handleFile(e.target.files[0]);
const handleDrop = (e) => {
  isDragging.value = false;
  handleFile(e.dataTransfer.files[0]);
};

const removeImage = () => {
  form.image = null;
  previewUrl.value = null;
  if (fileInput.value) fileInput.value.value = "";
};

const handleCancel = () => {
  if (confirm("確定要取消嗎？")) router.back();
};

const handleSubmit = async () => {
  if (!authStore.isLoggedIn) return alert("請先登入");
  if (!form.image) return (errorMessage.value = "請上傳照片");

  isSubmitting.value = true;
  try {
    await itemsApi.createItem({ ...form });
    alert("刊登成功！");
    router.push("/");
  } catch (err) {
    console.error(err);
    errorMessage.value = "刊登失敗，請稍後再試";
  } finally {
    isSubmitting.value = false;
  }
};

onMounted(() => fetchCategories());
</script>

<style scoped>
.post-container {
  max-width: 750px;
  margin: 40px auto;
  padding: 0 20px;
}

.post-card {
  background: white;
  border-radius: 16px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.05);
  padding: 40px;
}

.card-header {
  text-align: center;
  margin-bottom: 35px;
}
.card-header h2 {
  color: #2c3e50;
  margin: 0 0 8px;
  font-size: 1.8rem;
}
.subtitle {
  color: #94a3b8;
  font-size: 0.95rem;
}

/* 表單佈局 */
.post-form {
  display: flex;
  flex-direction: column;
  gap: 25px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

label {
  font-size: 0.9rem;
  font-weight: 600;
  color: #475569;
  margin-left: 4px;
}
.required {
  color: #e74c3c;
}

/* --- ✨ 重點優化：輸入框樣式 --- */
.form-row {
  display: flex;
  gap: 20px;
}
.flex-1 {
  flex: 1;
}
.flex-2 {
  flex: 2;
} /* 名稱欄位寬一點 */

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

/* 圖示 */
.input-icon {
  position: absolute;
  left: 14px;
  font-size: 1.1rem;
  color: #94a3b8;
  z-index: 2;
  pointer-events: none; /* 讓點擊穿透圖示 */
}

/* 通用輸入框 */
.styled-input {
  width: 100%;
  padding: 12px 15px 12px 42px; /* 左邊留給圖示 */
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  background-color: #f8fafc;
  font-size: 1rem;
  color: #334155;
  transition: all 0.25s ease;
}

.styled-input::placeholder {
  color: #cbd5e1;
}

/* 輸入框 Focus 狀態 */
.styled-input:focus {
  background-color: #fff;
  border-color: #42b983;
  box-shadow: 0 0 0 4px rgba(66, 185, 131, 0.1);
  outline: none;
}

/* --- 自訂 Select 下拉選單 --- */
.select-wrapper {
  position: relative;
}

.styled-select {
  appearance: none; /* 隱藏預設箭頭 */
  -webkit-appearance: none;
  cursor: pointer;
  padding-right: 40px; /* 右邊留給自訂箭頭 */
}

.select-arrow {
  position: absolute;
  right: 15px;
  color: #94a3b8;
  font-size: 0.7rem;
  pointer-events: none;
}

.styled-select:focus + .select-arrow {
  color: #42b983;
}

/* 未選擇時的顏色變淡 */
.placeholder-selected {
  color: #94a3b8;
}

/* TextArea 獨立樣式 */
.textarea-input {
  padding: 15px; /* 不需要左邊縮排 */
  min-height: 120px;
  resize: vertical;
}

/* --- 上傳區塊 --- */
.image-upload-area {
  border: 2px dashed #cbd5e0;
  border-radius: 12px;
  padding: 20px;
  text-align: center;
  cursor: pointer;
  background: #f8fafc;
  transition: 0.3s;
  min-height: 180px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.image-upload-area:hover,
.image-upload-area.is-dragging {
  border-color: #42b983;
  background: #f0fdf4;
}
.hidden-input {
  display: none;
}

.upload-placeholder .icon {
  font-size: 2.5rem;
  display: block;
  margin-bottom: 10px;
  opacity: 0.5;
}
.upload-placeholder p {
  color: #64748b;
  font-size: 0.9rem;
  margin: 0;
}

.preview-container {
  position: relative;
  width: 100%;
}
.preview-container img {
  max-height: 250px;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}
.btn-remove {
  position: absolute;
  top: -10px;
  right: -10px;
  background: #ef4444;
  color: white;
  border: none;
  border-radius: 20px;
  padding: 4px 12px;
  font-size: 0.8rem;
  cursor: pointer;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
}

/* 按鈕與 RWD */
.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 15px;
  margin-top: 10px;
}
.btn-cancel {
  padding: 10px 20px;
  background: #fff;
  border: 1px solid #cbd5e0;
  border-radius: 8px;
  cursor: pointer;
  color: #64748b;
}
.btn-submit {
  padding: 10px 24px;
  background: #42b983;
  border: none;
  border-radius: 8px;
  color: white;
  font-weight: 600;
  cursor: pointer;
  transition: 0.2s;
}
.btn-submit:hover:not(:disabled) {
  background: #3aa876;
  transform: translateY(-1px);
}
.btn-submit:disabled {
  background: #94a3b8;
  cursor: not-allowed;
}
.error-alert {
  color: #ef4444;
  background: #fef2f2;
  padding: 10px;
  border-radius: 8px;
  font-size: 0.9rem;
  text-align: center;
}

@media (max-width: 600px) {
  .post-card {
    padding: 20px;
  }
  .form-row {
    flex-direction: column;
    gap: 15px;
  }
}
</style>
