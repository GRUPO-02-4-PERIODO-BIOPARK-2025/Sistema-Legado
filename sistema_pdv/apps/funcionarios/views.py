"""Funcionarios views placeholder"""
from django.shortcuts import render

def index(request):
    return render(request, 'funcionarios/index.html')
