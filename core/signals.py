from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Candidate, Employer, User


@receiver(post_save, sender=User)
def create_or_sync_profile(sender, instance, created, **kwargs):
    if instance.role == User.Role.EMPLOYER:
        Employer.objects.get_or_create(
            user=instance,
            defaults={"company_name": "", "location": ""},
        )
    elif instance.role == User.Role.CANDIDATE:
        candidate, _ = Candidate.objects.get_or_create(
            user=instance,
            defaults={
                "full_name": instance.get_full_name() or instance.email.split("@")[0],
                "phone": instance.phone,
            },
        )
        if not created and candidate.phone != instance.phone:
            candidate.phone = instance.phone
            candidate.save(update_fields=["phone"])