from rest_framework.permissions import BasePermission

from .models import User


class HasRole(BasePermission):
    role = None

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and user.role == self.role)


class IsAdminRole(HasRole):
    role = User.Role.ADMIN


class IsEmployer(HasRole):
    role = User.Role.EMPLOYER


class IsCandidate(HasRole):
    role = User.Role.CANDIDATE