# 透過 Cloudformation 部署服務

### 建立 Stack
> Stack 建置順序為 **network > security > data > app**

1. 點選 `Create stack` > `With new resources`
2. 設置選擇 `Choose an existing template`、`Upload a template file`
3. 點選 `Choose file` 上傳 .yaml 檔
4. 點選 `Next`
5. 按照 .yaml 檔的名稱（ex. network-stack）輸入 Stack name
6. 一路滑到最底按 `Next`，最後 `Submit`
7. 等待服務建置完畢（可以點轉圈圈刷新狀態）

### 更新 Stack

1. 點擊進入要更新的 Stack
2. 點選 `Update stack` > `Make a direct update`
3. 設置選擇 `Replace existing template`、`Upload a template file`
4. 點選 `Choose file` 上傳 .yaml 檔
5. 一路滑到最底按 `Next`，最後 `Submit`
6. 等待服務更新完畢（可以點轉圈圈刷新狀態）

```
若有更新 EC2 設置則需要手動終止舊的兩台 instances，終止後 Auto Scaling Group 自動啟動的兩台新 instances 便會套用新設置
```

### 補充

- 建置完畢後，S3 會有兩個新 Buckets
  - `mywebarchitecture-assets`：將 FastAPI 專案打包成 `backend.zip` 放在這裡
  - `mywebarchitecture-frontend`：託管靜態網站，把編譯後 Vue 產生的 dist 資料夾裡所有檔案放在這裡
  
