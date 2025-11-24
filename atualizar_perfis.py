"""
Script para atualizar perfis existentes sem permissão definida.
Executa: python sistema_pdv/manage.py shell < atualizar_perfis.py
"""
from apps.usuarios.models import Perfil

perfis_atualizados = 0
perfis_existentes = Perfil.objects.filter(permissao='usuario')

for perfil in perfis_existentes:
    perfil.permissao = 'administrador'  # Define como administrador por padrão
    perfil.save()
    perfis_atualizados += 1
    print(f'✓ Perfil de {perfil.usuario.username} atualizado para administrador')

print(f'\n{perfis_atualizados} perfis foram atualizados!')
