from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from .forms import FuncionarioForm
from .models import Funcionario
from . import services


def index(request):
    funcionarios = services.buscar_funcionarios()
    form = FuncionarioForm()
    return render(request, 'funcionarios/index.html', {
        'funcionarios': funcionarios,
        'form': form,
    })


def create(request):
    if request.method == 'POST':
        form = FuncionarioForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse('funcionarios:index'))
    return redirect(reverse('funcionarios:index'))


def edit(request, pk):
    funcionario = get_object_or_404(Funcionario, pk=pk)
    if request.method == 'POST':
        form = FuncionarioForm(request.POST, instance=funcionario)
        if form.is_valid():
            form.save()
            return redirect(reverse('funcionarios:index'))
    else:
        form = FuncionarioForm(instance=funcionario)
    funcionarios = services.buscar_funcionarios()
    return render(request, 'funcionarios/index.html', {
        'funcionarios': funcionarios,
        'form': form,
        'edit_id': funcionario.pk,
    })


def delete(request, pk):
    funcionario = get_object_or_404(Funcionario, pk=pk)
    if request.method == 'POST':
        funcionario.delete()
    return redirect(reverse('funcionarios:index'))
