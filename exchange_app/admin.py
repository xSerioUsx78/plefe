from django.contrib import admin
from . import models


admin.site.register([
    models.Symbol,
    models.TimeFrame,
    models.Exchange,
    models.ExchangeTransaction
])
