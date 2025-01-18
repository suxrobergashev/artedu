from django.urls import path
from .views import UserViewSet, CourseViewSet

urlpatterns = [
    path('register/', UserViewSet.as_view({'post': 'register'}), name='register'),
    path('login/', UserViewSet.as_view({'post': 'login'}), name='login'),
    path('auth/me/', UserViewSet.as_view({'patch': 'auth_me_update', 'get': 'auth_me'}), name='auth_me'),

    path('history/', UserViewSet.as_view({'get': 'history'}), name='history'),

    path('courses/', CourseViewSet.as_view({'get': 'list'}), name='courses'),
    path('courses/<int:pk>/', CourseViewSet.as_view({'get': 'retrieve'}), name='courses_detail'),
    path('courses/<int:pk>/homework/', CourseViewSet.as_view({'post': 'course_homework'}), name='course_homework'),

    path('categories/', CourseViewSet.as_view({'get': 'list_categories'}), name='categories'),
    path('courses/<int:pk>/quiz/', CourseViewSet.as_view({'post': 'quiz_answers'}), name='quiz_answers'),

]
