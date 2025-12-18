## iam 模組
1. Frontend 傳送 Google (或 Cognito) 的 Token 給後端。
2. Backend 驗證 Token 合法性 (透過 AWS Cognito)。
3. Backend 檢查資料庫有無此人：
* 若無：自動註冊 (將 Cognito 資料寫入 Postgres)。
* 若有：更新最後登入時間。
4. Backend 回傳使用者資訊。