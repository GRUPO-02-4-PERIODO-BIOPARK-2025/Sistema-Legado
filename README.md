# Sistema PDV - Sistema Legado

Sistema de Ponto de Venda (PDV) desenvolvido em Django com MySQL.

## 📋 Pré-requisitos

Antes de começar, certifique-se de ter instalado em sua máquina:

### 1. Python
- **Versão recomendada:** Python 3.9 ou superior
- **Download:** https://www.python.org/downloads/
- Durante a instalação, marque a opção "Add Python to PATH"
- Verificar instalação:
```powershell
python --version
```

### 2. Docker Desktop
- **Versão recomendada:** Docker Desktop 4.0 ou superior
- **Download:** https://www.docker.com/products/docker-desktop/
- O Docker será usado para executar o MySQL e phpMyAdmin
- Verificar instalação:
```powershell
docker --version
docker-compose --version
```

### 3. Git (opcional)
- **Versão recomendada:** Git 2.30 ou superior
- **Download:** https://git-scm.com/downloads

## 🚀 Passo a Passo para Executar o Projeto

### Passo 1: Clonar o Projeto (se ainda não tiver)

```powershell
git clone https://github.com/GRUPO-02-4-PERIODO-BIOPARK-2025/Sistema-Legado.git
cd Sistema-Legado
```

Ou simplesmente navegue até a pasta do projeto se já o tiver baixado.

### Passo 2: Configurar o Ambiente Virtual Python

Abra o PowerShell na raiz do projeto e execute:

```powershell
# Criar ambiente virtual
python -m venv venv

# Ativar o ambiente virtual
.\venv\Scripts\Activate.ps1
```

**Nota:** Se encontrar erro de execução de scripts, execute primeiro:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Passo 3: Instalar Dependências Python

Com o ambiente virtual ativado, instale as dependências:

```powershell
cd sistema_pdv
pip install -r requirements.txt
```

As dependências instaladas serão:
- **Django >= 4.0** - Framework web
- **PyMySQL >= 1.1** - Conector MySQL para Python
- **cryptography >= 41.0.0** - Biblioteca de criptografia

### Passo 4: Iniciar os Containers Docker (MySQL e phpMyAdmin)

Volte para a raiz do projeto e inicie os containers:

```powershell
cd ..
docker-compose up -d
```

Este comando irá:
- Baixar as imagens do MySQL 8.0 e phpMyAdmin
- Criar e iniciar os containers
- MySQL estará disponível na porta **3307**
- phpMyAdmin estará disponível na porta **8080**

Verificar se os containers estão rodando:
```powershell
docker ps
```

Você deverá ver dois containers:
- `mysql_pdv` (porta 3307:3306)
- `phpmyadmin_pdv` (porta 8080:80)

### Passo 5: Configurar o Banco de Dados

Com os containers rodando, execute as migrações do Django:

```powershell
cd sistema_pdv
python manage.py migrate
```

Este comando criará todas as tabelas necessárias no banco de dados MySQL.

### Passo 6: Criar Superusuário (Admin)

Crie um usuário administrador para acessar o sistema:

```powershell
python manage.py createsuperuser
```

Preencha as informações solicitadas:
- Username
- Email (pode deixar em branco)
- Password
- Password (confirmação)

### Passo 7: Executar o Servidor Django

Inicie o servidor de desenvolvimento:

```powershell
python manage.py runserver
```

O servidor iniciará em: **http://127.0.0.1:8000**

## 🌐 Acessando o Sistema

### Sistema PDV
- **URL:** http://127.0.0.1:8000
- **Login:** Use o superusuário criado no Passo 6

### Admin Django
- **URL:** http://127.0.0.1:8000/admin
- **Login:** Use o superusuário criado no Passo 6

### phpMyAdmin (Gerenciador de Banco de Dados)
- **URL:** http://localhost:8080
- **Servidor:** mysql
- **Usuário:** root
- **Senha:** root

## 📁 Estrutura de Arquivos Importantes

### Arquivos de Configuração

