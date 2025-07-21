# serializers.py
from django.contrib.auth.management.commands.changepassword import UserModel
from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate
from .models import *

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'phone', 'full_name', 'password', 'role', 'age', 'gender')
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

class LoginSerializer(serializers.Serializer):
    phone = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        phone = data.get('phone')
        password = data.get('password')
        user = authenticate(phone=phone, password=password)
        if not user:
            raise serializers.ValidationError("Invalid phone number or password")
        data['user'] = user
        return data

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ('id', 'name')

class ModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Module
        fields = ('id', 'name', 'course')

class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = ('id', 'name', 'status', 'module')

class DaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Day
        fields = ('id', 'name')

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('id', 'name', 'course', 'teacher', 'days', 'start_date', 'end_date', 'students')

class AttendanceSerializer(serializers.ModelSerializer):
    student = serializers.PrimaryKeyRelatedField(queryset=User.objects.filter(role='student'))
    group = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all())

    class Meta:
        model = Attendance
        fields = ['id', 'student', 'group', 'date', 'status']





class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price']

class OrderSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Order
        fields = ['id', 'product_id', 'ordered_at']

    def validate(self, data):
        user = self.context['request'].user
        if user.role != 'student':
            raise serializers.ValidationError("Faqat studentlar zakaz bera oladi.")

        try:
            product = Product.objects.get(id=data['product_id'])
        except Product.DoesNotExist:
            raise serializers.ValidationError("Mahsulot topilmadi.")

        if user.coins < product.price:
            raise serializers.ValidationError("Yetarli coins yo‘q.")

        data['product'] = product
        return data

    def create(self, validated_data):
        user = self.context['request'].user
        product = validated_data['product']

        # coinsni kamaytirish
        user.coins -= product.price
        user.save()

        return Order.objects.create(product=product, student=user)




class AddCoinSerializer(serializers.Serializer):
    student_id = serializers.IntegerField()
    amount = serializers.IntegerField()

    def validate(self, data):
        user = self.context['request'].user
        if user.role not in ['director', 'teacher']:
            raise serializers.ValidationError("Faqat teacher yoki director coin qo‘sha oladi.")
        try:
            student = User.objects.get(id=data['student_id'])
        except User.DoesNotExist:
            raise serializers.ValidationError("Student topilmadi.")
        data['student'] = student
        return data

    def save(self):
        student = self.validated_data['student']
        amount = self.validated_data['amount']
        student.coins += amount
        student.save()
        return student