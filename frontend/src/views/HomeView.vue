<!-- 首頁 (搜尋 + 物品列表) -->
 <template>
  <div class="home-container">
    <h1>物品列表</h1>
    
    <div class="filter-section">
      <input v-model="searchKeyword" placeholder="搜尋物品名稱..." @keyup.enter="fetchItems" />
      <select v-model="selectedCategory" @change="fetchItems">
        <option value="">所有分類</option>
        <option value="TEXTBOOK">教科書</option>
        <option value="3C">3C 周邊</option>
        <option value="DAILY">生活用品</option>
        <option value="OTHER">其他</option>
      </select>
      <button @click="fetchItems">搜尋</button>
    </div>

    <div v-if="loading">載入中...</div>
    <div v-else class="items-grid">
      <div v-for="item in items" :key="item.id" class="item-card" @click="goToDetail(item.id)">
        <img :src="item.image_url || 'https://via.placeholder.com/150'" alt="item image" />
        <h3>{{ item.title }}</h3>
        <p class="category-tag">{{ item.category }}</p>
      </div>
    </div>
    
    <div v-if="items.length === 0 && !loading">
      沒有找到相關物品。
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { itemsApi } from '@/api'; // 引入我們寫好的 API

const router = useRouter();
const items = ref([]);
const loading = ref(false);
const searchKeyword = ref('');
const selectedCategory = ref('');

// 抓取物品列表
const fetchItems = async () => {
  loading.value = true;
  try {
    const params = {};
    if (searchKeyword.value) params.keyword = searchKeyword.value;
    if (selectedCategory.value) params.category = selectedCategory.value;

    const response = await itemsApi.getItems(params);
    items.value = response.data; // 假設後端直接回傳 list，或是 response.data.items
  } catch (error) {
    console.error('抓取失敗', error);
  } finally {
    loading.value = false;
  }
};

// 跳轉到詳情頁
const goToDetail = (id) => {
  router.push(`/items/${id}`);
};

// 畫面載入時自動抓一次
onMounted(() => {
  fetchItems();
});
</script>

<style scoped>
.home-container {
  padding: 20px;
}
.filter-section {
  margin-bottom: 20px;
  gap: 10px;
  display: flex;
}
.items-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 20px;
}
.item-card {
  border: 1px solid #ddd;
  padding: 10px;
  border-radius: 8px;
  cursor: pointer;
  transition: transform 0.2s;
}
.item-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}
.item-card img {
  width: 100%;
  height: 150px;
  object-fit: cover;
  border-radius: 4px;
}
.category-tag {
  background: #eee;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 0.8rem;
  display: inline-block;
}
</style>