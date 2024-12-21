# core/webhooks.py
import requests
import json
from django.conf import settings
from .models import Evento, Inscricao

class WebhookService:
    @staticmethod
    def enviar_notificacao_inscricao(inscricao):
        """
        Envia notificação via webhook quando uma nova inscrição é realizada
        """
        url_webhook = settings.WEBHOOK_NOTIFICACOES_URL
        
        payload = {
            'evento': inscricao.evento.nome,
            'participante': inscricao.usuario.username,
            'data_inscricao': inscricao.data_inscricao.isoformat(),
            'status': inscricao.status
        }
        
        try:
            response = requests.post(url_webhook, json=payload, timeout=5)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            # Log do erro de webhook
            print(f"Erro ao enviar webhook: {e}")

    @staticmethod
    def notificar_proximidade_evento(evento):
        """
        Envia notificação de proximidade de evento
        """
        url_webhook = settings.WEBHOOK_EVENTOS_PROXIMOS_URL
        
        # Buscar inscritos no evento
        inscritos = Inscricao.objects.filter(evento=evento, status='CONFIRMADA')
        
        payload = {
            'evento': {
                'nome': evento.nome,
                'data_inicio': evento.data_inicio.isoformat(),
                'local': evento.local
            },
            'inscritos': [
                {
                    'nome': inscricao.usuario.username,
                    'email': inscricao.usuario.email
                } for inscricao in inscritos
            ]
        }
        
        try:
            response = requests.post(url_webhook, json=payload, timeout=5)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Erro ao enviar webhook de eventos próximos: {e}")

# settings.py - adicionar no final do arquivo
WEBHOOK_NOTIFICACOES_URL = 'https://seu-servico-webhook.com/notificacoes'
WEBHOOK_EVENTOS_PROXIMOS_URL = 'https://seu-servico-webhook.com/eventos-proximos'