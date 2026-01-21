# 🚗 Sistema de Gestão de Frota Globo

Sistema web moderno desenvolvido em Python com Flask para gerenciamento completo da frota de veículos para as Olimpíadas de Inverno.

## ✨ Funcionalidades Principais

### 🎯 Dashboard Interativo
- **Métricas em Tempo Real:** Veículos disponíveis, viagens em rota e viagens do dia
- **Cards Clicáveis:** Detalhamento instantâneo ao clicar nas métricas
- **Visualização Intuitiva:** Interface moderna com paleta Globo/Globoplay

### 🚙 Gestão de Veículos
- Cadastro completo de veículos (placa, marca, modelo, ano, cor, combustível)
- Controle de KM atual e próximas revisões
- Status automático: Disponível, Em Uso, Manutenção

### 📅 Sistema de Agendamentos
- Agendamento de veículos com data, hora e destinos
- Confirmação de agendamentos (admin)
- Gestão de passageiros e observações
- Integração com eventos/produções

### 🛣️ Controle de Viagens
- Registro de saída com KM inicial e motorista
- Registro de chegada com KM final
- Histórico detalhado com datas, horários e distâncias percorridas
- Cronograma de viagens em andamento

### 👥 Gerenciamento de Usuários
- Sistema de autenticação seguro (Flask-Login + Bcrypt)
- Níveis de permissão: Admin e Motorista
- Cadastro de novos usuários, motoristas e veículos

### 📊 Relatórios
- Relatórios de viagens por data
- Análise de quilometragem por veículo
- Estatísticas de uso da frota

### 🎨 Interface Moderna
- Design responsivo com Bootstrap 5
- Paleta de cores Globo/Globoplay (gradiente vermelho-laranja)
- Modo claro/escuro com persistência
- Animações suaves e feedback visual

## 🚀 Tecnologias Utilizadas

- **Backend:** Python 3.10+, Flask 3.0
- **Banco de Dados:** PostgreSQL 15+ com SQLAlchemy ORM
- **Autenticação:** Flask-Login, Flask-Bcrypt
- **Frontend:** HTML5, CSS3, Bootstrap 5.3, JavaScript
- **Migrações:** Flask-Migrate (Alembic)
- **Cache:** Flask-Caching
- **Timezone:** zoneinfo (America/Sao_Paulo)

## 📋 Pré-requisitos

- Python 3.10 ou superior
- PostgreSQL 15 ou superior
- Git

## ⚙️ Instalação e Configuração

### 1️⃣ Clone o Repositório
```bash
git clone https://github.com/seu-usuario/sistema-frota-fundec.git
cd sistema-frota-fundec
```

### 2️⃣ Crie e Ative o Ambiente Virtual
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3️⃣ Instale as Dependências
```bash
pip install -r requirements.txt
```

### 4️⃣ Configure o Banco de Dados PostgreSQL

Crie um banco de dados PostgreSQL:
```sql
CREATE DATABASE frota_globo;
CREATE USER frota_user WITH PASSWORD 'sua_senha_segura';
GRANT ALL PRIVILEGES ON DATABASE frota_globo TO frota_user;
```

### 5️⃣ Configure as Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto:
```env
FLASK_ENV=development
SECRET_KEY=sua_chave_secreta_muito_segura
DATABASE_URL=postgresql://frota_user:sua_senha_segura@localhost:5432/frota_globo
```

Ou use `.env.example` como base:
```bash
cp .env.example .env
# Edite o arquivo .env com suas configurações
```

### 6️⃣ Inicialize o Banco de Dados

Execute o script de inicialização:
```bash
# Inicialização simples (cria tabelas e admin padrão)
python init_db_simple.py

# OU inicialização completa (com dados de exemplo)
python init_db.py
```

**Credenciais padrão do admin:**
- Email: `admin@frota.local`
- Senha: `admin123`

### 7️⃣ Execute a Aplicação
```bash
# Modo desenvolvimento
python app.py

# OU usando Flask CLI
flask run
```

Acesse: `http://localhost:5000`

## 🗂️ Estrutura do Projeto

