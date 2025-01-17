from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import UntypedToken


def decode_token(token):
    try:
        payload = UntypedToken(token)
        return payload
    except TokenError:
        return None
