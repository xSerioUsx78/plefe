from django.db.models.signals import post_save
from django.contrib.auth import get_user_model
from .models import Profile, Setting


User = get_user_model()


def create_profile(sender, created, instance, *args, **kwargs):
    if created:
        Profile.objects.create(user=instance)


post_save.connect(create_profile, sender=User)


def create_setting(sender, created, instance, *args, **kwargs):
    if created:
        Setting.objects.create(user=instance)


post_save.connect(create_setting, sender=User)