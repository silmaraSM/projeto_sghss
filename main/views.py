from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework import generics
from .models import Usuario, Paciente, Consulta, Leito, Suprimento, Medico, Enfermeiro, Secretaria
from .serializers import UsuarioSerializer, PacienteSerializer, ConsultaSerializer, LeitoSerializer, SuprimentoSerializer, MedicoSerializer, EnfermeiroSerializer, SecretariaSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from django.http import HttpResponse
import logging
from rest_framework import permissions
from django_filters.rest_framework import DjangoFilterBackend

logger= logging.getLogger(__name__)


class RegistroUsuarioView(generics.CreateAPIView):
    queryset= Usuario.objects.all()
    serializer_class= UsuarioSerializer
    permission_classes=[AllowAny]
    
    def perform_create(self, serializer):
        perfil_enviado= self.request.data.get('perfil', 'PACIENTE')
        if perfil_enviado in ['MEDICO', 'ADMIN', 'ENFERMEIRO', 'SECRETARIA']:
            perfil_enviado='PACIENTE'
        serializer.save(perfil=perfil_enviado)

class PerfilUsuarioView(APIView):
    permission_classes=[IsAuthenticated]

    def get(self, request):
        serializer= UsuarioSerializer(request.user)
        return Response(serializer.data)


class PacienteViewSet(viewsets.ModelViewSet):
    serializer_class= PacienteSerializer
    permission_classes=[IsAuthenticated]

    def get_queryset(self):
        user= self.request.user
        if user.perfil in ['MEDICO', 'ENFERMEIRO', 'ADMIN']:
            return Paciente.objects.all()
        return Paciente.objects.filter(usuario=user)

    def perform_create(self, serializer):
        serializer.save()
    
    def retrieve(self, request, *args, **kwargs):
        instace= self.get_object()
        logger.info(f'O usuário {request.user.username} acessou o prontário do paciente {instace.nome}')
        return super().retrieve(request, *args, **kwargs)


class Funcionario(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.perfil in ['ADMIN','MEDICO','ENFERMEIRO','SECRETARIA']

class SecretariaViewSet(viewsets.ModelViewSet):
    queryset=Secretaria.objects.all()
    serializer_class=SecretariaSerializer
    permission_classes=[permissions.IsAdminUser]

class ConsultaViewSet(viewsets.ModelViewSet):
    queryset= Consulta.objects.all()
    serializer_class=ConsultaSerializer
    filter_backends= [DjangoFilterBackend]
    filterset_fields= ['status', 'medico', 'tipo']


    def get_queryset(self):
        user= self.request.user
        if user.perfil in ['MEDICO', 'ENFERMEIRO','SECRETARIA']:
            return Consulta.objects.all()
        return Consulta.objects.filter(paciente__usuario=user)
  
    @action(detail=True, methods=['post'])
    def cancelar(self, request, pk=None):
        consulta= self.get_object()
        consulta.status= 'CANCELADA'
        consulta.save()
        return Response({'status': 'Consulta cancelada'}, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['patch'], name='Emitir receita')
    def emitir_receita(self, request, pk=None):
        consulta= self.get_object()
        if request.user != consulta.medico:
            return Response({'erro':'Apenas o médico responsável pode emitir a receita.'},status=status.HTTP_403_FORBIDDEN)
        
        receita=request.data.get('receita_digital')
        if not receita:
            return Response({'erro':'O conteúdo da receita é obrigatório'}, status=status.HTTP_400_BAD_REQUEST)

        consulta.receita_digital= receita
        consulta.save()
        return Response({'mensagem': 'Rceita criada'}, status=status.HTTP_200_OK)



class LeitoViewSet(viewsets.ModelViewSet):
    queryset= Leito.objects.all()
    serializer_class=LeitoSerializer
    permission_classes=[Funcionario]


    def get_queryset(self):
        user= self.request.user
        if user.perfil in ['MEDICO', 'ADMIN', 'ENFERMEIRO']:
            return Leito.objects.all()
        return Leito.objects.none()
    
    @action(detail=False, methods=['get'])
    def relatorio(self, request):
        if request.user.perfil != 'ADMIN':
            return Response({'erro':'Acesso negado'}, status=status.HTTP_403_FORBIDDEN)
        
        total= Leito.objects.count()
        ocupados= Leito.objects.filter(ocupado=True).count()
        disponivel= total-ocupados
        
        return Response({
            'total_de_leitos':total,
            'ocupado':ocupados,
            'disponiveis': disponivel,
            'ocupação': f"{(ocupados/total)*100:.2f}%" if total > 0 else 0
        })



class SuprimentoViewSet(viewsets.ModelViewSet):
    queryset= Suprimento.objects.all()
    serializer_class= SuprimentoSerializer
    permission_classes= [Funcionario]
    def get_permissions(self):
        if self.action in 'destroy':
            return [IsAdminUser()]
        return super().get_permissions()

class MedicoViewSet(viewsets.ModelViewSet):
    queryset= Medico.objects.all()
    serializer_class= MedicoSerializer
    permission_classes=[permissions.IsAdminUser]

class EnfermeiroViewSet(viewsets.ModelViewSet):
    queryset= Enfermeiro.objects.all()
    serializer_class= EnfermeiroSerializer
    permission_classes=[permissions.IsAdminUser]