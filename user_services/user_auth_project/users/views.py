from django.contrib.auth import get_user_model
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.views import APIView
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from users.serializers import UserSerializer, RegisterSerializer
from django.utils.encoding import force_bytes, force_str


User = get_user_model()

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer

class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]

class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")

        if not user.check_password(old_password):
            return Response({"error": "Incorrect old password"}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()
        return Response({"message": "Password changed successfully"}, status=status.HTTP_200_OK)
    
# Request Password Reset: User submits their email address.
class PasswordResetRequestView(APIView):
    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({"error": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "User with this email does not exist."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Generate token and uid
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        
        # Build a reset link (in production, send this via email)
        reset_link = f"http://yourfrontend.com/reset-password/{uid}/{token}/"
        
        # Example: send_mail('Password Reset Request', f"Reset your password using the link: {reset_link}", 'noreply@example.com', [email])
        # For now, we return the reset link in the response.
        return Response({"message": "Password reset link has been sent to your email.", "reset_link": reset_link}, status=status.HTTP_200_OK)
    

# Password Reset Confirm: User submits new password along with uid and token.
class PasswordResetConfirmView(APIView):
    def post(self, request, uid, token):
        new_password = request.data.get("new_password")
        if not new_password:
            return Response({"error": "New password is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            uid_decoded = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=uid_decoded)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({"error": "Invalid user."}, status=status.HTTP_400_BAD_REQUEST)
        
        if not default_token_generator.check_token(user, token):
            return Response({"error": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)
        
        user.set_password(new_password)
        user.save()
        return Response({"message": "Password has been reset successfully."}, status=status.HTTP_200_OK)
