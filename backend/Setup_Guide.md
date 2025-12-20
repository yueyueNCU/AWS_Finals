## 如何設定環境

1. 進入 backend 資料夾

   ```
   cd backend
   ```

2. 執行創建環境的命令:  
   Windows
   ```
   py -m venv .venv
   ```
   Mac
   ```
   python3 -m venv .venv
   ```

## 進入 Virtual Environment (開始寫專案時就要進入)

1. 在 vscode powershell 中打上  
   Windows
   ```
   .\.venv\Scripts\activate
   ```
   Mac
   ```
   source .venv/bin/activate
   ```
2. 開始下載套件
   ```
   pip install -r requirements.txt
   ```

## 更新或加入套件

1. 安裝你的 Dependency
   ```
   pip install {你的Dependency}
   ```
2. 將 Dependency 寫入 requirements.txt
   ```
   pip freeze > requirements.txt
   ```

## 如何開啟後端 fastAPi server

1. 進入 backend 資料夾
   ```
   cd backend
   ```
2. 開啟 server
   ```
   uvicorn src.main:app --reload
   ```
