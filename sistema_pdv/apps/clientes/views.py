from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from .forms import ClienteForm
from .models import Cliente
from . import services


def index(request):
    clientes = services.buscar_clientes()
    form = ClienteForm()
    return render(request, 'clientes/index.html', {
        'clientes': clientes,
        'form': form,
    })


def create(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse('clientes:index'))
    return redirect(reverse('clientes:index'))


def edit(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)

    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            return redirect(reverse('clientes:index'))
    else:
        form = ClienteForm(instance=cliente)

    clientes = services.buscar_clientes()

    return render(request, 'clientes/index.html', {
        'clientes': clientes,
        'form': form,
        'edit_id': cliente.pk,
    })


def delete(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)

    if request.method == 'POST':
        cliente.delete()

    return redirect(reverse('clientes:index'))
