from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers

from users.models import UserProfile

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "password", "first_name", "last_name"]

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        # Profile is auto-created by signal
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        user = authenticate(username=attrs["username"], password=attrs["password"])
        if not user:
            raise serializers.ValidationError("Invalid credentials")
        attrs["user"] = user
        return attrs


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ["bio", "avatar", "phone_number", "created_at"]


class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name", "profile"]
        ref_name = "AuthzAppUser"


class UserUpdateSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(partial=True)

    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name", "profile"]
        extra_kwargs = {
            "username": {"required": False, "allow_blank": True},
            "email": {"required": False},
        }

    def validate_email(self, value):
        if (
            User.objects.filter(email__iexact=value.lower())
            .exclude(pk=self.instance.pk)
            .exists()
        ):
            raise serializers.ValidationError("This email is already in use.")
        return value.lower()

    def update(self, validated_data):
        profile_data = validated_data.pop("profile", {})
        user = super().update(self.instance, validated_data)
        if profile_data:
            profile_serializer = UserProfileSerializer(
                instance=user.profile, data=profile_data, partial=True
            )
            profile_serializer.is_valid(raise_exception=True)
            profile_serializer.save()
        if "email" in validated_data:
            user.welcome_email_sent = False
            user.save(update_fields=["welcome_email_sent"])
        return user


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField(write_only=True)
