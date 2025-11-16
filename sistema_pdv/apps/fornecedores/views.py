from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from .forms import FornecedorForm
from .models import Fornecedor
from . import services


def index(request):
    fornecedores = services.buscar_fornecedores()
    form = FornecedorForm()
    return render(request, 'fornecedores/index.html', {
        'fornecedores': fornecedores,
        'form': form,
    })


def create(request):
    if request.method == 'POST':
        form = FornecedorForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse('fornecedores:index'))
    return redirect(reverse('fornecedores:index'))


def edit(request, pk):
    fornecedor = get_object_or_404(Fornecedor, pk=pk)
    if request.method == 'POST':
        form = FornecedorForm(request.POST, instance=fornecedor)
        if form.is_valid():
            form.save()
            return redirect(reverse('fornecedores:index'))
    else:
        form = FornecedorForm(instance=fornecedor)
    fornecedores = services.buscar_fornecedores()
    return render(request, 'fornecedores/index.html', {
        'fornecedores': fornecedores,
        'form': form,
        'edit_id': fornecedor.pk,
    })


def delete(request, pk):
    fornecedor = get_object_or_404(Fornecedor, pk=pk)
    if request.method == 'POST':
        fornecedor.delete()
    return redirect(reverse('fornecedores:index'))
