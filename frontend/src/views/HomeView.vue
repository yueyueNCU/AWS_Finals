<template>
  <div class="home-container">
    <section class="hero-section">
      <h1>👋 歡迎來到返璞歸真福利社</h1>
      <p>尋找你需要的物品，或是讓閒置物品發揮新價值</p>

      <div class="search-bar-wrapper">
        <div class="search-inputs">
          <div class="input-group flex-2">
            <span class="icon">🔍</span>
            <input
              v-model="filters.search"
              @keyup.enter="fetchItems"
              type="text"
              placeholder="搜尋物品名稱..."
              class="styled-input"
            />
          </div>

          <div class="input-group flex-1">
            <span class="icon">🏷️</span>
            <select
              v-model="filters.category"
              @change="fetchItems"
              class="styled-input styled-select"
            >
              <option value="">所有分類</option>
              <option v-for="cat in categories" :key="cat.id" :value="cat.id">
                {{ cat.name }}
              </option>
            </select>
            <span class="arrow">▼</span>
          </div>

          <button @click="fetchItems" class="btn-search">搜尋</button>
        </div>
      </div>
    </section>

    <section class="items-grid-container">
      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
        <p>正在載入物品...</p>
      </div>

      <div v-else-if="items.length === 0" class="empty-state">
        <span class="empty-icon">📦</span>
        <h3>目前沒有符合條件的物品</h3>
        <p>試試看其他關鍵字，或是 <router-link to="/post">成為第一個刊登的人</router-link>！</p>
      </div>

      <div v-else class="items-grid">
        <ItemCard v-for="item in items" :key="item.id" :item="item" :categories="categories" />
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from "vue";
import { itemsApi } from "@/api";
import ItemCard from "@/components/ItemCard.vue";

const items = ref([]);
const categories = ref([]);
const loading = ref(false);

const filters = reactive({
  search: "",
  category: "",
});

// 取得分類清單
const fetchCategories = async () => {
  try {
    const res = await itemsApi.getCategories();
    categories.value = res.data;
  } catch (error) {
    console.error("無法取得分類:", error);
  }
};

// 取得物品列表
const fetchItems = async () => {
  loading.value = true;
  try {
    // 組合查詢參數
    const params = {};
    if (filters.search) params.keyword = filters.search;
    if (filters.category) params.category = filters.category;

    const res = await itemsApi.getItems(params);
    items.value = res.data; // 假設後端直接回傳 list 或 { data: [] }
  } catch (error) {
    console.error("無法取得物品:", error);
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  fetchCategories();
  fetchItems();
});
</script>

<style scoped>
.home-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

/* Hero Section */
.hero-section {
  text-align: center;
  margin-bottom: 40px;
  padding: 40px 20px;
  background: linear-gradient(135deg, #f0fdf4 0%, #ffffff 100%);
  border-radius: 20px;
  box-shadow: inset 0 0 20px rgba(66, 185, 131, 0.05);
}

.hero-section h1 {
  color: #2c3e50;
  margin-bottom: 10px;
  font-size: 2rem;
}

.hero-section p {
  color: #64748b;
  margin-bottom: 30px;
}

/* Search Bar */
.search-bar-wrapper {
  max-width: 800px;
  margin: 0 auto;
  background: white;
  padding: 10px;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.search-inputs {
  display: flex;
  gap: 10px;
}

@media (max-width: 768px) {
  .search-inputs {
    flex-direction: column;
  }
}

.flex-1 {
  flex: 1;
}
.flex-2 {
  flex: 2;
}

.input-group {
  position: relative;
  display: flex;
  align-items: center;
}

.input-group .icon {
  position: absolute;
  left: 15px;
  color: #94a3b8;
  pointer-events: none;
  z-index: 10;
}

.styled-input {
  width: 100%;
  padding: 12px 15px 12px 45px; /* 左邊留空間給 Icon */
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  font-size: 1rem;
  background-color: #f8fafc;
  transition: all 0.3s;
}

.styled-input:focus {
  background-color: white;
  border-color: #42b983;
  box-shadow: 0 0 0 3px rgba(66, 185, 131, 0.1);
  outline: none;
}

.styled-select {
  appearance: none;
  cursor: pointer;
}

.input-group .arrow {
  position: absolute;
  right: 15px;
  font-size: 0.8rem;
  color: #94a3b8;
  pointer-events: none;
}

.btn-search {
  padding: 0 30px;
  background-color: #42b983;
  color: white;
  border: none;
  border-radius: 10px;
  font-weight: bold;
  cursor: pointer;
  transition: 0.2s;
  min-height: 48px; /* 確保跟輸入框一樣高 */
}

.btn-search:hover {
  background-color: #3aa876;
}

/* Grid Layout */
.items-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 30px;
  padding: 10px;
}

/* Loading & Empty States */
.loading-state,
.empty-state {
  text-align: center;
  padding: 60px 20px;
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

.empty-icon {
  font-size: 4rem;
  display: block;
  margin-bottom: 20px;
  opacity: 0.5;
}

.empty-state a {
  color: #42b983;
  font-weight: bold;
  text-decoration: none;
}
.empty-state a:hover {
  text-decoration: underline;
}
</style>
