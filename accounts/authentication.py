from abc import ABC, abstractmethod
import jwt
from django.contrib.auth.backends import ModelBackend
from rest_framework.authentication import BaseAuthentication
from config import custom_exception
from .models import User
from .utils import decode_jwt
from django.core.cache import caches


class AbstractTokenAuthentication(ABC, BaseAuthentication):

    @abstractmethod
    def authenticate(self, request):
        ...

    @staticmethod
    def get_payload(token):
        payload = decode_jwt(token)
        return payload

    @staticmethod
    def get_user_from_payload(payload):
        user_id = payload.get('user_id')
        try:
            user = User.objects.get(id=user_id)
        except:
            raise custom_exception.UserNotFound

        if not user.is_active:
            raise custom_exception.NotActiveUserError

        return user

    @staticmethod
    def validate_jti_token(payload):
        jti = payload.get('jti')
        user_id = payload.get('user_id')
        if not caches['auth'].keys(f"user_{user_id} || {jti}"):
            raise custom_exception.InvalidTokenError



