from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
User=get_user_model()
class RegistrationTests(TestCase):
 def test_patient_registers(self):
  r=APIClient().post("/api/auth/register/",{"username":"pat","first_name":"Pat","email":"pat@example.com","role":"patient","password":"SafePass123!"},format="json")
  self.assertEqual(r.status_code,201)
 def test_admin_public_registration_blocked(self):
  r=APIClient().post("/api/auth/register/",{"username":"admin","first_name":"Admin","email":"admin@example.com","role":"admin","password":"SafePass123!"},format="json")
  self.assertEqual(r.status_code,400)
