// 對應後端 inventory 模組 (刊登、搜尋、詳情)
import apiClient from './index';

export default {
  // 1. 取得物品列表 (支援搜尋與篩選)
  // params 範例: { keyword: '微積分', category: 'TEXTBOOK' }
  getItems(params) {
    return apiClient.get('/items/', { params });
  },

  // 2. 取得單一物品詳情
  getItem(id) {
    return apiClient.get(`/items/${id}`);
  },

  // 取得我刊登的物品
  getMyItems() {
    return apiClient.get('/items/me');
  },

  // 3. 刊登物品 (需要上傳圖片，所以要用 FormData)
  createItem(data) {
    const formData = new FormData();
    formData.append('title', data.title);
    formData.append('description', data.description);
    formData.append('category', data.category);
    // data.image 必須是 File 物件 (從 <input type="file"> 拿到的)
    formData.append('image', data.image); 

    return apiClient.post('/items/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },
  
  // 4. 下架或管理狀態 (如果未來有的話)
  updateItemStatus(id, status) {
      return apiClient.patch(`/items/${id}/status`, { status });
  }
};