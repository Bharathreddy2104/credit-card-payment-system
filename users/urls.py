from django.urls import path

from .views import (
    RegisterView,
    LoginView,
    ProfileView,
    EditProfileView,
    ChangePasswordView,
    DeleteAccountView,
)


urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),

    path("login/", LoginView.as_view(), name="login"),

    path("profile/", ProfileView.as_view(), name="profile"),

    path(
        "edit-profile/<int:user_id>/",
        EditProfileView.as_view(),
        name="edit-profile"
    ),

    path(
        "change-password/<int:user_id>/",
        ChangePasswordView.as_view(),
        name="change-password"
    ),

    path(
        "delete-account/<int:user_id>/",
        DeleteAccountView.as_view(),
        name="delete-account"
    ),
]