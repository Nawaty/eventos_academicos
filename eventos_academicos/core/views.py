# core/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse
from .models import Evento, Inscricao, Palestra, Usuario, Certificado
from .webhooks import WebhookService
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.db import IntegrityError
from django.contrib.auth import get_user_model
from django.utils.timezone import now
from datetime import datetime


def home(request):
    return render(request, 'home.html')  # Renderiza o template 'home.html'
def cadastro(request):
    if request.method == 'POST':
        # Pegando os dados do formulário
        username = request.POST.get('username')
        email = request.POST.get('email')
        cpf = request.POST.get('cpf')
        instituicao = request.POST.get('instituicao')
        tipo_usuario = request.POST.get('tipo_usuario')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        # Verificando se as senhas coincidem
        if password1 != password2:
            return HttpResponse("As senhas não coincidem.")

        # Verificando se o CPF já está cadastrado
        if Usuario.objects.filter(cpf=cpf).exists():
            return HttpResponse("Erro: CPF já cadastrado.")
        
        # Verificando se o nome de usuário já existe
        if get_user_model().objects.filter(username=username).exists():
            return HttpResponse("Erro: Nome de usuário já cadastrado.")

        # Criação do usuário
        try:
            usuario = Usuario.objects.create_user(
                username=username,
                email=email,
                password=password1,
                cpf=cpf,
                instituicao=instituicao,
                tipo_usuario=tipo_usuario
            )
            login(request, usuario)  # Fazendo login do usuário após cadastro
            return redirect('home')  # Alterar para a URL de destino

        except IntegrityError as e:
            return HttpResponse(f"Erro: {e}")
    else:
        return render(request, 'cadastro.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "Login bem-sucedido!")
            return redirect('home')  # Redireciona para a página inicial após o login
        else:
            messages.error(request, "Usuário ou senha inválidos.")
    
    return render(request, 'login.html')
@login_required
def lista_eventos(request):
    eventos = Evento.objects.all()
    return render(request, 'eventos/lista_eventos.html', {'eventos': eventos})

@login_required
def detalhes_evento(request, evento_id):
    evento = get_object_or_404(Evento, pk=evento_id)
    palestras = Palestra.objects.filter(evento=evento)
    ja_inscrito = False
    
    if request.user.is_authenticated:
        # Mudando de participante para usuario
        ja_inscrito = Inscricao.objects.filter(evento=evento, usuario=request.user).exists()
    
    context = {
        'evento': evento,
        'palestras': palestras,
        'ja_inscrito': ja_inscrito,
    }
    
    # Se for uma requisição HTMX, retorna apenas o conteúdo parcial
    if request.headers.get('HX-Request'):
        return render(request, 'eventos/detalhes_evento.html', context)
    # Se não for HTMX, retorna a página completa
    return render(request, 'eventos/detalhes_evento_completo.html', context)

@login_required
def inscrever_evento(request, evento_id):
    evento = get_object_or_404(Evento, pk=evento_id)
    
    try:
        # Verifica se já existe uma inscrição
        inscricao = Inscricao.objects.create(
            evento=evento,
            usuario=request.user,
            status='CONFIRMADA'
        )
        messages.success(request, 'Inscrição realizada com sucesso!')
        
        # Retorna uma resposta adequada para o HTMX
        return HttpResponse('<div class="alert alert-success">Inscrição realizada com sucesso!</div>')
        
    except IntegrityError:  # Se houver erro de duplicidade
        messages.info(request, 'Você já está inscrito neste evento.')
        return HttpResponse('<div class="alert alert-info">Você já está inscrito neste evento.</div>')

@login_required
def lista_eventos(request):
    eventos = Evento.objects.all()
    # Verifica se o usuário é professor
    is_professor = request.user.tipo_usuario == 'PROFESSOR'
    return render(request, 'eventos/lista_eventos.html', {
        'eventos': eventos,
        'is_professor': is_professor
    })

def confirmar_inscricao(request, inscricao_id):
    try:
        inscricao = Inscricao.objects.get(id=inscricao_id, usuario=request.user)
        if inscricao.status != 'CONFIRMADA':
            inscricao.status = 'CONFIRMADA'
            inscricao.save()
        # A criação do certificado será feita automaticamente no método save da Inscricao
        return redirect('lista_eventos')
    except Inscricao.DoesNotExist:
        return redirect('erro')  # ou alguma página de erro se não encontrar a inscrição
    
@login_required
def certificado_evento(request, evento_id):
    # Busca o certificado específico pelo ID do certificado
    certificado = get_object_or_404(Certificado, id=evento_id)

    return render(request, 'certificados/certificado_template.html', {
        'certificado': certificado
    })

@login_required
def certificados_gerados(request):
    # Filtra os certificados que têm o nome do participante igual ao nome do usuário logado
    certificados = Certificado.objects.filter(nome_participante=request.user.username)

    return render(request, 'certificados/certificados_gerados.html', {
        'certificados': certificados
    })

def is_professor(user):
    return user.is_authenticated and user.tipo_usuario == 'PROFESSOR'

@user_passes_test(is_professor)
def cadastrar_evento(request):
    if request.method == 'POST':
        try:
            evento = Evento.objects.create(
                nome=request.POST['nome'],
                descricao=request.POST['descricao'],
                data_inicio=request.POST['data_inicio'],
                data_fim=request.POST['data_fim'],
                local=request.POST['local'],
                organizador=request.user,
                valor_inscricao=request.POST['valor_inscricao']
            )
            messages.success(request, 'Evento cadastrado com sucesso!')
            return redirect('lista_eventos')
        except Exception as e:
            messages.error(request, f'Erro ao cadastrar evento: {str(e)}')
    
    return render(request, 'eventos/cadastrar_evento.html')

@user_passes_test(is_professor)
def gerar_certificado(request, inscricao_id):
    if request.method == 'POST':
        inscricao = get_object_or_404(Inscricao, id=inscricao_id)
        
        # Verifica se o professor é organizador do evento
        if inscricao.evento.organizador != request.user:
            messages.error(request, 'Você não tem permissão para gerar este certificado.')
            return redirect('lista_eventos')
        
        # Cria ou atualiza o certificado
        certificado, created = Certificado.objects.get_or_create(
            usuario=inscricao.usuario,
            evento=inscricao.evento,
            defaults={
                'nome_participante': inscricao.usuario.username,
                'data_emissao': datetime.now().date()
            }
        )
        
        messages.success(request, 'Certificado gerado com sucesso!')
        return redirect('detalhes_evento', evento_id=inscricao.evento.id)

@user_passes_test(is_professor)
def listar_participantes(request, evento_id):
    evento = get_object_or_404(Evento, id=evento_id)
    
    # Verifica se o professor é organizador do evento
    if evento.organizador != request.user:
        messages.error(request, 'Você não tem permissão para ver os participantes deste evento.')
        return redirect('lista_eventos')
    
    inscricoes = Inscricao.objects.filter(evento=evento)
    return render(request, 'eventos/listar_participantes.html', {
        'evento': evento,
        'inscricoes': inscricoes
    })
@login_required
def confirmar_inscricao(request, inscricao_id):
    inscricao = get_object_or_404(Inscricao, pk=inscricao_id)
    
    # Verifica se o usuário logado é o organizador do evento
    if request.user == inscricao.evento.organizador:
        inscricao.status = 'CONFIRMADA'
        inscricao.save()
        messages.success(request, 'Inscrição confirmada com sucesso!')
    else:
        messages.error(request, 'Você não tem permissão para confirmar esta inscrição.')
    
    return redirect('listar_participantes', evento_id=inscricao.evento.id)