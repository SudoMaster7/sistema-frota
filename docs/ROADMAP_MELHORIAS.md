# 🚀 Roadmap de Melhorias - Sistema Frota Globo

**Versão Atual:** 2.0 - Refatoração Globo Frotas  
**Data:** Janeiro 2026  
**Objetivo:** Transformar em um sistema profissional de nível corporativo

---

## 📋 Índice

1. [Melhorias Críticas](#-críticas-alta-prioridade)
2. [Melhorias Importantes](#-importantes-média-prioridade)
3. [Melhorias Desejáveis](#-desejáveis-baixa-prioridade)
4. [Segurança & Compliance](#️-segurança--compliance)
5. [UX/UI](#-uxui)
6. [Infraestrutura](#️-infraestrutura)
7. [Roadmap Sugerido](#-roadmap-sugerido-12-meses)
8. [Estimativas de Esforço](#-estimativas-de-esforço)

---

## 🔴 CRÍTICAS (Alta Prioridade)

### 1. Migrar de Google Sheets para Banco de Dados Real

**Problema Atual:**
- Google Sheets tem limite de 300 requisições/minuto por usuário
- Não suporta transações ACID
- Performance degradada com muitos dados
- Sem relacionamentos nativos entre tabelas

**Solução Proposta:**
- **PostgreSQL** (recomendado para produção)
- **MySQL** (alternativa robusta)
- **SQLite** (desenvolvimento/testes)

**Tecnologias:**
```python
# SQLAlchemy ORM
pip install flask-sqlalchemy psycopg2-binary

# Migrations
pip install flask-migrate alembic
```

**Benefícios:**
- ✅ Performance 100x maior
- ✅ Transações ACID garantidas
- ✅ Relacionamentos (Foreign Keys)
- ✅ Backups automáticos
- ✅ Índices para queries rápidas
- ✅ Suporta milhões de registros

**Esforço:** 40 horas | **Complexidade:** Alta

---

### 2. Adicionar Validação de Dados Robusta

**Problema Atual:**
- Validação apenas no frontend (fácil de burlar)
- Dados inconsistentes podem ser salvos
- Sem sanitização de inputs

**Solução Proposta:**
```python
# Flask-WTF para validação
pip install flask-wtf email-validator

# Exemplo de validação
from flask_wtf import FlaskForm
from wtforms import StringField, DateField, SelectField
from wtforms.validators import DataRequired, Length, Regexp

class AgendamentoForm(FlaskForm):
    placa = StringField('Placa', validators=[
        DataRequired(),
        Regexp(r'^[A-Z]{3}[0-9][A-Z0-9][0-9]{2}$', message='Placa inválida (formato ABC1D23)')
    ])
    data = DateField('Data', validators=[DataRequired()])
    motorista = SelectField('Motorista', validators=[DataRequired()])
```

**Validações Necessárias:**
- ✅ Placas (formato Mercosul: ABC1D23 e antigo: ABC-1234)
- ✅ CPF (11 dígitos, validação de dígito verificador)
- ✅ Telefone (formato brasileiro)
- ✅ Datas (não permitir datas passadas para agendamentos)
- ✅ Horários (início < fim, sem conflitos)
- ✅ Email (formato válido)

**Esforço:** 20 horas | **Complexidade:** Média

---

### 3. Implementar Sistema de Logs Profissional

**Problema Atual:**
- Apenas `print()` no console
- Logs perdidos ao reiniciar aplicação
- Difícil debugar erros em produção

**Solução Proposta:**
```python
# Configuração de logging
import logging
from logging.handlers import RotatingFileHandler

# Criar logger
logger = logging.getLogger('frota_globo')
logger.setLevel(logging.DEBUG)

# Handler para arquivo (10MB, 5 backups)
file_handler = RotatingFileHandler(
    'logs/frota_globo.log',
    maxBytes=10485760,
    backupCount=5
)
file_handler.setLevel(logging.INFO)

# Formato dos logs
formatter = logging.Formatter(
    '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Uso
logger.info(f'Usuário {current_user.id} fez login')
logger.error(f'Erro ao agendar veículo: {str(e)}')
logger.warning(f'Tentativa de acesso negada: {ip_address}')
```

**Estrutura de Logs:**
```
logs/
├── frota_globo.log          # Log atual
├── frota_globo.log.1        # Backup 1
├── frota_globo.log.2        # Backup 2
├── ...
└── error.log                # Apenas erros críticos
```

**Benefícios:**
- ✅ Rastreabilidade completa
- ✅ Debug em produção
- ✅ Auditoria de segurança
- ✅ Análise de performance

**Esforço:** 15 horas | **Complexidade:** Baixa

---

### 4. Cache para Reduzir Chamadas à API

**Problema Atual:**
- Cada página faz 5-10 chamadas ao Google Sheets
- Lentidão em horários de pico
- Risco de atingir limites da API

**Solução Proposta:**
```python
# Redis para cache
pip install flask-caching redis

# Configuração
from flask_caching import Cache

cache = Cache(app, config={
    'CACHE_TYPE': 'redis',
    'CACHE_REDIS_URL': 'redis://localhost:6379/0',
    'CACHE_DEFAULT_TIMEOUT': 300  # 5 minutos
})

# Uso
@app.route('/veiculos')
@cache.cached(timeout=600)  # Cache por 10 minutos
def listar_veiculos():
    veiculos = veiculos_sheet.get_all_records()
    return render_template('veiculos.html', veiculos=veiculos)

# Invalidar cache ao modificar
@app.route('/veiculos/editar', methods=['POST'])
def editar_veiculo():
    # ... salvar mudanças ...
    cache.delete_memoized(listar_veiculos)
    flash('Veículo atualizado!', 'success')
```

**Benefícios:**
- ✅ Velocidade 10x maior
- ✅ Redução de 80% nas chamadas à API
- ✅ Melhor experiência do usuário
- ✅ Economia de custos

**Esforço:** 25 horas | **Complexidade:** Média

---

### 5. Testes Automatizados

**Problema Atual:**
- Zero testes automatizados
- Bugs descobertos apenas em produção
- Medo de fazer mudanças (pode quebrar)

**Solução Proposta:**
```python
# pytest + coverage
pip install pytest pytest-cov pytest-flask faker

# tests/test_auth.py
def test_login_sucesso(client):
    response = client.post('/login', data={
        'username': 'admin',
        'password': 'admin123'
    })
    assert response.status_code == 302  # Redirect
    assert b'Dashboard' in response.data

def test_login_senha_errada(client):
    response = client.post('/login', data={
        'username': 'admin',
        'password': 'errado'
    })
    assert b'incorreta' in response.data

# tests/test_agendamentos.py
def test_criar_agendamento(client, auth):
    auth.login()
    response = client.post('/agendar-veiculo', data={
        'placa': 'ABC1D23',
        'data': '2026-02-01',
        'hora_inicio': '08:00',
        'hora_fim': '18:00'
    })
    assert response.status_code == 302
```

**Cobertura de Testes:**
- ✅ Autenticação (login, logout, permissões)
- ✅ CRUD de agendamentos
- ✅ CRUD de veículos
- ✅ Validações de formulários
- ✅ Filtros e pesquisas
- ✅ Relatórios
- ✅ Auditoria

**Meta:** 80%+ de cobertura

**Esforço:** 80 horas | **Complexidade:** Alta

---

## 🟡 IMPORTANTES (Média Prioridade)

### 6. API RESTful

**Objetivo:** Permitir integração com outros sistemas

**Endpoints:**
```python
# Autenticação JWT
POST /api/v1/auth/login
POST /api/v1/auth/refresh

# Veículos
GET    /api/v1/veiculos
GET    /api/v1/veiculos/{placa}
POST   /api/v1/veiculos
PUT    /api/v1/veiculos/{placa}
DELETE /api/v1/veiculos/{placa}

# Agendamentos
GET    /api/v1/agendamentos
GET    /api/v1/agendamentos/{id}
POST   /api/v1/agendamentos
PUT    /api/v1/agendamentos/{id}
DELETE /api/v1/agendamentos/{id}

# Relatórios
GET    /api/v1/relatorios/veiculos-mais-usados
GET    /api/v1/relatorios/producao-por-evento
GET    /api/v1/relatorios/custos
```

**Tecnologias:**
```python
pip install flask-restful flask-jwt-extended marshmallow
```

**Documentação:**
- Swagger UI (automático)
- Postman Collection
- Exemplos de código

**Esforço:** 60 horas | **Complexidade:** Média

---

### 7. Notificações em Tempo Real

**Canais:**

#### **Email (SMTP)**
```python
pip install flask-mail

# Enviar quando agendamento for aprovado
@app.route('/agendamentos/aprovar/<id>')
def aprovar_agendamento(id):
    # ... aprovar ...
    
    msg = Message(
        'Agendamento Aprovado',
        recipients=[motorista.email]
    )
    msg.body = f'''
    Seu agendamento foi aprovado!
    
    Veículo: {agendamento.placa}
    Data: {agendamento.data}
    Horário: {agendamento.hora_inicio} - {agendamento.hora_fim}
    '''
    mail.send(msg)
```

#### **WhatsApp (Twilio)**
```python
pip install twilio

# Lembrete 1h antes
client = Client(account_sid, auth_token)
message = client.messages.create(
    body='🚗 Lembrete: Você tem um agendamento em 1 hora!',
    from_='whatsapp:+14155238886',
    to=f'whatsapp:+55{motorista.telefone}'
)
```

#### **Push Notifications (PWA)**
```javascript
// Service Worker
self.addEventListener('push', event => {
    const data = event.data.json();
    self.registration.showNotification(data.title, {
        body: data.body,
        icon: '/static/icons/icon-192.png'
    });
});
```

**Gatilhos de Notificação:**
- ✅ Agendamento criado
- ✅ Agendamento aprovado/rejeitado
- ✅ Lembrete 1h antes da saída
- ✅ Alerta de atraso na devolução
- ✅ Manutenção programada
- ✅ Revisão vencendo

**Esforço:** 30 horas | **Complexidade:** Média

---

### 8. Dashboard Avançado com Gráficos

**Visualizações:**

#### **Chart.js**
```javascript
// Gráfico de veículos por status
const ctx = document.getElementById('statusChart').getContext('2d');
new Chart(ctx, {
    type: 'doughnut',
    data: {
        labels: ['Disponíveis', 'Em Uso', 'Manutenção'],
        datasets: [{
            data: [15, 8, 2],
            backgroundColor: ['#34a853', '#fbbc04', '#ea4335']
        }]
    }
});

// Gráfico de agendamentos por mês
const lineChart = new Chart(ctx2, {
    type: 'line',
    data: {
        labels: ['Jan', 'Fev', 'Mar', 'Abr'],
        datasets: [{
            label: 'Agendamentos',
            data: [45, 67, 89, 103]
        }]
    }
});
```

**KPIs (Key Performance Indicators):**
- 📊 Veículos disponíveis vs. em uso
- 📊 Taxa de ocupação mensal
- 📊 Veículos mais solicitados
- 📊 Motoristas mais ativos
- 📊 Produção/Evento mais frequente
- 📊 Custo médio por km
- 📊 Tempo médio de uso

**Filtros:**
- 📅 Período (hoje, semana, mês, ano, customizado)
- 🎬 Produção/Evento
- 🚗 Veículo específico
- 👤 Motorista
- 📍 Destino

**Esforço:** 50 horas | **Complexidade:** Média

---

### 9. Exportação de Relatórios

**Formatos:**

#### **PDF**
```python
pip install weasyprint

from weasyprint import HTML

@app.route('/relatorios/export/pdf')
def export_pdf():
    html = render_template('relatorio_pdf.html', 
                          agendamentos=agendamentos,
                          periodo=periodo)
    pdf = HTML(string=html).write_pdf()
    
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=relatorio.pdf'
    return response
```

#### **Excel**
```python
pip install openpyxl

from openpyxl import Workbook

@app.route('/relatorios/export/excel')
def export_excel():
    wb = Workbook()
    ws = wb.active
    ws.title = "Agendamentos"
    
    # Cabeçalhos
    ws.append(['ID', 'Data', 'Veículo', 'Motorista', 'Status'])
    
    # Dados
    for ag in agendamentos:
        ws.append([ag.id, ag.data, ag.placa, ag.motorista, ag.status])
    
    # Salvar
    wb.save('relatorio.xlsx')
```

#### **CSV**
```python
import csv
from io import StringIO

@app.route('/relatorios/export/csv')
def export_csv():
    si = StringIO()
    writer = csv.writer(si)
    writer.writerow(['ID', 'Data', 'Veículo', 'Motorista'])
    
    for ag in agendamentos:
        writer.writerow([ag.id, ag.data, ag.placa, ag.motorista])
    
    output = make_response(si.getvalue())
    output.headers['Content-Type'] = 'text/csv'
    output.headers['Content-Disposition'] = 'attachment; filename=agendamentos.csv'
    return output
```

**Esforço:** 35 horas | **Complexidade:** Média

---

### 10. Sistema de Manutenção de Veículos

**Funcionalidades:**

#### **Registro de Manutenções**
- Data da manutenção
- Tipo (preventiva/corretiva)
- Descrição
- Peças trocadas
- Custo
- Oficina responsável
- Próxima revisão (KM ou data)

#### **Alertas Automáticos**
```python
# Verificar veículos que precisam de manutenção
def verificar_manutencoes():
    veiculos = Veiculo.query.all()
    
    for veiculo in veiculos:
        # Alerta por KM
        if veiculo.km_atual >= veiculo.km_proxima_revisao:
            enviar_alerta_manutencao(veiculo, tipo='km')
        
        # Alerta por data
        if datetime.now() >= veiculo.data_proxima_revisao:
            enviar_alerta_manutencao(veiculo, tipo='data')
```

#### **Histórico Completo**
- Timeline de todas as manutenções
- Custos acumulados
- Gráfico de gastos por veículo
- Comparativo entre veículos

**Esforço:** 45 horas | **Complexidade:** Média

---

### 11. Controle de Combustível

**Funcionalidades:**

#### **Registro de Abastecimentos**
```python
class Abastecimento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    placa = db.Column(db.String(10))
    data = db.Column(db.DateTime)
    litros = db.Column(db.Float)
    valor_total = db.Column(db.Float)
    km_atual = db.Column(db.Integer)
    tipo_combustivel = db.Column(db.String(20))  # Gasolina, Etanol, Diesel
    posto = db.Column(db.String(100))
```

#### **Cálculos Automáticos**
```python
def calcular_consumo(veiculo):
    abastecimentos = Abastecimento.query.filter_by(
        placa=veiculo.placa
    ).order_by(Abastecimento.km_atual).all()
    
    if len(abastecimentos) < 2:
        return None
    
    ultimo = abastecimentos[-1]
    penultimo = abastecimentos[-2]
    
    km_rodados = ultimo.km_atual - penultimo.km_atual
    consumo = km_rodados / ultimo.litros
    
    return consumo  # km/L
```

#### **Relatórios**
- Consumo médio por veículo
- Gasto mensal com combustível
- Posto mais utilizado
- Veículos com maior/menor eficiência
- Comparativo de custos

**Esforço:** 40 horas | **Complexidade:** Média

---

### 12. Autenticação com 2FA (Two-Factor Authentication)

**Implementação:**

```python
pip install pyotp qrcode

# Gerar QR Code para Google Authenticator
import pyotp
import qrcode
from io import BytesIO

@app.route('/2fa/setup')
@login_required
def setup_2fa():
    # Gerar secret único
    secret = pyotp.random_base32()
    current_user.totp_secret = secret
    db.session.commit()
    
    # Gerar QR Code
    totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
        name=current_user.id,
        issuer_name='Frota Globo'
    )
    
    qr = qrcode.make(totp_uri)
    buf = BytesIO()
    qr.save(buf)
    buf.seek(0)
    
    return send_file(buf, mimetype='image/png')

# Validar código 2FA no login
@app.route('/login/2fa', methods=['POST'])
def verify_2fa():
    code = request.form.get('code')
    
    totp = pyotp.TOTP(current_user.totp_secret)
    
    if totp.verify(code):
        login_user(current_user)
        return redirect(url_for('index'))
    else:
        flash('Código inválido', 'danger')
        return redirect(url_for('login'))
```

**Benefícios:**
- ✅ Segurança adicional contra roubo de senha
- ✅ Compliance com normas de segurança
- ✅ Proteção contra brute force

**Esforço:** 25 horas | **Complexidade:** Média

---

### 13. Versionamento da API

**Estratégia:**

```python
# api/v1/routes.py
@app.route('/api/v1/veiculos')
def api_v1_veiculos():
    return jsonify(veiculos)

# api/v2/routes.py (com melhorias)
@app.route('/api/v2/veiculos')
def api_v2_veiculos():
    # Nova estrutura de resposta
    return jsonify({
        'data': veiculos,
        'meta': {
            'total': len(veiculos),
            'page': 1,
            'per_page': 20
        }
    })

# Deprecation warning
@app.route('/api/v1/veiculos')
def api_v1_veiculos():
    response = jsonify(veiculos)
    response.headers['Warning'] = '299 - "API v1 será descontinuada em 2027-01-01"'
    return response
```

**Changelog Automático:**
```markdown
# API Changelog

## v2.0.0 (2026-06-01)
- ✨ Paginação em todos os endpoints
- ✨ Metadados na resposta
- 🔧 Performance melhorada em 40%

## v1.1.0 (2026-03-01)
- ✨ Novo endpoint /api/v1/relatorios
- 🐛 Fix: filtro de datas corrigido
```

**Esforço:** 20 horas | **Complexidade:** Baixa

---

## 🟢 DESEJÁVEIS (Baixa Prioridade)

### 14. PWA (Progressive Web App)

**Funcionalidades:**
- ✅ Instalável no celular (Android/iOS)
- ✅ Funciona offline
- ✅ Push notifications
- ✅ Ícone na tela inicial

**Implementação:**

```javascript
// manifest.json
{
  "name": "Frota Globo",
  "short_name": "Frota",
  "start_url": "/",
  "display": "standalone",
  "theme_color": "#1a73e8",
  "background_color": "#ffffff",
  "icons": [
    {
      "src": "/static/icons/icon-192.png",
      "sizes": "192x192",
      "type": "image/png"
    },
    {
      "src": "/static/icons/icon-512.png",
      "sizes": "512x512",
      "type": "image/png"
    }
  ]
}

// service-worker.js
const CACHE_NAME = 'frota-v1';
const urlsToCache = [
  '/',
  '/static/css/style.css',
  '/static/js/app.js'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(urlsToCache))
  );
});

self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => response || fetch(event.request))
  );
});
```

**Esforço:** 70 horas | **Complexidade:** Alta

---

### 15. Multi-tenancy (Múltiplas Empresas)

**Arquitetura:**

```python
# Modelo de Tenant
class Tenant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100))
    slug = db.Column(db.String(50), unique=True)
    logo = db.Column(db.String(200))
    cor_primaria = db.Column(db.String(7))  # #1a73e8
    dominio = db.Column(db.String(100))     # empresa.frotaglobo.com
    
# Middleware para identificar tenant
@app.before_request
def identify_tenant():
    # Por subdomínio
    subdomain = request.host.split('.')[0]
    g.tenant = Tenant.query.filter_by(slug=subdomain).first()
    
    # Por domínio customizado
    if not g.tenant:
        g.tenant = Tenant.query.filter_by(dominio=request.host).first()

# Filtrar dados por tenant
@app.route('/veiculos')
def listar_veiculos():
    veiculos = Veiculo.query.filter_by(tenant_id=g.tenant.id).all()
    return render_template('veiculos.html', veiculos=veiculos)
```

**Benefícios:**
- ✅ Uma aplicação para múltiplos clientes
- ✅ Isolamento total de dados
- ✅ Branding personalizado
- ✅ Escalável comercialmente

**Esforço:** 100 horas | **Complexidade:** Muito Alta

---

### 16. Geolocalização e Rastreamento GPS

**Funcionalidades:**

```javascript
// Capturar localização em tempo real
navigator.geolocation.watchPosition(position => {
    const coords = {
        lat: position.coords.latitude,
        lng: position.coords.longitude,
        timestamp: new Date()
    };
    
    // Enviar para servidor via WebSocket
    socket.emit('update_location', coords);
});

// Exibir no mapa (Leaflet.js)
const map = L.map('map').setView([-22.9068, -43.1729], 13);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);

// Adicionar marcador do veículo
const marker = L.marker([lat, lng]).addTo(map);
```

**Alertas:**
- 🚨 Veículo fora da rota planejada
- 🚨 Velocidade acima do permitido
- 🚨 Parada não autorizada
- 🚨 Entrada em área restrita

**Esforço:** 80 horas | **Complexidade:** Alta

---

### 17. Assinatura Digital

**Implementação:**

```javascript
// Canvas para assinatura
const canvas = document.getElementById('signature-pad');
const signaturePad = new SignaturePad(canvas);

// Salvar assinatura
document.getElementById('save-signature').addEventListener('click', () => {
    const dataURL = signaturePad.toDataURL();
    
    fetch('/api/assinaturas', {
        method: 'POST',
        body: JSON.stringify({
            agendamento_id: 123,
            tipo: 'saida',
            assinatura: dataURL
        })
    });
});
```

**Uso:**
- ✅ Assinatura na saída do veículo
- ✅ Assinatura na chegada
- ✅ Assinatura em termos de uso
- ✅ PDF com assinatura incorporada

**Esforço:** 30 horas | **Complexidade:** Média

---

### 18. Integração com ERP/SAP

**Webhooks:**

```python
# Notificar ERP quando agendamento for criado
@app.route('/agendamentos', methods=['POST'])
def criar_agendamento():
    agendamento = Agendamento(**request.json)
    db.session.add(agendamento)
    db.session.commit()
    
    # Webhook para ERP
    requests.post('https://erp.globo.com/api/webhooks/agendamentos', json={
        'evento': 'agendamento.criado',
        'data': agendamento.to_dict()
    })
    
    return jsonify(agendamento.to_dict()), 201
```

**Sincronização:**
- ✅ Importar dados de funcionários do ERP
- ✅ Exportar custos de combustível
- ✅ Sincronizar centro de custos
- ✅ Integrar com folha de pagamento

**Esforço:** 60 horas | **Complexidade:** Alta

---

### 19. App Mobile Nativo

**Tecnologias:**
- React Native ou Flutter
- Firebase Cloud Messaging (push)
- Câmera para fotos

**Funcionalidades:**
- 📱 Agendamento rápido
- 📱 Check-in com QR Code
- 📱 Foto de danos no veículo
- 📱 Navegação GPS integrada
- 📱 Notificações push nativas

**Esforço:** 200 horas | **Complexidade:** Muito Alta

---

### 20. BI e Analytics

**Power BI Integration:**

```python
# Endpoint para Power BI consumir
@app.route('/api/bi/agendamentos')
@require_api_key
def bi_agendamentos():
    agendamentos = Agendamento.query.all()
    
    return jsonify([{
        'id': ag.id,
        'data': ag.data.isoformat(),
        'veiculo': ag.placa,
        'producao': ag.producao_evento,
        'custo_combustivel': ag.custo_combustivel,
        'km_rodados': ag.km_rodados
    } for ag in agendamentos])
```

**Machine Learning:**
```python
# Prever demanda de veículos
from sklearn.ensemble import RandomForestRegressor

def prever_demanda(data_futura):
    # Treinar modelo com histórico
    X = historico[['dia_semana', 'mes', 'feriado']]
    y = historico['num_agendamentos']
    
    model = RandomForestRegressor()
    model.fit(X, y)
    
    # Prever
    previsao = model.predict([[data_futura.weekday(), data_futura.month, 0]])
    return int(previsao[0])
```

**Esforço:** 120 horas | **Complexidade:** Muito Alta

---

## 🛡️ SEGURANÇA & COMPLIANCE

### 21. HTTPS Obrigatório

```python
# Force HTTPS
from flask_talisman import Talisman

Talisman(app, 
         force_https=True,
         strict_transport_security=True,
         strict_transport_security_max_age=31536000)
```

**Esforço:** 5 horas

---

### 22. Rate Limiting

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

@app.route('/login', methods=['POST'])
@limiter.limit("5 per minute")
def login():
    # Máximo 5 tentativas de login por minuto
    pass
```

**Esforço:** 10 horas

---

### 23. LGPD/GDPR Compliance

**Funcionalidades:**
- ✅ Consentimento de coleta de dados
- ✅ Exportar todos os dados do usuário
- ✅ Direito ao esquecimento (deletar conta)
- ✅ Política de privacidade
- ✅ Termos de uso

```python
@app.route('/meus-dados/exportar')
@login_required
def exportar_meus_dados():
    dados = {
        'usuario': current_user.to_dict(),
        'agendamentos': [ag.to_dict() for ag in current_user.agendamentos],
        'viagens': [v.to_dict() for v in current_user.viagens]
    }
    
    return send_file(
        BytesIO(json.dumps(dados).encode()),
        mimetype='application/json',
        as_attachment=True,
        attachment_filename='meus_dados.json'
    )
```

**Esforço:** 40 horas

---

### 24. Auditoria Completa

**Já implementado parcialmente**, melhorar com:
- ✅ IP address
- ✅ User agent
- ✅ Geolocalização (se disponível)
- ✅ Logs imutáveis (blockchain?)

**Esforço:** 20 horas

---

### 25. Backup Automático

```bash
# Cron job diário (Linux)
0 2 * * * /usr/bin/pg_dump frota_globo > /backups/frota_$(date +\%Y\%m\%d).sql

# Script Python
import subprocess
from datetime import datetime

def fazer_backup():
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'backup_{timestamp}.sql'
    
    subprocess.run([
        'pg_dump',
        '-U', 'postgres',
        '-d', 'frota_globo',
        '-f', f'/backups/{filename}'
    ])
    
    # Upload para S3
    s3.upload_file(f'/backups/{filename}', 'backups-frota', filename)
```

**Esforço:** 15 horas

---

## 🎨 UX/UI

### 26-30. Melhorias de Interface

**Itens:**
- ✅ Design totalmente responsivo (mobile-first)
- ✅ Acessibilidade WCAG 2.1 nível AA
- ✅ Internacionalização (PT, EN, ES)
- ✅ Onboarding interativo
- ✅ Temas personalizáveis

**Esforço Total:** 100 horas

---

## ⚙️ INFRAESTRUTURA

### 31. Docker & Kubernetes

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

```yaml
# docker-compose.yml
version: '3.8'
services:
  web:
    build: .
    ports:
      - "5000:5000"
    environment:
      - DATABASE_URL=postgresql://postgres:senha@db:5432/frota
    depends_on:
      - db
      - redis
  
  db:
    image: postgres:15
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  redis:
    image: redis:7-alpine
```

**Esforço:** 40 horas

---

### 32. Monitoramento

**Ferramentas:**
- Sentry (erros)
- New Relic (performance)
- Uptime Robot (disponibilidade)

**Esforço:** 25 horas

---

### 33-35. Infraestrutura Avançada

- CDN (CloudFlare)
- Load Balancer (Nginx)
- Ambiente de Staging

**Esforço Total:** 60 horas

---

## 📅 ROADMAP SUGERIDO (12 meses)

### **Q1 - Jan a Mar 2026** (Fundação)
**Objetivo:** Estabilidade e Performance

- ✅ Sprint 1-2: Migração PostgreSQL + Logs
- ✅ Sprint 3-4: Validação + Cache Redis
- ✅ Sprint 5-6: Testes Automatizados (80% cobertura)

**Entregáveis:**
- Sistema 10x mais rápido
- Zero downtime
- 80% de código testado

---

### **Q2 - Abr a Jun 2026** (Expansão)
**Objetivo:** Novas Funcionalidades

- ✅ Sprint 7-8: API RESTful + JWT
- ✅ Sprint 9-10: Notificações (Email + WhatsApp)
- ✅ Sprint 11-12: Dashboard com Gráficos

**Entregáveis:**
- API pública documentada
- Notificações automáticas
- KPIs visuais

---

### **Q3 - Jul a Set 2026** (Gestão)
**Objetivo:** Controle Total da Frota

- ✅ Sprint 13-14: Sistema de Manutenção
- ✅ Sprint 15-16: Controle de Combustível
- ✅ Sprint 17-18: Exportação de Relatórios (PDF/Excel)

**Entregáveis:**
- Histórico completo de manutenções
- Análise de consumo
- Relatórios profissionais

---

### **Q4 - Out a Dez 2026** (Inovação)
**Objetivo:** Tecnologias Avançadas

- ✅ Sprint 19-20: PWA (Progressive Web App)
- ✅ Sprint 21-22: Geolocalização GPS
- ✅ Sprint 23-24: 2FA + Segurança Avançada

**Entregáveis:**
- App instalável no celular
- Rastreamento em tempo real
- Segurança de nível bancário

---

## 💰 ESTIMATIVAS DE ESFORÇO

### Por Categoria

| Categoria | Horas | Desenvolvedores | Prazo |
|-----------|-------|-----------------|-------|
| **Críticas** | 180h | 2 devs | 2 meses |
| **Importantes** | 350h | 2 devs | 4 meses |
| **Desejáveis** | 600h | 3 devs | 6 meses |
| **Segurança** | 90h | 1 dev | 1.5 mês |
| **UX/UI** | 100h | 1 designer | 2 meses |
| **Infraestrutura** | 125h | 1 devops | 2 meses |
| **TOTAL** | **1.445h** | **5-6 pessoas** | **12 meses** |

### Investimento Estimado

**Equipe:**
- 2 Desenvolvedores Backend (R$ 12.000/mês cada)
- 1 Desenvolvedor Frontend (R$ 10.000/mês)
- 1 Designer UX/UI (R$ 8.000/mês)
- 1 DevOps (R$ 14.000/mês)

**Total:** R$ 56.000/mês × 12 meses = **R$ 672.000/ano**

**Infraestrutura:**
- Servidor (AWS/DigitalOcean): R$ 2.000/mês
- Banco de dados managed: R$ 1.500/mês
- CDN + Storage: R$ 500/mês
- Ferramentas (Sentry, New Relic): R$ 1.000/mês

**Total Infraestrutura:** R$ 5.000/mês × 12 = **R$ 60.000/ano**

---

## 🎯 PRIORIZAÇÃO FINAL

### **Fazer AGORA** (ROI Imediato)
1. PostgreSQL (performance crítica)
2. Logs profissionais (debug essencial)
3. Cache Redis (velocidade perceptível)
4. Validação de dados (evitar bugs)
5. Testes automatizados (confiança)

### **Fazer em BREVE** (3-6 meses)
6. API RESTful (integração)
7. Notificações (engajamento)
8. Dashboard gráficos (insights)
9. Manutenção (controle)
10. Combustível (custos)

### **Fazer DEPOIS** (6-12 meses)
11. PWA (conveniência)
12. Geolocalização (rastreamento)
13. App Mobile (mobilidade)
14. BI/Analytics (inteligência)

---

**Próximos Passos:**
1. Aprovar roadmap com stakeholders
2. Definir orçamento e equipe
3. Iniciar Sprint 1: Migração PostgreSQL
4. Setup CI/CD e ambientes

---

**Documento vivo - Atualizar conforme progresso**  
**Versão:** 1.0  
**Última atualização:** Janeiro 2026
