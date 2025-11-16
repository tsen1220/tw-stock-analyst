"""Fundamental data processing and formatting."""

from typing import Optional


class FundamentalFormatter:
    """Format fundamental data for embedding."""

    @staticmethod
    def format_as_text(
        stock_id: str,
        stock_name: str,
        fundamentals: dict,
        price: Optional[float] = None
    ) -> str:
        """
        Format fundamental data as natural language text.

        Args:
            stock_id: Stock code
            stock_name: Stock name
            fundamentals: Dictionary with fundamental metrics
            price: Current stock price (optional)

        Returns:
            Formatted text description
        """
        # Extract data
        data = {
            'revenue': fundamentals.get('revenue', 0),
            'operating_income': fundamentals.get('operating_income', 0),
            'net_income': fundamentals.get('net_income', 0),
            'eps': fundamentals.get('eps', 0),
            'date': fundamentals.get('date', 'N/A'),
        }

        # Build lines
        lines = [
            f"股票代碼：{stock_id}",
            f"公司名稱：{stock_name}",
            f"財報日期：{data['date']}",
            "",
            "基本面資訊：",
            f"營收：{data['revenue'] / 1_000_000:.2f}百萬元",
            f"營業利益：{data['operating_income'] / 1_000_000:.2f}百萬元",
            f"淨利：{data['net_income'] / 1_000_000:.2f}百萬元",
            f"每股盈餘(EPS)：{data['eps']:.2f}元",
        ]

        # Add calculated metrics
        if data['revenue'] > 0:
            if data['operating_income']:
                om = (data['operating_income'] / data['revenue']) * 100
                lines.append(f"營業利益率：{om:.2f}%")
            if data['net_income']:
                nm = (data['net_income'] / data['revenue']) * 100
                lines.append(f"淨利率：{nm:.2f}%")

        if price and data['eps'] > 0:
            pe = price / data['eps']
            lines.append(f"本益比(PE)：{pe:.2f}")

        return "\n".join(lines)

    @staticmethod
    def calculate_ratios(fundamentals: dict, price: Optional[float] = None) -> dict:
        """
        Calculate financial ratios.

        Args:
            fundamentals: Dictionary with fundamental metrics
            price: Current stock price

        Returns:
            Dictionary with calculated ratios
        """
        ratios = {}

        revenue = fundamentals.get('revenue', 0)
        operating_income = fundamentals.get('operating_income', 0)
        net_income = fundamentals.get('net_income', 0)
        eps = fundamentals.get('eps', 0)

        if revenue and revenue > 0:
            if operating_income:
                ratios['operating_margin'] = (operating_income / revenue) * 100
            if net_income:
                ratios['net_margin'] = (net_income / revenue) * 100

        if price and eps and eps > 0:
            ratios['pe_ratio'] = price / eps

        return ratios


from ..config import settings


def get_stock_name(stock_id: str) -> str:
    """
    Get stock name from code.

    Args:
        stock_id: Stock code

    Returns:
        Stock name, or stock code if not found
    """
    return settings.data.stocks.get(stock_id, stock_id)
