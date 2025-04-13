import logging
from django.utils import timezone
from core.celery_app import app
from utils.mexc.api import MexcClient
from utils.binance.api import BinanceClient
from utils.bitunix.api import BitunixClient
from utils.convertors import unix_to_datetime
from . import models
from . import helpers


logger = logging.getLogger(__name__)


@app.task
def get_mexc_symbols_task():
    client = MexcClient()
    symbols = client.get_default_symbols()
    if not symbols:
        return

    exchange, _ = models.Exchange.objects.get_or_create(
        name="Mexc",
        symbol="MEXC"
    )

    symbols_create = []

    for symbol in symbols:
        symbol_ins = models.Symbol(
            exchange=exchange,
            name=symbol
        )
        symbols_create.append(symbol_ins)

    models.Symbol.objects.bulk_create(
        symbols_create,
        ignore_conflicts=True
    )


@app.task
def get_binance_symbols_task():
    client = BinanceClient()
    symbols = client.get_exchange_info("symbols")
    if not symbols:
        return

    exchange, _ = models.Exchange.objects.get_or_create(
        name="Binance",
        symbol="BINANCE"
    )

    symbols_create = []

    for symbol in symbols:
        symbol_ins = models.Symbol(
            exchange=exchange,
            name=symbol['symbol']
        )
        symbols_create.append(symbol_ins)

    models.Symbol.objects.bulk_create(
        symbols_create,
        ignore_conflicts=True
    )


def get_mexc_symbols_task_debug():
    client = MexcClient()
    symbols = client.get_default_symbols()
    if not symbols:
        return

    exchange, _ = models.Exchange.objects.get_or_create(
        name="Mexc",
        symbol="MEXC"
    )

    symbols_create = []

    for symbol in symbols:
        symbol_ins = models.Symbol(
            exchange=exchange,
            name=symbol
        )
        symbols_create.append(symbol_ins)

    models.Symbol.objects.bulk_create(
        symbols_create,
        ignore_conflicts=True
    )


@app.task
def get_bitunix_symbols_task():
    client = BitunixClient()
    symbols = client.get_default_symbols()
    if not symbols:
        return

    exchange, _ = models.Exchange.objects.get_or_create(
        name="Bitunix",
        symbol="BITUNIX"
    )

    symbols_create = []

    for symbol in symbols:
        symbol_ins = models.Symbol(
            exchange=exchange,
            name=symbol['symbol']
        )
        symbols_create.append(symbol_ins)

    models.Symbol.objects.bulk_create(
        symbols_create,
        ignore_conflicts=True
    )


@app.task
def get_mexc_exchange_transactions_task():
    exchange, _ = models.Exchange.objects.get_or_create(
        name="Mexc",
        symbol="MEXC"
    )

    frames = [
        # "5m",
        # "15m",
        # "30m",
        "60m",
        "4h",
        "1d",
        "1W",
        "1M"
    ]

    frames_create = []

    for frame in frames:
        time_frame_ins = models.TimeFrame(
            exchange=exchange,
            name=frame,
            seconds=helpers.get_frame_seconds(frame)
        )
        frames_create.append(time_frame_ins)

    models.TimeFrame.objects.bulk_create(
        frames_create,
        ignore_conflicts=True
    )

    symbols = models.Symbol.objects.filter(
        exchange=exchange
    )

    if not symbols.exists():
        return

    for frame in frames:
        get_mexc_exchange_transactions_frame_task.delay(
            exchange.id,
            frame
        )


