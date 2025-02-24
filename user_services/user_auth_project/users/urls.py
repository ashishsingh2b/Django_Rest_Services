from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import RegisterView, UserListView, UserDetailView, ChangePasswordView,PasswordResetConfirmView,PasswordResetRequestView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('users/', UserListView.as_view(), name='user_list'),
    path('users/<int:pk>/', UserDetailView.as_view(), name='user_detail'),
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),    # Password Reset Endpoints
    path('password-reset/', PasswordResetRequestView.as_view(), name='password_reset'),
    path('password-reset-confirm/<uid>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
]

