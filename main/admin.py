from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario, Paciente, Consulta, Leito, Suprimento, Medico, Enfermeiro, Secretaria

class MedicoInLine(admin.StackedInline):
    model=Medico
    can_delete=False
    verbose_name_plural= 'Informções de médico(CRM)'

class EnfermeiroInLine(admin.StackedInline):
    model=Enfermeiro
    can_delete=False
    verbose_name_plural='Informações de Enfermeiro(COREN)'


class UsuarioAdmin(UserAdmin):
    inlines= [MedicoInLine, EnfermeiroInLine]

    list_display= ['username','email', 'perfil','is_staff']
    list_filter=['perfil']
    campos_extras= (
        ('Informações hospitalares', {
            'fields':('perfil', 'cpf')
        }),
    )

    fieldsets=UserAdmin.fieldsets+ campos_extras
admin.site.register(Usuario, UsuarioAdmin)
admin.site.register(Secretaria)
admin.site.register(Paciente)
admin.site.register(Medico)
admin.site.register(Enfermeiro)
admin.site.register(Consulta)
admin.site.register(Leito)
admin.site.register(Suprimento)