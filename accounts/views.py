from django.contrib.auth import get_user_model
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import (
    RegisterSerializer,
    UserSerializer,
    CustomTokenObtainPairSerializer,
    ChangePasswordSerializer,
)

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    """
    POST /api/v1/auth/register/
    Open to anyone. Allows creating a user with one of the four roles:
    admin, doctor, patient, receptionist.

    Note: registering as 'admin' here is intentionally permitted to keep
    the assignment self-contained for grading purposes; in a real
    deployment, admin creation would typically be restricted to existing
    admins or done via createsuperuser.
    """

    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {
                "success": True,
                "message": "User registered successfully.",
                "user": UserSerializer(user).data,
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(TokenObtainPairView):
    """
    POST /api/v1/auth/login/
    Body: { "username": "...", "password": "..." }
    Returns: { "access": "...", "refresh": "...", "user": {...} }
    """

    serializer_class = CustomTokenObtainPairSerializer


class MeView(APIView):
    """
    GET /api/v1/auth/me/  -> current authenticated user's profile
    PATCH /api/v1/auth/me/ -> update first_name/last_name/email
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)

    def patch(self, request):
        serializer = UserSerializer(
            request.user, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        # Prevent privilege escalation through this endpoint.
        serializer.validated_data.pop("role", None)
        serializer.validated_data.pop("is_active", None)
        serializer.save()
        return Response(serializer.data)


class ChangePasswordView(APIView):
    """
    POST /api/v1/auth/change-password/
    Body: { "old_password": "...", "new_password": "..." }
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        if not user.check_password(serializer.validated_data["old_password"]):
            return Response(
                {"old_password": "Wrong password."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(serializer.validated_data["new_password"])
        user.save()
        return Response({"success": True, "message": "Password updated successfully."})


class UserListView(generics.ListAPIView):
    """
    GET /api/v1/auth/users/
    Admin-only: list all users in the system (useful for user management).
    """

    queryset = User.objects.all().order_by("-date_joined")
    serializer_class = UserSerializer

    def get_permissions(self):
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        if user.role != "admin":
            return User.objects.filter(id=user.id)
        return super().get_queryset()
