# Taiwan Stock Analyst

> 🚀 A Taiwan Stock Market intelligent analysis system based on RAG architecture, integrating vector database, local LLM, and technical indicators analysis

A fully locally-deployed Taiwan stock market analysis system that combines Retrieval-Augmented Generation (RAG) technology, vector database, and local large language models to provide professional, real-time, and privacy-preserving stock market analysis services.

## ✨ Key Features

- **🔒 Fully Local Deployment** - All data processing and model inference run locally, no cloud services required
- **🤖 Intelligent Q&A System** - Ask questions in natural language and get data-driven professional analysis
- **📊 Multi-dimensional Data Analysis** - Integrates technical indicators (MA, RSI, MACD, KD, etc.) and fundamental financial data
- **🔍 Semantic Retrieval** - Vector-based precise data retrieval for quick access to relevant stock information
- **⚡ Real-time Data Synchronization** - Supports incremental updates to automatically fetch latest Taiwan stock data
- **🌐 Chinese Language Optimized** - Full support for Traditional Chinese interaction and analysis
- **📈 Taiwan Stock Focused** - Pre-configured to monitor 15 Taiwan tech leading stocks (customizable)

## 🏗️ System Architecture

```
┌─────────────┐
│     User    │
└──────┬──────┘
       │ Natural Language Query
       ▼
┌─────────────────────────────────────┐
│      CLI Interface (Rich)           │
└─────────────┬───────────────────────┘
              │
       ┌──────┴──────┐
       │             │
       ▼             ▼
┌────────────┐  ┌──────────────┐
│ Data Sync  │  │   RAG Layer  │
│  FinMind   │  │  ┌─────────┐ │
│  twstock   │  │  │Retriever│ │
└─────┬──────┘  │  └────┬────┘ │
      │         │       │      │
      │         │  ┌────▼────┐ │
      │         │  │Generator│ │
      │         │  │Deepseek │ │
      │         │  └─────────┘ │
      │         └──────────────┘
      ▼
┌──────────────────────────┐
│   Sentence Transformers   │
│   (Embedding 384-dim)     │
└───────────┬───────────────┘
            │
            ▼
┌──────────────────────────┐
│   Qdrant Vector DB       │
│   (Docker Container)      │
└──────────────────────────┘
```

## 🛠️ Tech Stack

| Category | Technology |
|----------|------------|
| **Language** | Python 3.12+ |
| **Vector Database** | Qdrant |
| **Embedding Model** | Sentence Transformers (paraphrase-multilingual-MiniLM-L12-v2) |
| **Local LLM** | Ollama + Deepseek R1 (1.5B) |
| **Taiwan Stock Data** | FinMind API, twstock |
| **Technical Indicators** | ta (MA, RSI, MACD, KD, Bollinger Bands, ATR, OBV) |
| **Data Processing** | Pandas, NumPy |
| **CLI Interface** | Rich |
| **Configuration** | Pydantic, PyYAML |
| **Containerization** | Docker Compose |
| **Package Manager** | uv |

## 📋 System Requirements

### Software Requirements

- **Python**: 3.12 or higher
- **Docker**: Latest version (for running Qdrant)
- **Ollama**: Latest version (for running local LLM)
- **uv**: Python package management tool

### Hardware Recommendations

- **RAM**: Minimum 8GB (16GB+ recommended)
- **Disk Space**: At least 10GB (for models and data storage)
- **Network**: Stable internet connection (for initial model download and data synchronization)

## 🚀 Quick Start

### 1. Environment Setup

#### Install Python 3.12+

```bash
# Check Python version
python --version  # Should be >= 3.12
```

#### Install uv Package Manager

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

#### Install Docker

