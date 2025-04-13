from django.urls import path
from .views import (
    LoginView, UserView, LogoutView, UsersListView,
    CreateUserView, PasswordChangeByAdmin, EditUserByAdminDetail,
    PermissionsView, EditUserPermissionsView, UserDeleteView, UserChangeImageProfileView,
    UserChangeInfoView, UserChangePasswordView, UserChangeSettingsView,
    UserChangeThemeView
)


urlpatterns = [
    path('login/', LoginView.as_view()),
    path('logout/', LogoutView.as_view()),
    path('user/', UserView.as_view()),
    path('change-image/', UserChangeImageProfileView.as_view()),
    path('change-info/', UserChangeInfoView.as_view()),
    path('change-settings/', UserChangeSettingsView.as_view()),
    path('change-theme/', UserChangeThemeView.as_view()),
    path('change-password/', UserChangePasswordView.as_view()),
    path('list/', UsersListView.as_view()),
    path('create/', CreateUserView.as_view()),
    path('edit-by-admin-detail/<username>/', EditUserByAdminDetail.as_view()),
    path('permissions/', PermissionsView.as_view()),
    path('edit-user-permissions/<username>/',
         EditUserPermissionsView.as_view()),
    path('change-password-by-admin/', PasswordChangeByAdmin.as_view()),
    path('delete/', UserDeleteView.as_view())
]
