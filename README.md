# 台股分析 RAG 系統 (Taiwan Stock Market RAG System)

基於向量資料庫與本地 LLM 的台灣股市智能分析系統，使用 Retrieval-Augmented Generation (RAG) 技術提供專業的股市問答與分析。

## 特色功能

- **本地化部署**：使用 Ollama 運行本地 LLM (Deepseek)，無需依賴雲端 API
- **向量檢索**：透過 Qdrant 向量資料庫實現語義搜索
- **技術分析**：自動計算 MA、RSI、MACD、KD、布林通道等多項技術指標
- **基本面數據**：整合財報資料（營收、EPS、獲利能力等）
- **增量同步**：智能去重，支持歷史資料的增量更新
- **互動式介面**：Rich CLI 提供友善的問答體驗
- **多語言支持**：使用多語言 Embedding 模型，支持中英文查詢

## 系統架構

```
┌─────────────┐
│  User Query │
└──────┬──────┘
       │
       ▼
┌──────────────────┐
│ Embedding Model  │ (Sentence Transformers)
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│ Qdrant Vector DB │ (Semantic Search)
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│ Context Retrieval│ (Top-K Documents)
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│  Ollama LLM      │ (Deepseek R1)
│  (RAG Generate)  │
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│  Analysis Result │
└──────────────────┘
```

## 技術棧

| 組件 | 技術 | 用途 |
|------|------|------|
| **LLM** | Ollama (Deepseek R1 1.5B) | 本地推理與回答生成 |
| **Vector DB** | Qdrant | 向量存儲與語義檢索 |
| **Embedding** | sentence-transformers | 多語言文本向量化 |
| **資料來源** | FinMind API + twstock | 台股即時與歷史資料 |
| **技術指標** | ta (Technical Analysis) | 股價技術分析計算 |
| **配置管理** | Pydantic + YAML | 類型安全的設定系統 |
| **CLI** | Rich | 終端機互動介面 |
| **語言** | Python 3.12+ | |
| **套件管理** | uv | 高速依賴安裝 |

## 快速開始

### 1. 環境需求

- **Python 3.12+**
- **Docker** (用於 Qdrant 向量資料庫)
- **Ollama** (用於本地 LLM)
- **uv** (推薦的 Python 套件管理工具)

### 2. 安裝 Ollama

```bash
# macOS
brew install ollama

# Linux
curl -fsSL https://ollama.com/install.sh | sh

# 啟動 Ollama 服務
ollama serve

# 下載 Deepseek 模型
ollama pull deepseek-r1:1.5b
```

### 3. 啟動向量資料庫

```bash
docker compose up -d
```

Qdrant 將在 `localhost:6333` 運行，資料持久化於 `./qdrant_storage/`。

### 4. 安裝專案依賴

```bash
# 安裝 uv (如果尚未安裝)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 同步依賴
uv sync
```

### 5. 配置設定

```bash
# 複製範例配置檔
cp config.yaml.example config.yaml

# 編輯配置 (可選)
# - 修改股票清單
# - 設定 FinMind API token (可選，未設定時使用免費額度)
# - 調整 RAG 檢索參數
```

### 6. 載入股市資料

```bash
# 同步最近 30 天的資料
uv run stock-sync --days 30 -v

# 同步特定股票
uv run stock-sync --stocks 2330 2454 --days 7

# 跳過基本面資料 (僅同步技術指標)
uv run stock-sync --skip-fundamentals --days 10
```

### 7. 開始問答

```bash
uv run stock-qa
```

範例問題：
- "台積電最近的技術指標表現如何？"
- "鴻海的營收狀況？"
- "聯發科的 RSI 是否過熱？"
- "分析大立光的布林通道走勢"

## 配置說明

### config.yaml 結構

