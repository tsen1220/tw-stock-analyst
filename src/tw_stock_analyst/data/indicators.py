"""Technical indicators calculation using TA library."""

import pandas as pd
import ta


class TechnicalIndicators:
    """Calculate technical indicators for stock data."""

    @staticmethod
    def add_all_indicators(df: pd.DataFrame) -> pd.DataFrame:
        """
        Add all technical indicators to dataframe.

        Args:
            df: DataFrame with OHLCV data

        Returns:
            DataFrame with added indicator columns
        """
        df = df.copy()

        # Ensure numeric types
        for col in ['Open', 'High', 'Low', 'Close', 'Volume']:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        # Moving Averages
        df['MA5'] = ta.trend.sma_indicator(df['Close'], window=5)
        df['MA10'] = ta.trend.sma_indicator(df['Close'], window=10)
        df['MA20'] = ta.trend.sma_indicator(df['Close'], window=20)
        df['MA60'] = ta.trend.sma_indicator(df['Close'], window=60)

        # Exponential Moving Averages
        df['EMA12'] = ta.trend.ema_indicator(df['Close'], window=12)
        df['EMA26'] = ta.trend.ema_indicator(df['Close'], window=26)

        # RSI (Relative Strength Index)
        df['RSI'] = ta.momentum.rsi(df['Close'], window=14)

        # MACD
        macd = ta.trend.MACD(df['Close'])
        df['MACD'] = macd.macd()
        df['MACD_Signal'] = macd.macd_signal()
        df['MACD_Diff'] = macd.macd_diff()

        # Bollinger Bands
        bollinger = ta.volatility.BollingerBands(df['Close'])
        df['BB_High'] = bollinger.bollinger_hband()
        df['BB_Mid'] = bollinger.bollinger_mavg()
        df['BB_Low'] = bollinger.bollinger_lband()

        # KD (Stochastic Oscillator)
        stoch = ta.momentum.StochasticOscillator(
            df['High'], df['Low'], df['Close']
        )
        df['K'] = stoch.stoch()
        df['D'] = stoch.stoch_signal()

        # ATR (Average True Range)
        df['ATR'] = ta.volatility.average_true_range(
            df['High'], df['Low'], df['Close']
        )

        # OBV (On Balance Volume)
        df['OBV'] = ta.volume.on_balance_volume(df['Close'], df['Volume'])

        # Price change
        df['Price_Change'] = df['Close'].pct_change() * 100

        return df

    @staticmethod
    def get_latest_indicators(df: pd.DataFrame) -> dict:
        """
        Get latest technical indicator values.

        Args:
            df: DataFrame with calculated indicators

        Returns:
            Dictionary of latest indicator values
        """
        if df.empty:
            return {}

        latest = df.iloc[-1]
        return {
            'date': latest.get('Date', ''),
            'close': float(latest.get('Close', 0)),
            'volume': int(latest.get('Volume', 0)),
            'price_change': float(latest.get('Price_Change', 0)),
            'ma5': float(latest.get('MA5', 0)),
            'ma20': float(latest.get('MA20', 0)),
            'ma60': float(latest.get('MA60', 0)),
            'rsi': float(latest.get('RSI', 0)),
            'macd': float(latest.get('MACD', 0)),
            'macd_signal': float(latest.get('MACD_Signal', 0)),
            'k': float(latest.get('K', 0)),
            'd': float(latest.get('D', 0)),
            'bb_high': float(latest.get('BB_High', 0)),
            'bb_low': float(latest.get('BB_Low', 0)),
        }

    @staticmethod
    def format_as_text(stock_id: str, stock_name: str, indicators: dict) -> str:
        """
        Format indicators as natural language text for embedding.

        Args:
            stock_id: Stock code
            stock_name: Stock name
            indicators: Dictionary of indicator values

        Returns:
            Formatted text description
        """
        lines = [
            f"股票代碼：{stock_id}",
            f"公司名稱：{stock_name}",
            f"日期：{indicators.get('date', 'N/A')}",
            f"收盤價：{indicators.get('close', 0):.2f}元",
            f"漲跌幅：{indicators.get('price_change', 0):+.2f}%",
            f"成交量：{indicators.get('volume', 0):,}張",
            "",
            "技術指標：",
            f"- MA5：{indicators.get('ma5', 0):.2f}",
            f"- MA20：{indicators.get('ma20', 0):.2f}",
            f"- MA60：{indicators.get('ma60', 0):.2f}",
            f"- RSI(14)：{indicators.get('rsi', 0):.2f}",
            f"- MACD：{indicators.get('macd', 0):.4f}",
            f"- MACD訊號：{indicators.get('macd_signal', 0):.4f}",
            f"- KD指標：K={indicators.get('k', 0):.2f}, D={indicators.get('d', 0):.2f}",
            f"- 布林通道：上軌{indicators.get('bb_high', 0):.2f}, 下軌{indicators.get('bb_low', 0):.2f}",
        ]

        return "\n".join(lines)
