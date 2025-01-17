from django.urls import path
from .views import UserViewSet, CourseViewSet

urlpatterns = [
    path('register/', UserViewSet.as_view({'post': 'register'}), name='register'),
    path('login/', UserViewSet.as_view({'post': 'login'}), name='login'),

    path('courses/', CourseViewSet.as_view({'get': 'list'}), name='courses'),
    path('courses/<int:pk>/', CourseViewSet.as_view({'get': 'retrieve'}), name='courses_detail'),
    path('courses/<int:pk>/homework/', CourseViewSet.as_view({'post': 'course_homework'}), name='course_homework'),


    path('categories/', CourseViewSet.as_view({'get': 'list_categories'}), name='categories'),
    path('quiz/<int:pk>/', CourseViewSet.as_view({'get': 'quiz_list'}), name='quiz_list'),
    path('quiz/<int:pk>/answer/', CourseViewSet.as_view({'post': 'quiz_answers'}), name='quiz_answers'),


]
