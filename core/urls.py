from django.urls import path
from . import views
from .views import UserTestAPI, JobListAPI, JobCreateAPI, RegisterView, SignupView, LogoutView
from .views import JobApplicationAPI, AdminUsersAPI,CandidateProfileAPI, EmployerProfileAPI, ResumeUploadAPI, JobDetailsAPI
from .views import EmployerJobUpdateAPI, EmployerJobStatusAPI
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('', views.home, name='home'),
    path('test/', UserTestAPI.as_view(), name='user-test'),
    path('jobs/', JobListAPI.as_view(), name='job-list'),
    path('jobs/create/', JobCreateAPI.as_view(), name='job-create'),
    path("register/", RegisterView.as_view(), name="register"),
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('applications/', JobApplicationAPI.as_view(),name='job-application'),
    path('admin/users/', AdminUsersAPI.as_view(), name='admin-users'),
    path('candidate/profile/', CandidateProfileAPI.as_view(), name='candidate-profile'),
    path('employer/profile/', EmployerProfileAPI.as_view(), name='employer-profile'),
    path("candidate/resume/upload/", ResumeUploadAPI.as_view(), name="candidate-resume-upload"),
    path('jobs/<int:pk>/',JobDetailsAPI.as_view(),name='job-details'),
    path("employer/jobs/<int:pk>/update/",EmployerJobUpdateAPI.as_view(),name="employer-job-update"),
    path("employer/jobs/<int:pk>/status/",EmployerJobStatusAPI.as_view(),name="employer-job-status"),
]