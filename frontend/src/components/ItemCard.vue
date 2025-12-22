<template>
  <div class="item-card" @click="goToDetail">
    <div class="card-image">
      <img :src="imageUrl" alt="Item Image" @error="handleImageError" />
      <div v-if="item.status && item.status !== 'available'" class="status-badge">
        {{ getStatusText(item.status) }}
      </div>
    </div>

    <div class="card-content">
      <h3 class="item-title">{{ item.title }}</h3>

      <div class="item-meta">
        <span class="category-tag"> 🏷️ {{ categoryName }} </span>
        <span class="time-ago">
          {{ formatDate(item.created_at) }}
        </span>
      </div>

      <div class="card-footer">
        <button class="btn-view">查看詳情</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from "vue";
import { useRouter } from "vue-router";

const props = defineProps({
  item: {
    type: Object,
    required: true,
  },
  categories: {
    type: Array,
    default: () => [],
  },
});

const router = useRouter();

// 處理圖片路徑 (假設後端回傳的是相對路徑或完整 URL)
const imageUrl = computed(() => {
  if (!props.item.image_url) return "https://via.placeholder.com/300x200?text=No+Image";
  // 如果是相對路徑，可能需要補上 backend base url，這裡先假設是完整 url 或能直接存取
  return props.item.image_url;
});

// 取得分類名稱
const categoryName = computed(() => {
  if (!props.categories.length) return "未分類";
  const cat = props.categories.find(
    (c) => c.id === props.item.category_id || c.id === props.item.category
  );
  return cat ? cat.name : "其他";
});

const goToDetail = () => {
  router.push(`/items/${props.item.id}`);
};

const handleImageError = (e) => {
  e.target.src = "https://via.placeholder.com/300x200?text=Image+Error";
};

const getStatusText = (status) => {
  const map = {
    exchanged: "已交換",
    reserved: "洽談中",
    closed: "已結案",
  };
  return map[status] || status;
};

const formatDate = (dateString) => {
  if (!dateString) return "";
  return new Date(dateString).toLocaleDateString();
};
</script>

<style scoped>
.item-card {
  background: white;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
  cursor: pointer;
  border: 1px solid #f0f0f0;
  display: flex;
  flex-direction: column;
}

.item-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 12px 25px rgba(0, 0, 0, 0.1);
  border-color: #42b983;
}

.card-image {
  width: 100%;
  padding-top: 66.67%; /* 3:2 Aspect Ratio */
  position: relative;
  background-color: #f8fafc;
}

.card-image img {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.5s ease;
}

.item-card:hover .card-image img {
  transform: scale(1.05);
}

.status-badge {
  position: absolute;
  top: 10px;
  right: 10px;
  background: rgba(0, 0, 0, 0.7);
  color: white;
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: bold;
}

.card-content {
  padding: 16px;
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.item-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: #2c3e50;
  margin: 0;
  line-height: 1.4;
  /* 限制兩行 */
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.item-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.85rem;
  color: #94a3b8;
  margin-top: auto; /* 推到底部 */
}

.category-tag {
  background-color: #f0fdf4;
  color: #166534;
  padding: 2px 8px;
  border-radius: 6px;
}

.card-footer {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #f1f5f9;
}

.btn-view {
  width: 100%;
  padding: 8px;
  background-color: transparent;
  border: 1px solid #42b983;
  color: #42b983;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-view:hover {
  background-color: #42b983;
  color: white;
}
</style>
