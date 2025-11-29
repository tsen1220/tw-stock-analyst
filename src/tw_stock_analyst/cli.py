"""Command-line interface for stock analysis Q&A."""

import sys
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.markdown import Markdown

from .config import settings
from .vectordb.qdrant_client import StockVectorDB
from .vectordb.embeddings import EmbeddingModel
from .rag.retriever import StockRetriever
from .rag.generator import StockAnalysisGenerator


console = Console()


def main():
    """Main CLI entry point."""
    console.print(Panel.fit(
        "[bold cyan]台股分析 RAG 系統[/bold cyan]\n"
        f"使用本地 {settings.ollama.model} 模型進行股市問答",
        border_style="cyan"
    ))

    # Initialize components
    try:
        console.print("\n[yellow]正在初始化系統...[/yellow]")

        # Vector DB (uses config.yaml settings)
        vector_db = StockVectorDB()

        # Check collection
        info = vector_db.get_collection_info()
        if "error" in info:
            console.print(
                f"[red]錯誤：無法連接到 Qdrant。請確認 Docker 容器已啟動。[/red]\n"
                f"提示：執行 `docker compose up -d`"
            )
            return

        console.print(f"[green]✓[/green] Qdrant 已連接 (向量數量: {info.get('vectors_count', 0)})")

        # Embedding model
        embedding_model = EmbeddingModel(settings.embedding.model)
        console.print(f"[green]✓[/green] Embedding 模型已載入")

        # Generator
        generator = StockAnalysisGenerator(
            model_name=settings.ollama.model,
            ollama_host=settings.ollama.host
        )

        # Check if model is available
        if not generator.check_model_available():
            console.print(
                f"[yellow]警告：Ollama 模型 '{settings.ollama.model}' 未找到[/yellow]\n"
                f"請執行：ollama pull {settings.ollama.model}"
            )
            response = Prompt.ask("是否繼續", choices=["y", "n"], default="n")
            if response == "n":
                return

        console.print(f"[green]✓[/green] {settings.ollama.model} 模型已就緒\n")

        # Retriever
        retriever = StockRetriever(vector_db, embedding_model)

        # Interactive Q&A loop
        console.print("[bold]開始問答（輸入 'quit' 或 'exit' 退出）[/bold]\n")

        while True:
            try:
                query = Prompt.ask("\n[bold cyan]您的問題[/bold cyan]")

                if query.lower() in ['quit', 'exit', 'q']:
                    console.print("[yellow]再見！[/yellow]")
                    break

                if not query.strip():
                    continue

                # Retrieve relevant documents
                console.print("[dim]正在檢索相關資料...[/dim]")
                results = retriever.retrieve(query, top_k=settings.rag.top_k)

                if not results:
                    console.print("[yellow]找不到相關的股市資料。請先載入資料。[/yellow]")
                    continue

                # Format context
                context = retriever.format_context(results)

                # Generate response
                console.print("[dim]正在生成回答...[/dim]\n")
                response = generator.generate(
                    query, context, system_prompt=settings.system_prompt
                )

                # Display response
                console.print(Panel(
                    Markdown(response),
                    title="[bold green]分析結果[/bold green]",
                    border_style="green"
                ))

                # Show sources
                console.print("\n[dim]資料來源：[/dim]")
                for i, result in enumerate(results, 1):
                    console.print(
                        f"  {i}. {result['stock_name']} ({result['stock_id']}) "
                        f"- {result['date']} "
                        f"[dim](相關度: {result['score']:.3f})[/dim]"
                    )

            except KeyboardInterrupt:
                console.print("\n[yellow]再見！[/yellow]")
                break
            except Exception as e:
                console.print(f"[red]錯誤：{e}[/red]")
                continue

    except Exception as e:
        console.print(f"[red]系統初始化失敗：{e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
