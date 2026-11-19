from uuid import uuid4

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.db.models.functions import Lower
from django.utils import timezone


class UsuarioManager(BaseUserManager):
    use_in_migrations = True

    @classmethod
    def normalize_email(cls, email):
        return super().normalize_email(email).strip().lower()

    def get_by_natural_key(self, email):
        return self.get(email=self.normalize_email(email))

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("O e-mail é obrigatório.")
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("tipo", Usuario.Tipo.EQUIPE)
        return self.create_user(email, password, **extra_fields)


class Usuario(AbstractBaseUser, PermissionsMixin):
    class Tipo(models.TextChoices):
        PRESTADOR = "prestador", "Prestador"
        EMPRESA = "empresa", "Usuário de empresa"
        EQUIPE = "equipe", "Equipe BicoJá"

    uuid = models.UUIDField(default=uuid4, unique=True, editable=False)
    email = models.EmailField("e-mail", unique=True)
    tipo = models.CharField(max_length=10, choices=Tipo.choices, default=Tipo.PRESTADOR)
    is_active = models.BooleanField("ativo", default=True)
    is_staff = models.BooleanField("acesso ao painel", default=False)
    criado_em = models.DateTimeField("criado em", default=timezone.now, editable=False)

    objects = UsuarioManager()

    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "usuário"
        verbose_name_plural = "usuários"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(email=Lower("email")),
                name="usuario_email_minusculo",
            ),
        ]

    def clean(self):
        super().clean()
        self.email = type(self).objects.normalize_email(self.email)

    def __str__(self):
        return self.email
