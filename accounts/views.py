from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import Department, Organization
from .permissions import IsBackofficeUser
from .serializers import (
    DepartmentSerializer,
    OrganizationSerializer,
    RegisterSerializer,
    UserSerializer,
)

User = get_user_model()


class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user, context={'request': request}).data)


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.select_related('department').all().order_by('first_name', 'username')
    serializer_class = UserSerializer
    permission_classes = [IsBackofficeUser]
    search_fields = ['username', 'email', 'first_name', 'last_name', 'job_title']
    filterset_fields = ['role', 'department', 'is_staff_member']


class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsBackofficeUser]
    lookup_field = 'slug'
    search_fields = ['name', 'slug']


class OrganizationViewSet(viewsets.ModelViewSet):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'
    search_fields = ['name', 'slug']

    def get_permissions(self):
        if self.action in ('create', 'update', 'partial_update', 'destroy'):
            return [IsBackofficeUser()]
        return super().get_permissions()
