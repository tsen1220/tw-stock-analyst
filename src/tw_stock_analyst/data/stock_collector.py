"""Taiwan stock data collection using FinMind and twstock."""

from datetime import datetime, timedelta
from typing import Optional
import pandas as pd
import requests
import twstock

from ..config import settings


class TaiwanStockCollector:
    """Collect Taiwan stock market data."""

    def __init__(self, finmind_token: str = ""):
        """Initialize collector with optional FinMind token."""
        self.finmind_token = finmind_token
        self.api_url = settings.finmind.api_url

    def get_stock_price(
        self,
        stock_id: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> pd.DataFrame:
        """
        Get historical stock price data.

        Args:
            stock_id: Stock code (e.g., "2330" for TSMC)
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format

        Returns:
            DataFrame with OHLCV data
        """
        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")
        if not start_date:
            start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")

        try:
            # Try FinMind API first (more comprehensive data)
            params = {
                "dataset": "TaiwanStockPrice",
                "data_id": stock_id,
                "start_date": start_date,
                "end_date": end_date,
            }
            if self.finmind_token:
                params["token"] = self.finmind_token

            response = requests.get(self.api_url, params=params)
            data = response.json()

            if data.get("status") == 200 and data.get("data"):
                df = pd.DataFrame(data["data"])
                df = df.rename(columns={
                    'date': 'Date',
                    'open': 'Open',
                    'max': 'High',
                    'min': 'Low',
                    'close': 'Close',
                    'Trading_Volume': 'Volume'
                })
                return df[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']]

        except Exception as e:
            print(f"FinMind API failed: {e}, falling back to twstock")

        # Fallback to twstock
        stock = twstock.Stock(stock_id)
        data = stock.fetch_from(
            int(start_date[:4]),
            int(start_date[5:7])
        )

        df = pd.DataFrame([{
            'Date': d.date.strftime('%Y-%m-%d'),
            'Open': d.open,
            'High': d.high,
            'Low': d.low,
            'Close': d.close,
            'Volume': d.capacity
        } for d in data])

        return df

    def get_fundamentals(self, stock_id: str, num_quarters: int = None) -> list[dict]:
        """
        Get fundamental data for a stock (multiple quarters).

        Args:
            stock_id: Stock code
            num_quarters: Number of recent quarters to return (default: from config)

        Returns:
            List of dictionaries with fundamental metrics, sorted by date (newest first)
        """
        # Use config value if not specified
        if num_quarters is None:
            num_quarters = settings.data.num_quarters

        try:
            # Calculate years back based on num_quarters (4 quarters = 1 year, with buffer)
            # Formula: at least 2 years, add 1 year for every 4 quarters beyond that
            years_back = max(2, (num_quarters // 4) + 1)
            start_date = (datetime.now() - timedelta(days=365*years_back)).strftime("%Y-%m-%d")
            params = {
                "dataset": "TaiwanStockFinancialStatements",
                "data_id": stock_id,
                "start_date": start_date,
            }
            if self.finmind_token:
                params["token"] = self.finmind_token

            response = requests.get(self.api_url, params=params)
            data = response.json()

            if data.get("status") == 200 and data.get("data"):
                df = pd.DataFrame(data["data"])
                if not df.empty:
                    # Sort by date descending (newest first) to ensure we get the latest data
                    df = df.sort_values('date', ascending=False)

                    # Take only the most recent N quarters
                    recent_df = df.head(num_quarters)

                    # Convert to list of dicts
                    fundamentals = []
                    for _, row in recent_df.iterrows():
                        fundamentals.append({
                            'stock_id': stock_id,
                            'date': row.get('date', ''),
                            'revenue': row.get('revenue', 0),
                            'operating_income': row.get('OperatingIncome', 0),
                            'net_income': row.get('NetIncome', 0),
                            'eps': row.get('eps', 0),
                        })

                    return fundamentals

        except Exception as e:
            print(f"Failed to get fundamentals: {e}")

        return []

    def get_tech_stocks(self) -> list[str]:
        """
        Get list of Taiwan tech stock codes from config.

        Returns:
            List of stock codes
        """
        return settings.data.stock_codes
