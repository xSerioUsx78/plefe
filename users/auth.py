from rest_framework.response import Response
from .utils import set_token_in_cookie, expire_token_from_cookie


def cookie_login_with_token(res: Response, token: str) -> None:
    set_token_in_cookie(res, token)

def cookie_logout_with_token(res: Response) -> None:
    expire_token_from_cookie(res)