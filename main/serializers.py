from rest_framework import serializers
from .models import Usuario, Paciente, Consulta, Leito, Suprimento, Medico, Enfermeiro, Secretaria
from django.contrib.auth.hashers import make_password
import re


def validar_cpf(value):
    cpf_limpo= re.sub(r'[^0-9]', '', value)
    if len(cpf_limpo)!=11:
        raise serializers.ValidationError('O cpf deve ter 11 números.')

    elif cpf_limpo in [str(i)*11 for i in range(10)]:
        raise serializers.ValidationError('Cpf inválido')
    return cpf_limpo

class SecretariaSerializer(serializers.ModelSerializer):
    class Meta:
        model=Secretaria
        fields='__all__'

class PacienteSerializer(serializers.ModelSerializer):
    class Meta:
        model=Paciente
        fields='__all__'
    def validate_cpf(self, value):
        return validar_cpf(value)

class MedicoSerializer(serializers.ModelSerializer):
    class Meta:
        model=Medico
        fields= ['id','usuario','crm', 'especialidade']

    def validate_crm(self, value):
        return value

class EnfermeiroSerializer(serializers.ModelSerializer):
    class Meta:
        model=Enfermeiro
        fields=['id','usuario','coren', 'setor']


class UsuarioSerializer(serializers.ModelSerializer):
    detalhe_pa=PacienteSerializer(source='dados_paciente', read_only=True)
    detalhe_me=MedicoSerializer(source='perfil_medico', read_only=True)
    detalhe_en= EnfermeiroSerializer(source='perfil_enfermeiro', read_only=True)
    detalhe_se= SecretariaSerializer(source='perfil_secretaria', read_only=True)
    class Meta:
        model= Usuario
        fields=['id', 'username', 'email', 'password', 'perfil', 'cpf', 'detalhe_pa','detalhe_me', 'detalhe_en', 'detalhe_se']
        extra_kwargs={
            'password':{'write_only':True},
            'email':{'required':True}}
    def validate_username(self, value):
        if len(value)<4:
            raise serializers.ValidationError('O nome de usuário deve conter mais de 4 caracteres')
        return value
    
    def validate_email(self, value):
        if not value:
            raise serializers.ValidationError('O email é obrigatório.')
        return value

    def validate_cpf(self, value):
        return validar_cpf(value)


    def create(self, validated_data):
        validated_data['password']= make_password(validated_data.get('password'))
        return super(UsuarioSerializer, self).create(validated_data)

class ConsultaSerializer(serializers.ModelSerializer):
    class Meta:
        model=Consulta
        fields= '__all__'
    def validate(self, data):
        user= self.context.get('request').user
        if data.get('status')=='AGENDADA':
            if user.perfil not in ['SECRETARIA', 'MEDICO','ENFERMEIRO','ADMIN']:
                raise serializers.ValidationError({'status':'Apenas funcionários podem confirmar a consulta'})
        return data
class LeitoSerializer(serializers.ModelSerializer):
    class Meta:
        model=Leito
        fields='__all__'

    def validate(self, data):
        if data.get('ocupado') is True and not data.get('paciente_atual'):
            raise serializers.ValidationError('Informe o paciente atual.')
        
        if data.get('ocupado') is False:
            data['paciente_atual']= None
        return data

class SuprimentoSerializer(serializers.ModelSerializer):
    class Meta:
        model= Suprimento
        fields= '__all__'
