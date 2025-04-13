import datetime
from django.core import exceptions
from django.contrib.auth import authenticate, get_user_model, password_validation
from django.contrib.auth.hashers import check_password
from rest_framework import serializers
from ipware import get_client_ip
from activity_logger.handlers import action
from activity_logger.choices import LogBadgeChoices
from .models import Profile, Setting, CustomPermission, UserPasswordHistory
from . import consts


User = get_user_model()


class UserGlobalSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email')


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ('image',)


class SettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Setting
        fields = ('token_expire_duration', 'theme')


class CustomPermissionSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomPermission
        fields = ('id', 'name', 'codename', 'branch',
                  'category')


class UserSerializer(serializers.ModelSerializer):

    profile = ProfileSerializer()
    setting = SettingSerializer()
    permissions = CustomPermissionSerializer(many=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 
                  'profile', 'setting', 'permissions', 'has_full_permissions')


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)

    def send_log(self, user, client_ip_address, data, reason):
        action.send(
            user,
            user=user,
            is_authentication=True,
            category="user",
            action="login",
            badge=LogBadgeChoices.RED,
            title="Login Failed",
            description=f'Login failed by "{client_ip_address}".',
            ip_address=client_ip_address,
            target=user,
            details=[
                {'title': 'Username', 'description': data.get('username')},
                {'title': 'Reason', 'description': reason}
            ]
        )

    def validate(self, data):
        request = self.context['request']
        client_ip_address = get_client_ip(request)

        user = authenticate(request, **data)
        if user and user.is_active:
            return user

        """
        We check if there was not user we try to get the user by that username
        to assign the log for.
        """
        if not user:
            user = User.objects.filter(username=data.get('username')).first()
            if user:
                if user.check_password(data.get('password')):
                    if not user.is_active:
                        reason = 'Inactive user.'
                    else:
                        reason = 'Invalid username or password.'
                else:
                    reason = 'Invalid username or password.'
                    
    
        self.send_log(
            user, 
            client_ip_address, 
            data,
            reason
        )
        raise serializers.ValidationError(
            "Username or Password are invalid check you'r provided credentials!"
        )


class UserListSerializer(serializers.ModelSerializer):

    date_joined = serializers.DateTimeField(format='%Y %b %d')
    last_login = serializers.DateTimeField(format='%Y %b %d')

    class Meta:
        model = User
        fields = (
            'id', 'username', 'email',
            'first_name', "last_name", 'is_active',
            'has_full_permissions',
            'date_joined', 'last_login'
        )


class CreateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email',
                  'first_name', 'last_name', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, data):
        # get the password from the data
        password = data.get('password')

        errors = {}
        try:
            # validate the password and catch the exception
            password_validation.validate_password(password=password, user=User)

        # the exception raised here is different than serializers.ValidationError
        except exceptions.ValidationError as e:
            errors['password'] = list(e.messages)

        if errors:
            raise serializers.ValidationError(errors)

        return super(CreateUserSerializer, self).validate(data)

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class ChangePasswordByAdminSerializer(serializers.Serializer):
    password = serializers.CharField(required=True, max_length=50)

    def validate(self, data):
        password = data['password']
        if password:
            errors = {}
            try:
                password_validation.validate_password(password, User)
                return password
            except exceptions.ValidationError as e:
                errors['password'] = list(e)
                raise serializers.ValidationError(errors)
        raise serializers.ValidationError("You should set password!")


class EditUserByAdminDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name',
                  'last_name', 'is_active')


class UserPermissionsSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('permissions', 'has_full_permissions')


class ChangeImageProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ('image',)


class ChangeUserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'username')

    def validate(self, attrs):
        user = self.context['request'].user
        email = attrs['email']
        errors = {}
        if email:
            if User.objects.filter(email=email).exclude(id=user.id).exists():
                errors['email'] = ['This email is already in used.']
                raise serializers.ValidationError(errors)
        return super().validate(attrs)


class ChangeUserSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Setting
        fields = ("token_expire_duration", "theme")
    
    def validate(self, attrs):
        attrs = super().validate(attrs)
        token_expire_duration: datetime.timedelta = attrs.get('token_expire_duration')

        if token_expire_duration:
            if token_expire_duration.total_seconds() < consts.MIN_TOKEN_EXPIRE_DURATION:
                raise serializers.ValidationError(
                    {
                        'token_expire_duration': 
                        f'Minumim time is {int(consts.MIN_TOKEN_EXPIRE_DURATION / 60)} minutes!'
                    }
                )
            
            if token_expire_duration.total_seconds() > consts.MAX_TOKEN_EXPIRE_DURATION:
                raise serializers.ValidationError(
                    {
                        'token_expire_duration': 
                        f'Maximum time is {int(consts.MAX_TOKEN_EXPIRE_DURATION / 60 / 60)} hours!'
                    }
                )

        return attrs


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, max_length=50)

    def validate(self, data):
        request = self.context['request']
        new_password = data.get('new_password')
        old_password = data.get('old_password')

        if not request.user.check_password(old_password):
            raise serializers.ValidationError(
                {"old_password": "The current password is incorrect!"}
            )
        
        if new_password:
            if request.user.check_password(new_password):
                raise serializers.ValidationError(
                    {'new_password': "Please set a new password!"}
                )
            last_2_passes = UserPasswordHistory.objects.filter(
                user=request.user
            ).order_by(
                '-created_at'
            ).values_list('password', flat=True)[1:3]
            
            if last_2_passes.exists():
                for password in last_2_passes:
                    if check_password(new_password, password):
                        raise serializers.ValidationError(
                            {"new_password": "This password has been used in the last 2 times!"}
                        )

            errors = {}
            try:
                password_validation.validate_password(new_password, User)
                return new_password
            except exceptions.ValidationError as e:
                errors['new_password'] = list(e)
                raise serializers.ValidationError(errors)
        raise serializers.ValidationError("You should set a new password!")
