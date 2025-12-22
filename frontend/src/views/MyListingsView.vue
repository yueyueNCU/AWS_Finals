<template>
  <div class="container">
    <h1>我的物品管理</h1>
    
    <div v-if="loading" class="loading">載入中...</div>
    
    <div v-else-if="myItems.length === 0" class="empty-state">
      <p>你還沒有刊登任何物品。</p>
      <router-link to="/post" class="btn-primary">立即刊登</router-link>
    </div>

    <div v-else class="listings-table">
      <div class="table-header">
        <div class="col-info">物品資訊</div>
        <div class="col-status">狀態</div>
        <div class="col-deal">交易紀錄 / 對象</div>
        <div class="col-action">操作</div>
      </div>

      <div v-for="item in myItems" :key="item.id" class="table-row">
        <div class="col-info">
          <img :src="item.image_url || 'https://via.placeholder.com/80'" class="thumb" />
          <div class="text">
            <h4>{{ item.title }}</h4>
            <span class="date">刊登於 {{ new Date(item.created_at).toLocaleDateString() }}</span>
          </div>
        </div>

        <div class="col-status">
          <span class="badge" :class="item.status">{{ translateStatus(item.status) }}</span>
        </div>

        <div class="col-deal">
          <template v-if="item.activeExchange">
            <p class="partner">
              交易對象: <strong>{{ item.activeExchange.partner.name }}</strong>
            </p>
            <p class="deal-status">
               ({{ translateExchangeStatus(item.activeExchange.status) }})
            </p>
            <router-link :to="`/exchanges/${item.activeExchange.exchange_id}`" class="link">
              查看詳情
            </router-link>
          </template>
          
          <template v-else>
            <span class="text-muted">尚無成交紀錄</span>
            <p v-if="item.requestCount > 0" class="pending-count">
              有 {{ item.requestCount }} 個等待中的請求
            </p>
          </template>
        </div>

        <div class="col-action">
          <router-link :to="`/items/${item.id}`" class="btn-view">
            查看頁面
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { itemsApi, exchangesApi } from '@/api';

const myItems = ref([]);
const loading = ref(true);

// 狀態翻譯對照
const translateStatus = (status) => {
  const map = { AVAILABLE: '上架中', TRADING: '交易中', COMPLETED: '已完成' };
  return map[status] || status;
};

const translateExchangeStatus = (status) => {
  const map = { pending: '等待中', accepted: '已接受', completed: '已完成' };
  return map[status] || status;
};

const fetchData = async () => {
  loading.value = true;
  try {
    // 平行呼叫兩支 API
    const [itemsRes, exchangesRes] = await Promise.all([
      itemsApi.getMyItems(),
      exchangesApi.getExchanges('owner') // 取得別人對我的請求
    ]);

    const items = itemsRes.data;
    const exchanges = exchangesRes.data;

    // 資料整合：把交換資訊「掛」到物品上
    myItems.value = items.map(item => {
      // 1. 找出這個物品所有相關的請求
      const relatedExchanges = exchanges.filter(ex => ex.target_item.item_id === item.id);
      
      // 2. 找出是否有「進行中 (Accepted)」或是「已完成 (Completed)」的交易
      //    這代表這個物品目前的 "Active Deal"
      // const activeExchange = relatedExchanges.find(ex => 
      //   ['accepted', 'completed', 'trading'].includes(ex.status)
      // );

      // 3. 計算有多少個 Pending 請求
      const requestCount = relatedExchanges.filter(ex => ex.status === 'pending').length;

      return {
        ...item,
        // activeExchange, // 綁定成交資訊
        requestCount    // 綁定請求數量
      };
    });

  } catch (error) {
    console.error(error);
    alert('載入失敗');
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  fetchData();
});
</script>

<style scoped>
.container { max-width: 900px; margin: 40px auto; padding: 0 20px; }
h1 { margin-bottom: 30px; color: #333; }

/* 表格排版 */
.listings-table { border: 1px solid #eee; border-radius: 8px; overflow: hidden; }

/* 標頭列：背景色、文字顏色、加粗 */
.table-header { 
  display: flex; 
  background: #f8f9fa; 
  padding: 15px; 
  font-weight: bold; 
  color: #666; 
}

/* [標頭] 強制所有標題欄位都「置中」 */
.table-header .col-info,
.table-header .col-status,
.table-header .col-deal,
.table-header .col-action {
  justify-content: center;
  text-align: center;
}

/* 內容列：滑鼠移過去變色 */
.table-row { display: flex; border-top: 1px solid #eee; padding: 20px 15px; align-items: center; background: #fff; }
.table-row:hover { background: #fafafa; }

/* --- [修改重點] 讓內容欄位也全部置中對齊 --- */

/* 1. 物品資訊 (圖片+文字) */
.col-info { 
  flex: 3; 
  display: flex; 
  gap: 15px; 
  align-items: center; 
  justify-content: center; /* [新增] 讓圖片與文字整體水平置中 */
  text-align: left;        /* (選填) 保持文字在圖片右側時靠左對齊，讀起來比較順 */
}

/* 2. 狀態 */
.col-status { 
  flex: 1; 
  display: flex;           /* [新增] Flex 佈局 */
  justify-content: center; /* [新增] 水平置中 */
  align-items: center;     /* [新增] 垂直置中 */
  text-align: center; 
}

/* 3. 交易紀錄 */
.col-deal { 
  flex: 2; 
  padding: 0 15px; 
  font-size: 0.9rem;
  display: flex;           /* [新增] Flex 佈局 */
  flex-direction: column;  /* [新增] 垂直排列 (讓多行文字上下排) */
  justify-content: center; /* [新增] 垂直置中 */
  align-items: center;     /* [新增] 水平置中 */
  text-align: center;      /* [新增] 文字置中 */
}

/* 4. 操作 (按鈕) */
.col-action { 
  flex: 1; 
  display: flex;           /* [新增] Flex 佈局 */
  justify-content: center; /* [新增] 水平置中 (原本是靠右) */
  align-items: center;     /* [新增] 垂直置中 */
  text-align: center;
}

/* --- 其他元件樣式 (保持不變) --- */
.thumb { width: 60px; height: 60px; object-fit: cover; border-radius: 4px; }
.text h4 { margin: 0 0 5px 0; font-size: 1rem; }
.date { color: #999; font-size: 0.8rem; }

.badge { padding: 4px 8px; border-radius: 12px; font-size: 0.85rem; font-weight: bold; }
.badge.AVAILABLE { background: #e3f2fd; color: #1976d2; }
.badge.TRADING { background: #fff3e0; color: #f57c00; }
.badge.COMPLETED { background: #e8f5e9; color: #388e3c; }

.partner { margin: 0; color: #333; }
.deal-status { color: #666; font-size: 0.85rem; margin-top: 2px; }
.pending-count { color: #f57c00; font-weight: bold; font-size: 0.85rem; }
.link { color: #1976d2; text-decoration: underline; font-size: 0.85rem; cursor: pointer; }

.btn-view { padding: 6px 12px; border: 1px solid #ddd; border-radius: 4px; color: #555; text-decoration: none; transition: all 0.2s; }
.btn-view:hover { border-color: #333; color: #333; }

.btn-primary { display: inline-block; background: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 4px; }
</style>