from django.conf import settings
from django.contrib.auth import (
    BACKEND_SESSION_KEY,
    HASH_SESSION_KEY
)
from channels.auth import (
    AuthMiddleware, CookieMiddleware, SessionMiddleware, get_user,
    _get_user_session_key, load_backend, constant_time_compare
)
from channels.db import database_sync_to_async
from rest_framework.authtoken.models import Token


@database_sync_to_async
def get_user(scope):
    """
    Return the user model instance associated with the given scope.
    If no user is retrieved, return an instance of `AnonymousUser`.
    """
    # postpone model import to avoid ImproperlyConfigured error before Django
    # setup is complete.
    from django.contrib.auth.models import AnonymousUser

    user = None
    """
    We get the token from the cookie then we try to authenticate the user with the cookie
    our first priority is cookie authentication if there not then we leave channels do his proccess
    """
    cookies = scope['cookies']
    if 'token' in cookies:
        token = Token.objects.filter(key=cookies['token']).first()
        if token:
            user = token.user
    else:
        if "session" not in scope:
            raise ValueError(
                "Cannot find session in scope. You should wrap your consumer in "
                "SessionMiddleware."
            )
        session = scope["session"]
        try:
            user_id = _get_user_session_key(session)
            backend_path = session[BACKEND_SESSION_KEY]
        except KeyError:
            pass
        else:
            if backend_path in settings.AUTHENTICATION_BACKENDS:
                backend = load_backend(backend_path)
                user = backend.get_user(user_id)
                # Verify the session
                if hasattr(user, "get_session_auth_hash"):
                    session_hash = session.get(HASH_SESSION_KEY)
                    session_hash_verified = session_hash and constant_time_compare(
                        session_hash, user.get_session_auth_hash()
                    )
                    if not session_hash_verified:
                        session.flush()
                        user = None
    return user or AnonymousUser()


class CustomAuthMiddleware(AuthMiddleware):
    """
    Overriding the channels default AuthMiddleware behavior to 
    use our get_user method implmentation
    """

    async def resolve_scope(self, scope):
        scope["user"]._wrapped = await get_user(scope)


def AuthMiddlewareStack(inner):
    return CookieMiddleware(SessionMiddleware(CustomAuthMiddleware(inner)))