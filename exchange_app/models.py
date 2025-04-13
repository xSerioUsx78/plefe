from django.db import models
from utils.models import TimestampedModel
from utils.convertors import unix_to_datetime, to_timezone


class Exchange(TimestampedModel):
    name = models.CharField(
        max_length=50,
        null=True
    )
    symbol = models.CharField(
        max_length=10,
        null=True
    )

    def __str__(self) -> str:
        return self.name


class Symbol(TimestampedModel):
    exchange = models.ForeignKey(
        Exchange,
        on_delete=models.CASCADE,
        related_name="symbols"
    )
    name = models.CharField(
        max_length=50
    )

    def __str__(self):
        return self.name

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['exchange', 'name'],
                name='Unique symbol for each exchange.'
            )
        ]


class TimeFrame(TimestampedModel):
    exchange = models.ForeignKey(
        Exchange,
        on_delete=models.CASCADE,
        related_name="time_frames",
        null=True
    )
    name = models.CharField(
        max_length=20
    )
    seconds = models.PositiveBigIntegerField(
        null=True
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ("seconds",)
        constraints = [
            models.UniqueConstraint(
                fields=['exchange', 'name'],
                name='Unique frame for each exchange.'
            )
        ]


class ExchangeTransaction(TimestampedModel):
    symbol = models.ForeignKey(
        Symbol,
        on_delete=models.CASCADE,
        null=True,
        related_name="transactions"
    )
    time_frame = models.ForeignKey(
        TimeFrame,
        on_delete=models.CASCADE,
        null=True,
        related_name="transactions"
    )
    open_time = models.PositiveBigIntegerField(
        null=True
    )
    open_price = models.CharField(
        max_length=50,
        null=True
    )
    high_price = models.CharField(
        max_length=50,
        null=True
    )
    low_price = models.CharField(
        max_length=50,
        null=True
    )
    close_price = models.CharField(
        max_length=50,
        null=True
    )
    volume = models.CharField(
        max_length=50,
        null=True
    )
    close_time = models.PositiveBigIntegerField(
        null=True
    )
    quote_asset_volume = models.CharField(
        max_length=50,
        null=True
    )
    number_of_trades = models.PositiveBigIntegerField(
        null=True
    )
    taker_by_base_asset_volume = models.CharField(
        max_length=50,
        null=True
    )
    taker_by_quote_asset_volume = models.CharField(
        max_length=50,
        null=True
    )
    engulfing_bullish = models.BooleanField(
        default=None,
        null=True
    )
    engulfing_bearish = models.BooleanField(
        default=None,
        null=True
    )
    engulf_at = models.DateTimeField(
        null=True
    )

    def __str__(self) -> str:
        return str(self.id)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['symbol', 'open_time', 'time_frame'],
                name='Unique transaction for each symbol.'
            )
        ]

    def get_unix_date(self, time: int) -> str:
        if not time:
            return None

        return to_timezone(unix_to_datetime(time / 1000))

    @property
    def open_time_date(self):
        return self.get_unix_date(
            self.open_time
        )

    @property
    def close_time_date(self):
        return self.get_unix_date(
            self.close_time
        )

    @property
    def first_signal(self):
        return ExchangeTransaction.objects.filter(
            symbol=self.symbol,
            time_frame=self.time_frame,
            engulfing_bullish=self.engulfing_bullish,
            engulfing_bearish=self.engulfing_bearish
        ).order_by(
            'open_time'
        ).first()

    @property
    def passed_time(self):
        return self.open_time_date
