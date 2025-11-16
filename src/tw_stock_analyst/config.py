"""Configuration management using YAML."""

from pathlib import Path
from typing import Optional
import yaml
from pydantic import BaseModel, Field


class QdrantConfig(BaseModel):
    """Qdrant configuration."""
    host: str = "localhost"
    port: int = 6333
    collection_name: str = "stock_analysis"


class FinMindConfig(BaseModel):
    """FinMind API configuration."""
    api_url: str = "https://api.finmindtrade.com/api/v4/data"
    token: str = ""


class OllamaConfig(BaseModel):
    """Ollama configuration."""
    host: str = "http://localhost:11434"
    model: str = "deepseek-r1:1.5b"


class EmbeddingConfig(BaseModel):
    """Embedding model configuration."""
    model: str = "paraphrase-multilingual-MiniLM-L12-v2"
    vector_size: int = 384


class DataConfig(BaseModel):
    """Data loading configuration."""
    default_days: int = 30
    stocks: dict[str, str] = {
        "2330": "台積電",
        "2317": "鴻海",
        "2454": "聯發科",
        "2303": "聯電",
        "3711": "日月光投控",
        "2382": "廣達",
        "2308": "台達電",
        "2357": "華碩",
        "2379": "瑞昱",
        "3034": "聯詠",
        "2327": "國巨",
        "2408": "南亞科",
        "3008": "大立光",
        "2301": "光寶科",
        "2337": "旺宏",
    }

    @property
    def stock_codes(self) -> list[str]:
        """Get list of stock codes."""
        return list(self.stocks.keys())


class RAGConfig(BaseModel):
    """RAG configuration."""
    top_k: int = 5


class Settings(BaseModel):
    """Application settings."""
    qdrant: QdrantConfig = Field(default_factory=QdrantConfig)
    finmind: FinMindConfig = Field(default_factory=FinMindConfig)
    ollama: OllamaConfig = Field(default_factory=OllamaConfig)
    embedding: EmbeddingConfig = Field(default_factory=EmbeddingConfig)
    data: DataConfig = Field(default_factory=DataConfig)
    rag: RAGConfig = Field(default_factory=RAGConfig)
    system_prompt: str = """你是一個專業的台灣股市分析助手。
請根據提供的歷史資料和技術指標，提供專業、客觀的分析和建議。
注意：
1. 僅根據提供的資料進行分析
2. 說明你的分析依據
3. 避免過度承諾或保證
4. 提醒投資風險"""

    @classmethod
    def from_yaml(cls, config_path: Optional[Path] = None) -> "Settings":
        """Load settings from YAML file."""
        if config_path is None:
            config_path = Path("config.yaml")

        if not config_path.exists():
            # Return default settings if no config file
            return cls()

        with open(config_path, "r", encoding="utf-8") as f:
            config_data = yaml.safe_load(f)

        return cls(**config_data)


# Load settings from config.yaml (or use defaults)
settings = Settings.from_yaml()
