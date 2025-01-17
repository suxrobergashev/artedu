from .get_untyped_token import decode_token
from course.models import User


def validate_token(token):
    if not token:
        return
    if len(token.split()) < 2 or token.split()[0] != 'Bearer':
        return
    payload = decode_token(token.split()[1])
    if not payload:
        return
    user_id = payload.get('user_id', None)
    if not user_id:
        return
    user = User.objects.filter(id=user_id).first()
    if not user:
        return
    return payload
