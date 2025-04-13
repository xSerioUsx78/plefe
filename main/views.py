from django.shortcuts import render
from django.db.models import Q
from exchange_app import models


def index(request):
    return render(request, 'index.html')


def engulfing(request):
    return render(
        request,
        'engulfing.html'
    )


def short(request, time_frame: str):
    transactions = models.ExchangeTransaction.objects.filter(
        time_frame__name=time_frame,
        engulfing_bearish=True
    ).select_related(
        "symbol",
        "symbol__exchange"
    ).order_by(
        '-open_time'
    )[:200]

    ctx = {
        "transactions": transactions,
        "time_frame": time_frame
    }
    return render(
        request,
        'short.html',
        ctx
    )


def long(request, time_frame: str):
    transactions = models.ExchangeTransaction.objects.filter(
        time_frame__name=time_frame,
        engulfing_bullish=True
    ).select_related(
        "symbol",
        "symbol__exchange"
    ).order_by(
        '-open_time'
    )[:200]

    ctx = {
        "transactions": transactions,
        "time_frame": time_frame
    }
    return render(
        request,
        'long.html',
        ctx
    )
