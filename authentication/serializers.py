from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'name', 'username', 'email', 'date_joined')
        read_only_fields = ('id', 'date_joined')

    def get_name(self, obj):
        return obj.get_full_name() or obj.username


class RegisterSerializer(serializers.ModelSerializer):
    name = serializers.CharField(write_only=True, required=True)
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'},
    )

    class Meta:
        model = User
        fields = ('name', 'email', 'password')

    def validate_email(self, value):
        value = value.strip().lower()
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError('A user with this email already exists.')
        return value

    def create(self, validated_data):
        name = validated_data.pop('name').strip()
        email = validated_data['email']
        # Use the email as the username so users can log in with either.
        username = email
        while User.objects.filter(username__iexact=username).exists():
            username = f'{username}+{User.objects.count() + 1}'
        first_name, _, last_name = name.partition(' ')
        return User.objects.create_user(
            username=username[:150],
            email=email,
            password=validated_data['password'],
            first_name=first_name,
            last_name=last_name.strip(),
        )


class LoginSerializer(serializers.Serializer):
    identifier = serializers.CharField(
        required=False,
        help_text='Email address or username',
    )
    email = serializers.EmailField(required=False)
    password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
    )

    def validate(self, attrs):
        identifier = (attrs.get('identifier') or attrs.get('email') or '').strip()
        password = attrs['password']

        if not identifier:
            raise serializers.ValidationError(
                {'identifier': 'Email address or username is required.'}
            )

        user = User.objects.filter(email__iexact=identifier).first()
        if user is None:
            user = User.objects.filter(username__iexact=identifier).first()
        if user is None or not user.check_password(password):
            raise serializers.ValidationError(
                {'detail': 'Invalid credentials. Please check your email/username and password.'}
            )
        if not user.is_active:
            raise serializers.ValidationError({'detail': 'This account has been deactivated.'})

        attrs['user'] = user
        return attrs


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }
