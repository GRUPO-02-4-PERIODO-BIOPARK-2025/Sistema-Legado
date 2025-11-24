from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError

class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Digite seu nome de usuário',
            'autocomplete': 'username'
        }),
        label='Nome de Usuário',
        error_messages={
            'required': 'O nome de usuário é obrigatório.'
        }
    )
    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Digite sua senha',
            'autocomplete': 'current-password'
        }),
        label='Senha',
        error_messages={
            'required': 'A senha é obrigatória.'
        }
    )

class CadastroForm(UserCreationForm):
    TIPO_USUARIO_CHOICES = [
        ('administrador', 'Administrador'),
        ('funcionario', 'Funcionário'),
    ]
    
    full_name = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Digite seu nome completo'}),
        label='Nome Completo'
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Digite seu e-mail'}),
        label='E-mail'
    )
    username = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Digite seu nome de usuário'}),
        label='Nome de Usuário'
    )
    tipo_usuario = forms.ChoiceField(
        choices=TIPO_USUARIO_CHOICES,
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Tipo de Usuário',
        initial='funcionario'
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Digite sua senha'}),
        label='Senha'
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirme sua senha'}),
        label='Confirmar Senha'
    )

    class Meta:
        model = User
        fields = ['full_name', 'username', 'email', 'tipo_usuario', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('Este e-mail já está cadastrado.')
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError('Este nome de usuário já está em uso.')
        return username

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        full_name = self.cleaned_data.get('full_name', '')
        tipo_usuario = self.cleaned_data.get('tipo_usuario', 'funcionario')
        
        name_parts = full_name.split(' ', 1)
        user.first_name = name_parts[0]
        user.last_name = name_parts[1] if len(name_parts) > 1 else ''
        
        if commit:
            user.save()
            from .models import Perfil
            Perfil.objects.create(usuario=user, permissao=tipo_usuario)
        return user


class RecuperarSenhaForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite seu nome de usuário',
            'autocomplete': 'username'
        }),
        label='Nome de Usuário',
        error_messages={
            'required': 'O nome de usuário é obrigatório.'
        }
    )
