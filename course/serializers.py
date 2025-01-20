from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from .models import User, CourseCategory, Course, AdditionalMaterials, TestAnswer, Test, TestResult, CourseHomework


class LoginSerializer(serializers.Serializer):
    password = serializers.CharField(required=True)
    phone_number = serializers.CharField(required=True)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'phone_number', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def validate_phone_number(self, value):
        # Foydalanuvchini filtrlash uchun queryset yarating
        queryset = User.objects.filter(phone_number=value)

        # Agar instance mavjud bo'lsa (update uchun), o'zini chetlab o'ting
        if self.instance:
            queryset = queryset.exclude(id=self.instance.id)

        # Agar raqam boshqa foydalanuvchida mavjud bo'lsa, xatolik ko'tarish
        if queryset.exists():
            raise serializers.ValidationError('Phone number already exists')

        return value

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if 'password' in validated_data:
            validated_data['password'] = make_password(validated_data['password'])

        return super().update(instance, validated_data)


class CourseCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseCategory
        fields = ('id', 'name')


class AdditionalMaterialsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdditionalMaterials
        fields = ('id', 'name', 'file')


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ('id', 'title', 'category', 'image', 'description', 'video', 'homework', 'created_at')

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['views_count'] = instance.student_count
        return ret


class CourseRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ('id', 'title', 'category', 'image', 'description', 'video', 'homework', 'created_at')

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['category'] = instance.category.name
        ret['views_count'] = instance.student_count
        ret['student_subscription'] = instance.student_subscription(self.context['request'].user)
        ret['student_homework'] = instance.student_homework_check(self.context['request'].user)
        ret['test_result'] = instance.test_result(self.context['request'].user)
        ret['additional_materials'] = AdditionalMaterialsSerializer(instance.additional_materials, many=True).data
        ret['questions'] = TestSerializer(instance.tests, many=True, context=self.context).data
        return ret


class TestAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestAnswer
        fields = ('id', 'answer')


class TestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Test
        fields = ('id', 'question',)

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['answers'] = TestAnswerSerializer(instance.question_answers, many=True).data
        return ret


class TestResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestResult
        fields = ('id', 'question', 'answer', 'user', 'is_correct')


class CourseHomeworkSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseHomework
        fields = ('id', 'file', 'user', 'course')


class QuizAnswerSerializer(serializers.Serializer):
    question = serializers.IntegerField()
    answer = serializers.IntegerField()
