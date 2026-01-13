from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db import models

class Usuario(AbstractUser):
    PERFIL_CHOICES= (
        ('ADMIN', 'Administrador'),
        ('MEDICO', 'Médico'),
        ('PACIENTE', 'Paciente'),
        ('ENFERMEIRO', 'Enfermeiro'),
        ('SECRETARIA', 'Secretaria'),

    )
    
    perfil= models.CharField(max_length=10, choices=PERFIL_CHOICES, default='PACIENTE')
    cpf= models.CharField(max_length=11, unique=True, null=True, blank=True)
    telefone= models.CharField(max_length=15, null=True, blank=True)

    def __str__(self):
        return f"{self.username} ({self.get_perfil_display()})"

class Paciente(models.Model):
    usuario=models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='dados_paciente')
    nome= models.CharField(max_length=100)
    cpf= models.CharField(max_length=11, unique=True)
    data_d_nascimento= models.DateField()
    medico= models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, related_name='meus_pacientes')
    diagnostico=models.TextField()
    data_consulta=models.DateTimeField(auto_now_add=True)
    historico_medico= models.TextField(blank=True, null=True)
    cadastro_por= models.ForeignKey(Usuario, on_delete=models.CASCADE)

    def __str__(self):
        return f'Ficha clínica de {self.usuario.username}'

class Medico(models.Model):
    usuario= models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='perfil_medico')
    crm= models.CharField(max_length=20, unique=True)
    especialidade= models.CharField(max_length=100)

class Enfermeiro(models.Model):
    usuario=models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='perfil_enfermeiro')
    coren= models.CharField(max_length=20, unique=True)
    setor=models.CharField(max_length=100)
class Secretaria(models.Model):
    usuario= models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='perfil_secretaria')
    setor_designado=models.CharField(max_length=100, default='Recepção principal')

    def __str__(self):
        return f'Secretária: {self.usuario.username}'

class Consulta(models.Model):
    TIPO_CHOICES= [
        ('PRESENCIAL', 'Presencial'),
        ('TELEMEDICINA', 'Telemedicina')
    ]
    STATUS_CHOICES=[
        ('AGENDADA', 'Agendada'),
        ('REALIZADA', 'Realizada'),
        ('CANCELADA', 'Cancelada'),
        ('PENDENTE','pendente')
    ]

    paciente= models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='consultas')
    medico=models.ForeignKey(Usuario, on_delete=models.CASCADE, limit_choices_to={'perfil':'MEDICO'})
    data_hora=models.DateTimeField()
    tipo= models.CharField(max_length=20, choices=TIPO_CHOICES, default='PRESENCIAL')
    status=models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDENTE')
    link_vd= models.URLField(max_length=500, blank=True, null=True)
    receita_digital= models.TextField(blank=True)
    secretaria_responsavel=models.ForeignKey('Secretaria', on_delete=models.SET_NULL, null=True, blank=True)
    

    def __str__(self):
        return f'{self.tipo}-{self.paciente.nome} ({self.data_hora})'

class Leito(models.Model):
    numero= models.CharField(max_length=10, unique=True)
    tipo= models.CharField(max_length=50)
    ocupado=models.BooleanField(default=False)
    paciente_atual=models.OneToOneField(Paciente, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f'Leito {self.numero}-{self.tipo}'


class Suprimento(models.Model):
    nome= models.CharField(max_length=100)
    quantidade= models.IntegerField(default=0)
    preco_da_unidade=models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.nome