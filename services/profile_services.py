
from django.shortcuts import get_object_or_404

from core.models import User, Candidate, Employer


def get_profile_user(request_user, role, user_id=None):
    """
    Get the profile owner based on the logged-in user's role.
    Admins can access profiles using user_id.
    """

    if request_user.role == User.Role.ADMIN:
        if not user_id:
            return None

        return get_object_or_404(
            User,
            id=user_id,
            role=role
        )

    if request_user.role == role:
        return request_user

    return None


def get_active_profile(model, user):
    """Retrieve an active profile."""
    return get_object_or_404(
        model,
        user=user,
        is_deleted=False
    )


def soft_delete_profile(profile):
    """Soft-delete a profile."""
    profile.is_deleted = True
    profile.save(update_fields=["is_deleted"])

    return profile
