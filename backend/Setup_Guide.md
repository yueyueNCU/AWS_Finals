## 如何設定環境
1. 進入backend資料夾
    ```
    cd backend
    ```
2. 執行創建環境的命令:
    py -m venv .venv
## 進入Virtual Environment (開始寫專案時就要進入)

1. 在vscode powershell中打上
    ```
    .\.venv\Scripts\activate 
    ```
2. 開始下載套件
    ```
    pip install -r requirements.txt
    ```

## 更新或加入套件 
1. 安裝你的Dependency
    ```
    pip install {你的Dependency}
    ```
2. 將Dependency寫入requirements.txt
    ```
    pip freeze > requirements.txt
    ```

## 如何開啟後端fastAPi server 
1. 進入backend資料夾
    ```
    cd backend
    ```
2. 開啟server
    ```
    uvicorn src.main:app --reload
    ```