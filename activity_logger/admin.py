from django.contrib import admin
from .models import Log, LogDetail


admin.site.register(Log)
admin.site.register(LogDetail)