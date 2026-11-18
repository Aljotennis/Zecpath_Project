from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User, Job, Application
from .models import Candidate, Employer

class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        validators=[
            UniqueValidator(
                queryset=User.objects.all(),
                lookup="iexact"
            )
        ]
    )

    password = serializers.CharField(
        write_only=True,
        validators=[validate_password]
    )

    class Meta:
        model = User
        fields = ["id", "email", "phone", "role", "password"]

    def validate_role(self, value):
        if value not in (User.Role.EMPLOYER, User.Role.CANDIDATE):
            raise serializers.ValidationError(
                "Role must be employer or candidate."
            )
        return value

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True,validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            "email",
            "phone",
            "role",
            "password",
            "confirm_password"
        ]

    def validate_role(self, value):
        if value not in (User.Role.EMPLOYER, User.Role.CANDIDATE):
            raise serializers.ValidationError(
                "Role must be employer or candidate."
            )
        return value

    def validate(self, attrs):
        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError({
                "password": "Passwords do not match."
            })
        return attrs

    def create(self, validated_data):
        validated_data.pop("confirm_password")
        return User.objects.create_user(**validated_data)


class JobSerializer(serializers.ModelSerializer):

    class Meta:
        model = Job
        fields = [
            "id",
            "title",
            "description",
            "skills",
            "experience",
            "location",
            "job_type",
            "salary_min",
            "salary_max",
            "status",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "status",
            "created_at",
            "updated_at",
        ]

    def validate(self, attrs):
        salary_min = attrs.get("salary_min")
        salary_max = attrs.get("salary_max")

        if (
            salary_min is not None
            and salary_max is not None
            and salary_max < salary_min
        ):
            raise serializers.ValidationError(
                "Maximum salary cannot be less than minimum salary."
            )

        return attrs


class ApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = [
            "id",
            "job",
            "cover_letter",
            "status",
            "applied_at"
        ]
        read_only_fields = ["id", "status", "applied_at"]

    def validate_job(self, value):
        if value.status != Job.Status.OPEN:
            raise serializers.ValidationError(
                "You can only apply for open jobs."
            )
        return value

    def validate(self, attrs):
        request = self.context.get("request")

        if request and request.user.is_authenticated:
            candidate = getattr(request.user, "candidate", None)

            if candidate is None:
                raise serializers.ValidationError({
                    "candidate": "Candidate profile not found."
                })

            if Application.objects.filter(
                candidate=candidate,
                job=attrs["job"]
            ).exists():
                raise serializers.ValidationError({
                    "job": "You have already applied for this job."
                })

        return attrs


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def validate(self, attrs):
        self.token = attrs["refresh"]
        return attrs

    def save(self, **kwargs):
        token = RefreshToken(self.token)
        token.blacklist()


class CandidateProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Candidate
        fields = [
            "id",
            "full_name",
            "phone",
            "resume",
            "skills",
            "education",
            "experience",
            "expected_salary",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_expected_salary(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError(
                "Expected salary cannot be negative."
            )
        return value
    

class EmployerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employer
        fields = [
            "id",
            "company_name",
            "industry",
            "domain",
            "company_size",
            "website",
            "location",
            "is_verified",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        request = self.context.get("request")

        if not request or not request.user.is_authenticated:
            self.fields["is_verified"].read_only = True

        elif not request.user.is_staff:
            self.fields["is_verified"].read_only = True
            

class ResumeUploadSerializer(serializers.ModelSerializer):

    class Meta:
        model = Candidate
        fields = ["resume"]

    def validate_resume(self, value):
        if not value:
            raise serializers.ValidationError(
                "Please upload a resume."
            )
        return value
