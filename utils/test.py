from django.contrib.auth import get_user_model
from django.core.management import call_command
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token


User = get_user_model()


class CustomAPITestCase(APITestCase):

    def setUp(self):
        self.superuser = User.objects.create_user(
            username="superuser",
            password="superuser",
            is_staff=True,
            is_superuser=True
        )
        self.admin = User.objects.create_user(
            username="admin",
            password="admin",
            is_staff=True
        )
        self.user = User.objects.create_user(
            username="user",
            password="user"
        )

    def authenticate(self, user=None):
        if not user:
            user = self.user
        token = Token.objects.create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")


class APIPermissionTestCase(CustomAPITestCase):

    def setUp(self):
        super().setUp()
        call_command('createpermissions')
    
    def set_permissions(self, user, permissions):
        user.c_set_permissions(permissions)
        user.refresh_from_db()

    def add_permissions(self, user, permissions):
        user.c_add_permissions(permissions)
        user.refresh_from_db()