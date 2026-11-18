from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from rest_framework.response import Response
from rest_framework import generics, permissions, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.shortcuts import get_object_or_404
from rest_framework.parsers import MultiPartParser, FormParser
from .responses import success_response
from .models import Job, Candidate, Application, User, Employer
from .pagination import CustomPagination
from django.db.models import Q
from .serializers import (
    JobSerializer,
    RegisterSerializer,
    SignupSerializer,
    LogoutSerializer,
    ApplicationSerializer,
    CandidateProfileSerializer,
    EmployerProfileSerializer,
    ResumeUploadSerializer
)

from services.profile_services import (
    get_profile_user,
    get_active_profile,
    soft_delete_profile,
)

from .permissions import IsEmployer, IsCandidate, IsAdminRole


def home(request):
    return JsonResponse({
        "message": "Hello Zecpath Backend"
    })
    
class UserTestAPI(APIView):

    def get(self, request):
        return Response({
            "message": "Welcome to Zecpath API",
            "status": "success"
        })
        
class JobListAPI(APIView):

    permission_classes = [AllowAny]

    def get(self, request):
        jobs = Job.objects.select_related("employer").all().order_by("id")
        job_status = request.query_params.get("status")

        if job_status:
            jobs = jobs.filter(status=job_status)
            
        from_date = request.query_params.get("from_date")
        to_date = request.query_params.get("to_date")

        if from_date:
            jobs = jobs.filter(created_at__date__gte=from_date)

        if to_date:
            jobs = jobs.filter(created_at__date__lte=to_date)

        search = request.query_params.get("search")

        if search:
            jobs = jobs.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(location__icontains=search)
            )
            
        paginator = CustomPagination()
        page = paginator.paginate_queryset(jobs, request)

        serializer = JobSerializer(page, many=True)

        return success_response(
            data={
                "count": paginator.page.paginator.count,
                "next": paginator.get_next_link(),
                "previous": paginator.get_previous_link(),
                "results": serializer.data
            },
            message="Jobs retrieved successfully.",
            status_code=status.HTTP_200_OK
        )
    


class JobCreateAPI(APIView):

    permission_classes = [IsAuthenticated, IsEmployer]

    def post(self, request):

        employer = get_active_profile(
            Employer,
            request.user
        )

        serializer = JobSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        job = serializer.save(employer=employer)

        return success_response(
            data=JobSerializer(job).data,
            message="Job created successfully.",
            status_code=status.HTTP_201_CREATED
        )


