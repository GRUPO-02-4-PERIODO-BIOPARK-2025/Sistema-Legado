from django.shortcuts import render

def index(request):
    return render(request, 'vendas/index.html')
