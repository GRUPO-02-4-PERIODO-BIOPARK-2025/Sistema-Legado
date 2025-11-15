from django.shortcuts import render

def login_view(request):
    return render(request, 'usuarios/login.html')

def cadastro_view(request):
    return render(request, 'usuarios/cadastro.html')

def recuperar_senha_view(request):
    return render(request, 'usuarios/recuperar_senha.html')
