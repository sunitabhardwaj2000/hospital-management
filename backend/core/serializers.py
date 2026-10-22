from rest_framework import serializers
from django.contrib.auth import authenticate
from django.db import transaction
from .models import User, Department, DoctorProfile, PatientProfile, Appointment, Prescription, Notification

class RegisterSerializer(serializers.ModelSerializer):
    password=serializers.CharField(write_only=True,min_length=8)
    class Meta:
        model=User
        fields=["id","username","first_name","last_name","email","phone","role","password"]
    def validate_role(self,role):
        if role not in ("patient","doctor"): raise serializers.ValidationError("Only patient and doctor public registration is allowed.")
        return role
    @transaction.atomic
    def create(self,data):
        password=data.pop("password"); role=data["role"]
        user=User(**data,is_approved=(role=="patient"))
        user.set_password(password); user.save()
        if role=="patient": PatientProfile.objects.create(user=user)
        else: DoctorProfile.objects.create(user=user)
        return user

class LoginSerializer(serializers.Serializer):
    email=serializers.EmailField(); password=serializers.CharField(write_only=True)
    def validate(self,data):
        user=authenticate(username=data["email"],password=data["password"])
        if not user or not user.is_active: raise serializers.ValidationError("Invalid email/password or inactive account.")
        if user.role=="doctor" and not user.is_approved: raise serializers.ValidationError("Doctor account is awaiting admin approval.")
        data["user"]=user; return data

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta: model=Department; fields=["id","name","description","is_active"]

class DoctorSerializer(serializers.ModelSerializer):
    user_id=serializers.IntegerField(source="user.id",read_only=True)
    name=serializers.SerializerMethodField()
    email=serializers.EmailField(source="user.email",read_only=True)
    department=serializers.CharField(source="department.name",read_only=True)
    class Meta:
        model=DoctorProfile
        fields=["id","user_id","name","email","department","specialization","qualifications","experience_years","consultation_fee","bio"]
    def get_name(self,obj): return obj.user.get_full_name() or obj.user.email

class AppointmentSerializer(serializers.ModelSerializer):
    patient_name=serializers.SerializerMethodField(); doctor_name=serializers.SerializerMethodField()
    class Meta:
        model=Appointment
        fields=["id","patient","patient_name","doctor","doctor_name","appointment_date","appointment_time","reason","status","created_at"]
        read_only_fields=["patient","status","created_at"]
    def get_patient_name(self,obj): return obj.patient.get_full_name() or obj.patient.email
    def get_doctor_name(self,obj): return obj.doctor.get_full_name() or obj.doctor.email
    def validate_doctor(self,value):
        if value.role!="doctor" or not value.is_approved or not value.is_active: raise serializers.ValidationError("Choose an approved doctor.")
        return value
    def validate(self,data):
        from datetime import date
        if self.context["request"].user.role!="patient": raise serializers.ValidationError("Only patients can book appointments.")
        if data["appointment_date"]<date.today(): raise serializers.ValidationError("Date cannot be in the past.")
        return data
    def create(self,data):
        data["patient"]=self.context["request"].user
        return super().create(data)

class AppointmentStatusSerializer(serializers.Serializer):
    status=serializers.ChoiceField(choices=["confirmed","completed","cancelled","rejected"])

class PrescriptionSerializer(serializers.ModelSerializer):
    class Meta: model=Prescription; fields="__all__"
