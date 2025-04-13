from django.contrib import admin
from . import models


admin.site.register([
    models.Task,
    models.TaskChecklist,
    models.TaskCoin,
    models.TaskComment,
    models.TaskUser
])