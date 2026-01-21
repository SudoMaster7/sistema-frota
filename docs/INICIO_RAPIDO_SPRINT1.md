# 🚀 INÍCIO RÁPIDO - Sprint 1 Migração PostgreSQL

## ⏱️ Tempo Total: 2-3 horas

---

## 📝 Pré-requisitos

- ✅ Python 3.8+
- ✅ Docker Desktop (recomendado) ou PostgreSQL local
- ✅ Git
- ✅ VSCode ou IDE preferida

---

## 🎯 Passo 1: Clonar e Preparar (5 min)

```bash
# Navegar para o projeto
cd "c:\Users\leosc\OneDrive\Área de Trabalho\Frota Globo\sistema-frota-fundec"

# Criar venv
python -m venv venv

# Ativar venv
.\venv\Scripts\activate.bat

# Atualizar pip
python -m pip install --upgrade pip
```

---

## 🎯 Passo 2: Instalar Dependências (5 min)

```bash
# Instalar todas as dependências da Sprint 1
pip install -r requirements.txt
```

---

## 🎯 Passo 3: Iniciar Infraestrutura (10 min)

### **Opção A: Docker (Recomendado)**

```bash
# Iniciar PostgreSQL + Redis + pgAdmin + Redis Commander
docker-compose up -d

# Verificar status
docker-compose ps

# Acessar interfaces:
# pgAdmin: http://localhost:5050 (admin@frota.local / admin)
# Redis Commander: http://localhost:8081
```

### **Opção B: PostgreSQL Local**

```bash
# Criar banco de dados
psql -U postgres -c "CREATE DATABASE frota_globo OWNER postgres;"

# Verificar
psql -U postgres -d frota_globo -c "\dt"
```

---

## 🎯 Passo 4: Configurar Variáveis de Ambiente (5 min)

```bash
# Copiar exemplo
copy .env.example .env

# Editar .env com seus valores (recomendado: VSCode)
code .env
```

**Mínimo necessário para desenvolvimento:**

```env
FLASK_ENV=development
FLASK_DEBUG=1
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/frota_globo
REDIS_URL=redis://:redis_password@localhost:6379/0
```

---

## 🎯 Passo 5: Criar Tabelas no Banco (10 min)

```python
# Abrir Python interativo
python

# Copiar e executar:
from app import app, db
from models import Usuario, Veiculo, Agendamento, Viagem

with app.app_context():
    db.create_all()
    print("✅ Tabelas criadas com sucesso!")

# Sair
exit()
```

---

## 🎯 Passo 6: Criar Usuário Admin (5 min)

```python
# Abrir Python interativo
python

# Executar:
from app import app, db
from models import Usuario
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

with app.app_context():
    # Criar admin
    admin = Usuario(
        id='admin',
        password_hash=bcrypt.generate_password_hash('admin123').decode('utf-8'),
        role='admin',
        telefone='11999999999',
        email='admin@frotaglobo.com'
    )
    db.session.add(admin)
    db.session.commit()
    print("✅ Usuário admin criado!")
    print("   Usuário: admin")
    print("   Senha: admin123")

exit()
```

---

## 🎯 Passo 7: Migrar Dados do Google Sheets (45 min)

```bash
# Executar script de migração
python migrations/migrate_from_sheets.py

# Será exibido:
# 1️⃣ Conectando ao Google Sheets...
# 2️⃣ Migrando Usuários...
# 3️⃣ Migrando Veículos...
# ... e assim por diante
```

---

## ✅ Passo 8: Iniciar Aplicação (2 min)

```bash
# Iniciar Flask
python app.py

# Ou com Gunicorn (produção)
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

**Acessar em:** http://localhost:5000

**Login de teste:**
- Usuário: `admin`
- Senha: `admin123`

---

## 🔍 Passo 9: Validar Tudo (10 min)

```bash
# Terminal 1: Rodar testes
pytest test_migration.py -v

# Terminal 2: Verificar logs
tail -f logs/frota_globo.log

# Terminal 3: Monitorar banco
# Abrir http://localhost:5050 (pgAdmin)
```

---

## 📊 Dashboard de Monitoramento

- **pgAdmin** (Banco PostgreSQL): http://localhost:5050
- **Redis Commander** (Cache): http://localhost:8081
- **Aplicação**: http://localhost:5000

---

## 🐛 Troubleshooting Rápido

### **Erro: "psycopg2: password authentication failed"**

```bash
# Resetar senha do postgres
psql -U postgres -c "ALTER USER postgres WITH PASSWORD 'postgres';"
```

### **Erro: "database frota_globo does not exist"**

```bash
# Criar banco via Docker
docker exec frota_postgres psql -U postgres -c "CREATE DATABASE frota_globo OWNER postgres;"
```

### **Erro: "Cannot connect to Docker daemon"**

```bash
# Verificar se Docker está rodando
docker ps

# Se não estiver, inicie o Docker Desktop
```

### **Redis connection refused**

```bash
# Verificar Redis
docker logs frota_redis

# Reiniciar
docker-compose restart redis
```

---

## 📁 Estrutura Criada

```
sistema-frota-fundec/
├── models.py                          ← Modelos SQLAlchemy
├── config.py                          ← Configuração
├── app.py                             ← Aplicação (será refatorada)
├── setup.py                           ← Script de setup
├── requirements.txt                   ← Dependências (atualizado)
├── .env.example                       ← Template de variáveis
├── .env                               ← Variáveis (não commitar!)
├── docker-compose.yml                 ← Infraestrutura Docker
├── migrations/
│   └── migrate_from_sheets.py         ← Script de migração
├── logs/
│   └── frota_globo.log               ← Logs da aplicação
└── tests/
    └── test_migration.py              ← Testes de validação
```

---

## 🎓 Próximas Sprints

**Sprint 2 (Semana 2):**
- Implementar Logging profissional
- Setup Redis Cache
- Validação com Flask-WTF

**Sprint 3-4 (Semanas 3-4):**
- Testes automatizados (pytest)
- Refatorar rotas para ORM
- API RESTful básica

---

## 📞 Suporte

Se algo não funcionar:

1. Verifique o arquivo `.env` está configurado
2. Verifique se containers Docker estão rodando: `docker-compose ps`
3. Verifique se PostgreSQL está acessível: `psql -U postgres -d frota_globo -c "SELECT 1;"`
4. Consulte logs: `docker logs frota_postgres`

---

**Estimado:** 2-3 horas para completar tudo  
**Próximo:** Seguir com Sprint 2 após validação

✅ **Status:** Pronto para começar!
