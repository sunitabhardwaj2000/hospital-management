from django.core.management.base import BaseCommand
from core.models import Department
class Command(BaseCommand):
 help="Create common hospital departments"
 def handle(self,*args,**kwargs):
  for name,desc in [("Cardiology","Heart care"),("Neurology","Brain and nervous system"),("Pediatrics","Children's healthcare"),("Orthopedics","Bones and joints"),("Dermatology","Skin care"),("General Medicine","General health")]:
   Department.objects.get_or_create(name=name,defaults={"description":desc})
  self.stdout.write(self.style.SUCCESS("Departments ready"))
