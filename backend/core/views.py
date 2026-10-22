from django.contrib.auth import get_user_model
from django.db.models import Count
from rest_framework import generics, permissions, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from .models import Department, DoctorProfile, Appointment, Prescription
from .serializers import RegisterSerializer, LoginSerializer, DepartmentSerializer, DoctorSerializer, AppointmentSerializer, AppointmentStatusSerializer, PrescriptionSerializer
User=get_user_model()

class RegisterView(generics.CreateAPIView):
    serializer_class=RegisterSerializer
    permission_classes=[permissions.AllowAny]

@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def login_view(request):
    s=LoginSerializer(data=request.data); s.is_valid(raise_exception=True); u=s.validated_data["user"]
    token,_=Token.objects.get_or_create(user=u)
    return Response({"token":token.key,"user":{"id":u.id,"name":u.get_full_name() or u.email,"email":u.email,"role":u.role}})

@api_view(["POST"])
def logout_view(request):
    Token.objects.filter(user=request.user).delete()
    return Response({"message":"Logged out"})

@api_view(["GET"])
def me_view(request):
    u=request.user
    return Response({"id":u.id,"name":u.get_full_name() or u.email,"email":u.email,"role":u.role,"phone":u.phone})

class DepartmentList(generics.ListAPIView):
    queryset=Department.objects.filter(is_active=True); serializer_class=DepartmentSerializer
    permission_classes=[permissions.AllowAny]

class DoctorList(generics.ListAPIView):
    serializer_class=DoctorSerializer; permission_classes=[permissions.AllowAny]
    def get_queryset(self): return DoctorProfile.objects.select_related("user","department").filter(user__role="doctor",user__is_approved=True,user__is_active=True)

class AppointmentViewSet(viewsets.ModelViewSet):
    serializer_class=AppointmentSerializer
    def get_queryset(self):
        u=self.request.user; q=Appointment.objects.select_related("patient","doctor")
        if u.is_superuser or u.role=="admin": return q
        if u.role=="doctor": return q.filter(doctor=u)
        return q.filter(patient=u)
    def get_permissions(self):
        if self.action in ("update","partial_update","destroy"): return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]
    def create(self,request,*args,**kwargs):
        if request.user.role!="patient": return Response({"detail":"Only patients can book."},status=403)
        return super().create(request,*args,**kwargs)
    @action(detail=True,methods=["post"])
    def cancel(self,request,pk=None):
        a=self.get_object()
        if request.user.role!="admin" and not request.user.is_superuser and a.patient_id!=request.user.id: return Response({"detail":"Not allowed."},status=403)
        if a.status not in ("pending","confirmed"): return Response({"detail":"This appointment cannot be cancelled."},status=400)
        a.status="cancelled"; a.save(); return Response(self.get_serializer(a).data)
    @action(detail=True,methods=["patch"],url_path="status")
    def update_status(self,request,pk=None):
        a=self.get_object()
        if request.user.role not in ("doctor","admin") and not request.user.is_superuser: return Response({"detail":"Doctor/admin only."},status=403)
        if request.user.role=="doctor" and a.doctor_id!=request.user.id: return Response({"detail":"Not your appointment."},status=403)
        s=AppointmentStatusSerializer(data=request.data); s.is_valid(raise_exception=True)
        a.status=s.validated_data["status"]; a.save(); return Response(self.get_serializer(a).data)

@api_view(["GET"])
def dashboard_summary(request):
    if request.user.role!="admin" and not request.user.is_superuser: return Response({"detail":"Admin access required."},status=403)
    return Response({"patients":User.objects.filter(role="patient").count(),"doctors":User.objects.filter(role="doctor").count(),"appointments":Appointment.objects.count(),"pending":Appointment.objects.filter(status="pending").count(),"completed":Appointment.objects.filter(status="completed").count(),"cancelled":Appointment.objects.filter(status="cancelled").count(),"by_status":list(Appointment.objects.values("status").annotate(total=Count("id")))})

class PrescriptionList(generics.ListCreateAPIView):
    serializer_class=PrescriptionSerializer
    permission_classes=[permissions.IsAuthenticated]
    def get_queryset(self):
        u=self.request.user; q=Prescription.objects.select_related("appointment")
        if u.is_superuser or u.role=="admin": return q
        if u.role=="doctor": return q.filter(appointment__doctor=u)
        return q.filter(appointment__patient=u)
    def perform_create(self,serializer):
        u=self.request.user; a=serializer.validated_data["appointment"]
        if u.role not in ("doctor","admin") and not u.is_superuser: from rest_framework.exceptions import PermissionDenied; raise PermissionDenied("Doctor/admin only.")
        if u.role=="doctor" and a.doctor_id!=u.id: from rest_framework.exceptions import PermissionDenied; raise PermissionDenied("Not your appointment.")
        serializer.save()
