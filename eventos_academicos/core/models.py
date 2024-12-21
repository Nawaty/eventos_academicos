from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
import re
from django.core.exceptions import ValidationError
from datetime import date
from django.conf import settings


def validate_cpf(value):
    if not re.match(r'^\d{11}$', value):
        raise ValidationError('CPF deve ter 11 dígitos numéricos.')


class Usuario(AbstractUser):
    # Campos adicionais para usuários
    cpf = models.CharField(max_length=11, unique=True, validators=[validate_cpf])
    instituicao = models.CharField(max_length=100, blank=True)
    tipo_usuario = models.CharField(max_length=20, choices=[
        ('ADMIN', 'Administrador'),
        ('PROFESSOR', 'Professor'),
        ('ALUNO', 'Aluno')
    ])


class Evento(models.Model):
    nome = models.CharField(max_length=200)
    descricao = models.TextField()
    data_inicio = models.DateTimeField()
    data_fim = models.DateTimeField()
    local = models.CharField(max_length=200)
    organizador = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='eventos_organizados')
    valor_inscricao = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    def __str__(self):
        return self.nome


class Palestra(models.Model):
    titulo = models.CharField(max_length=200)
    palestrante = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE, related_name='palestras')
    data_hora = models.DateTimeField()
    duracao = models.IntegerField(help_text='Duração em minutos')
    
    def __str__(self):
        return self.titulo


class Inscricao(models.Model):
    STATUS_CHOICES = [
        ('CONFIRMADA', 'Confirmada'),
        ('PENDENTE', 'Pendente'),
        ('CANCELADA', 'Cancelada'),
    ]
    
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,default=1)
    data_inscricao = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='CONFIRMADA'
    )
    class Meta:
        unique_together = ['evento', 'usuario']

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

class Certificado(models.Model):
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,default=1)
    data_emissao = models.DateTimeField(auto_now_add=True)
    nome_participante = models.CharField(max_length=255)
