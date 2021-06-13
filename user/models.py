from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.conf import settings
from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver
from allauth.socialaccount.signals import social_account_added, pre_social_login

from tips.models import Tips


class Profile(models.Model):
    LEVELS = [('Beginner', 1), ('Intermediate', 2), ('Advanced', 3)]
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    username = models.CharField(max_length=256, blank=True)
    level = models.CharField(max_length=256, default=1, choices=LEVELS)
    favourites = models.ManyToManyField(Tips)
    verified = models.BooleanField(default=False)

    def __str__(self):
        return self.username if self.username else f"{self.user}"


class UserManager(BaseUserManager):

    def create_user(self, email, name='', password=None):
        if not email: raise ValueError("User must have a valid email address")
        if not password: raise ValueError("Password must be set")
        user = self.model(email=self.normalize_email(email), name=name)
        user.set_password(password)
        user.save(using=self._db)
        Profile.objects.create(user=user, username=user.email)
        return user

    def create_superuser(self, email, password=None):
        user = self.create_user(email, name='', password=password)
        user.is_admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, verbose_name='Email Address', max_length=256, help_text='Valid Email Address')
    name = models.CharField(max_length=256, blank=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    date_joined = models.DateField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = UserManager()

    def __str__(self):
        return self.email

    def get_full_name(self):
        return self.name if self.name else self.email

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)

    @property
    def is_staff(self):
        return self.is_admin

    @property
    def is_superuser(self):
        return self.is_admin


@receiver(post_save, sender=User)
def update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance, username=instance.email)
    instance.profile.save()


# @receiver(pre_social_login)
# def test(request, sociallogin, **kwargs):
#     print(sociallogin)
