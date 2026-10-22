from django.urls import path,include
from rest_framework.routers import DefaultRouter
from .views import RegisterView,login_view,logout_view,me_view,DepartmentList,DoctorList,AppointmentViewSet,dashboard_summary,PrescriptionList
router=DefaultRouter(); router.register("appointments",AppointmentViewSet,basename="appointments")
urlpatterns=[
 path("auth/register/",RegisterView.as_view()),path("auth/login/",login_view),path("auth/logout/",logout_view),path("auth/me/",me_view),
 path("departments/",DepartmentList.as_view()),path("doctors/",DoctorList.as_view()),path("dashboard/summary/",dashboard_summary),
 path("prescriptions/",PrescriptionList.as_view()),path("",include(router.urls))]
