from .get_untyped_token import decode_token
from authentication.models import User


def validate_token(token):
    if not token:
        return
    if len(token.split()) < 2 or token.split()[0] != 'Bearer':
        return
    payload = decode_token(token.split()[1])
    if not payload:
        return
    user_id = payload.get('user_id', None)
    login_time = payload.get('login_time', None)
    if not user_id or not login_time:
        return
    user = User.objects.filter(id=user_id, login_time=login_time).first()
    if not user:
        return
    return payload
