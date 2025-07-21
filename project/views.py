from drf_yasg import openapi
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .permissions import IsDirector, IsTeacher, IsStudent
from .models import *
from .serializers import *
from rest_framework import status
from django.contrib.auth import authenticate, login
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from datetime import datetime, timedelta
import calendar
from drf_yasg.utils import swagger_auto_schema

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        login(request, user)

        if user.role == 'director':
            dashboard = '/director/dashboard/'
        elif user.role == 'teacher':
            dashboard = '/teacher/dashboard/'
        else:
            dashboard = '/student/dashboard/'

        return Response({
            'message': 'Login successful',
            'redirect': dashboard,
            'user_id': user.id,
            'role': user.role
        }, status=status.HTTP_200_OK)

# ---------------------- DIRECTOR ----------------------

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsDirector])
def director_dashboard(request):
    return Response({
        "teachers": User.objects.filter(role='teacher').count(),
        "students": User.objects.filter(role='student').count(),
        "courses": Course.objects.count(),
        "modules": Module.objects.count(),
        "topics": Topic.objects.count(),
        "groups": Group.objects.count(),
    })

def generate_crud_viewset(model_class, serializer_class):
    @api_view(['GET', 'POST'])
    @permission_classes([IsAuthenticated, IsDirector])
    def list_create(request):
        if request.method == 'GET':
            items = model_class.objects.all()
            return Response(serializer_class(items, many=True).data)
        elif request.method == 'POST':
            serializer = serializer_class(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=201)
            return Response(serializer.errors, status=400)

    @api_view(['GET', 'PUT', 'DELETE'])
    @permission_classes([IsAuthenticated, IsDirector])
    def detail(request, pk):
        try:
            item = model_class.objects.get(pk=pk)
        except model_class.DoesNotExist:
            return Response(status=404)

        if request.method == 'GET':
            return Response(serializer_class(item).data)
        elif request.method == 'PUT':
            serializer = serializer_class(item, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=400)
        elif request.method == 'DELETE':
            item.delete()
            return Response(status=204)

    return list_create, detail

director_courses_list_create, director_course_detail = generate_crud_viewset(Course, CourseSerializer)
director_modules_list_create, director_module_detail = generate_crud_viewset(Module, ModuleSerializer)
director_topics_list_create, director_topic_detail = generate_crud_viewset(Topic, TopicSerializer)
director_groups_list_create, director_group_detail = generate_crud_viewset(Group, GroupSerializer)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated, IsDirector])
def director_students_list_create(request):
    if request.method == 'GET':
        students = User.objects.filter(role='student')
        serializer = UserSerializer(students, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        data = request.data.copy()
        data['role'] = 'student'
        serializer = UserSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated, IsDirector])
def director_student_detail(request, pk):
    try:
        student = User.objects.get(pk=pk, role='student')
    except User.DoesNotExist:
        return Response(status=404)

    if request.method == 'GET':
        return Response(UserSerializer(student).data)
    elif request.method == 'PUT':
        serializer = UserSerializer(student, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)
    elif request.method == 'DELETE':
        student.delete()
        return Response(status=204)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated, IsDirector])
def director_teachers(request):
    if request.method == 'GET':
        teachers = User.objects.filter(role='teacher')
        serializer = UserSerializer(teachers, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        data = request.data.copy()
        data['role'] = 'teacher'
        serializer = UserSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated, IsDirector])
def director_teacher_detail(request, pk):
    try:
        teacher = User.objects.get(pk=pk, role='teacher')
    except User.DoesNotExist:
        return Response(status=404)

    if request.method == 'GET':
        return Response(UserSerializer(teacher).data)
    elif request.method == 'PUT':
        serializer = UserSerializer(teacher, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)
    elif request.method == 'DELETE':
        teacher.delete()
        return Response(status=204)

# ---------------------- TEACHER ----------------------

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsTeacher])
def teacher_dashboard(request):
    groups = Group.objects.filter(teacher=request.user)
    return Response({
        "full_name": request.user.full_name,
        "group_count": groups.count(),
        "groups": GroupSerializer(groups, many=True).data
    })


