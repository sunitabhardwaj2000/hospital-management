from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User,Department,DoctorProfile,PatientProfile,Appointment,Prescription,Notification
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display=("email","first_name","last_name","role","is_approved","is_active","is_staff")
    list_filter=("role","is_approved","is_active"); search_fields=("email","first_name","last_name"); ordering=("email",)
    fieldsets=BaseUserAdmin.fieldsets+(("Hospital access",{"fields":("role","phone","is_approved")}),)
    add_fieldsets=BaseUserAdmin.add_fieldsets+(("Hospital access",{"fields":("email","role","phone","is_approved")}),)
@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin): list_display=("name","is_active"); search_fields=("name",)
@admin.register(DoctorProfile)
class DoctorProfileAdmin(admin.ModelAdmin): list_display=("user","department","specialization","consultation_fee")
@admin.register(PatientProfile)
class PatientProfileAdmin(admin.ModelAdmin): list_display=("user","age","gender")
@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin): list_display=("patient","doctor","appointment_date","appointment_time","status"); list_filter=("status","appointment_date")
admin.site.register(Prescription); admin.site.register(Notification)
