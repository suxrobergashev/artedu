from django.contrib import admin
from .models import User, Course, CourseCategory, Test, TestAnswer, TestResult


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'last_name', 'first_name', 'phone_number')
    list_display_links = ('id', 'last_name', 'first_name')
    search_fields = ('last_name', 'first_name', 'phone_number')
    list_filter = ('last_name', 'first_name', 'created_at')


@admin.register(CourseCategory)
class CourseCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    list_display_links = ('id', 'name')


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('id', 'title')
    list_display_links = ('id', 'title')
    search_fields = ('title', 'description')
    list_filter = ('title', 'created_at')


class TestAnswerAdminInline(admin.TabularInline):
    model = TestAnswer
    extra = 0


@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    list_display = ('id', 'course', 'question')
    inlines = [TestAnswerAdminInline]

@admin.register(TestResult)
class TestResultAdmin(admin.ModelAdmin):
    list_display = ('id', 'course', 'question')