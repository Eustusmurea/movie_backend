# users/signals.py
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import UserProfile
from .tasks import send_welcome_email_task

User = get_user_model()


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

    profile = instance.profile
    if instance.email and instance.email.strip() and not profile.welcome_email_sent:
        try:
            send_welcome_email_task.delay(instance.email)
            profile.welcome_email_sent = True
            profile.save(update_fields=["welcome_email_sent"])
        except Exception as e:
            import logging

            logger = logging.getLogger(__name__)
            logger.error(f"Failed to queue welcome email for {instance.email}: {e}")