```yaml
# Qdrant 向量資料庫
qdrant:
  host: localhost
  port: 6333
  collection_name: stock_analysis

# FinMind API (可選)
finmind:
  api_url: https://api.finmindtrade.com/api/v4/data
  token: ""  # 可填入 API token 以提升額度

# Ollama 本地 LLM
ollama:
  host: http://localhost:11434
  model: deepseek-r1:1.5b

# Embedding 模型
embedding:
  model: paraphrase-multilingual-MiniLM-L12-v2
  vector_size: 384

# 資料設定
data:
  default_days: 30
  stocks:
    "2330": "台積電"
    "2317": "鴻海"
    # ... 更多股票

# RAG 檢索
rag:
  top_k: 5  # 每次檢索返回的文檔數量

# 系統提示詞
system_prompt: |
  你是一個專業的台灣股市分析助手...
```

## 專案結構

```
stock-analyst/
├── src/
│   └── tw_stock_analyst/
│       ├── __init__.py
│       ├── config.py          # 配置管理 (Pydantic)
│       ├── cli.py             # 問答 CLI 入口
│       ├── data_sync.py       # 資料同步腳本
│       ├── data/              # 資料收集與處理
│       │   ├── stock_collector.py   # FinMind + twstock
│       │   ├── indicators.py        # 技術指標計算
│       │   └── fundamentals.py      # 基本面資料
│       ├── vectordb/          # 向量資料庫
│       │   ├── qdrant_client.py     # Qdrant 客戶端
│       │   └── embeddings.py        # Sentence Transformers
│       └── rag/               # RAG 檢索與生成
│           ├── retriever.py         # 向量檢索器
│           └── generator.py         # LLM 回答生成
├── config.yaml.example        # 配置範例
├── docker-compose.yml         # Qdrant 容器配置
├── pyproject.toml             # 專案依賴與元數據
├── uv.lock                    # 依賴鎖定檔
└── logs/                      # 同步日誌
```

## 核心模組說明

### 1. 資料收集 (`data/`)

- **stock_collector.py**：使用 FinMind API 與 twstock 抓取 OHLCV 資料
- **indicators.py**：計算 MA、RSI、MACD、KD、布林通道等技術指標
- **fundamentals.py**：處理財報資料（營收、淨利、EPS、本益比等）

### 2. 向量資料庫 (`vectordb/`)

- **embeddings.py**：使用 `paraphrase-multilingual-MiniLM-L12-v2` 生成 384 維向量
- **qdrant_client.py**：
  - UUID 生成策略：`SHA256(stock_id_date_datatype)[:32]` 確保去重
  - 支援 Cosine 相似度搜索
  - 支援 stock_id、data_type、date 過濾

### 3. RAG 系統 (`rag/`)

- **retriever.py**：
  - 查詢向量化
  - Top-K 語義檢索
  - 上下文格式化
- **generator.py**：
  - Ollama 客戶端封裝
  - 結合 System Prompt + Context + Query
  - 生成專業分析回答

### 4. 資料同步 (`data_sync.py`)

- 增量同步：檢查資料是否已存在，避免重複
- 批次處理：支援多檔股票並行處理
- 日誌記錄：所有操作記錄於 `logs/stock_sync.log`
- CLI 參數：
  - `--stocks`：指定股票代碼
  - `--days`：同步天數
  - `--skip-fundamentals`：跳過財報
  - `-v`：詳細輸出

## 使用範例

### CLI 問答介面

```bash
$ uv run stock-qa

┌──────────────────────────────┐
│ 台股分析 RAG 系統             │
│ 使用本地 Deepseek 模型進行   │
│ 股市問答                     │
└──────────────────────────────┘

正在初始化系統...
✓ Qdrant 已連接 (向量數量: 1500)
✓ Embedding 模型已載入
✓ Deepseek 模型已就緒

開始問答（輸入 'quit' 或 'exit' 退出）

您的問題> 台積電最近的技術指標如何？

正在檢索相關資料...
正在生成回答...

┌─────────────────────────────┐
│ 分析結果                     │
│                             │
│ 根據最近的技術指標資料...   │
│ (AI 生成的分析內容)         │
└─────────────────────────────┘

資料來源：
  1. 台積電 (2330) - 2025-11-28 (相關度: 0.892)
  2. 台積電 (2330) - 2025-11-27 (相關度: 0.854)
  ...
```