Download and install Docker from the [official Docker website](https://www.docker.com/get-started) for your operating system.

#### Install Ollama

Download and install from the [official Ollama website](https://ollama.ai).

### 2. Project Setup

#### Clone the Repository

```bash
git clone https://github.com/your-username/tw-stock-analyst.git
cd tw-stock-analyst
```

#### Install Python Dependencies

```bash
# Install dependencies using uv
uv pip install -e .
```

#### Configure Settings

```bash
# Copy configuration template
cp config.yaml.example config.yaml

# Edit configuration file (Optional: Set FinMind API Token for higher rate limits)
nano config.yaml
```

**Key config.yaml settings**:
```yaml
data:
  stocks:
    - 2330  # TSMC
    - 2317  # Hon Hai (Foxconn)
    - 2454  # MediaTek
    # ... Add more stock codes to monitor

finmind:
  token: "YOUR_FINMIND_TOKEN"  # Optional, register at https://finmindtrade.com
```

### 3. Start Services

#### Start Qdrant Vector Database

```bash
# Start using Docker Compose
docker compose up -d

# Verify service status
curl http://localhost:6333/health
# Should return: {"title":"qdrant - vector search engine","version":"..."}
```

#### Download and Start Ollama LLM

```bash
# Start Ollama service in one terminal
ollama serve

# In another terminal, download Deepseek model
ollama pull deepseek-r1:1.5b
```

### 4. Synchronize Stock Data

Before first use, synchronize Taiwan stock data to the vector database:

```bash
# Sync last 30 days of data for all configured stocks (including technical indicators and financials)
stock-sync --days 30 -v

# Or sync specific stocks only
stock-sync --stocks 2330 2317 2454 --days 7 -v

# Skip financial data (faster sync)
stock-sync --days 7 --skip-fundamentals -v
```

**Sync Parameter Descriptions**:
- `--days N`: Sync data from the last N days
- `--stocks CODE1 CODE2 ...`: Specify stock codes (if not specified, uses list from config.yaml)
- `--skip-fundamentals`: Skip financial statement data
- `-v` or `--verbose`: Show detailed logs

### 5. Start Using

```bash
# Launch interactive Q&A interface
stock-qa
```

**Usage Examples**:

```
Your question: How are TSMC's recent technical indicators performing?

[Analyzing...]

Answer: Based on the latest data, TSMC (2330) technical indicators show:

1. Trend Analysis:
   - 5-day MA is above 20-day MA, showing short-term upward trend
   - MACD indicator is positive, strong buy signal

2. Momentum Indicators:
   - RSI(14) is at 68, approaching overbought but still in reasonable range
   - KD indicator shows golden cross, K value > D value

3. Recommendation: Short-term bullish pattern, but watch if RSI enters overbought zone (>70)
```

```
Your question: Compare the revenue growth rates of TSMC and MediaTek

[Analyzing...]

Answer: [Revenue comparison analysis based on financial data...]
```

Type `exit` or `quit` to exit the Q&A system.

## 📁 Project Structure

```
tw-stock-analyst/
├── README.md                      # Project documentation
├── LICENSE                        # MIT License
├── pyproject.toml                 # Project configuration and dependencies
├── config.yaml.example            # Configuration template
├── docker-compose.yml             # Qdrant container configuration
├── uv.lock                        # Dependency lock file
├── qdrant_storage/                # Qdrant data persistence directory
└── src/tw_stock_analyst/          # Main source code
    ├── __init__.py
    ├── cli.py                     # Interactive CLI main program
    ├── config.py                  # Configuration loading and validation
    ├── data_sync.py               # Data synchronization script
    ├── data/                      # Data collection module
    │   ├── stock_collector.py     # Taiwan stock data fetching
    │   ├── indicators.py          # Technical indicators calculation
    │   └── fundamentals.py        # Financial data formatting
    ├── vectordb/                  # Vector database module
    │   ├── qdrant_client.py       # Qdrant client wrapper
    │   └── embeddings.py          # Embedding model
    └── rag/                       # RAG retrieval and generation module
        ├── retriever.py           # Document retriever
        └── generator.py           # LLM answer generator
```

## ⚙️ Configuration Guide

### FinMind API Token (Optional)

Without a token, FinMind API has rate limits. Recommended steps:

1. Visit [FinMind Trade](https://finmindtrade.com) and register an account
2. Obtain an API Token from your personal settings
3. Add the token to the `finmind.token` field in `config.yaml`

### Stock Monitoring List

Edit the `data.stocks` section in `config.yaml`:

```yaml
data:
  stocks:
    - 2330  # TSMC
    - 2317  # Hon Hai
    - 2454  # MediaTek
    - 2412  # Chunghwa Telecom
    - 2308  # Delta Electronics
    # ... Add more stock codes
```

### RAG Retrieval Parameters

Adjust retrieval precision:

```yaml
rag:
  top_k: 5          # Number of documents to return per retrieval (1-10)
  score_threshold: 0.5  # Minimum similarity threshold (0-1)
```

## 🔧 Advanced Usage

### Scheduled Automatic Sync

Use cron (Linux/macOS) or Task Scheduler (Windows) to set up daily automatic synchronization:

```bash
# Sync previous day's data every day at 9:00 AM
0 9 * * * /path/to/stock-sync --days 1 --skip-fundamentals
```

### Custom LLM Model

Change to another Ollama-supported model:

```yaml
ollama:
  base_url: "http://localhost:11434"
  model: "llama3:8b"  # Or other models
```

### Batch Query Mode

Create a query script:

```python
from tw_stock_analyst.rag import Retriever, Generator

retriever = Retriever()
generator = Generator()

questions = [
    "What is TSMC's RSI indicator?",
    "How is Hon Hai's year-over-year revenue growth?",
]

for q in questions:
    context = retriever.retrieve(q)
    answer = generator.generate(q, context)
    print(f"Q: {q}\nA: {answer}\n")
```

## ❓ FAQ

### Q: Qdrant connection failed

**A**: Verify that the Docker container is running:
```bash
docker ps | grep qdrant
docker compose logs qdrant
```

### Q: Ollama model loading is slow

**A**: First-time loading will download the model (approximately 1-3GB), please be patient. You can use a smaller model like `deepseek-r1:1.5b`.

### Q: FinMind API returns 429 error

**A**: Exceeded free tier limits, please:
1. Register and set up an API Token
2. Reduce the `--days` parameter
3. Sync stocks in batches

### Q: Out of memory

**A**: Try:
1. Use a smaller LLM model
2. Reduce the `rag.top_k` parameter
3. Limit the number of monitored stocks

## 🤝 Contributing

Issues and Pull Requests are welcome!

## 📄 License

This project is licensed under the [MIT License](LICENSE).

## 🙏 Acknowledgments

- [FinMind](https://finmindtrade.com) - Taiwan stock data API provider
- [Qdrant](https://qdrant.tech) - High-performance vector database
- [Ollama](https://ollama.ai) - Simplified local LLM deployment
- [Sentence Transformers](https://www.sbert.net) - Powerful embedding models

## 📧 Contact

For questions or suggestions, please open an [Issue](https://github.com/your-username/tw-stock-analyst/issues).

---

**Disclaimer**: The analysis provided by this system is for reference only and does not constitute investment advice. Investing involves risks; please make decisions carefully.