@app.task
def get_mexc_exchange_transactions_frame_task(
    exchange_id: int,
    frame_name: str
):
    exchange = models.Exchange.objects.filter(
        id=exchange_id
    ).first()
    if not exchange:
        return

    frame = models.TimeFrame.objects.filter(
        exchange=exchange,
        name=frame_name
    ).first()
    if not frame:
        return

    symbols = models.Symbol.objects.filter(
        exchange=exchange
    )

    client = MexcClient()

    now = timezone.now()

    for symbol in symbols:
        last_exchange = None
        start_time = None
        end_time = None

        if models.ExchangeTransaction.objects.filter(
            symbol=symbol,
            time_frame=frame
        ).exists():
            # Check if the time of each frame is passed.
            if frame.seconds is None:
                continue

            last_exchange = models.ExchangeTransaction.objects.filter(
                symbol=symbol,
                time_frame=frame
            ).order_by(
                "-close_time"
            ).first()

            date_time = unix_to_datetime(
                last_exchange.close_time / 1000
            )
            time_diff = now - date_time
            total_secs = time_diff.total_seconds()
            if abs(total_secs) < frame.seconds:
                continue

        klines = client.get_klines(
            symbol.name,
            frame.name,
            start_time=start_time,
            end_time=end_time,
            limit=4
        )
        if not klines:
            return

        for kline in klines[:-1]:
            open_time = kline[0]
            open_price = kline[1]
            high_price = kline[2]
            low_price = kline[3]
            close_price = kline[4]
            volume_price = kline[5]
            close_time = kline[6]
            quote_asset_volume = kline[7]

            if models.ExchangeTransaction.objects.filter(
                symbol=symbol,
                open_time=open_time,
                time_frame=frame
            ).exists():
                continue
            try:
                models.ExchangeTransaction.objects.create(
                    symbol=symbol,
                    time_frame=frame,
                    open_time=open_time,
                    open_price=open_price,
                    high_price=high_price,
                    low_price=low_price,
                    close_price=close_price,
                    volume=volume_price,
                    close_time=close_time,
                    quote_asset_volume=quote_asset_volume
                )
            except Exception as e:
                logger.info("Error occured when creating transaction ...")
                logger.error(e, exc_info=1)
                continue


def get_mexc_exchange_transactions_task_debug():
    client = MexcClient()

    exchange, _ = models.Exchange.objects.get_or_create(
        name="Mexc",
        symbol="MEXC"
    )

    frames = [
        # "5m",
        # "15m",
        # "30m",
        "60m",
        "4h",
        "1d",
        "1W",
        "1M"
    ]

    frames_create = []

    for frame in frames:
        time_frame_ins = models.TimeFrame(
            name=frame
        )
        frames_create.append(time_frame_ins)

    models.TimeFrame.objects.bulk_create(
        frames_create,
        ignore_conflicts=True
    )

    symbols = models.Symbol.objects.filter(
        exchange=exchange
    )[:10]

    if not symbols.exists():
        return

    times_frames = models.TimeFrame.objects.filter(
        name__in=frames
    )

    now = timezone.now()
    for fi, frame in enumerate(times_frames, 1):
        print("Frame: ", frame.id)
        print("Count: ", fi)
        for si, symbol in enumerate(symbols, 1):
            last_exchange = None
            start_time = None
            end_time = None

            if models.ExchangeTransaction.objects.filter(
                symbol=symbol,
                time_frame=frame
            ).exists():
                # Check if the time of each frame is passed.
                frame_sec = helpers.get_frame_seconds(frame.name)
                if frame_sec is None:
                    continue

                last_exchange = models.ExchangeTransaction.objects.filter(
                    symbol=symbol,
                    time_frame=frame
                ).order_by(
                    "-close_time"
                ).first()

                date_time = unix_to_datetime(
                    last_exchange.close_time / 1000
                )
                time_diff = now - date_time
                total_secs = time_diff.total_seconds()
                if abs(total_secs) < frame_sec:
                    continue

            klines = client.get_klines(
                symbol.name,
                frame,
                start_time=start_time,
                end_time=end_time,
                limit=4
            )
            print("Total klines: ", len(klines))
            if not klines:
                return

            for kline in klines:
                open_time = kline[0]
                open_price = kline[1]
                high_price = kline[2]
                low_price = kline[3]
                close_price = kline[4]
                volume_price = kline[5]
                close_time = kline[6]
                quote_asset_volume = kline[7]

                if models.ExchangeTransaction.objects.filter(
                    symbol=symbol,
                    open_time=open_time,
                    time_frame=frame
                ).exists():
                    continue

                models.ExchangeTransaction.objects.create(
                    symbol=symbol,
                    time_frame=frame,
                    open_time=open_time,
                    open_price=open_price,
                    high_price=high_price,
                    low_price=low_price,
                    close_price=close_price,
                    volume=volume_price,
                    close_time=close_time,
                    quote_asset_volume=quote_asset_volume
                )
            print("Symbol: ", symbol.name)
            print("Count: ", si)


@app.task
def get_binance_exchange_transactions_task():
    exchange, _ = models.Exchange.objects.get_or_create(
        name="Binance",
        symbol="BINANCE"
    )

    frames = [
        # "5m",
        # "15m",
        # "30m",
        "1h",
        "4h",
        "12h",
        "1d",
        "1w",
        "1M"
    ]

    frames_create = []

    for frame in frames:
        time_frame_ins = models.TimeFrame(
            exchange=exchange,
            name=frame,
            seconds=helpers.get_frame_seconds(frame)
        )
        frames_create.append(time_frame_ins)

    models.TimeFrame.objects.bulk_create(
        frames_create,
        ignore_conflicts=True
    )

    symbols = models.Symbol.objects.filter(
        exchange=exchange
    )

    if not symbols.exists():
        return

    for frame in frames:
        get_binance_exchange_transactions_frame_task.delay(
            exchange.id,
            frame
        )


