from django.urls import path
from . import views
from .views import UserTestAPI, JobListAPI, JobCreateAPI, RegisterView

urlpatterns = [
    path('', views.home, name='home'),
    path('test/', UserTestAPI.as_view(), name='user-test'),
    path('jobs/', JobListAPI.as_view(), name='job-list'),
    path('jobs/create/', JobCreateAPI.as_view(), name='job-create'),
    path("register/", RegisterView.as_view(), name="register"),
]