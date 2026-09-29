from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated


from .serializers import LoginSerializer

class RegisterView(APIView):

    def post(self, request):
        username = request.data.get("username")
        email = request.data.get("email")
        password = request.data.get("password")

        if not username or not email or not password:
            return Response(
                {"error": "Username, email and password are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if User.objects.filter(username=username).exists():
            return Response(
                {"error": "Username already exists"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if User.objects.filter(email=email).exists():
            return Response(
                {"error": "Email already exists"},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        return Response(
            {
                "message": "User registered successfully",
                "user_id": user.id,
                "username": user.username,
                "email": user.email
            },
            status=status.HTTP_201_CREATED
        )
class LoginView(APIView):

    def post(self, request):
        serializer = LoginSerializer(data=request.data)

        if serializer.is_valid():
            return Response(
                serializer.validated_data,
                status=status.HTTP_200_OK
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
class EditProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, user_id):
        if request.user.id != user_id:
            return Response(
                {"error": "You can only edit your own profile"},
                status=status.HTTP_403_FORBIDDEN
            )

        user = User.objects.get(id=user_id)

        username = request.data.get("username")
        email = request.data.get("email")

        if username:
            user.username = username

        if email:
            user.email = email

        user.save()

        return Response(
            {
                "message": "Profile updated successfully",
                "user_id": user.id,
                "username": user.username,
                "email": user.email
            },
            status=status.HTTP_200_OK
        )
class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, user_id):
        if request.user.id != user_id:
            return Response(
                {"error": "You can only change your own password"},
                status=status.HTTP_403_FORBIDDEN
            )

        user = User.objects.get(id=user_id)

        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")

        if not old_password or not new_password:
            return Response(
                {"error": "Old password and new password are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not user.check_password(old_password):
            return Response(
                {"error": "Old password is incorrect"},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.set_password(new_password)
        user.save()

        return Response(
            {"message": "Password changed successfully"},
            status=status.HTTP_200_OK
        )
class DeleteAccountView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, user_id):
        if request.user.id != user_id:
            return Response(
                {"error": "You can only delete your own account"},
                status=status.HTTP_403_FORBIDDEN
            )

        user = User.objects.get(id=user_id)
        user.delete()

        return Response(
            {"message": "Account deleted successfully"},
            status=status.HTTP_200_OK
        )
class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            "user_id": request.user.id,
            "username": request.user.username,
            "email": request.user.email
        })