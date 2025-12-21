// frontend/src/api/items.js
import apiClient from './index';

export default {
  // 1. 取得物品列表 (支援搜尋與篩選)
  getItems(params) {
    return apiClient.get('/items/', { params });
  },

  // 2. 取得單一物品詳情
  getItem(id) {
    return apiClient.get(`/items/${id}`);
  },

  // 3. 刊登物品
  createItem(data) {
    const formData = new FormData();
    formData.append('title', data.title);
    formData.append('description', data.description);
    formData.append('category', data.category);
    formData.append('image', data.image); 

    return apiClient.post('/items/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },
  
  // 4. 更新物品狀態
  updateItemStatus(id, status) {
      return apiClient.patch(`/items/${id}/status`, { status });
  },

  // [新增] 5. 取得我的物品 (我的物品頁面用)
  getMyItems() {
    return apiClient.get('/items/me');
  },

  // [新增] 6. 取得分類清單 (首頁選單用)
  getCategories() {
    return apiClient.get('/items/categories');
  }
};