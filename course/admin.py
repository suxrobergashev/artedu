from django.contrib import admin
from django.contrib.auth.hashers import make_password

from .models import User, Course, CourseCategory, Test, TestAnswer, TestResult, AdditionalMaterials


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'last_name', 'first_name', 'phone_number')
    list_display_links = ('id', 'last_name', 'first_name')
    search_fields = ('last_name', 'first_name', 'phone_number')
    list_filter = ('last_name', 'first_name', 'created_at')

    def save_model(self, request, obj, form, change):
        # Check if this is a new user or if the password is being updated
        if not obj.pk or 'password' in form.changed_data:
            obj.password = make_password(obj.password)

        # Call the parent class's save_model method
        super().save_model(request, obj, form, change)



@admin.register(CourseCategory)
class CourseCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    list_display_links = ('id', 'name')



class AdditionalMaterialsAdminInline(admin.TabularInline):
    model = AdditionalMaterials
    extra = 0

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('id', 'title')
    list_display_links = ('id', 'title')
    search_fields = ('title', 'description')
    list_filter = ('title', 'created_at')
    inlines = [AdditionalMaterialsAdminInline]

class TestAnswerAdminInline(admin.TabularInline):
    model = TestAnswer
    extra = 0


@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    list_display = ('id', 'course',)
    inlines = [TestAnswerAdminInline]


@admin.register(TestResult)
class TestResultAdmin(admin.ModelAdmin):
    list_display = ('id', 'course', 'question')