```
sistema-frota-fundec/
├── app.py                      # Aplicação Flask principal
├── config.py                   # Configurações do ambiente
├── models.py                   # Modelos SQLAlchemy (ORM)
├── requirements.txt            # Dependências Python
├── init_db.py                  # Script de inicialização do BD
├── init_db_simple.py           # Script simplificado
├── setup.py                    # Utilitário de setup
├── .env.example                # Template de variáveis de ambiente
├── static/
│   └── css/
│       └── style.css           # Estilos customizados (paleta Globo)
├── templates/                  # Templates HTML
│   ├── base.html               # Template base
│   ├── index.html              # Dashboard
│   ├── login.html              # Login
│   ├── agendamentos.html       # Lista de agendamentos
│   ├── agendar_veiculo.html    # Novo agendamento
│   ├── cronograma.html         # Viagens em andamento
│   ├── historico.html          # Histórico de viagens
│   ├── registrar_saida.html    # Registro de saída
│   ├── registrar_chegada.html  # Registro de chegada
│   ├── gerenciar.html          # Gestão de usuários/veículos
│   ├── relatorios.html         # Relatórios
│   └── ...
├── migrations/                 # Migrações do banco de dados
├── tests/                      # Scripts de teste
├── utils/                      # Utilitários diversos
└── docs/                       # Documentação adicional
```

## 🗄️ Modelo de Dados

### Tabelas Principais

- **usuarios:** Usuários do sistema (admin/motorista)
- **veiculos:** Cadastro de veículos da frota
- **agendamentos:** Agendamentos de veículos
- **viagens:** Registro de viagens realizadas
- **manutencoes:** Histórico de manutenções
- **abastecimentos:** Controle de abastecimentos
- **auditoria:** Log de ações no sistema

## 🔐 Segurança

- Senhas criptografadas com Bcrypt
- Proteção CSRF nos formulários
- Sessões seguras com Flask-Login
- Validação de permissões por role (admin/motorista)
- Auditoria de ações

## 🎨 Paleta de Cores (Globo/Globoplay)

```css
--primary-gradient: linear-gradient(90deg, #ff002b 0%, #ff7b00 100%);
--accent-color: #ff002b;
--bg-color: #F2F2F2;
--card-bg: #FFFFFF;
--text-main: #1A1A1A;
--text-muted: #666666;
```

## 📱 Uso do Sistema

### Para Administradores

1. **Dashboard:** Visualize métricas em tempo real
2. **Gerenciar:** Adicione veículos, usuários e motoristas
3. **Agendamentos:** Confirme ou cancele solicitações
4. **Registrar Saída:** Inicie viagens confirmadas
5. **Registrar Chegada:** Finalize viagens em andamento
6. **Relatórios:** Analise dados de uso da frota

### Para Motoristas/Usuários

1. **Agendar Veículo:** Solicite uso de veículos
2. **Cronograma:** Visualize viagens em andamento
3. **Agendamentos:** Acompanhe suas solicitações

## 🐛 Troubleshooting

### Erro de conexão com PostgreSQL
```bash
# Verifique se o PostgreSQL está rodando
# Windows
pg_ctl status

# Verifique a string de conexão no .env
DATABASE_URL=postgresql://usuario:senha@localhost:5432/nome_bd
```

### Erro de importação de módulos
```bash
# Reinstale as dependências
pip install --upgrade -r requirements.txt
```

### Problemas com timezone
O sistema usa `America/Sao_Paulo` por padrão. Verifique `models.py` e `app.py`.

## 🚀 Deploy (Produção)

Para deploy em produção, consulte `docs/DEPLOYMENT_PRODUCAO.md`.

Recomendações:
- Use Gunicorn ou uWSGI como servidor WSGI
- Configure PostgreSQL com backup automático
- Utilize HTTPS (certificado SSL)
- Configure variáveis de ambiente seguras
- Implemente rate limiting e monitoramento

## 📄 Licença

Uso interno - FUNDEC. Todos os direitos reservados.

## 👨‍💻 Desenvolvimento

Para contribuir ou reportar bugs, entre em contato com a equipe de TI da FUNDEC.

---

**Versão:** 2.0 (PostgreSQL)  
**Última Atualização:** Janeiro 2026
