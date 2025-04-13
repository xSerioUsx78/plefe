import requests
from django.conf import settings


COINGECKO_API_URL = getattr(settings, 'COINGECKO_API_URL', "")


def get_coins_list(include_platform: bool = True) -> requests.Response:
    res = requests.get(
        f'{COINGECKO_API_URL}coins/list',
        params={
            'include_platform': include_platform
        },
        json=True
    )
    return res
