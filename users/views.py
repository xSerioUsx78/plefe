from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from django.utils import timezone
from rest_framework import generics, status, permissions, serializers
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.authtoken.models import Token
from utils.drf import permissions as c_permissions
from utils.drf.generics import (
    CustomListAPIView, CustomRetrieveAPIView, CustomGenericAPIView
)
from utils.drf.views import CustomAPIView
from activity_logger.signals import action, action_bulk
from activity_logger.choices import LogBadgeChoices
from ipware import get_client_ip
from .serializers import (
    CustomPermissionSerializer, LoginSerializer, UserSerializer,
    UserListSerializer, CreateUserSerializer, ChangePasswordByAdminSerializer,
    EditUserByAdminDetailSerializer, UserPermissionsSerializer,
    ChangeImageProfileSerializer, ChangeUserInfoSerializer, ChangePasswordSerializer,
    ChangeUserSettingsSerializer
)
from .models import Profile, Setting, CustomPermission, UserPasswordHistory
from .auth import cookie_login_with_token, cookie_logout_with_token
from .utils import destroy_token
from . import filters, codenames

User = get_user_model()


class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = (permissions.AllowAny,)
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data

        # We remove the old token first.
        destroy_token(user)

        # Then we create a new one.
        token = Token.objects.create(user=user)
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])
        action.send(
            user,
            user=user,
            is_authentication=True,
            category="user",
            action="login",
            badge=LogBadgeChoices.GREEN,
            title="Logged in",
            description=f'"{user.username}" logged in.',
            ip_address=get_client_ip(request),
            target=user
        )
        res = Response()
        cookie_login_with_token(res, token)
        res.data = {
            "user": UserSerializer(user, context=self.get_serializer_context()).data
        }
        return res


class UserView(generics.RetrieveAPIView):
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


class LogoutView(generics.GenericAPIView):

    def post(self, request, *args, **kwargs):
        user = request.user
        destroy_token(user)
        action.send(
            user,
            user=user,
            category="user",
            is_authentication=True,
            action="logout",
            badge=LogBadgeChoices.RED,
            title="Logged out",
            description=f'"{user.username}" logged out.',
            ip_address=get_client_ip(request),
            target=user
        )
        res = Response()
        cookie_logout_with_token(res)
        res.status_code = 204
        return res


class UsersListView(CustomListAPIView):
    permission_classes = [c_permissions.HasPermsPermissions]
    perms = [codenames.VIEW_USER]
    serializer_class = UserListSerializer
    queryset = User.objects.filter(is_superuser=False).order_by('-date_joined')

    def get_queryset(self):
        queryset = super().get_queryset().exclude(id=self.request.user.id)
        q = self.request.query_params.get('q' or None)
        if q:
            queryset = queryset.filter(username__icontains=q).distinct()
        return queryset

    def before_raising_not_authenticated_error(self):
        client_ip_address = get_client_ip(self.request)
        action.send(
            None,
            category="user",
            action="error",
            badge=LogBadgeChoices.RED,
            title="Authentication error",
            description=f'"{client_ip_address}" tried to perform view action on users.',
            ip_address=client_ip_address,
            is_authorization=True
        )

    def before_raising_permission_denied_error(self):
        user = self.request.user
        action.send(
            user,
            user=user,
            category="user",
            action="error",
            badge=LogBadgeChoices.RED,
            title="Permission denied error",
            description=f'"{user.username}" tried to perform view action on users.',
            ip_address=get_client_ip(self.request),
            is_authorization=True
        )


class CreateUserView(CustomGenericAPIView):
    permission_classes = [c_permissions.HasPermsPermissions]
    perms = [codenames.ADD_USER]
    serializer_class = CreateUserSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            instance = serializer.save()
            UserPasswordHistory.objects.create(
                user=instance,
                password=instance.password
            )
            action.send(
                instance,
                user=request.user,
                category="user",
                action="create",
                badge=LogBadgeChoices.GREEN,
                title="User created",
                description=f'User with username "{instance.username}" has been created by "{request.user.username}".',
                ip_address=get_client_ip(request),
                target=instance,
                is_authorization=True
            )
            return Response(status=status.HTTP_201_CREATED)
        action.send(
            None,
            user=request.user,
            category="user",
            action="error",
            badge=LogBadgeChoices.RED,
            title="User creation error",
            description=f'User creation failed by "{request.user.username}".',
            ip_address=get_client_ip(request),
            is_authorization=True
        )
        raise ValidationError(serializer.errors)

    def before_raising_not_authenticated_error(self):
        client_ip_address = get_client_ip(self.request)
        action.send(
            None,
            category="user",
            action="error",
            badge=LogBadgeChoices.RED,
            title="Authentication error",
            description=f'"{client_ip_address}" tried to perform create action on users.',
            ip_address=client_ip_address,
            is_authorization=True
        )

    def before_raising_permission_denied_error(self):
        user = self.request.user
        action.send(
            user,
            user=user,
            category="user",
            action="error",
            badge=LogBadgeChoices.RED,
            title="Permission denied error",
            description=f'"{user.username}" tried to perform create action on users.',
            ip_address=get_client_ip(self.request),
            is_authorization=True
        )


