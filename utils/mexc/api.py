import logging

import requests


logger = logging.getLogger(__name__)


class MexcClient:
    base_url = "https://api.mexc.com"

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
        return f"{self.base_url}/api/v3/{path}"

    def _get_default_req_params(self):
        return {
            "timeout": self.api_req_timeout,
            "json": True
        }

    def get_default_symbols(self) -> list[str]:
        data = []

        url = self._get_api_url("defaultSymbols")

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

        data = res.json()["data"]
        return data

    def get_klines(
        self,
        symbol: str,
        interval: str,
        start_time: int = None,
        end_time: int = None,
        limit: int = 500
    ) -> list[list]:
        assert limit < 1000, "Maximum length for limit is 1000."

        data = []

        url = self._get_api_url("klines")
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

        data = res.json()
        return data
