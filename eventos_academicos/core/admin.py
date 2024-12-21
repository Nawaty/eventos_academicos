from django.contrib import admin
from .models import Usuario, Evento, Palestra, Inscricao, Certificado
from django.apps import apps

# Registro manual dos modelos no admin
admin.site.register(Evento)
admin.site.register(Palestra)
admin.site.register(Inscricao)

# Configuração personalizada do modelo Certificado
@admin.register(Certificado)
class CertificadoAdmin(admin.ModelAdmin):
    # Campos que serão exibidos no Django Admin
    list_display = ('id', 'nome_participante', 'evento', 'data_emissao')
    search_fields = ('nome_participante', 'evento__nome', 'data_emissao')
    list_filter = ('evento', 'data_emissao')

    # Define os campos que podem ser editados diretamente no admin
    fields = ('nome_participante', 'evento', 'data_emissao')

# Configuração personalizada do modelo Usuario no admin
@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'cpf', 'tipo_usuario', 'instituicao']
    search_fields = ['username', 'cpf', 'email']
    list_filter = ['tipo_usuario']

# Registro automático de outros modelos
for model in apps.get_models():
    if model not in admin.site._registry:
        try:
            admin.site.register(model)
        except admin.sites.AlreadyRegistered:
            pass