class PasswordChangeByAdmin(CustomGenericAPIView):
    permission_classes = [c_permissions.HasPermsPermissions]
    perms = [codenames.CHANGE_PASSWORD_USER]
    serializer_class = ChangePasswordByAdminSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        password = serializer.validated_data
        username = request.data.get('username')
        user = User.objects.filter(username=username).first()
        if not user:
            action.send(
            None,
            user=request.user,
            category="user",
            action="error",
            badge=LogBadgeChoices.RED,
            title="User password change error",
            description=f'User password changing failed by "{request.user.username}".',
            ip_address=get_client_ip(request),
            is_authorization=True
        )
            raise ValidationError('No User found!')

        if user.check_password(password):
            raise serializers.ValidationError(
                {'password': "Please set a new password!"}
            )
        last_2_passes = UserPasswordHistory.objects.filter(
            user=user
        ).order_by(
            '-created_at'
        ).values_list('password', flat=True)[1:3]
        
        if last_2_passes.exists():
            for last_password in last_2_passes:
                if check_password(password, last_password):
                    raise serializers.ValidationError(
                        {"password": "This password has been used in the last 2 times!"}
                    )
                
        user.set_password(password)
        user.save(update_fields=['password'])
        UserPasswordHistory.objects.create(
            user=user,
            password=user.password
        )
        action.send(
            user,
            user=request.user,
            category="user",
            action="update",
            badge=LogBadgeChoices.INFO,
            title="User password changed",
            description=f'"{user.username}\'s" password has been changed by {request.user.username}".',
            ip_address=get_client_ip(request),
            target=user,
            is_authorization=True
        )
        # Now we should destroy then token from db
        destroy_token(user)
        return Response(status=status.HTTP_200_OK)
        

    def before_raising_not_authenticated_error(self):
        client_ip_address = get_client_ip(self.request)
        action.send(
            None,
            category="user",
            action="error",
            badge=LogBadgeChoices.RED,
            title="Authentication error",
            description=f'"{client_ip_address}" tried to perform change password action on users.',
            ip_address=client_ip_address,
            is_authorization=True
        )

    def before_raising_permission_denied_error(self):
        user = self.request.user
        action.send(
            user,
            user=user,
            category="user",
            action="error",
            badge=LogBadgeChoices.RED,
            title="Permission denied error",
            description=f'"{user.username}" tried to perform change password action on users.',
            ip_address=get_client_ip(self.request),
            is_authorization=True
        )


class EditUserByAdminDetail(CustomRetrieveAPIView):
    permission_classes = [c_permissions.HasPermsPermissions]
    perms = []
    serializer_class = EditUserByAdminDetailSerializer
    queryset = User.objects.all()
    lookup_field = 'username'

    def get_permissions(self):
        method = self.request.method
        if method == 'GET':
            self.perms = [codenames.VIEW_USER]
        elif method == 'PUT':
            self.perms = [codenames.CHANGE_USER]
        return super().get_permissions()

    def get(self, *args, **kwagrs):
        object_serializer = EditUserByAdminDetailSerializer(self.get_object())
        data = {
            'object': object_serializer.data
        }
        return Response(data, status=status.HTTP_200_OK)

    def put(self, request, *args, **kwargs):
        obj = self.get_object()
        serializer = self.get_serializer(obj, data=request.data)
        if serializer.is_valid():
            instance = serializer.save()
            action.send(
                instance,
                user=request.user,
                category="user",
                action="update",
                badge=LogBadgeChoices.INFO,
                title="User updated",
                description=f'User with username "{instance.username}" has been updated by "{request.user.username}".',
                ip_address=get_client_ip(request),
                target=instance,
                is_authorization=True
            )
            return Response(serializer.data, status=status.HTTP_200_OK)
        action.send(
            None,
            user=request.user,
            category="user",
            action="error",
            badge=LogBadgeChoices.RED,
            title="User update error",
            description=f'User update failed by "{request.user.username}".',
            ip_address=get_client_ip(request),
            is_authorization=True
        )
        raise ValidationError(serializer.errors)
    
    def before_raising_not_authenticated_error(self):
        client_ip_address = get_client_ip(self.request)
        method = self.request.method
        description = None
        if method == 'GET':
            description = f'"{client_ip_address}" tried to perform view action on user.'
        if method == 'PUT':
            description = f'"{client_ip_address}" tried to perform update action on user.'
        action.send(
            None,
            category="user",
            action="error",
            badge=LogBadgeChoices.RED,
            title="Authentication error",
            description=description,
            ip_address=client_ip_address,
            is_authorization=True
        )

    def before_raising_permission_denied_error(self):
        user = self.request.user
        method = self.request.method
        description = None
        if method == 'GET':
            description = f'"{user.username}" tried to perform view action on user.'
        if method == 'PUT':
            description = f'"{user.username}" tried to perform update action on user.'
        action.send(
            user,
            user=user,
            category="user",
            action="error",
            badge=LogBadgeChoices.RED,
            title="Permission denied error",
            description=description,
            ip_address=get_client_ip(self.request),
            is_authorization=True
        )


