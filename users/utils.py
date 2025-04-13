from django.conf import settings
from rest_framework.authtoken.models import Token
from rest_framework.response import Response


HTTP_ONLY_TOKEN_KEY = getattr(settings, 'HTTP_ONLY_TOKEN_KEY', 'token')
DEBUG = getattr(settings, 'DEBUG', False)


def destroy_token(user):
    """
    It will delete the token from db if there was any.
    """
    Token.objects.filter(user=user).delete()


def set_token_in_cookie(res: Response, token: str) -> None:
    max_age = 365 * 24 * 60 * 60 # One year
    res.set_cookie(
        key=HTTP_ONLY_TOKEN_KEY,
        value=token ,
        httponly=True,
        max_age=max_age,
        samesite='strict',
        secure=DEBUG == False,
        path='/'
    )


def expire_token_from_cookie(res: Response) -> None:
    res.set_cookie(
        key=HTTP_ONLY_TOKEN_KEY,
        max_age=-1
    )