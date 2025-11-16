"""Load Taiwan tech stock data into vector database."""

from datetime import datetime, timedelta
from rich.console import Console
from rich.progress import track

from .config import settings
from .data.stock_collector import TaiwanStockCollector
from .data.indicators import TechnicalIndicators
from .data.fundamentals import FundamentalFormatter, get_stock_name
from .vectordb.qdrant_client import StockVectorDB
from .vectordb.embeddings import EmbeddingModel


console = Console()


def load_stock_data(
    stock_ids: list[str] = None,
    days_back: int = 30,
    skip_fundamentals: bool = False
):
    """
    Load stock data into vector database.

    Args:
        stock_ids: List of stock codes (default: tech stocks)
        days_back: Number of days of historical data to load
        skip_fundamentals: Skip fundamental data collection
    """
    console.print("[bold cyan]台股資料載入程序[/bold cyan]\n")

    # Initialize components
    console.print("[yellow]初始化組件...[/yellow]")

    collector = TaiwanStockCollector(settings.finmind.token)
    formatter = FundamentalFormatter()
    tech_indicators = TechnicalIndicators()

    vector_db = StockVectorDB()  # Uses config.yaml settings

    embedding_model = EmbeddingModel(settings.embedding.model)

    # Create collection
    vector_size = embedding_model.get_dimension()
    vector_db.create_collection(vector_size)

    # Get stock list
    if stock_ids is None:
        stock_ids = settings.data.stock_codes

    console.print(f"[green]將載入 {len(stock_ids)} 檔股票的資料[/green]\n")

    # Date range
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")

    total_inserted = 0

    # Process each stock
    for stock_id in track(stock_ids, description="處理股票資料"):
        stock_name = get_stock_name(stock_id)
        console.print(f"\n處理 {stock_name} ({stock_id})")

        try:
            # Get price data
            df = collector.get_stock_price(stock_id, start_date, end_date)

            if df.empty:
                console.print(f"  [yellow]無價格資料[/yellow]")
                continue

            # Add technical indicators
            df = tech_indicators.add_all_indicators(df)

            # Insert daily technical data (last 7 days)
            recent_df = df.tail(7)

            for _, row in recent_df.iterrows():
                try:
                    indicators = {
                        'date': row['Date'],
                        'close': float(row.get('Close', 0)),
                        'volume': int(row.get('Volume', 0)),
                        'price_change': float(row.get('Price_Change', 0)),
                        'ma5': float(row.get('MA5', 0)),
                        'ma20': float(row.get('MA20', 0)),
                        'ma60': float(row.get('MA60', 0)),
                        'rsi': float(row.get('RSI', 0)),
                        'macd': float(row.get('MACD', 0)),
                        'macd_signal': float(row.get('MACD_Signal', 0)),
                        'k': float(row.get('K', 0)),
                        'd': float(row.get('D', 0)),
                        'bb_high': float(row.get('BB_High', 0)),
                        'bb_low': float(row.get('BB_Low', 0)),
                    }

                    # Format as text
                    text = tech_indicators.format_as_text(
                        stock_id, stock_name, indicators
                    )

                    # Generate embedding
                    vector = embedding_model.encode(text).tolist()

                    # Insert into vector DB
                    vector_db.insert_stock_data(
                        text=text,
                        vector=vector,
                        stock_id=stock_id,
                        stock_name=stock_name,
                        date=row['Date'],
                        data_type="technical",
                        metadata=indicators
                    )

                    total_inserted += 1

                except Exception as e:
                    console.print(f"  [red]錯誤（技術指標）: {e}[/red]")
                    continue

            # Get and insert fundamental data
            if not skip_fundamentals:
                try:
                    fundamentals = collector.get_fundamentals(stock_id)

                    if fundamentals:
                        latest_price = float(df.iloc[-1]['Close'])

                        fund_text = formatter.format_as_text(
                            stock_id, stock_name, fundamentals, latest_price
                        )

                        fund_vector = embedding_model.encode(fund_text).tolist()

                        vector_db.insert_stock_data(
                            text=fund_text,
                            vector=fund_vector,
                            stock_id=stock_id,
                            stock_name=stock_name,
                            date=fundamentals.get('date', ''),
                            data_type="fundamental",
                            metadata=fundamentals
                        )

                        total_inserted += 1

                except Exception as e:
                    console.print(f"  [yellow]無法取得財報資料: {e}[/yellow]")

        except Exception as e:
            console.print(f"  [red]錯誤: {e}[/red]")
            continue

    # Summary
    console.print(f"\n[bold green]完成！[/bold green]")
    console.print(f"總共插入 {total_inserted} 筆向量資料")

    info = vector_db.get_collection_info()
    console.print(f"向量資料庫總數量: {info.get('vectors_count', 0)}")


def main():
    """CLI entry point for data loader."""
    import argparse

    parser = argparse.ArgumentParser(description="載入台股資料到向量資料庫")
    parser.add_argument(
        "--stocks",
        nargs="+",
        help="股票代碼列表（例如：2330 2454）"
    )
    parser.add_argument(
        "--days",
        type=int,
        default=30,
        help="載入幾天的歷史資料（預設：30）"
    )
    parser.add_argument(
        "--skip-fundamentals",
        action="store_true",
        help="跳過財報資料"
    )

    args = parser.parse_args()

    load_stock_data(
        stock_ids=args.stocks,
        days_back=args.days,
        skip_fundamentals=args.skip_fundamentals
    )


if __name__ == "__main__":
    main()