class EmployerJobUpdateAPI(APIView):

    permission_classes = [IsAuthenticated, IsEmployer]

    def put(self, request, pk):

        employer = get_active_profile(
            Employer,
            request.user
        )

        job = get_object_or_404(
            Job,
            id=pk,
            employer=employer
        )

        serializer = JobSerializer(
            job,
            data=request.data
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return success_response(
            data=serializer.data,
            message="Job updated successfully.",
            status_code=status.HTTP_200_OK
        )


class EmployerJobStatusAPI(APIView):

    permission_classes = [IsAuthenticated, IsEmployer]

    def patch(self, request, pk):

        employer = get_active_profile(
            Employer,
            request.user
        )

        job = get_object_or_404(
            Job,
            id=pk,
            employer=employer
        )

        new_status = request.data.get("status")

        if new_status not in [
            Job.Status.OPEN,
            Job.Status.CLOSED
        ]:
            
            return Response(
                {
                "success": False,
                "status_code": status.HTTP_400_BAD_REQUEST,
                "message": "Request failed.",
                "errors": {
                "status": "Invalid job status."
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

        job.status = new_status
        job.save(update_fields=["status", "updated_at"])

        return success_response(
            data=JobSerializer(job).data,
            message="Job status updated successfully.",
            status_code=status.HTTP_200_OK
        )


class JobDetailsAPI(APIView):

    permission_classes = [AllowAny]

    def get(self, request, pk):
        job = get_object_or_404(
            Job,
            id=pk,
            status=Job.Status.OPEN
        )

        serializer = JobSerializer(job)

        return success_response(
            data=serializer.data,
            message="Job retrieved successfully.",
            status_code=status.HTTP_200_OK
        )


class JobApplicationAPI(APIView):

    permission_classes = [IsAuthenticated, IsCandidate]
    
    
    def get(self, request):
        candidate = get_active_profile(
            Candidate,
            request.user
        )

        applications = Application.objects.filter(
            candidate=candidate
        )

        serializer = ApplicationSerializer(
            applications,
            many=True
        )

        return success_response(
            data=serializer.data,
            message="Applications retrieved successfully.",
            status_code=status.HTTP_200_OK
        )

    def post(self, request):
        candidate = get_active_profile(
            Candidate,
            request.user
        )
        
        serializer = ApplicationSerializer(
            data=request.data,
            context={"request": request}
        )

        serializer.is_valid(raise_exception=True)
        serializer.save(candidate=candidate)

        return success_response(
            data=serializer.data,
            message="Application submitted successfully.",
            status_code=status.HTTP_201_CREATED
        )


class AdminUsersAPI(APIView):

    permission_classes = [IsAuthenticated, IsAdminRole]

    def get(self, request):

        users = User.objects.all()

        role = request.query_params.get("role")

        if role:
            users = users.filter(role=role)

        users = users.values(
            "id",
            "email",
            "phone",
            "role",
            "is_verified",
            "created_at"
        )

        return success_response(
            data=list(users),
            message="Users retrieved successfully.",
            status_code=status.HTTP_200_OK
        )
    

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        return success_response(
            data=serializer.data,
            message="User registered successfully.",
            status_code=status.HTTP_201_CREATED
        )
    
    
class SignupView(generics.CreateAPIView):
    serializer_class = SignupSerializer
    permission_classes = [AllowAny]
    authentication_classes = []

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        return success_response(
            data=serializer.data,
            message="User signed up successfully.",
            status_code=status.HTTP_201_CREATED
        )
    
    
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return success_response(
            message="Logout successful.",
            status_code=status.HTTP_205_RESET_CONTENT
        )
        

class CandidateProfileAPI(APIView):

    permission_classes = [IsAuthenticated]

    def get_target_user(self, request):
        return get_profile_user(
            request.user,
            User.Role.CANDIDATE,
            request.query_params.get("user_id")
        )

    
    def get(self, request):
        user = self.get_target_user(request)

        if user is None:
            return Response(
                {"error": "Candidate access only."},
                status=status.HTTP_403_FORBIDDEN
            )

        profile = get_active_profile(Candidate, user)

        serializer = CandidateProfileSerializer(profile)

        return success_response(
            data=serializer.data,
            message="Candidate profile retrieved successfully.",
            status_code=status.HTTP_200_OK
        )


    def post(self, request):
        if request.user.role == User.Role.ADMIN:
            user_id = request.data.get("user_id")

            if not user_id:
                return Response(
                    {"error": "user_id is required for admin."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            user = get_object_or_404(
                User,
                id=user_id,
                role=User.Role.CANDIDATE
            )

        elif request.user.role == User.Role.CANDIDATE:
            user = request.user

        else:
            return Response(
                {"error": "Candidate access only."},
                status=status.HTTP_403_FORBIDDEN
            )

        if Candidate.objects.filter(user=user).exists():
            raise ValidationError(
                {"profile": ["Candidate profile already exists."]}
            )

        serializer = CandidateProfileSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=user)

        return success_response(
            data=serializer.data,
            message="Candidate profile created successfully.",
            status_code=status.HTTP_201_CREATED
        )
    
    
    def put(self, request):
        user = self.get_target_user(request)

        if user is None:
            return Response(
                {"error": "Candidate access only."},
                status=status.HTTP_403_FORBIDDEN
            )

        profile = get_active_profile(Candidate, user)

        serializer = CandidateProfileSerializer(
            profile,
            data=request.data
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return success_response(
            data=serializer.data,
            message="Candidate profile updated successfully.",
            status_code=status.HTTP_200_OK
        )

    def delete(self, request):
        user = self.get_target_user(request)

        if user is None:
            return Response(
                {"error": "Candidate access only."},
                status=status.HTTP_403_FORBIDDEN
            )

        profile = get_object_or_404(
            Candidate,
            user=user,
            is_deleted=False
        )

        soft_delete_profile(profile)

        return success_response(
            message="Candidate profile deleted successfully.",
            status_code=status.HTTP_200_OK
        )
        
    def patch(self, request):
        user = self.get_target_user(request)

        if user is None:
            raise PermissionDenied("Candidate access only.")

        profile = get_active_profile(Candidate, user)

        serializer = CandidateProfileSerializer(
            profile,
            data=request.data,
            partial=True
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return success_response(
            data=serializer.data,
            message="Candidate profile partially updated successfully.",
            status_code=status.HTTP_200_OK
        )

class EmployerProfileAPI(APIView):

    permission_classes = [IsAuthenticated]

    def get_target_user(self, request):
        if request.user.role == User.Role.ADMIN:
            user_id = request.query_params.get("user_id")
            if not user_id:
                return None
            return get_object_or_404(
                User,
                id=user_id,
                role=User.Role.EMPLOYER
            )

        if request.user.role != User.Role.EMPLOYER:
            return None

        return request.user

    def get(self, request):
        user = self.get_target_user(request)

        if user is None:
            raise PermissionDenied("Employer access only.")

        profile = get_object_or_404(
            Employer,
            user=user,
            is_deleted=False
        )

        serializer = EmployerProfileSerializer(
            profile,
            context={"request": request}
        )

        return success_response(
            data=serializer.data,
            message="Employer profile retrieved successfully.",
            status_code=status.HTTP_200_OK
        )

    
    def post(self, request):
        if request.user.role == User.Role.ADMIN:
            user_id = request.data.get("user_id")

            if not user_id:
                raise ValidationError({
                    "user_id": ["This field is required for admin."]
                })

            user = get_object_or_404(
                User,
                id=user_id,
                role=User.Role.EMPLOYER
            )

        elif request.user.role == User.Role.EMPLOYER:
            user = request.user

        else:
            raise PermissionDenied("Employer access only.")

        if Employer.objects.filter(user=user).exists():
            raise ValidationError({
                "profile": ["Employer profile already exists."]
            })

        serializer = EmployerProfileSerializer(
            data=request.data,
            context={"request": request}
        )

        serializer.is_valid(raise_exception=True)
        serializer.save(user=user)

        return success_response(
            data=serializer.data,
            message="Employer profile created successfully.",
            status_code=status.HTTP_201_CREATED
        )

    def put(self, request):
        user = self.get_target_user(request)

        if user is None:
            raise PermissionDenied("Employer access only.")

        profile = get_object_or_404(
            Employer,
            user=user,
            is_deleted=False
        )

        serializer = EmployerProfileSerializer(
            profile,
            data=request.data,
            context={"request": request}
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return success_response(
            data=serializer.data,
            message="Employer profile updated successfully.",
            status_code=status.HTTP_200_OK
        )

    def delete(self, request):
        user = self.get_target_user(request)

        if user is None:
            raise PermissionDenied("Employer access only.")

        profile = get_object_or_404(
            Employer,
            user=user,
            is_deleted=False
        )

        soft_delete_profile(profile)

        return success_response(
            message="Employer profile deleted successfully.",
            status_code=status.HTTP_200_OK
        )
    
    
    def patch(self, request):
        user = self.get_target_user(request)

        if user is None:
            raise PermissionDenied("Employer access only.")

        profile = get_object_or_404(
            Employer,
            user=user,
            is_deleted=False
        )

        serializer = EmployerProfileSerializer(
            profile,
            data=request.data,
            partial=True,
            context={"request": request}
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return success_response(
            data=serializer.data,
            message="Employer profile partially updated successfully.",
            status_code=status.HTTP_200_OK
        )
   

class ResumeUploadAPI(APIView):
    permission_classes = [IsAuthenticated, IsCandidate]
    parser_classes = [MultiPartParser, FormParser]

    # GET - View uploaded resume
    def get(self, request):
        candidate = get_object_or_404(
            Candidate,
            user=request.user,
            is_deleted=False
        )

        if not candidate.resume:
            raise NotFound("No resume uploaded yet.")

        return success_response(
            data={
                "resume": request.build_absolute_uri(
                    candidate.resume.url
                )
            },
            message="Resume retrieved successfully.",
            status_code=status.HTTP_200_OK
        )

    # POST - Upload resume
    def post(self, request):
        candidate = get_object_or_404(
            Candidate,
            user=request.user,
            is_deleted=False
        )

        uploaded_file = request.FILES.get("resume")

        if not uploaded_file:
            raise ValidationError({
                "resume": ["No resume file received."]
            })

        old_resume_name = (
            candidate.resume.name if candidate.resume else None
        )

        serializer = ResumeUploadSerializer(
            candidate,
            data={"resume": uploaded_file},
            partial=True
        )

        serializer.is_valid(raise_exception=True)
        candidate = serializer.save()

        if (
            old_resume_name
            and old_resume_name != candidate.resume.name
        ):
            candidate.resume.storage.delete(old_resume_name)

        return success_response(
            data={
                "resume": request.build_absolute_uri(
                    candidate.resume.url
                )
            },
            message="Resume uploaded successfully.",
            status_code=status.HTTP_200_OK
        )