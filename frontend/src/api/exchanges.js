import apiClient from './index';

export default {
  // --- 交換流程 ---

  // 1. 提出交換請求
  createExchange(itemId, data) {
    // data 範例: { offered_item_id: 205, message: "我想換..." }
    return apiClient.post(`/items/${itemId}/exchanges`, data);
  },

  // 2. 取得我的交換列表
  // role: 'requester' (我提的) 或 'owner' (別人提的)
  getExchanges(role) {
    return apiClient.get('/exchanges', { params: { role } });
  },

  // 3. 取得單一交換詳情
  getExchangeDetail(id) {
    return apiClient.get(`/exchanges/${id}`);
  },

  // 4. 更新交換狀態 (接受/拒絕)
  // data 範例: { action: 'accept', meetup_location_id: 1 }
  updateExchangeStatus(id, data) {
    return apiClient.patch(`/exchanges/${id}/status`, data);
  },

  // --- 系統資訊 (地點與分類) ---
  
  // 5. 取得面交地點清單
  getLocations() {
    return apiClient.get('/locations');
  },
  
  // 6. 取得分類清單
  getCategories() {
      return apiClient.get('/categories');
  }
};