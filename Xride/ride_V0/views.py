from rest_framework import viewsets
from .models import Car
from .serializers import CarSerializer
from django.http import HttpResponse
from rest_framework.permissions import IsAuthenticated


class CarViewSet(viewsets.ModelViewSet):
    queryset = Car.objects.all()
    serializer_class = CarSerializer
    permission_classes = [IsAuthenticated] 

# Create your views here.
def home(request):
    
    return HttpResponse('html_content')   