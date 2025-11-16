# 台股分析 RAG 系統

使用向量資料庫 (Qdrant) 和本地 Deepseek 模型，打造台灣股市智能問答系統。

## 功能特色

- 台股科技股資料收集（FinMind + twstock）
- 技術指標計算（MA、RSI、MACD、KD 等）
- 財報基本面資料整合
- 向量化搜尋（使用 Qdrant）
- 本地 LLM 推理（Deepseek via Ollama）
- RAG (Retrieval-Augmented Generation) 問答

## 系統需求

- Python 3.12+
- Docker (for Qdrant)
- Ollama (for Deepseek)
- UV (Python package manager)

## 快速開始

### 1. 安裝 Ollama 並下載 Deepseek 模型

```bash
# 安裝 Ollama (macOS)
brew install ollama

# 啟動 Ollama 服務
ollama serve

# 下載 Deepseek 模型
ollama pull deepseek-r1:1.5b
```

### 2. 啟動 Qdrant 向量資料庫

```bash
# 使用 Docker Compose 啟動
docker compose up -d

# 檢查狀態
docker ps
```

### 3. 安裝專案依賴

```bash
# 使用 UV 安裝
uv sync
```

### 4. 配置設定（可選）

系統已包含預設配置 `config.yaml`，可直接使用。如需自訂：

```bash
# 編輯 config.yaml 檔案
vim config.yaml

# 主要設定項目：
# - qdrant.host/port: 向量資料庫位置
# - finmind.token: FinMind API token（可選，留空使用免費額度）
# - ollama.model: 使用的 LLM 模型
# - data.stocks: 要追蹤的股票清單（含名稱）
```

### 5. 載入股票資料

```bash
# 載入台股科技股資料（預設最近 30 天）
uv run stock-load

# 指定股票代碼
uv run stock-load --stocks 2330 2454 2317

# 指定天數
uv run stock-load --days 60

# 跳過財報資料
uv run stock-load --skip-fundamentals
```

### 6. 定期自動更新（選用）

使用 `stock-sync` 命令配置 cronjob 定期更新資料：

```bash
# 增量同步（只抓最近 2 天資料，自動去重）
uv run stock-sync

# 顯示詳細輸出
uv run stock-sync -v

# 設定 cronjob（每天收盤後更新）
# 編輯 crontab：crontab -e
# 加入：30 14 * * 1-5 cd /path/to/stock-analyst && uv run stock-sync
```

詳細的 cronjob 設置請參考 [CRONJOB_SETUP.md](CRONJOB_SETUP.md)

### 7. 啟動問答系統

```bash
uv run stock-qa
```

## 使用範例

啟動後，可以詢問如下問題：

```
您的問題> 台積電最近的技術面表現如何？

您的問題> 聯發科和台積電的 RSI 指標比較

您的問題> 哪些科技股目前處於超買狀態？

您的問題> 分析鴻海最近的股價走勢
```

## 專案結構

```
stock-analyst/
├── src/stock_analyst/
│   ├── data/              # 資料收集與處理
│   │   ├── stock_collector.py
│   │   ├── indicators.py
│   │   └── fundamentals.py
│   ├── vectordb/          # 向量資料庫
│   │   ├── qdrant_client.py
│   │   └── embeddings.py
│   ├── rag/               # RAG 系統
│   │   ├── retriever.py
│   │   └── generator.py
│   ├── config.py          # 配置管理
│   ├── cli.py             # 問答介面
│   └── data_loader.py     # 資料載入
├── config.yaml            # YAML 配置檔
├── docker-compose.yml     # Qdrant 部署
├── pyproject.toml         # UV 專案配置
└── README.md
```

## 配置說明

`config.yaml` 結構：

```yaml
qdrant:
  host: localhost          # Qdrant 主機
  port: 6333              # Qdrant 端口
  collection_name: stock_analysis

finmind:
  api_url: https://api.finmindtrade.com/api/v4/data
  token: ""               # FinMind API token（可選）

ollama:
  host: http://localhost:11434
  model: deepseek-r1:1.5b

embedding:
  model: paraphrase-multilingual-MiniLM-L12-v2
  vector_size: 384

data:
  default_days: 30        # 預設載入天數
  stocks:                 # 股票清單（字典格式）
    "2330": "台積電"
    "2454": "聯發科"
    # ... 更多股票

rag:
  top_k: 5                # 檢索文檔數量

system_prompt: |          # 自訂系統提示詞
  你是專業的台股分析助手...
```

## 技術棧

- **資料來源**: FinMind API, twstock
- **技術分析**: ta (Technical Analysis Library)
- **向量資料庫**: Qdrant
- **Embedding 模型**: Sentence Transformers (multilingual-MiniLM)
- **LLM**: Deepseek (via Ollama)
- **開發工具**: UV, Python 3.12, Docker
- **配置管理**: YAML

## 自訂追蹤股票

直接編輯 `config.yaml` 中的 `data.stocks` 即可：

```yaml
data:
  stocks:
    "2330": "台積電"
    "2454": "聯發科"
    "YOUR_CODE": "公司名稱"  # 加入你想追蹤的股票
```

重新載入資料後即可分析新股票：
```bash
uv run stock-load
```

## 注意事項

1. 本系統僅供學習與研究用途
2. 投資決策請參考專業意見，不應僅依賴本系統
3. 歷史資料不代表未來表現
4. FinMind API 有請求限制，建議註冊取得 token

## License

MIT
