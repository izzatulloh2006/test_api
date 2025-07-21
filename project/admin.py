from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User, Course, Module, Topic, Day, Group, Attendance, Order, Product


class CustomUserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm

    list_display = ('id', 'full_name', 'phone', 'role', 'age', 'gender', 'is_active', 'is_staff', 'coins')
    list_filter = ('role', 'gender', 'is_active', 'is_staff')
    search_fields = ('full_name', 'phone')
    ordering = ('id',)
    fieldsets = (
        (None, {'fields': ('phone', 'password')}),
        ('Personal info', {'fields': ('full_name', 'age', 'gender', 'role')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone', 'full_name', 'role', 'password1', 'password2'),
        }),
    )
    filter_horizontal = ('groups', 'user_permissions')


admin.site.register(User, CustomUserAdmin)


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'course')


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'status', 'module')
    list_filter = ('status',)


@admin.register(Day)
class DayAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'course', 'teacher', 'start_date', 'end_date')
    filter_horizontal = ('days', 'students')
    list_filter = ('course', 'teacher')

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('id', 'group', 'student', 'date', 'status')
    list_filter = ('status', 'date', 'group')
    search_fields = ('student__full_name', 'group__name')


@admin.register(Order)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['product', 'student', 'ordered_at']


@admin.register(Product)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'price', 'added_by', 'created_at']

