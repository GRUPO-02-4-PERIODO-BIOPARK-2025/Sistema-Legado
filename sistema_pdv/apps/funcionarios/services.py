from .models import Funcionario


def buscar_funcionarios():
    return Funcionario.objects.all()
