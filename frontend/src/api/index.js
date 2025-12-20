// Axios 的全域設定 (設定 BaseURL, Interceptor)import axios from 'axios';

// 1. 建立 axios 實體
// import.meta.env.VITE_API_URL 會讀取 .env 檔案裡的設定
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000', 
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000, // 請求超過 10 秒算逾時
});

// 2. 請求攔截器 (Request Interceptor)
// 每次發送請求前，自動去 localStorage 抓 Token 帶入 Header
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

export default apiClient;

export { default as authApi } from './auth';
export { default as itemsApi } from './items';
export { default as exchangesApi } from './exchanges';