@api_view(['GET', 'POST'])
@permission_classes([IsTeacher])
def teacher_group_attendance(request, group_id):
    try:
        group = Group.objects.get(pk=group_id, teacher=request.user)
    except Group.DoesNotExist:
        return Response({'error': 'Group not found'}, status=status.HTTP_404_NOT_FOUND)

    group_days = group.days.all()
    group_day_names = [day.name.lower() for day in group_days]
    start_date = group.start_date
    end_date = group.end_date

    # Get all valid lesson dates for the group
    lesson_dates = []
    current_date = start_date
    while current_date <= end_date:
        weekday_name = calendar.day_name[current_date.weekday()].lower()
        if weekday_name in group_day_names:
            lesson_dates.append(current_date)
        current_date += timedelta(days=1)

    students = group.students.all()
    attendance_records = Attendance.objects.filter(group=group)

    if request.method == 'GET':
        result = {}
        for student in students:
            result[student.full_name] = {}
            for date_obj in lesson_dates:
                formatted_date = date_obj.strftime('%d.%m.%Y')
                att = attendance_records.filter(student=student, date=date_obj).first()
                result[student.full_name][formatted_date] = att.status if att else None

        return Response({
            'group_id': group.id,
            'group_name': group.name,
            'dates': [d.strftime('%d.%m.%Y') for d in lesson_dates],
            'attendance': result
        })

    elif request.method == 'POST':
        student_id = request.data.get('student_id')
        date_str = request.data.get('date')
        status_value = request.data.get('status')

        if not all([student_id, date_str, status_value]):
            return Response({'error': 'Missing required fields'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            student = students.get(id=student_id)
        except User.DoesNotExist:
            return Response({'error': 'Student not found in group'}, status=status.HTTP_404_NOT_FOUND)

        try:
            date_obj = datetime.strptime(date_str, '%d.%m.%Y').date()
            weekday_name = calendar.day_name[date_obj.weekday()].lower()
            if date_obj < start_date or date_obj > end_date or weekday_name not in group_day_names:
                return Response({'error': 'Date not valid for group schedule'}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError:
            return Response({'error': 'Invalid date format. Use dd.mm.yyyy'}, status=status.HTTP_400_BAD_REQUEST)

        if status_value.lower() not in ['keldi', 'kelmadi']:
            return Response({'error': 'Invalid status. Use Keldi or Kelmadi'}, status=status.HTTP_400_BAD_REQUEST)

        attendance, created = Attendance.objects.update_or_create(
            student=student,
            group=group,
            date=date_obj,
            defaults={'status': status_value.lower()}
        )

        return Response({
            'message': 'Attendance recorded' if created else 'Attendance updated',
            'student': student.full_name,
            'date': date_str,
            'status': status_value
        }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated, IsTeacher])
def teacher_topics_manage(request, group_id, module_id):
    try:
        group = Group.objects.get(id=group_id, teacher=request.user)
        module = Module.objects.get(id=module_id, course=group.course)
    except (Group.DoesNotExist, Module.DoesNotExist):
        return Response(status=404)

    if request.method == 'GET':
        topics = Topic.objects.filter(module=module)
        return Response(TopicSerializer(topics, many=True).data)
    elif request.method == 'POST':
        topic_id = request.data.get('topic_id')
        status_val = request.data.get('status')
        try:
            topic = Topic.objects.get(id=topic_id, module=module)
            topic.status = status_val
            topic.save()
            return Response({"status": "updated"})
        except Topic.DoesNotExist:
            return Response(status=404)

# ---------------------- STUDENT ----------------------

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsStudent])
def student_dashboard(request):
    groups = request.user.groups.all()
    courses = [group.course for group in groups]
    return Response(CourseSerializer(courses, many=True).data)

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsStudent])
def student_course_modules(request, course_id):
    modules = Module.objects.filter(course_id=course_id)
    return Response(ModuleSerializer(modules, many=True).data)

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsStudent])
def student_module_topics(request, module_id):
    student = request.user

    # Получаем группы, где состоит студент
    student_groups = student.student_groups.select_related('course', 'teacher')

    # Получаем все пары (course_id, teacher_id), к которым принадлежит студент
    allowed_course_teacher_pairs = set(
        (group.course_id, group.teacher_id) for group in student_groups
    )

    # Получаем топики, которые is_active, и модуль которых связан с нужной парой (курс+преподаватель)
    topics = Topic.objects.filter(
        status='is_active',
        module_id=module_id,
    ).select_related('module', 'module__course')

    # Фильтруем вручную по allowed (course, teacher)
    filtered_topics = [
        topic for topic in topics
        if (topic.module.course_id, topic.module.course.group_set.first().teacher_id) in allowed_course_teacher_pairs
    ]

    return Response(TopicSerializer(filtered_topics, many=True).data)