@app.task
def get_binance_exchange_transactions_frame_task(
    exchange_id: int,
    frame_name: str
):
    exchange = models.Exchange.objects.filter(
        id=exchange_id
    ).first()
    if not exchange:
        return

    frame = models.TimeFrame.objects.filter(
        exchange=exchange,
        name=frame_name
    ).first()
    if not frame:
        return

    symbols = models.Symbol.objects.filter(
        exchange=exchange
    )

    client = BinanceClient()

    now = timezone.now()

    for symbol in symbols:
        last_exchange = None
        start_time = None
        end_time = None

        if models.ExchangeTransaction.objects.filter(
            symbol=symbol,
            time_frame=frame
        ).exists():
            # Check if the time of each frame is passed.
            if frame.seconds is None:
                continue

            last_exchange = models.ExchangeTransaction.objects.filter(
                symbol=symbol,
                time_frame=frame
            ).order_by(
                "-close_time"
            ).first()

            date_time = unix_to_datetime(
                last_exchange.close_time / 1000
            )
            time_diff = now - date_time
            total_secs = time_diff.total_seconds()
            if abs(total_secs) < frame.seconds:
                continue
        klines = client.get_klines_data(
            symbol.name,
            frame.name,
            startTime=start_time,
            endTime=end_time,
            limit=4
        )
        if not klines:
            return

        for kline in klines[:-1]:
            open_time = kline['open_time']
            open_price = kline['open_price']
            high_price = kline['high_price']
            low_price = kline['low_price']
            close_price = kline['close_price']
            volume_price = kline['volume']
            close_time = kline['close_time']
            quote_asset_volume = kline['quote_asset_volume']
            number_of_trades = kline['number_of_trades']
            taker_by_base_asset_volume = kline['taker_by_base_asset_volume']
            taker_by_quote_asset_volume = kline['taker_by_quote_asset_volume']

            if models.ExchangeTransaction.objects.filter(
                symbol=symbol,
                open_time=open_time,
                time_frame=frame
            ).exists():
                continue
            try:
                models.ExchangeTransaction.objects.create(
                    symbol=symbol,
                    time_frame=frame,
                    open_time=open_time,
                    open_price=open_price,
                    high_price=high_price,
                    low_price=low_price,
                    close_price=close_price,
                    volume=volume_price,
                    close_time=close_time,
                    quote_asset_volume=quote_asset_volume,
                    number_of_trades=number_of_trades,
                    taker_by_base_asset_volume=taker_by_base_asset_volume,
                    taker_by_quote_asset_volume=taker_by_quote_asset_volume
                )
            except Exception as e:
                logger.info("Error occured when creating transaction ...")
                logger.error(e, exc_info=1)
                continue


@app.task
def check_engulfing_strategy_task():
    exchanges = models.Exchange.objects.filter(name="Bitunix")
    for exchange in exchanges:
        time_frames = models.TimeFrame.objects.filter(
            exchange=exchange
        ).prefetch_related(
            'transactions'
        ).order_by('seconds')
        for time_frame in time_frames:
            check_engulfing_strategy_frame_task.delay(
                exchange.pk,
                time_frame.pk
            )