### 程式化使用

```python
from tw_stock_analyst.config import settings
from tw_stock_analyst.vectordb.qdrant_client import StockVectorDB
from tw_stock_analyst.vectordb.embeddings import EmbeddingModel
from tw_stock_analyst.rag.retriever import StockRetriever
from tw_stock_analyst.rag.generator import StockAnalysisGenerator

# 初始化
vector_db = StockVectorDB()
embedding_model = EmbeddingModel(settings.embedding.model)
retriever = StockRetriever(vector_db, embedding_model)
generator = StockAnalysisGenerator(settings.ollama.model)

# 查詢
query = "台積電的 RSI 是否過熱？"
results = retriever.retrieve(query, top_k=5)
context = retriever.format_context(results)
response = generator.generate(query, context)

print(response)
```

## 開發指南

### 新增股票

編輯 `config.yaml`：

```yaml
data:
  stocks:
    "2330": "台積電"
    "1234": "新股票"  # 新增這行
```

### 更換 LLM 模型

```yaml
ollama:
  model: llama3:8b  # 或其他 Ollama 支援的模型
```

然後執行：
```bash
ollama pull llama3:8b
```

### 調整檢索數量

```yaml
rag:
  top_k: 10  # 增加檢索文檔數量
```

### 客製化提示詞

修改 `config.yaml` 中的 `system_prompt` 欄位。

### 開發模式安裝

```bash
uv pip install -e .
```

### 執行測試

```bash
# TODO: 新增測試套件
uv run pytest tests/
```

## 常見問題

### Q1: Qdrant 無法連接

```bash
# 確認容器運行
docker ps | grep qdrant

# 重啟容器
docker compose restart
```

### Q2: Ollama 模型未找到

```bash
# 檢查已安裝模型
ollama list

# 下載缺少的模型
ollama pull deepseek-r1:1.5b
```

### Q3: FinMind API 額度不足

在 `config.yaml` 填入 FinMind API token：
```yaml
finmind:
  token: "your_api_token_here"
```

### Q4: 清空向量資料庫

```bash
# 停止容器
docker compose down

# 刪除資料
rm -rf qdrant_storage/

# 重新啟動
docker compose up -d
```

### Q5: 查看同步日誌

```bash
tail -f logs/stock_sync.log
```

## 效能優化

### 向量檢索優化

- 使用 `data_type` 過濾減少檢索範圍
- 調整 `top_k` 平衡準確度與速度

### LLM 推理優化

- 使用較小的模型 (如 `deepseek-r1:1.5b`)
- 限制 Context 長度

### 資料同步優化

- 使用 `--skip-fundamentals` 跳過非必要資料
- 減少 `--days` 參數值

## 授權

本專案採用 [MIT License](LICENSE)。

## 作者

Ken Tseng

## 貢獻

歡迎提交 Issue 或 Pull Request！

## 相關資源

- [Qdrant Documentation](https://qdrant.tech/documentation/)
- [Ollama Documentation](https://ollama.com/docs)
- [FinMind API](https://finmindtrade.com/)
- [Sentence Transformers](https://www.sbert.net/)

## Roadmap

- [ ] 新增回測功能
- [ ] 支援更多技術指標 (威廉指標、ADX 等)
- [ ] Web UI 介面
- [ ] 多檔股票比較分析
- [ ] 即時資料串流
- [ ] 單元測試覆蓋
- [ ] Docker 一鍵部署
- [ ] 英文介面支援

---

**免責聲明**：本系統僅供學習與研究用途，不構成投資建議。投資有風險，請謹慎評估。