#### `docker-compose.yml` (Raiz do projeto)
Configuração dos containers Docker:
- MySQL: porta 3307, usuário: user, senha: userpass
- phpMyAdmin: porta 8080

#### `sistema_pdv/sistema_pdv/settings.py`
Configurações principais do Django:
- Banco de dados (MySQL na porta 3307)
- Apps instalados
- Configurações de sessão
- URLs de login/logout

#### `sistema_pdv/requirements.txt`
Dependências Python do projeto.

### Estrutura de Aplicações

O projeto está dividido em módulos (apps Django):

- **clientes/** - Gerenciamento de clientes
- **dashboard/** - Dashboard principal
- **estoque/** - Controle de estoque
- **fornecedores/** - Cadastro de fornecedores
- **funcionarios/** - Gerenciamento de funcionários
- **produtos/** - Cadastro de produtos
- **usuarios/** - Autenticação e usuários
- **vendas/** - Registro de vendas

## 🔧 Configurações do Banco de Dados

As configurações do banco de dados estão em `sistema_pdv/sistema_pdv/settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'sistema_pdv',
        'USER': 'user',
        'PASSWORD': 'userpass',
        'HOST': '127.0.0.1',
        'PORT': '3307',
    }
}
```

**Importante:** A porta MySQL está mapeada para **3307** (não 3306) para evitar conflitos com instalações locais do MySQL.

## 🛑 Parando o Projeto

### Parar o servidor Django
Pressione `Ctrl + C` no terminal onde o servidor está rodando.

### Parar os containers Docker
```powershell
docker-compose down
```

Para parar e remover também os volumes (apaga dados do banco):
```powershell
docker-compose down -v
```

## 🔄 Comandos Úteis

### Resetar o Banco de Dados
```powershell
# Parar containers
docker-compose down -v

# Iniciar containers novamente
docker-compose up -d

# Executar migrações
cd sistema_pdv
python manage.py migrate

# Criar superusuário novamente
python manage.py createsuperuser
```

### Criar novas migrações (após alterar models.py)
```powershell
python manage.py makemigrations
python manage.py migrate
```

### Coletar arquivos estáticos
```powershell
python manage.py collectstatic
```

### Ver logs dos containers Docker
```powershell
docker-compose logs -f
```

## ⚠️ Problemas Comuns e Soluções

### Erro: "Can't connect to MySQL server"
- Verifique se os containers Docker estão rodando: `docker ps`
- Aguarde alguns segundos após iniciar os containers
- Verifique se a porta 3307 não está em uso

### Erro: "Port is already allocated"
- Alguma aplicação está usando as portas 3307 ou 8080
- Altere as portas no `docker-compose.yml` se necessário

### Erro ao ativar ambiente virtual
Execute no PowerShell como Administrador:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Migrações não aplicadas
```powershell
python manage.py migrate --run-syncdb
```

## 📝 Versões Testadas

- **Python:** 3.9+
- **Django:** 4.0+
- **MySQL:** 8.0
- **PyMySQL:** 1.1+
- **Docker:** 20.10+
- **Docker Compose:** 1.29+

## 📧 Configuração de E-mail (Recuperação de Senha)

Para habilitar a funcionalidade de recuperação de senha por e-mail:

### 1. Configurar Gmail

1. Acesse sua conta do Gmail
2. Ative a verificação em duas etapas
3. Gere uma senha de app em: https://myaccount.google.com/apppasswords
4. Copie a senha de app gerada (16 caracteres)

### 2. Configurar Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto (copie do `.env.example`):

```env
EMAIL_HOST_USER=seu-email@gmail.com
EMAIL_HOST_PASSWORD=sua-senha-app-do-gmail
```

### 3. Configurar no Windows (PowerShell)

```powershell
$Env:EMAIL_HOST_USER = "seu-email@gmail.com"
$Env:EMAIL_HOST_PASSWORD = "xxxx xxxx xxxx xxxx"
```

**Nota:** Se não configurar o e-mail, a nova senha será exibida na tela após a recuperação.

## 👥 Equipe

**Grupo 02 - 4º Período Biopark 2025**

## 📄 Licença

Este projeto é um sistema legado para fins educacionais.
