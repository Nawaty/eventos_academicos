from django.contrib import admin
from django.urls import path
from core import views
from django.contrib.auth import views as auth_views
from core.views import confirmar_inscricao,certificados_gerados

urlpatterns = [
    path('', views.home, name='home'),
    path('admin/', admin.site.urls),
    path('eventos/', views.lista_eventos, name='lista_eventos'),
    path('evento/<int:evento_id>/', views.detalhes_evento, name='detalhes_evento'),
    path('inscrever/<int:evento_id>/', views.inscrever_evento, name='inscrever_evento'),
    path('buscar-eventos/', views.lista_eventos, name='buscar_eventos'),
    path('cadastro/', views.cadastro, name='cadastro'),
    path('login/', views.login_view, name='login'),
    path('confirmar-inscricao/<int:inscricao_id>/', views.confirmar_inscricao, name='confirmar_inscricao'),
    path('certificados/', views.certificados_gerados, name='certificados_gerados'),
    path('certificado/<int:evento_id>/', views.certificado_evento, name='certificado_evento'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('evento/cadastrar/', views.cadastrar_evento, name='cadastrar_evento'),
    path('evento/<int:evento_id>/participantes/', views.listar_participantes, name='listar_participantes'),
    path('certificado/gerar/<int:inscricao_id>/', views.gerar_certificado, name='gerar_certificado'),
    path('confirmar-inscricao/<int:inscricao_id>/', views.confirmar_inscricao, name='confirmar_inscricao'),
]

