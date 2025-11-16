"""Incremental stock data sync for cronjob scheduling."""

import logging
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from .config import settings
from .data.stock_collector import TaiwanStockCollector
from .data.indicators import TechnicalIndicators
from .data.fundamentals import FundamentalFormatter, get_stock_name
from .vectordb.qdrant_client import StockVectorDB
from .vectordb.embeddings import EmbeddingModel


def setup_logger(log_file: Optional[str] = None, verbose: bool = False) -> logging.Logger:
    """
    Setup logger for sync operation.

    Args:
        log_file: Path to log file (default: logs/stock_sync.log)
        verbose: If True, also log to console

    Returns:
        Configured logger
    """
    logger = logging.getLogger("stock_sync")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    # File handler
    if log_file is None:
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        log_file = log_dir / "stock_sync.log"

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Console handler (only if verbose)
    if verbose:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger


def check_data_exists(
    vector_db: StockVectorDB,
    stock_id: str,
    date: str,
    data_type: str
) -> bool:
    """
    Check if data already exists in vector database.

    Args:
        vector_db: Vector database client
        stock_id: Stock code
        date: Date string (YYYY-MM-DD)
        data_type: Data type (technical/fundamental)

    Returns:
        True if data exists, False otherwise
    """
    try:
        # Search for existing data
        results = vector_db.search(
            query_vector=[0.0] * vector_db.vector_size,  # Dummy vector
            limit=1,
            stock_id=stock_id,
            data_type=data_type,
            filter_conditions={
                "must": [
                    {"key": "date", "match": {"value": date}}
                ]
            }
        )
        return len(results) > 0
    except Exception:
        return False


def sync_stock_data(
    stock_ids: Optional[list[str]] = None,
    days_back: int = 2,
    skip_fundamentals: bool = False,
    logger: Optional[logging.Logger] = None
) -> tuple[int, int]:
    """
    Incrementally sync stock data to vector database.

    Args:
        stock_ids: List of stock codes (default: from config)
        days_back: Number of days to sync (default: 2)
        skip_fundamentals: Skip fundamental data
        logger: Logger instance

    Returns:
        Tuple of (inserted_count, skipped_count)
    """
    if logger is None:
        logger = setup_logger()

    logger.info("=" * 50)
    logger.info("Stock data sync started")
    logger.info(f"Days back: {days_back}")
    logger.info(f"Skip fundamentals: {skip_fundamentals}")

    # Initialize components
    try:
        collector = TaiwanStockCollector(settings.finmind.token)
        formatter = FundamentalFormatter()
        tech_indicators = TechnicalIndicators()

        vector_db = StockVectorDB()  # Uses config.yaml settings

        embedding_model = EmbeddingModel(settings.embedding.model)

        # Ensure collection exists
        vector_size = embedding_model.get_dimension()
        vector_db.create_collection(vector_size)

    except Exception as e:
        logger.error(f"Failed to initialize components: {e}")
        return 0, 0

    # Get stock list
    if stock_ids is None:
        stock_ids = settings.data.stock_codes

    logger.info(f"Processing {len(stock_ids)} stocks")

    # Date range
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")

    logger.info(f"Date range: {start_date} to {end_date}")

    total_inserted = 0
    total_skipped = 0

    # Process each stock
    for stock_id in stock_ids:
        stock_name = get_stock_name(stock_id)
        logger.info(f"Processing {stock_name} ({stock_id})")

        try:
            # Get price data
            df = collector.get_stock_price(stock_id, start_date, end_date)

            if df.empty:
                logger.warning(f"  No price data for {stock_id}")
                continue

            # Add technical indicators
            df = tech_indicators.add_all_indicators(df)

            # Process each day
            for _, row in df.iterrows():
                date = row['Date']

                # Check if technical data already exists
                if check_data_exists(vector_db, stock_id, date, "technical"):
                    logger.debug(f"  Skipping {stock_id} {date} (already exists)")
                    total_skipped += 1
                    continue

                try:
                    indicators = {
                        'date': date,
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
                        date=date,
                        data_type="technical",
                        metadata=indicators
                    )

                    total_inserted += 1
                    logger.info(f"  Inserted technical data: {stock_id} {date}")

                except Exception as e:
                    logger.error(f"  Failed to insert technical data {stock_id} {date}: {e}")
                    continue

            # Sync fundamental data (only once per stock, not daily)
            if not skip_fundamentals:
                try:
                    fundamentals = collector.get_fundamentals(stock_id)

                    if fundamentals:
                        fund_date = fundamentals.get('date', '')

                        # Check if fundamental data already exists
                        if not check_data_exists(vector_db, stock_id, fund_date, "fundamental"):
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
                                date=fund_date,
                                data_type="fundamental",
                                metadata=fundamentals
                            )

                            total_inserted += 1
                            logger.info(f"  Inserted fundamental data: {stock_id} {fund_date}")
                        else:
                            logger.debug(f"  Skipping fundamental {stock_id} {fund_date} (already exists)")
                            total_skipped += 1

                except Exception as e:
                    logger.warning(f"  Failed to get fundamentals for {stock_id}: {e}")

        except Exception as e:
            logger.error(f"  Failed to process {stock_id}: {e}")
            continue

    # Summary
    logger.info("=" * 50)
    logger.info(f"Sync completed: {total_inserted} inserted, {total_skipped} skipped")

    try:
        info = vector_db.get_collection_info()
        logger.info(f"Total vectors in database: {info.get('vectors_count', 0)}")
    except Exception as e:
        logger.warning(f"Failed to get collection info: {e}")

    return total_inserted, total_skipped


def main():
    """CLI entry point for stock sync."""
    import argparse

    parser = argparse.ArgumentParser(
        description="增量同步台股資料（適合 cronjob）"
    )
    parser.add_argument(
        "--stocks",
        nargs="+",
        help="股票代碼列表（預設：使用 config 中的清單）"
    )
    parser.add_argument(
        "--days",
        type=int,
        default=2,
        help="同步最近幾天的資料（預設：2）"
    )
    parser.add_argument(
        "--skip-fundamentals",
        action="store_true",
        help="跳過財報資料"
    )
    parser.add_argument(
        "--log-file",
        type=str,
        help="日誌檔案路徑（預設：logs/stock_sync.log）"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="顯示詳細輸出到終端"
    )

    args = parser.parse_args()

    # Setup logger
    logger = setup_logger(log_file=args.log_file, verbose=args.verbose)

    try:
        inserted, skipped = sync_stock_data(
            stock_ids=args.stocks,
            days_back=args.days,
            skip_fundamentals=args.skip_fundamentals,
            logger=logger
        )

        if args.verbose:
            print(f"✓ Sync completed: {inserted} inserted, {skipped} skipped")

        # Exit code 0 for success
        sys.exit(0)

    except Exception as e:
        logger.error(f"Sync failed: {e}", exc_info=True)

        if args.verbose:
            print(f"✗ Sync failed: {e}")

        # Exit code 1 for failure
        sys.exit(1)


if __name__ == "__main__":
    main()
