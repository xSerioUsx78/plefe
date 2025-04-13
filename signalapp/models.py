from django.db import models
from utils.models import TimestampedModel


class SignalCoin(TimestampedModel):
    coin_id = models.CharField(max_length=256)
    symbol = models.CharField(max_length=256)
    name = models.CharField(max_length=256)

    def __str__(self) -> str:
        return self.name