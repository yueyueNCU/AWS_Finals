// 對應後端 iam 模組 (登入、取得個人資料)import apiClient from './index';

export default {
  // 1. Google/Cognito 登入 (用 code 換 token)
  login(code) {
    return apiClient.post('/auth/login', { code: code });
  },

  // 2. 取得當前使用者資料 (需帶 Token，interceptor 會自動處理)
  getMe() {
    return apiClient.get('/auth/me');
  }
};