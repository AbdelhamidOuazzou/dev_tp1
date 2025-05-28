from django.conf import settings
from django.db import models

class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    preferences = models.TextField(blank=True)
    travel_documents = models.FileField(upload_to='documents/', blank=True)

    def str(self):
        return self.user.username

class Circuit(models.Model):
    # ... your existing fields ...

    class Meta:
        permissions = [
            ("can_add_circuit", "Can add circuit"),
        ]

class Destination(models.Model):
    # ... your existing fields ...

    class Meta:
        permissions = [
            ("can_add_destination", "Can add destination"),
        ]

class OptionSupplement(models.Model):
    # ... your existing fields ...

    class Meta:
        permissions = [
            ("can_add_option", "Can add supplementary option"),
        ]