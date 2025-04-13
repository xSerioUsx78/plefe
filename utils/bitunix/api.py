import logging

import requests


logger = logging.getLogger(__name__)


class BitunixClient:
    base_url = "https://openapi.bitunix.com"

    def __init__(
        self,
        access_key: str = None,
        secret_key: str = None,
        api_req_timeout: int = 120
    ) -> None:
        self.access_key = access_key
        self.secret_key = secret_key
        self.api_req_timeout = api_req_timeout

    def _get_api_url(self, path: str) -> str:
        return f"{self.base_url}/api/spot/v1/{path}"

    def _get_default_req_params(self):
        return {
            "timeout": self.api_req_timeout,
            "json": True
        }

    def get_default_symbols(self) -> list[str]:
        data = []

        url = self._get_api_url("common/coin_pair/list")

        try:
            res = requests.get(
                url,
                **self._get_default_req_params()
            )
        except Exception as e:
            logger.error(e, exc_info=1)
            return data

        if not res.ok:
            logger.error(
                f"Response status not ok {res.status_code}", exc_info=1
            )
            if res.status_code < 500:
                logger.error(
                    f"error: {res.json()}", exc_info=1
                )
            return data

        json = res.json()

        if not json.get("success"):
            return data

        data = json["data"]

        return data

    def get_klines(
        self,
        symbol: str,
        interval: str,
        start_time: int = None,
        end_time: int = None,
        limit: int = 200
    ) -> list[list]:
        assert limit < 500, "Maximum length for limit is 500."

        data = []

        url = self._get_api_url("market/kline/history")
        params = {
            "symbol": symbol,
            "interval": interval,
            "startTime": start_time,
            "endTime": end_time,
            "limit": limit
        }
        try:
            res = requests.get(
                url,
                params=params,
                **self._get_default_req_params()
            )
        except Exception as e:
            logger.error(e, exc_info=1)
            return data

        if not res.ok:
            logger.error(
                f"Response status not ok {res.status_code}", exc_info=1
            )
            if res.status_code < 500:
                logger.error(
                    f"error: {res.json()}", exc_info=1
                )
            return data

        json = res.json()

        if not json.get("success"):
            return data

        data = json['data']

        return data
