import requests
from core.celery_app import app
from . import services, models


@app.task
def create_update_coins_task():
    try:
        res = services.get_coins_list()
    except (requests.ConnectTimeout, requests.ConnectionError) as e:
        raise create_update_coins_task.retry(
            exc=e,
            retry_backoff=True
        )
    
    if not res.ok:
        raise create_update_coins_task.retry(
            exc=e,
            retry_backoff=True
        )

    data = res.json()

    for coin in data:
        obj, created = models.UiCoin.objects.update_or_create(
            coin_id=coin['id'],
            defaults={
                'symbol': coin['symbol'],
                'name': coin['name']
            }
        )
        platforms: dict = coin['platforms']
        if platforms:
            if created:
                platforms_bulk = []
                for key, value in platforms.items():
                    platform = models.UiCoinPlatform(
                        coin=obj,
                        name=key,
                        contract_address=value
                    )
                    platforms_bulk.append(platform)
                models.UiCoinPlatform.objects.bulk_create(
                    platforms_bulk, 
                    batch_size=1000
                )
            else:
                for key, value in platforms.items():
                    platform, _ = models.UiCoinPlatform.objects.update_or_create(
                        coin=obj,
                        name=key,
                        defaults={
                            "contract_address": value
                        }
                    )
