import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from organization.models import Organization


class User(AbstractUser):
    """
    Modelo de usuario personalizado con relación a Organization.
    Extiende AbstractUser para mantener funcionalidad estándar de Django.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='users',
        verbose_name='Organización',
        null=True,
        blank=True,
        help_text='Organización a la que pertenece el usuario'
    )

    class Meta:
        db_table = 'users'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def __str__(self):
        return self.username