@app.task
def check_engulfing_strategy_frame_task(exchange_pk, time_frame_pk: int):
    frame = models.TimeFrame.objects.filter(
        exchange_id=exchange_pk,
        pk=time_frame_pk
    ).prefetch_related(
        'transactions'
    ).first()
    if not frame:
        return

    symbols = models.Symbol.objects.filter(exchange_id=exchange_pk)
    for symbol in symbols:
        transactions = frame.transactions.filter(
            symbol=symbol
        )

        if transactions.count() < 4:
            continue

        transactions = list(transactions)

        for i, tr in enumerate(transactions):

            if i < 3:
                continue

            close_price = float(tr.close_price)
            open_price = float(tr.open_price)

            engulfing_bullish = False
            engulfing_bearish = False

            one_before = transactions[i-1]
            one_before_close = float(one_before.close_price)

            two_before = transactions[i-2]
            two_before_close = float(two_before.close_price)

            three_before = transactions[i-3]
            three_before_close = float(three_before.close_price)

            four_before = transactions[i-4]
            four_before_close = float(four_before.close_price)

            check_engulfing_bullish = True
            check_engulfing_bearish = True

            if one_before.engulfing_bullish:
                check_engulfing_bullish = False
            elif two_before.engulfing_bullish and one_before_close >= two_before_close:
                check_engulfing_bullish = False
            elif three_before.engulfing_bullish and two_before_close >= three_before_close and one_before_close >= three_before_close:
                check_engulfing_bullish = False
            elif four_before.engulfing_bullish and three_before_close >= four_before_close and two_before_close >= four_before_close and one_before_close >= four_before_close:
                check_engulfing_bullish = False

            if one_before.engulfing_bearish:
                check_engulfing_bearish = False
            elif two_before.engulfing_bearish and one_before_close <= two_before_close:
                check_engulfing_bearish = False
            elif three_before.engulfing_bearish and two_before_close <= three_before_close and one_before_close <= three_before_close:
                check_engulfing_bullish = False
            elif four_before.engulfing_bearish and three_before_close <= four_before_close and two_before_close <= four_before_close and one_before_close <= four_before_close:
                check_engulfing_bullish = False

            if check_engulfing_bullish and close_price > open_price and close_price > one_before_close and close_price > two_before_close and close_price > three_before_close and close_price > four_before_close:
                engulfing_bullish = True
            elif check_engulfing_bearish and close_price < open_price and close_price < one_before_close and close_price < two_before_close and close_price < three_before_close and close_price < four_before_close:
                engulfing_bearish = True

            tr.engulfing_bullish = engulfing_bullish
            tr.engulfing_bearish = engulfing_bearish
            tr.engulf_at = timezone.now()
            tr.save(
                update_fields=[
                    "engulfing_bullish",
                    "engulfing_bearish",
                    "updated_at",
                    "engulf_at"
                ]
            )


def check_engulfing_strategy_task_debug():
    transactions = models.ExchangeTransaction.objects.filter(
        engulfing_bullish__isnull=True,
        engulfing_bearish__isnull=True
    ).order_by("open_time")
    for i, tr in enumerate(transactions):
        close_price = float(tr.close_price)
        open_price = float(tr.open_price)

        if i < 3:
            continue

        engulfing_bullish = False
        engulfing_bearish = False

        one_before = transactions[i-1]
        one_before_close = float(one_before.close_price)

        two_before = transactions[i-2]
        two_before_close = float(two_before.close_price)

        three_before = transactions[i-3]
        three_before_close = float(three_before.close_price)

        check_engulfing_bullish = True
        check_engulfing_bearish = True

        if one_before.engulfing_bullish:
            check_engulfing_bullish = False
        if two_before.engulfing_bullish and one_before_close >= two_before_close:
            check_engulfing_bullish = False
        if three_before.engulfing_bullish and two_before_close >= three_before_close and one_before_close >= three_before_close:
            check_engulfing_bullish = False

        if one_before.engulfing_bearish:
            check_engulfing_bearish = False
        if two_before.engulfing_bearish and one_before_close <= two_before_close:
            check_engulfing_bearish = False
        if three_before.engulfing_bearish and two_before_close <= three_before_close and one_before_close <= three_before_close:
            check_engulfing_bullish = False

        if check_engulfing_bullish and close_price > open_price and close_price > one_before_close and close_price > two_before_close and close_price > three_before_close:
            engulfing_bullish = True
        if check_engulfing_bearish and close_price < open_price and close_price < one_before_close and close_price < two_before_close and close_price < three_before_close:
            engulfing_bearish = True

        tr.engulfing_bullish = engulfing_bullish
        tr.engulfing_bearish = engulfing_bearish
        tr.engulf_at = timezone.now()
        tr.save(
            update_fields=[
                "engulfing_bullish",
                "engulfing_bearish",
                "updated_at",
                "engulf_at"
            ]
        )


@app.task
def get_bitunix_exchange_transactions_task():
    exchange, _ = models.Exchange.objects.get_or_create(
        name="Bitunix",
        symbol="BITUNIX"
    )

    frames = [
        "60",
        "240",
        "D",
        "W"
    ]

    frames_create = []

    for frame in frames:
        time_frame_ins = models.TimeFrame(
            exchange=exchange,
            name=frame,
            seconds=helpers.get_frame_seconds(frame)
        )
        frames_create.append(time_frame_ins)

    models.TimeFrame.objects.bulk_create(
        frames_create,
        ignore_conflicts=True
    )

    symbols = models.Symbol.objects.filter(
        exchange=exchange
    )

    if not symbols.exists():
        return

    for frame in frames:
        get_bitunix_exchange_transactions_frame_task.delay(
            exchange.id,
            frame
        )


