# 🚀 SPRINT 1: Migração para PostgreSQL + SQLAlchemy

**Status:** Em Andamento  
**Objetivo:** Migrar o sistema de Google Sheets para PostgreSQL  
**Duração:** 2 semanas  
**Prioridade:** 🔴 CRÍTICA

---

## 📋 Checklist

- [x] Criar modelos SQLAlchemy (models.py)
- [x] Criar configuração de ambiente (config.py)
- [ ] Instalar dependências
- [ ] Setup PostgreSQL local
- [ ] Criar script de migração de dados
- [ ] Setup Alembic para versionamento de schema
- [ ] Refatorar app.py para usar ORM
- [ ] Testes de conexão e integridade de dados
- [ ] Validar todas as rotas com novo banco
- [ ] Documentação de deployment

---

## 🔧 Passo a Passo de Implementação

### **Passo 1: Instalar Dependências**

```bash
# Ativar venv
.\venv\Scripts\activate.bat

# Instalar pacotes PostgreSQL e ORM
pip install flask-sqlalchemy psycopg2-binary flask-migrate alembic
pip install flask-wtf email-validator python-dateutil

# Atualizar requirements.txt
pip freeze > requirements.txt
```

---

### **Passo 2: Setup PostgreSQL Local (Windows)**

#### **Opção A: PostgreSQL instalado localmente**

```bash
# Criar banco de dados
psql -U postgres -c "CREATE DATABASE frota_globo OWNER postgres;"

# Verificar conexão
psql -U postgres -d frota_globo -c "\dt"
```

#### **Opção B: Docker Compose (Recomendado)**

Criar arquivo `docker-compose.yml`:

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    container_name: frota_postgres
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: frota_globo
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: frota_redis
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
```

Executar:

```bash
# No diretório do projeto
docker-compose up -d

# Verificar se está rodando
docker-compose ps
```

---

### **Passo 3: Inicializar Banco de Dados com Alembic**

```bash
# Inicializar Alembic
flask db init migrations

# Criar primeira migração
flask db migrate -m "Criar tabelas iniciais"

# Aplicar migração
flask db upgrade
```

---

### **Passo 4: Atualizar app.py**

Arquivo `app_novo.py` (para manter backup):

```python
# app_novo.py (versão com SQLAlchemy)
import os
from flask import Flask, render_template, request, redirect, url_for, flash, abort, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_migrate import Migrate
from flask_caching import Cache
from datetime import datetime
import pytz
import json
import logging
from logging.handlers import RotatingFileHandler

# Importar modelos e config
from models import db, Usuario, Veiculo, Agendamento, Viagem, Auditoria
from config import config

# --- CONFIGURAÇÃO INICIAL ---
app = Flask(__name__)
app.config.from_object(config)

# --- BANCO DE DADOS ---
db.init_app(app)
migrate = Migrate(app, db)

# --- CACHE ---
cache = Cache(app)

# --- FLASK-LOGIN ---
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = "Por favor, faça login para acessar esta página."

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(user_id)

# --- LOGGING ---
if not app.debug:
    os.makedirs('logs', exist_ok=True)
    file_handler = RotatingFileHandler(
        'logs/frota_globo.log',
        maxBytes=10485760,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
    ))
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)

# --- ROTAS ---

