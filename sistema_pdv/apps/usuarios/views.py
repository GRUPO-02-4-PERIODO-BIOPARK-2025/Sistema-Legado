from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import LoginForm, CadastroForm

def login_view(request):
    if request.user.is_authenticated:
        logout(request)
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                if user.is_active:
                    login(request, user)
                    nome = user.first_name if user.first_name else user.username
                    messages.success(request, f'Bem-vindo, {nome}!')
                    return redirect('dashboard:index')
                else:
                    messages.error(request, 'Sua conta está desativada. Entre em contato com o administrador.')
            else:
                messages.error(request, 'Usuário ou senha inválidos. Verifique suas credenciais e tente novamente.')
        else:
            messages.error(request, 'Por favor, corrija os erros no formulário.')
    else:
        form = LoginForm()
    
    return render(request, 'usuarios/login.html', {'form': form})

def cadastro_view(request):
    if request.user.is_authenticated:
        logout(request)
    
    if request.method == 'POST':
        form = CadastroForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Cadastro realizado com sucesso! Faça login para continuar.')
            return redirect('usuarios:login')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{error}')
    else:
        form = CadastroForm()
    
    return render(request, 'usuarios/cadastro.html', {'form': form})

@login_required(login_url='usuarios:login')
def logout_view(request):
    logout(request)
    messages.success(request, 'Você saiu do sistema com sucesso.')
    return redirect('usuarios:login')

def recuperar_senha_view(request):
    return render(request, 'usuarios/recuperar_senha.html')