@app.task
def get_bitunix_exchange_transactions_frame_task(
    exchange_id: int,
    frame_name: str
):
    exchange = models.Exchange.objects.filter(
        id=exchange_id
    ).first()
    if not exchange:
        return

    frame = models.TimeFrame.objects.filter(
        exchange=exchange,
        name=frame_name
    ).first()
    if not frame:
        return

    symbols = models.Symbol.objects.filter(
        exchange=exchange
    )

    client = BitunixClient()

    now = timezone.now()

    for symbol in symbols:
        last_exchange = None
        start_time = None
        end_time = None

        if models.ExchangeTransaction.objects.filter(
            symbol=symbol,
            time_frame=frame
        ).exists():
            # Check if the time of each frame is passed.
            if frame.seconds is None:
                continue

            last_exchange = models.ExchangeTransaction.objects.filter(
                symbol=symbol,
                time_frame=frame
            ).order_by(
                "-open_time"
            ).first()

            date_time = unix_to_datetime(
                last_exchange.open_time / 1000
            )
            time_diff = now - date_time
            total_secs = time_diff.total_seconds()
            if abs(total_secs) < frame.seconds:
                continue

        klines = client.get_klines(
            symbol.name,
            frame.name,
            start_time=start_time,
            end_time=end_time,
            limit=4
        )
        if not klines:
            return

        for kline in klines[:-1]:
            open_time = helpers.convert_iso_to_unix(kline['ts'])
            open_price = kline['open']
            high_price = kline["high"]
            low_price = kline['low']
            close_price = kline['close']

            if models.ExchangeTransaction.objects.filter(
                symbol=symbol,
                open_time=open_time,
                time_frame=frame
            ).exists():
                continue
            try:
                models.ExchangeTransaction.objects.create(
                    symbol=symbol,
                    time_frame=frame,
                    open_time=open_time,
                    open_price=open_price,
                    high_price=high_price,
                    low_price=low_price,
                    close_price=close_price,
                )
            except Exception as e:
                logger.info("Error occured when creating transaction ...")
                logger.error(e, exc_info=1)
                continue


def get_bitunix_exchange_transactions_task_debug():
    client = BitunixClient()

    exchange, _ = models.Exchange.objects.get_or_create(
        name="Bitunix",
        symbol="BITUNIX"
    )

    frames = [
        "1"
    ]

    frames_create = []

    for frame in frames:
        time_frame_ins = models.TimeFrame(
            name=frame
        )
        frames_create.append(time_frame_ins)

    models.TimeFrame.objects.bulk_create(
        frames_create,
        ignore_conflicts=True
    )

    symbols = models.Symbol.objects.filter(
        exchange=exchange
    )[:10]

    if not symbols.exists():
        return

    times_frames = models.TimeFrame.objects.filter(
        name__in=frames
    )

    now = timezone.now()
    for fi, frame in enumerate(times_frames, 1):
        print("Frame: ", frame.id)
        print("Count: ", fi)
        for si, symbol in enumerate(symbols, 1):
            last_exchange = None
            start_time = None
            end_time = None

            if models.ExchangeTransaction.objects.filter(
                symbol=symbol,
                time_frame=frame
            ).exists():
                # Check if the time of each frame is passed.
                if frame.seconds is None:
                    continue

                last_exchange = models.ExchangeTransaction.objects.filter(
                    symbol=symbol,
                    time_frame=frame
                ).order_by(
                    "-open_time"
                ).first()

                date_time = unix_to_datetime(
                    last_exchange.open_time / 1000
                )
                time_diff = now - date_time
                total_secs = time_diff.total_seconds()
                if abs(total_secs) < frame.seconds:
                    continue

            klines = client.get_klines(
                symbol.name,
                frame.name,
                start_time=start_time,
                end_time=end_time,
                limit=4
            )
            if not klines:
                return

            print("Total klines: ", len(klines))

            for kline in klines[:-1]:
                open_time = helpers.convert_iso_to_unix(kline['ts'])
                open_price = kline['open']
                high_price = kline["high"]
                low_price = kline['low']
                close_price = kline['close']

                if models.ExchangeTransaction.objects.filter(
                    symbol=symbol,
                    open_time=open_time,
                    time_frame=frame
                ).exists():
                    continue

                models.ExchangeTransaction.objects.create(
                    symbol=symbol,
                    time_frame=frame,
                    open_time=open_time,
                    open_price=open_price,
                    high_price=high_price,
                    low_price=low_price,
                    close_price=close_price,
                )
            print("Symbol: ", symbol.name)
            print("Count: ", si)
