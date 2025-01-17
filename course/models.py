from django.db import models
from abstarct_model.base_model import BaseModel
from ckeditor.fields import RichTextField
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from django.utils.functional import cached_property
from django.contrib.auth.hashers import make_password

class User(BaseModel):
    first_name = models.CharField(max_length=250)
    last_name = models.CharField(max_length=250)
    phone_number = models.CharField(max_length=14)
    password = models.CharField(max_length=250)

    def save(self, *args, **kwargs):
        # Check if the password is being set or updated
        if self.pk is None or 'password' in self.get_dirty_fields():
            # Hash the password before saving
            self.password = make_password(self.password)

        # Call the parent class's save method
        super().save(*args, **kwargs)

    def __str__(self):
        return self.first_name + " " + self.last_name


class CourseCategory(BaseModel):
    name = models.CharField(max_length=250)

    def __str__(self):
        return self.name


class Course(BaseModel):
    title = models.CharField(max_length=250)
    category = models.ForeignKey(CourseCategory, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="course/images/")
    description = RichTextField()
    video = models.URLField(null=True, blank=True)
    students = models.ManyToManyField(User, related_name="courses", blank=True)
    homework = models.FileField(upload_to="course/homework/")
    is_published = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    @cached_property
    def student_count(self):
        return self.students.count()

    def student_subscription(self, user):
        return self.students.filter(id=user.id).exists()

    def test_result(self, user):
        correct_answers = self.course_test_results.filter(user=user, is_correct=True).count()
        total_questions = self.tests.count()
        if total_questions == 0:
            return None
        if self.course_test_results.filter(user=user).exists():
            return (correct_answers / total_questions) * 100
        return None

    def student_homework_check(self, user):
        return self.homeworks_course.filter(user=user).exists()


# Signalni sozlash
@receiver(m2m_changed, sender=Course.students.through)
def update_student_count_cache(sender, instance, action, **kwargs):
    if action in ["post_add", "post_remove", "post_clear"]:
        if hasattr(instance, "student_count"):
            del instance.student_count


class AdditionalMaterials(BaseModel):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="additional_materials")
    name = models.CharField(max_length=250)
    file = models.FileField(upload_to="course/additional_materials/")

    def __str__(self):
        return self.name


class CourseHomework(BaseModel):
    file = models.FileField(upload_to="course/homework/")
    user = models.ForeignKey(User, related_name="homeworks_user", on_delete=models.CASCADE)
    course = models.ForeignKey(Course, related_name="homeworks_course", on_delete=models.CASCADE)

    def __str__(self):
        return f"user: {self.user.id} {self.user.first_name} -> course: {self.course.title}"


class Test(BaseModel):
    question = RichTextField()
    course = models.ForeignKey(Course, related_name="tests", on_delete=models.CASCADE)

    def __str__(self):
        return self.course.title + " " + str(self.id)


class TestAnswer(BaseModel):
    question = models.ForeignKey(Test, related_name="question_answers", on_delete=models.CASCADE)
    answer = models.TextField(max_length=500)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.question.course.title


class TestResult(BaseModel):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="course_test_results")
    question = models.ForeignKey(Test, related_name="test_results", on_delete=models.CASCADE)
    answer = models.ForeignKey(TestAnswer, related_name="test_results", on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name="test_results", on_delete=models.CASCADE)
    is_correct = models.BooleanField(default=False)


    def save(self, *args, **kwargs):
        # Automatically set is_correct based on the TestAnswer's is_correct
        self.is_correct = self.answer.is_correct
        super().save(*args, **kwargs)

    def __str__(self):
        return f"user: {self.user.id} {self.user.first_name} -> course: {self.question.course.title}"
