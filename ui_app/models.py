from django.db import models
from utils.models import TimestampedModel


class UiCoin(TimestampedModel):
    coin_id = models.CharField(max_length=256)
    symbol = models.CharField(max_length=256)
    name = models.CharField(max_length=256)

    def __str__(self) -> str:
        return self.name
    

class UiCoinPlatform(TimestampedModel):
    coin = models.ForeignKey(
        UiCoin,
        on_delete=models.CASCADE,
        related_name='platforms'
    )
    name = models.CharField(max_length=256)
    contract_address = models.CharField(max_length=256)

    def __str__(self) -> str:
        return self.name