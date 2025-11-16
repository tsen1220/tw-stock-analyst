# 快速開始指南

## 當前狀態 ✅

- ✅ UV 專案已初始化
- ✅ 所有依賴已安裝
- ✅ Qdrant 向量資料庫已啟動 (Docker)
- ✅ 專案結構已建立
- ✅ 所有核心模組已完成

## 下一步操作

### 1. 安裝並啟動 Ollama + Deepseek 模型

```bash
# 如果尚未安裝 Ollama
brew install ollama

# 在新終端啟動 Ollama 服務（保持運行）
ollama serve

# 在另一個終端下載 Deepseek 模型
ollama pull deepseek-r1:1.5b
```

**為什麼選擇 deepseek-r1:1.5b？**
- 輕量級模型，適合本地運行
- 對中文支援良好
- 推理速度快

### 2. 載入台股資料到向量資料庫

```bash
# 方式一：載入所有預設的台股科技股（15檔）
uv run stock-load

# 方式二：只載入特定股票（例如台積電、聯發科）
uv run stock-load --stocks 2330 2454

# 方式三：載入更多天數的歷史資料
uv run stock-load --days 60
```

這個步驟會：
1. 從 FinMind/twstock 抓取股價資料
2. 計算技術指標（MA、RSI、MACD、KD 等）
3. 抓取財報基本面資料
4. 將資料向量化並存入 Qdrant

**預計時間：** 約 2-5 分鐘（取決於股票數量和網路速度）

### 3. 啟動問答系統

```bash
uv run stock-qa
```

### 4. 開始提問

系統啟動後，嘗試以下問題：

```
您的問題> 台積電最近的技術面表現如何？
您的問題> RSI 超過 70 的科技股有哪些？
您的問題> 聯發科和台積電的股價走勢比較
您的問題> 分析鴻海最近的 MACD 指標
```

## 檢查各組件狀態

### 檢查 Qdrant（向量資料庫）

```bash
# 查看容器狀態
docker ps

# 查看 Qdrant Web UI
open http://localhost:6333/dashboard
```

### 檢查 Ollama（Deepseek 模型）

```bash
# 查看已安裝的模型
ollama list

# 測試模型
ollama run deepseek-r1:1.5b "你好"
```

### 檢查向量資料

進入 Python 環境測試：

```bash
uv run python
```

```python
from tw_stock_analyst.vectordb.qdrant_client import StockVectorDB

db = StockVectorDB()
info = db.get_collection_info()
print(f"向量數量: {info.get('vectors_count', 0)}")
```

## 常見問題

### Q: Qdrant 無法連接？

```bash
# 重啟 Docker 容器
docker compose restart

# 檢查日誌
docker compose logs qdrant
```

### Q: Ollama 模型無法使用？

```bash
# 確認 Ollama 服務是否運行
ps aux | grep ollama

# 手動啟動
ollama serve
```

### Q: 資料載入失敗？

- 檢查網路連線
- FinMind API 可能有限制，可以註冊取得 token
- 使用 `--skip-fundamentals` 跳過財報資料

### Q: 如何更新資料？

```bash
# 重新載入會自動覆蓋舊資料
uv run stock-load
```

### Q: 如何重置向量資料庫？

```python
from tw_stock_analyst.vectordb.qdrant_client import StockVectorDB

db = StockVectorDB()
db.delete_collection()  # 刪除 collection
db.create_collection()  # 重新建立
```

## 專案架構

```
資料流程：
1. 台股資料來源 (FinMind/twstock)
   ↓
2. 技術指標計算 (ta library)
   ↓
3. 文本格式化
   ↓
4. Embedding 向量化 (Sentence Transformers)
   ↓
5. 存入 Qdrant 向量資料庫
   ↓
6. 用戶查詢 → 向量搜尋 → 檢索相關文檔
   ↓
7. 組裝 Context + Prompt → Deepseek 生成回答
```

## 進階配置

編輯 `config.yaml` 檔案自訂配置：

```yaml
# Qdrant 向量資料庫
qdrant:
  host: localhost
  port: 6333

# FinMind API（可選）
finmind:
  api_url: https://api.finmindtrade.com/api/v4/data
  token: your_token_here

# Ollama 模型
ollama:
  host: http://localhost:11434
  model: deepseek-r1:1.5b

# Embedding 模型
embedding:
  model: paraphrase-multilingual-MiniLM-L12-v2

# 股票清單（含代碼和名稱）
data:
  stocks:
    "2330": "台積電"
    "2454": "聯發科"
    # ... 更多股票
```


## 如何追蹤更多股票

只需編輯 `config.yaml`，在 `data.tech_stocks` 中添加股票代碼：

```yaml
data:
  stocks:
    "2330": "台積電"
    "2317": "鴻海"
    "2454": "聯發科"
    # ... 預設 15 檔
    "2412": "中華電信"  # 新增
    "2881": "富邦金"    # 新增
```

新增後重新載入資料：
```bash
# 只載入新增的股票
uv run stock-load --stocks 2412 2881

# 或重新載入所有股票
uv run stock-load
```

**提示：**
- 可在[台灣證券交易所](https://www.twse.com.tw)查詢股票代碼
- 預設配置已包含 15 檔科技股
- 支援台股所有上市公司

## 祝使用愉快！

如有問題，請查看 README.md 或檢查各組件日誌。
