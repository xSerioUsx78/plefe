import logging

from binance.spot import Spot


logger = logging.getLogger(__name__)


class BinanceClient:
    def __init__(self):
        self.client = Spot()

    def get_exchange_info(self, key: str = None):
        """Symbol Data"""

        data = []

        try:
            exchange_info = self.client.exchange_info()
        except Exception as e:
            logger.error(e, exc_info=1)
            return data

        if not exchange_info:
            return data

        if key:
            return exchange_info[key]

        return exchange_info

    def get_klines_data(self, symbol: str, frame: str, **kwargs) -> list[dict]:
        """Chart Data"""

        try:
            klines = self.client.klines(symbol, frame, **kwargs)
        except Exception as e:
            logger.error(e, exc_info=1)
            return data

        if not klines:
            return data

        data = []
        for kline in klines:
            data.append({
                "open_time": kline[0],
                "open_price": kline[1],
                "high_price": kline[2],
                "low_price": kline[3],
                "close_price": kline[4],
                "volume": kline[5],
                "close_time": kline[6],
                "quote_asset_volume": kline[7],
                "number_of_trades": kline[8],
                "taker_by_base_asset_volume": kline[9],
                "taker_by_quote_asset_volume": kline[10]
            })

        return data
