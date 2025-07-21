# urls.py

from django.urls import path
from . import views
from .views import ProductView, OrderView, AddCoinsView2, AddCoinView

urlpatterns = [
    # --------- Director ---------
    path('api/login/', views.LoginView.as_view()),
    path('director/dashboard/', views.director_dashboard),

    path('director/teachers/', views.director_teachers),
    path('director/teachers/<int:pk>/', views.director_teacher_detail),

    path('director/students/', views.director_students_list_create),
    path('director/students/<int:pk>/', views.director_student_detail),

    path('director/courses/', views.director_courses_list_create),
    path('director/courses/<int:pk>/', views.director_course_detail),

    path('director/modules/', views.director_modules_list_create),
    path('director/modules/<int:pk>/', views.director_module_detail),

    path('director/topics/', views.director_topics_list_create),
    path('director/topics/<int:pk>/', views.director_topic_detail),

    path('director/groups/', views.director_groups_list_create),
    path('director/groups/<int:pk>/', views.director_group_detail),

    # --------- Teacher ---------
    path('teacher/dashboard/', views.teacher_dashboard),
    path('teacher/group/<int:group_id>/attendance/', views.teacher_group_attendance),
    path('teacher/group/<int:group_id>/module/<int:module_id>/topics/', views.teacher_topics_manage),

    # --------- Student ---------
    path('student/dashboard/', views.student_dashboard),
    path('student/course/<int:course_id>/modules/', views.student_course_modules),
    path('student/module/<int:module_id>/topics/', views.student_module_topics),
    path('coins/', AddCoinsView2.as_view()),
    path('products/', ProductView.as_view()),
    path('orders/', OrderView.as_view()),
    path('coin_add/', AddCoinView.as_view()),
]

