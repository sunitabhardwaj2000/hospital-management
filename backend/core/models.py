from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

class User(AbstractUser):
    ROLE_CHOICES=[("patient","Patient"),("doctor","Doctor"),("admin","Admin")]
    email=models.EmailField(unique=True)
    role=models.CharField(max_length=12,choices=ROLE_CHOICES,default="patient")
    phone=models.CharField(max_length=20,blank=True)
    is_approved=models.BooleanField(default=False)
    USERNAME_FIELD="email"
    REQUIRED_FIELDS=["username"]
    def __str__(self): return f"{self.email} ({self.role})"

class Department(models.Model):
    name=models.CharField(max_length=100,unique=True)
    description=models.TextField(blank=True)
    is_active=models.BooleanField(default=True)
    def __str__(self): return self.name

class DoctorProfile(models.Model):
    user=models.OneToOneField(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name="doctor_profile")
    department=models.ForeignKey(Department,on_delete=models.SET_NULL,null=True,blank=True,related_name="doctors")
    specialization=models.CharField(max_length=120,blank=True)
    qualifications=models.CharField(max_length=200,blank=True)
    experience_years=models.PositiveSmallIntegerField(default=0)
    consultation_fee=models.DecimalField(max_digits=8,decimal_places=2,default=0)
    bio=models.TextField(blank=True)
    def __str__(self): return self.user.email

class PatientProfile(models.Model):
    user=models.OneToOneField(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name="patient_profile")
    age=models.PositiveSmallIntegerField(null=True,blank=True)
    gender=models.CharField(max_length=30,blank=True)
    address=models.TextField(blank=True)
    def __str__(self): return self.user.email

class Appointment(models.Model):
    STATUS=[("pending","Pending"),("confirmed","Confirmed"),("completed","Completed"),("cancelled","Cancelled"),("rejected","Rejected")]
    patient=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name="patient_appointments")
    doctor=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name="doctor_appointments",limit_choices_to={"role":"doctor"})
    appointment_date=models.DateField()
    appointment_time=models.TimeField()
    reason=models.TextField()
    status=models.CharField(max_length=12,choices=STATUS,default="pending")
    created_at=models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering=["appointment_date","appointment_time"]
        constraints=[models.UniqueConstraint(fields=["doctor","appointment_date","appointment_time"],name="unique_doctor_slot")]
    def __str__(self): return f"{self.patient.email} - {self.doctor.email} - {self.appointment_date}"

class Prescription(models.Model):
    appointment=models.OneToOneField(Appointment,on_delete=models.CASCADE,related_name="prescription")
    diagnosis=models.TextField()
    medicines=models.TextField()
    instructions=models.TextField(blank=True)
    created_at=models.DateTimeField(auto_now_add=True)

class Notification(models.Model):
    recipient=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name="notifications")
    message=models.CharField(max_length=250)
    is_read=models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True)