class AddCoinsView2(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=OrderSerializer,
        operation_description="Mahsulot zakaz qilish (student uchun)",
        responses={201: openapi.Response('Zakaz yaratildi', OrderSerializer)}
    )
    def post(self, request):
        if request.user.role not in ['director', 'teacher']:
            return Response({"error": "Ruxsat yo‘q!"}, status=status.HTTP_403_FORBIDDEN)

        student_id = request.data.get("student_id")
        amount = int(request.data.get("amount", 0))

        try:
            student = User.objects.get(id=student_id, role='student')
            student.coins += amount
            student.save()
            return Response({"msg": f"{student.full_name} ga {amount} coins qo‘shildi."})
        except User.DoesNotExist:
            return Response({"error": "Student topilmadi."}, status=status.HTTP_404_NOT_FOUND)

    def get(self, request):
        if request.user.role not in ['director', 'teacher']:
            return Response({"error": "Ruxsat yo‘q!"}, status=status.HTTP_403_FORBIDDEN)

        students = User.objects.filter(role='student')
        data = [
            {"id": s.id, "full_name": s.full_name, "coins": s.coins}
            for s in students
        ]
        return Response(data)


class ProductView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=ProductSerializer,
        operation_description="Mahsulot zakaz qilish (student uchun)",
        responses={201: openapi.Response('Zakaz yaratildi', OrderSerializer)}
    )
    def post(self, request):
        if request.user.role != 'director':
            return Response({"error": "Faqat direktor mahsulot qo‘shadi!"}, status=403)

        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(added_by=request.user)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    def get(self, request):
        products = Product.objects.all().order_by('-created_at')
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)



class OrderView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=OrderSerializer,
        operation_description="Mahsulot zakaz qilish (student uchun)",
        responses={201: openapi.Response('Zakaz yaratildi', OrderSerializer)}
    )
    def post(self, request):
        if request.user.role != 'student':
            return Response({"error": "Faqat student zakaz qila oladi."}, status=403)

        serializer = OrderSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            order = serializer.save()
            return Response({"msg": "Zakaz muvaffaqiyatli qo‘shildi!"}, status=201)
        return Response(serializer.errors, status=400)

    def get(self, request):
        user = request.user
        if user.role in ['teacher', 'director']:
            orders = Order.objects.all().order_by('-ordered_at')
        elif user.role == 'student':
            orders = Order.objects.filter(student=user).order_by('-ordered_at')
        else:
            return Response({"error": "Ruxsat yo‘q!"}, status=403)

        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)


class AddCoinView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=AddCoinSerializer,
        operation_description="Mahsulot zakaz qilish (student uchun)",
        responses={201: openapi.Response('Zakaz yaratildi', AddCoinSerializer)}
    )
    def post(self, request):
        serializer = AddCoinSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            student = serializer.save()
            return Response({'msg': f"{serializer.validated_data['amount']} coin qo‘shildi", 'balance': student.coins})
        return Response(serializer.errors, status=400)