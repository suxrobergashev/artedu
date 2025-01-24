from django.contrib.auth.hashers import check_password
from django.db import transaction
from django.db.models import Q
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User, Course, CourseCategory, Test, CourseHomework, TestAnswer, TestResult
from .serializers import UserSerializer, LoginSerializer, CourseSerializer, CourseCategorySerializer, TestSerializer, \
    CourseHomeworkSerializer, QuizAnswerSerializer, CourseRetrieveSerializer


class UserViewSet(viewsets.ViewSet):
    @swagger_auto_schema(
        operation_summary='User registration',
        operation_description='User registration',
        responses={201: UserSerializer()},
        request_body=UserSerializer,
        tags=['User']
    )
    def register(self, request):
        serializer = UserSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(data={"error": serializer.errors, 'ok': False}, status=status.HTTP_400_BAD_REQUEST)
        user = serializer.save()
        refresh_token = RefreshToken.for_user(user)
        access_token = refresh_token.access_token
        return Response(
            data={'result': serializer.data, 'access_token': str(access_token), 'refresh_token': str(refresh_token),
                  'ok': True}, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        request_body=LoginSerializer,
        operation_summary='User login',
        operation_description='User login',
        responses={200: UserSerializer()},
        tags=['User']
    )
    def login(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(data={"error": serializer.errors, 'ok': False}, status=status.HTTP_400_BAD_REQUEST)
        user = User.objects.filter(phone_number=serializer.data.get('phone_number')).first()
        if not user:
            return Response(data={"error": 'User does not exist', 'ok': False}, status=status.HTTP_400_BAD_REQUEST)
        if not check_password(serializer.data.get('password'), user.password):
            return Response(data={"error": 'Incorrect password', 'ok': False}, status=status.HTTP_400_BAD_REQUEST)
        refresh_token = RefreshToken.for_user(user)
        access_token = refresh_token.access_token
        return Response(
            data={'result': {'access_token': str(access_token), 'refresh_token': str(refresh_token)}, 'ok': True},
            status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary='User me',
        operation_description='User me',
        responses={200: UserSerializer()},
        tags=['User']
    )
    def auth_me(self, request):
        user = request.user
        return Response({"result": UserSerializer(user).data, "ok": True}, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary='User update',
        operation_description='User update',
        request_body=UserSerializer,
        responses={200: UserSerializer()},
        tags=['User'],

    )
    def auth_me_update(self, request):
        user = request.user
        serializer = UserSerializer(user, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(data={"error": serializer.errors, 'ok': False}, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(data={'result': serializer.data, 'ok': True}, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary='User course history',
        operation_description='User course history',
        responses={200: CourseSerializer(many=True)},
        tags=['User']
    )
    def history(self, request):
        user = request.user
        courses = Course.objects.filter(students=user)
        return Response(
            data={'result': CourseSerializer(courses, many=True, context={'request': request}).data, 'ok': True},
            status=status.HTTP_200_OK)


class CourseViewSet(viewsets.ViewSet):
    @swagger_auto_schema(
        operation_summary='Course category list',
        responses={200: CourseCategorySerializer(many=True)},
        tags=['Course category']
    )
    def list_categories(self, request):
        categories = CourseCategory.objects.all()
        return Response(
            data={'result': CourseCategorySerializer(categories, many=True, context={'request': request}).data,
                  'ok': True},
            status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary='Course list',
        responses={200: CourseSerializer(many=True)},
        manual_parameters=[
            openapi.Parameter(name='category_id', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
                              description="Category id"),
            openapi.Parameter(name='q', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description="Search term"),
        ], tags=['Course']
    )
    def list(self, request):
        q = request.query_params.get('q')
        category = request.query_params.get('category_id')
        filter_ = Q()
        if category:
            filter_ |= Q(category_id=category)
        if q:
            filter_ |= Q(title__icontains=q)
        courses = Course.objects.filter(is_published=True).filter(filter_)
        serializer = CourseSerializer(courses, many=True, context={'request': request})
        return Response(data={'result': serializer.data, 'ok': True}, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary='Course detail',
        responses={200: CourseRetrieveSerializer()},
        tags=['Course']
    )
    def retrieve(self, request, pk=None):
        course = Course.objects.filter(id=pk, is_published=True).first()
        if not course:
            return Response(data={'error': "Course not Found", 'ok': False}, status=status.HTTP_404_NOT_FOUND)
        if not course.students.filter(id=request.user.id).exists():
            course.students.add(request.user)
        serializer = CourseRetrieveSerializer(course, context={'request': request})
        return Response(data={'result': serializer.data, 'ok': True}, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        request_body=CourseHomeworkSerializer,
        responses={200: CourseHomeworkSerializer()},
        tags=['Course']
    )
    def course_homework(self, request, pk):
        if CourseHomework.objects.filter(course_id=pk, user=request.user).exists():
            return Response(data={'error': "You are already send homework", 'ok': False},
                            status=status.HTTP_400_BAD_REQUEST)
        data = request.data.copy()  # request.data form-data ni oladi
        data['course'] = pk  # `course` ni request ma'lumotlariga qo'shamiz
        data['user'] = request.user.id  # `user`ni ham qo'shamiz
        serializer = CourseHomeworkSerializer(data=data, context={'request': request})
        if not serializer.is_valid():
            return Response(data={'error': serializer.errors, 'ok': False}, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(data={'result': serializer.data, 'ok': True}, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        request_body=QuizAnswerSerializer(many=True),
        responses={200: 'result:0'},
        tags=['Quiz answer']
    )
    def quiz_answers(self, request, pk):
        serializer = QuizAnswerSerializer(data=request.data, many=True)
        if not serializer.is_valid():
            return Response({'error': serializer.errors, 'ok': False}, status=status.HTTP_400_BAD_REQUEST)

        # Validate course existence
        try:
            course = Course.objects.get(pk=pk)
        except Course.DoesNotExist:
            return Response({'error': "Course not found.", 'ok': False}, status=status.HTTP_404_NOT_FOUND)
        if TestResult.objects.filter(course=course, user=request.user).exists():
            return Response({'result': course.test_result(request.user), 'ok': True}, status=status.HTTP_200_OK)
        # Fetch all questions and answers for the course in a single query
        questions = Test.objects.filter(course=course).select_related('course').prefetch_related('question_answers')
        question_map = {question.id: question for question in questions}

        # Fetch all answers for the course's questions
        answers = TestAnswer.objects.filter(question__in=questions)
        answer_map = {answer.id: answer for answer in answers}

        with transaction.atomic():
            for item in serializer.validated_data:
                question_id = item['question']
                answer_id = item['answer']

                # Validate question and answer from preloaded data
                question = question_map.get(question_id)
                answer = answer_map.get(answer_id)

                if not question:
                    return Response({'error': f"Question {question_id} not found in course.", 'ok': False},
                                    status=status.HTTP_404_NOT_FOUND)
                if not answer or answer.question.id != question_id:
                    return Response({'error': f"Answer {answer_id} not valid for question {question_id}.", 'ok': False},
                                    status=status.HTTP_404_NOT_FOUND)

                # Create TestResult using the save logic in the model
                test_result = TestResult(
                    course=course,
                    question=question,
                    answer=answer,
                    user=request.user  # Assuming user is passed in request
                )
                test_result.save()

        return Response({'result': course.test_result(request.user), 'ok': True}, status=status.HTTP_200_OK)
