from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Group
from .models import CustomerUser


@receiver(post_save, sender=CustomerUser)
def assign_user_to_group(sender, instance, created, **kwargs):
    """
    Adv feature: Auto assign user to django group based on role

    This signal runs AFTER a user is created
    If the user was just created (created=True), we assign permissions.
    """

    if created:
        group_name = f'{instance.role}_group'
        group , group_created = Group.objects.get_or_create(name=group_name)
        instance.groups.add(group)
        print(f"User {instance.username} added to {group_name} group")