import logging
from psycopg import errors as psycopg_errors
from django.db.utils import OperationalError
from django.http import JsonResponse
from rest_framework import status
from .error_codes import DATABASE_CONNECTION_ERROR


logger = logging.getLogger(__name__)


def catch_database_error(func):
    def wrapper(*args, **kwargs):
        try:
            res = func(*args, **kwargs)
            return res
        except (OperationalError, psycopg_errors.OperationalError) as e:
            logger.error(e, exc_info=1)
            return JsonResponse(
                data={
                    'detail': 'Database connection error, please contact the administrators to fix the problem.', 
                    'code': DATABASE_CONNECTION_ERROR
                }, 
                status=status.HTTP_400_BAD_REQUEST
            )
    return wrapper