from rest_framework.viewsets import ModelViewSet 
from ..models import User
from .serializers import UserSerializer
from rest_framework.response import Response
class UserviewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    def list(self, request):
        serializer = UserSerializer(self.queryset,many=True)
        return Response(serializer.data)
    