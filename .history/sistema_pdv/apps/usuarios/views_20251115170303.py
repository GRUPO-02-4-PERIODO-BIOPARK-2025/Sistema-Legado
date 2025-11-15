from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib import messages
from .forms import LoginForm, CadastroForm

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f'Bem-vindo, {user.first_name}!')
                return redirect('dashboard:index')
            else:
                messages.error(request, 'Usuário ou senha inválidos.')
    else:
        form = LoginForm()
    
    return render(request, 'usuarios/login.html', {'form': form})

def cadastro_view(request):
    if request.method == 'POST':
        form = CadastroForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Cadastro realizado com sucesso! Faça login para continuar.')
            return redirect('usuarios:login')
        else:
            # Adicionar mensagens de erro específicas
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{error}')
    else:
        form = CadastroForm()
    
    return render(request, 'usuarios/cadastro.html', {'form': form})

def recuperar_senha_view(request):
    return render(request, 'usuarios/recuperar_senha.html')
