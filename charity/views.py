from rest_framework.response import Response
from rest_framework.decorators import api_view

from .models import Charity
from .serializers import CharitySerializer

from django.shortcuts import get_object_or_404

# Create your views here.
@api_view(['GET'])
def charity_list(request):
    if request.method == 'GET':
        charity = Charity.objects.all()
        serializer = CharitySerializer(charity, many=True)
        return Response(data=serializer.data)
        
@api_view(['GET'])
def charity_detail(request, id):
    charity = get_object_or_404(Charity, charity_id=id)

    if request.method == 'GET':
        serializer = CharitySerializer(charity)
        return Response(serializer.data)