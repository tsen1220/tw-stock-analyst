"""RAG generator using local Deepseek model via Ollama."""

import ollama
from typing import Optional


class StockAnalysisGenerator:
    """Generate stock analysis using Deepseek model."""

    def __init__(
        self,
        model_name: str = "deepseek-r1:1.5b",
        ollama_host: Optional[str] = None
    ):
        """
        Initialize generator.

        Args:
            model_name: Ollama model name
            ollama_host: Ollama server URL (optional)
        """
        self.model_name = model_name
        if ollama_host:
            ollama.client = ollama.Client(host=ollama_host)

    def generate(
        self,
        query: str,
        context: str,
        system_prompt: Optional[str] = None
    ) -> str:
        """
        Generate response using RAG.

        Args:
            query: User query
            context: Retrieved context from vector DB
            system_prompt: System prompt (optional)

        Returns:
            Generated response
        """
        if system_prompt is None:
            system_prompt = """你是一個專業的台灣股市分析助手。
請根據提供的歷史資料和技術指標，提供專業、客觀的分析和建議。
注意：
1. 僅根據提供的資料進行分析
2. 說明你的分析依據
3. 避免過度承諾或保證
4. 提醒投資風險"""

        # Construct prompt
        full_prompt = f"""參考資料：
{context}

用戶問題：
{query}

請基於以上資料回答問題。"""

        try:
            response = ollama.chat(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": full_prompt}
                ]
            )

            return response['message']['content']

        except Exception as e:
            return f"生成回答時發生錯誤：{str(e)}\n\n請確認 Ollama 已啟動且已下載 {self.model_name} 模型。"

    def check_model_available(self) -> bool:
        """Check if the model is available in Ollama."""
        try:
            models = ollama.list()
            model_names = [m['name'] for m in models.get('models', [])]
            return any(self.model_name in name for name in model_names)
        except Exception as e:
            print(f"Error checking model availability: {e}")
            return False
