from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = (
        ('client', 'Client'),
        ('admin', 'Administrateur'),
        ('sub_admin', 'Sous-Administrateur'),
        ('agent', 'Agent'),
    )
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='client')
    telephone = models.CharField(max_length=20, blank=True)
    adresse = models.TextField(blank=True)
    
    def is_admin_user(self):
        return self.role == 'admin'
    
    def is_sub_admin(self):
        return self.role == 'sub_admin'
    
    def is_agent(self):
        return self.role == 'agent' 