class PermissionsView(CustomGenericAPIView):
    permission_classes = [c_permissions.HasPermsPermissions]
    perms = [codenames.SET_PERMISSIONS_TO_USER]
    serializer_class = CustomPermissionSerializer
    queryset = CustomPermission.objects.all()
    filterset_class = filters.CustomPermissionsFilter

    def get(self, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        data = self.get_serializer(queryset, many=True).data
        return Response(data)

    def before_raising_not_authenticated_error(self):
        client_ip_address = get_client_ip(self.request)
        action.send(
            None,
            category="user",
            action="error",
            badge=LogBadgeChoices.RED,
            title="Authentication error",
            description=f'"{client_ip_address}" tried to perform view action on permissions.',
            ip_address=client_ip_address,
            is_authorization=True
        )

    def before_raising_permission_denied_error(self):
        user = self.request.user
        action.send(
            user,
            user=user,
            category="user",
            action="error",
            badge=LogBadgeChoices.RED,
            title="Permission denied error",
            description=f'"{user.username}" tried to perform view action on permissions.',
            ip_address=get_client_ip(self.request),
            is_authorization=True
        )


class EditUserPermissionsView(CustomRetrieveAPIView):
    permission_classes = [c_permissions.HasPermsPermissions]
    perms = [codenames.SET_PERMISSIONS_TO_USER]
    serializer_class = UserPermissionsSerializer
    queryset = User.objects.all()
    lookup_field = 'username'

    def get(self, request, *args, **kwargs):
        object_data = self.get_serializer(self.get_object()).data
        permissions_qs = CustomPermission.objects.all()
        permissions_data = CustomPermissionSerializer(
            filters.CustomPermissionsFilter(request.GET, permissions_qs).qs,
            many=True
        ).data
        data = {
            'object': object_data,
            'permissions': permissions_data
        }
        return Response(data)

    def put(self, request, *args, **kwargs):
        obj = self.get_object()
        serializer = self.get_serializer(obj, data=request.data)
        if serializer.is_valid():
            instance = serializer.save()
            action.send(
                instance,
                user=request.user,
                category="user",
                action="update",
                badge=LogBadgeChoices.INFO,
                title="Permissions updated",
                description=f'"{instance.username}\'s permissions are updated by {request.user.username}".',
                ip_address=get_client_ip(request),
                target=instance,
                is_authorization=True
            )
            return Response(serializer.data, status=status.HTTP_200_OK)
        action.send(
            None,
            user=request.user,
            category="user",
            action="error",
            badge=LogBadgeChoices.RED,
            title="Permissions update error",
            description=f'User permissions update failed by "{request.user.username}".',
            ip_address=get_client_ip(request),
            is_authorization=True
        )
        raise ValidationError(serializer.errors)

    def before_raising_not_authenticated_error(self):
        client_ip_address = get_client_ip(self.request)
        action.send(
            None,
            category="user",
            action="error",
            badge=LogBadgeChoices.RED,
            title="Authentication error",
            description=f'"{client_ip_address}" tried to perform change permissions action on user.',
            ip_address=client_ip_address,
            is_authorization=True
        )

    def before_raising_permission_denied_error(self):
        user = self.request.user
        action.send(
            user,
            user=user,
            category="user",
            action="error",
            badge=LogBadgeChoices.RED,
            title="Permission denied error",
            description=f'"{user.username}" tried to perform change permissions action on user.',
            ip_address=get_client_ip(self.request),
            is_authorization=True
        )


class UserDeleteView(CustomAPIView):
    permission_classes = [c_permissions.HasPermsPermissions]
    perms = [codenames.DELETE_USER]

    def delete(self, request, *args, **kwargs):
        usernames = request.data.get('usernames')
        users = User.objects.filter(username__in=usernames)
        if users.exists():
            logs = [
                {
                    "user": request.user,
                    "category": "user",
                    "action": "delete",
                    "badge": LogBadgeChoices.RED,
                    "title": "User deleted",
                    "description": f'User with username "{instance.username}" has been deleted by "{request.user.username}".',
                    "ip_address": get_client_ip(request),
                    "target": instance,
                    'is_authorization': True
                }
                for instance in users
            ]
            users.delete()
            action_bulk.send('user', logs=logs)
        return Response(status=status.HTTP_200_OK)

    def before_raising_not_authenticated_error(self):
        client_ip_address = get_client_ip(self.request)
        action.send(
            None,
            category="user",
            action="error",
            badge=LogBadgeChoices.RED,
            title="Authentication error",
            description=f'"{client_ip_address}" tried to perform delete action on users.',
            ip_address=client_ip_address,
            is_authorization=True
        )

    def before_raising_permission_denied_error(self):
        user = self.request.user
        action.send(
            user,
            user=user,
            category="user",
            action="error",
            badge=LogBadgeChoices.RED,
            title="Permission denied error",
            description=f'"{user.username}" tried to perform delete action on users.',
            ip_address=get_client_ip(self.request),
            is_authorization=True
        )


class UserChangeImageProfileView(generics.GenericAPIView):
    serializer_class = ChangeImageProfileSerializer
    queryset = Profile.objects.all()

    def get_object(self):
        return self.request.user.profile

    def put(self, request, *args, **kwargs):
        obj = self.get_object()
        serializer = self.get_serializer(obj, data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        action.send(
            instance,
            user=request.user,
            category="user",
            action="update",
            badge=LogBadgeChoices.INFO,
            title="Image changed",
            description=f'"{instance.user.username}" changed image.',
            ip_address=get_client_ip(request),
            target=instance,
            is_authorization=True
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserChangeInfoView(generics.GenericAPIView):
    serializer_class = ChangeUserInfoSerializer
    queryset = User.objects.all()

    def get_object(self):
        return self.request.user

    def put(self, request, *args, **kwargs):
        obj = self.get_object()
        serializer = self.get_serializer(obj, data=self.request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        action.send(
            obj,
            user=obj,
            category="user",
            action="update",
            badge=LogBadgeChoices.INFO,
            title="Information updated",
            description=f'"{obj.username}" updated information.',
            ip_address=get_client_ip(request),
            target=obj,
            is_authorization=True
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserChangeSettingsView(generics.GenericAPIView):
    serializer_class = ChangeUserSettingsSerializer
    queryset = Setting.objects.all()

    def get_object(self):
        return self.request.user.setting

    def put(self, request, *args, **kwargs):
        obj = self.get_object()
        user = request.user
        serializer = self.get_serializer(obj, data=self.request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        action.send(
            user,
            user=user,
            category="setting",
            action="update",
            badge=LogBadgeChoices.INFO,
            title="Settings updated",
            description=f'"{user.username}" updated settings.',
            ip_address=get_client_ip(request),
            target=user,
            is_authorization=True
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserChangeThemeView(generics.GenericAPIView):
    serializer_class = ChangeUserSettingsSerializer
    queryset = Setting.objects.all()

    def get_object(self):
        return self.request.user.setting

    def put(self, request, *args, **kwargs):
        obj = self.get_object()
        serializer = self.get_serializer(obj, data=self.request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserChangePasswordView(generics.GenericAPIView):
    serializer_class = ChangePasswordSerializer
    queryset = User.objects.all()

    def get_object(self):
        return self.request.user

    def put(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(user, data=self.request.data)
        serializer.is_valid(raise_exception=True)
        new_password = self.request.data.get("new_password")
        user.set_password(new_password)
        user.save(update_fields=['password'])
        UserPasswordHistory.objects.create(
            user=user,
            password=user.password
        )
        action.send(
            user,
            user=user,
            category="user",
            action="update",
            badge=LogBadgeChoices.INFO,
            title="Password changed",
            description=f'"{user.username}" changed password.',
            ip_address=get_client_ip(request),
            target=user,
            is_authorization=True
        )
        destroy_token(user)
        res = Response()
        cookie_logout_with_token(res)
        return res