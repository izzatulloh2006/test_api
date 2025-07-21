from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


class UserManager(BaseUserManager):
    def create_user(self, phone, full_name, password=None, role=None):
        if not phone:
            raise ValueError("User must have a phone number")
        user = self.model(phone=phone, full_name=full_name, role=role)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, full_name, password):
        user = self.create_user(phone, full_name, password, role='director')
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('director', 'Director'),
        ('teacher', 'Teacher'),
        ('student', 'Student'),
    ]

    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=15, unique=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    age = models.PositiveIntegerField(null=True, blank=True)
    GENDER_CHOICES = [('male', 'Male'), ('female', 'Female')]
    gender = models.CharField(max_length=6, choices=GENDER_CHOICES, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    coins = models.PositiveIntegerField(default=0)

    objects = UserManager()

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ['full_name']

    def __str__(self):
        return f"{self.full_name} ({self.role})"


class Course(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Module(models.Model):
    name = models.CharField(max_length=255)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} ({self.course.name})"


class Topic(models.Model):
    STATUS_CHOICES = [('is_active', 'Active'), ('in_active', 'Inactive')]
    name = models.CharField(max_length=255)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='in_active')
    module = models.ForeignKey(Module, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Day(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Group(models.Model):
    name = models.CharField(max_length=255)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'teacher'})
    days = models.ManyToManyField(Day)
    start_date = models.DateField()
    end_date = models.DateField()
    students = models.ManyToManyField(User, related_name='student_groups', limit_choices_to={'role': 'student'})

    def __str__(self):
        return self.name


class Attendance(models.Model):
    STATUS_CHOICES = [('keldi', 'Keldi'), ('kelmadi', 'Kelmadi')]

    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    student = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'student'})
    date = models.DateField()  # новая дата
    status = models.CharField(max_length=8, choices=STATUS_CHOICES)

    class Meta:
        unique_together = ('group', 'student', 'date')

    def __str__(self):
        return f"{self.student.full_name} - {self.date} - {self.status}"


class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price = models.PositiveIntegerField()
    added_by = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'director'})
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.price} coins"


class Order(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    student = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'student'})
    ordered_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.full_name} ordered {self.product.name}"
