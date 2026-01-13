from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import RegistroUsuarioView, PacienteViewSet, PerfilUsuarioView, ConsultaViewSet, LeitoViewSet, SuprimentoViewSet, MedicoViewSet, EnfermeiroViewSet, SecretariaSerializer
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views

router= DefaultRouter()
router.register(r'pacientes', PacienteViewSet, basename='paciente')
router.register(r'secretarias', views.SecretariaViewSet)
router.register(r'consultas', ConsultaViewSet, basename='consulta')
router.register(r'leitos', LeitoViewSet, basename='leito')
router.register(r'suprimentos', SuprimentoViewSet, basename='suprimento')
router.register(r'medicos', views.MedicoViewSet)
router.register(r'enfermeiros', views.EnfermeiroViewSet)


urlpatterns = [
    path('registrar/', RegistroUsuarioView.as_view(), name='registrar'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('perfil/', PerfilUsuarioView.as_view(), name='perfil'),
    
]+ router.urls