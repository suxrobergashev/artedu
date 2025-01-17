from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from django.urls import reverse
from utils.check_token import validate_token


class UserAuthMiddleware(MiddlewareMixin):
    def process_request(self, request, *view_args, **view_kwargs):
        target=None
        pk = view_kwargs.get('pk')
        if pk is not None:
            target = [reverse('courses_detail', kwargs={'pk': pk}), reverse('course_homework', kwargs={'pk': pk}),
                      reverse('quiz_list', kwargs={'pk': pk}), reverse('quiz_answers', kwargs={'pk': pk})]

        if not target or request.path not in target:
            return
        payload = validate_token(request.headers.get('Authorization'))
        if not payload:
            return JsonResponse(data={'result': '', 'error': 'Unauthorized access', 'ok': False}, status=401)
        return