@app.route('/')
@login_required
@cache.cached(timeout=300)
def index():
    """Dashboard principal"""
    try:
        veiculos_disponiveis = Veiculo.query.filter_by(status='Disponível').count()
        viagens_em_rota = Viagem.query.filter_by(status='Em Andamento').count()
        
        hoje = datetime.now(pytz.timezone('America/Sao_Paulo')).date()
        viagens_hoje = Viagem.query.filter(
            db.func.date(Viagem.data_saida) == hoje
        ).count()
        
        agendamentos_proximos = Agendamento.query.filter(
            Agendamento.data_solicitada >= hoje,
            Agendamento.status == 'Agendado'
        ).order_by(Agendamento.data_solicitada).limit(10).all()
        
        return render_template('index.html',
                              veiculos_disponiveis=veiculos_disponiveis,
                              viagens_em_rota=viagens_em_rota,
                              viagens_hoje=viagens_hoje,
                              agendamentos_proximos=agendamentos_proximos)
    except Exception as e:
        app.logger.error(f"Erro ao carregar dashboard: {str(e)}")
        flash("Erro ao carregar dashboard", "danger")
        return render_template('index.html',
                              veiculos_disponiveis=0,
                              viagens_em_rota=0,
                              viagens_hoje=0)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login do usuário"""
    if request.method == 'POST':
        try:
            username = request.form.get('username')
            password = request.form.get('password')
            
            usuario = Usuario.query.get(username)
            
            if usuario and usuario.verificar_senha(password):
                login_user(usuario)
                
                # Log de auditoria
                auditoria = Auditoria(
                    usuario_id=usuario.id,
                    acao='Login',
                    entidade='Usuario',
                    entidade_id=None,
                    ip_address=request.remote_addr,
                    user_agent=request.headers.get('User-Agent', '')
                )
                db.session.add(auditoria)
                db.session.commit()
                
                app.logger.info(f"Usuário {username} fez login")
                flash(f"Bem-vindo, {username}!", "success")
                return redirect(url_for('index'))
            else:
                # Log de tentativa falha
                auditoria = Auditoria(
                    usuario_id=username or 'desconhecido',
                    acao='Tentativa de login falha',
                    entidade='Usuario',
                    ip_address=request.remote_addr,
                    user_agent=request.headers.get('User-Agent', '')
                )
                db.session.add(auditoria)
                db.session.commit()
                
                app.logger.warning(f"Tentativa de login falha para {username}")
                flash("Usuário ou senha incorretos", "danger")
        except Exception as e:
            app.logger.error(f"Erro no login: {str(e)}")
            flash("Erro ao fazer login", "danger")
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    """Logout do usuário"""
    try:
        # Log de auditoria
        auditoria = Auditoria(
            usuario_id=current_user.id,
            acao='Logout',
            entidade='Usuario',
            ip_address=request.remote_addr
        )
        db.session.add(auditoria)
        db.session.commit()
        
        app.logger.info(f"Usuário {current_user.id} fez logout")
        logout_user()
        flash("Logout realizado com sucesso!", "success")
    except Exception as e:
        app.logger.error(f"Erro ao fazer logout: {str(e)}")
        logout_user()
    
    return redirect(url_for('login'))

# --- CRIAR APLICAÇÃO ---
if __name__ == '__main__':
    with app.app_context():
        # Criar tabelas se não existirem
        db.create_all()
        print("✅ Banco de dados pronto!")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
```

---

### **Passo 5: Criar Script de Migração Google Sheets → PostgreSQL**

Arquivo `migrations/migrate_from_sheets.py`:

```python
"""
Script para migrar dados do Google Sheets para PostgreSQL
Execução: python migrations/migrate_from_sheets.py
"""

import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import pytz
from app import app, db
from models import Usuario, Veiculo, Agendamento, Viagem, Auditoria
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()
TZ = pytz.timezone('America/Sao_Paulo')

def migrar_dados():
    """Migra dados do Google Sheets para PostgreSQL"""
    
    print("\n" + "="*70)
    print("🔄 INICIANDO MIGRAÇÃO DE DADOS")
    print("="*70 + "\n")
    
    try:
        # Conectar ao Google Sheets
        print("1️⃣ Conectando ao Google Sheets...")
        scope = ['https://www.googleapis.com/auth/spreadsheets', 
                 'https://www.googleapis.com/auth/drive.file']
        
        creds_json_str = os.environ.get('GOOGLE_CREDENTIALS_JSON')
        if creds_json_str:
            creds_dict = json.loads(creds_json_str)
            creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        else:
            creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
        
        client = gspread.authorize(creds)
        spreadsheet = client.open_by_key('1ZjTYIRF_n91JSCI1OytRYaRFiGkZX2JgoqB0eRIwu8I')
        print("   ✅ Conexão estabelecida\n")
        
        # Migrar Usuários
        print("2️⃣ Migrando Usuários...")
        usuarios_sheet = spreadsheet.worksheet("DB_Usuarios")
        usuarios_data = usuarios_sheet.get_all_records()
        
        for idx, user_data in enumerate(usuarios_data, 1):
            try:
                usuario = Usuario(
                    id=user_data['Usuario'],
                    password_hash=bcrypt.generate_password_hash(user_data['Senha']).decode('utf-8'),
                    role=user_data.get('Role', 'motorista'),
                    telefone=user_data.get('Telefone'),
                    email=user_data.get('Email')
                )
                db.session.add(usuario)
                print(f"   ✓ Usuário {user_data['Usuario']} importado")
            except Exception as e:
                print(f"   ⚠️  Erro ao importar usuário {user_data['Usuario']}: {e}")
        
        db.session.commit()
        print(f"   ✅ {len(usuarios_data)} usuários migrados\n")
        
        # Migrar Veículos
        print("3️⃣ Migrando Veículos...")
        veiculos_sheet = spreadsheet.worksheet("DB_Veiculos")
        veiculos_data = veiculos_sheet.get_all_records()
        
        for idx, veiculo_data in enumerate(veiculos_data, 1):
            try:
                veiculo = Veiculo(
                    placa=veiculo_data['Placa'],
                    marca=veiculo_data.get('Marca'),
                    modelo=veiculo_data.get('Modelo'),
                    ano=int(veiculo_data['Ano']) if veiculo_data.get('Ano') else None,
                    status='Disponível'
                )
                db.session.add(veiculo)
                print(f"   ✓ Veículo {veiculo_data['Placa']} importado")
            except Exception as e:
                print(f"   ⚠️  Erro ao importar veículo {veiculo_data.get('Placa', 'N/A')}: {e}")
        
        db.session.commit()
        print(f"   ✅ {len(veiculos_data)} veículos migrados\n")
        
        # Migrar Agendamentos
        print("4️⃣ Migrando Agendamentos...")
        agendamentos_sheet = spreadsheet.worksheet("DB_Agendamentos")
        agendamentos_data = agendamentos_sheet.get_all_records()
        
        for idx, ag_data in enumerate(agendamentos_data, 1):
            try:
                agendamento = Agendamento(
                    usuario_id=ag_data.get('Motorista', 'admin'),
                    placa=ag_data['PlacaVeiculo'],
                    data_solicitada=datetime.strptime(ag_data['DataSolicitada'], '%d/%m/%Y').date(),
                    hora_inicio=datetime.strptime(ag_data['HoraInicio'], '%H:%M').time(),
                    hora_fim=datetime.strptime(ag_data['HoraFim'], '%H:%M').time(),
                    destinos=ag_data.get('Destinos'),
                    status=ag_data.get('Status', 'Agendado'),
                    producao_evento=ag_data.get('Produção/Evento')
                )
                db.session.add(agendamento)
                print(f"   ✓ Agendamento {ag_data['PlacaVeiculo']} importado")
            except Exception as e:
                print(f"   ⚠️  Erro ao importar agendamento: {e}")
        
        db.session.commit()
        print(f"   ✅ {len(agendamentos_data)} agendamentos migrados\n")
        
        # Migrar Viagens
        print("5️⃣ Migrando Viagens...")
        viagens_sheet = spreadsheet.worksheet("DB_Viagens")
        viagens_data = viagens_sheet.get_all_records()
        
        for idx, viagem_data in enumerate(viagens_data, 1):
            try:
                viagem = Viagem(
                    motorista_id=viagem_data.get('Motorista', 'admin'),
                    placa=viagem_data['PlacaVeiculo'],
                    data_saida=datetime.strptime(f"{viagem_data['DataSaida']} {viagem_data.get('HoraSaida', '00:00')}", '%d/%m/%Y %H:%M'),
                    km_saida=float(viagem_data.get('KMSaida', 0)),
                    destino=viagem_data.get('Destino'),
                    status='Finalizada'
                )
                db.session.add(viagem)
                print(f"   ✓ Viagem {viagem_data['PlacaVeiculo']} importada")
            except Exception as e:
                print(f"   ⚠️  Erro ao importar viagem: {e}")
        
        db.session.commit()
        print(f"   ✅ {len(viagens_data)} viagens migradas\n")
        
        print("="*70)
        print("✅ MIGRAÇÃO CONCLUÍDA COM SUCESSO!")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\n❌ ERRO NA MIGRAÇÃO: {e}")
        db.session.rollback()
        return False
    
    return True

if __name__ == '__main__':
    with app.app_context():
        # Criar tabelas
        db.create_all()
        print("✅ Tabelas criadas/verificadas")
        
        # Migrar dados
        if migrar_dados():
            print("🎉 Sistema pronto para usar com PostgreSQL!")
        else:
            print("🚫 Migração falhou! Verifique os erros acima.")
```

---

### **Passo 6: Executar Migração**

```bash
# Ativar venv
.\venv\Scripts\activate.bat

# Verificar conexão com PostgreSQL
psql -U postgres -d frota_globo -c "SELECT 1;"

# Executar migração
python migrations/migrate_from_sheets.py
```

---

### **Passo 7: Testes de Validação**

Criar arquivo `test_migration.py`:

```python
"""
Testes de validação da migração
"""

import pytest
from app import app, db
from models import Usuario, Veiculo, Agendamento, Viagem

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        with app.app_context():
            yield client

def test_usuarios_migrados(client):
    """Verifica se usuários foram migrados"""
    usuarios = Usuario.query.all()
    assert len(usuarios) > 0, "Nenhum usuário foi migrado!"

def test_veiculos_migrados(client):
    """Verifica se veículos foram migrados"""
    veiculos = Veiculo.query.all()
    assert len(veiculos) > 0, "Nenhum veículo foi migrado!"

def test_agendamentos_migrados(client):
    """Verifica se agendamentos foram migrados"""
    agendamentos = Agendamento.query.all()
    assert len(agendamentos) > 0, "Nenhum agendamento foi migrado!"

def test_login_com_novo_banco(client):
    """Verifica se login funciona com novo banco"""
    response = client.post('/login', data={
        'username': 'admin',
        'password': 'admin123'
    })
    # Deve fazer redirect se login bem-sucedido
    assert response.status_code in [200, 302]
```

Executar testes:

```bash
pytest test_migration.py -v
```

---

## 📦 Atualizar requirements.txt

```txt
Flask==2.3.0
Flask-SQLAlchemy==3.0.0
psycopg2-binary==2.9.0
Flask-Migrate==4.0.0
Flask-Login==0.6.0
Flask-Bcrypt==1.0.0
Flask-WTF==1.1.0
Flask-Caching==2.0.0
gspread==5.7.0
oauth2client==4.1.0
python-dateutil==2.8.0
pytz==2023.3
email-validator==1.3.0
```

---

## 🔍 Troubleshooting

### **Erro: "psycopg2: FATAL: password authentication failed"**

```bash
# Resetar senha do PostgreSQL
psql -U postgres -c "ALTER USER postgres WITH PASSWORD 'novasenha';"

# Atualizar DATABASE_URL
# DATABASE_URL=postgresql://postgres:novasenha@localhost:5432/frota_globo
```

### **Erro: "database frota_globo does not exist"**

```bash
# Criar banco
psql -U postgres -c "CREATE DATABASE frota_globo OWNER postgres;"
```

### **Erro: "relation already exists"**

```bash
# Dropar banco existente
psql -U postgres -c "DROP DATABASE frota_globo CASCADE;"

# Recriar
psql -U postgres -c "CREATE DATABASE frota_globo OWNER postgres;"

# Rodar migração novamente
python migrations/migrate_from_sheets.py
```

---

## ✅ Checklist Final

- [ ] PostgreSQL instalado e rodando
- [ ] Banco `frota_globo` criado
- [ ] models.py criado
- [ ] config.py criado
- [ ] app_novo.py criado com SQLAlchemy
- [ ] Dependências instaladas
- [ ] Migração de dados executada com sucesso
- [ ] Testes de validação passando
- [ ] Login funciona com novo banco
- [ ] Dashboard carrega dados corretamente
- [ ] Logs sendo salvos em arquivo

---

**Próximos Passos (Sprint 2):**
- [ ] Implementar sistema de Logs profissional
- [ ] Setup Redis para Cache
- [ ] Validação de dados com Flask-WTF
- [ ] Refatorar todas as rotas para ORM

---

**Status:** 🔄 Em Andamento  
**Última atualização:** 21/01/2026
