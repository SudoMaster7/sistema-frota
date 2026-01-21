# 📦 GUIA DE DEPLOYMENT - Sprint 1

**Objetivo:** Colocar Frota Globo em produção com PostgreSQL  
**Cenários:** Windows Local, Linux Server, AWS/Heroku, Docker Kubernetes

---

## 🔴 PRÉ-REQUISITOS DE PRODUÇÃO

- ✅ PostgreSQL 12+ (managed ou auto-hospedado)
- ✅ Redis 6+ (managed ou auto-hospedado)
- ✅ HTTPS/SSL Certificate
- ✅ Servidor Linux (recomendado Ubuntu 22.04)
- ✅ Domínio configurado
- ✅ Backup strategy definida

---

## 🟢 OPÇÃO 1: Servidor Linux (AWS EC2 / DigitalOcean)

### **1. Provisionar Servidor**

```bash
# Ubuntu 22.04 LTS
# Instâncias recomendadas:
# - Development: t3.small (1 CPU, 2GB RAM)
# - Production: t3.medium (2 CPU, 4GB RAM)
```

### **2. Setup Inicial**

```bash
# SSH no servidor
ssh ubuntu@seu-ip-publico.com

# Atualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar dependências
sudo apt install -y python3.10 python3-pip python3-venv
sudo apt install -y postgresql postgresql-contrib
sudo apt install -y redis-server
sudo apt install -y nginx
sudo apt install -y certbot python3-certbot-nginx
```

### **3. Configurar PostgreSQL**

```bash
# Conectar como postgres
sudo -u postgres psql

# Criar usuário
CREATE USER frota WITH PASSWORD 'senha_super_secreta_64_chars_aqui!!!';
ALTER ROLE frota SET client_encoding TO 'utf8';
ALTER ROLE frota SET default_transaction_isolation TO 'read committed';
ALTER ROLE frota SET default_transaction_deferrable TO on;
ALTER ROLE frota SET timezone TO 'America/Sao_Paulo';

# Criar banco
CREATE DATABASE frota_globo OWNER frota;

# Permitir conexão
\c frota_globo
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO frota;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO frota;
\q
```

### **4. Configurar Redis**

```bash
# Editar configuração
sudo nano /etc/redis/redis.conf

# Alterar para produção:
# requirepass senha_super_secreta_aqui
# maxmemory 512mb
# maxmemory-policy allkeys-lru

# Reiniciar
sudo systemctl restart redis-server
sudo systemctl enable redis-server
```

### **5. Clonar Projeto**

```bash
# Criar diretório
sudo mkdir -p /var/www/frota-globo
cd /var/www/frota-globo

# Clonar
git clone https://github.com/seu-usuario/frota-globo.git .

# Criar venv
python3 -m venv venv
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
pip install gunicorn
```

### **6. Configurar Variáveis de Ambiente**

```bash
# Criar .env
nano .env

# Conteúdo:
FLASK_ENV=production
DEBUG=0
SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')

DATABASE_URL=postgresql://frota:senha_aqui@localhost:5432/frota_globo
REDIS_URL=redis://:senha_aqui@localhost:6379/0

MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=seu-email@gmail.com
MAIL_PASSWORD=sua-senha-app

# Salvar (Ctrl+X, Y, Enter)
```

### **7. Gunicorn & Systemd Service**

```bash
# Criar arquivo de serviço
sudo nano /etc/systemd/system/frota-globo.service

# Conteúdo:
[Unit]
Description=Frota Globo Flask App
After=network.target

[Service]
User=www-data
WorkingDirectory=/var/www/frota-globo
Environment="PATH=/var/www/frota-globo/venv/bin"
ExecStart=/var/www/frota-globo/venv/bin/gunicorn \
    --workers 4 \
    --worker-class sync \
    --bind unix:frota-globo.sock \
    app:app
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
KillSignal=SIGQUIT
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target

# Salvar e ativar
sudo systemctl daemon-reload
sudo systemctl enable frota-globo
sudo systemctl start frota-globo
sudo systemctl status frota-globo
```

### **8. Nginx (Reverse Proxy)**

```bash
# Criar config
sudo nano /etc/nginx/sites-available/frota-globo

# Conteúdo:
upstream frota_app {
    server unix:/var/www/frota-globo/frota-globo.sock fail_timeout=0;
}

server {
    listen 80;
    server_name seu-dominio.com www.seu-dominio.com;
    client_max_body_size 20M;

    location / {
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_pass http://frota_app;
        proxy_redirect off;
    }

    location /static/ {
        alias /var/www/frota-globo/static/;
        expires 30d;
    }
}

# Habilitar
sudo ln -s /etc/nginx/sites-available/frota-globo /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### **9. SSL/HTTPS com Let's Encrypt**

```bash
# Gerar certificado
sudo certbot --nginx -d seu-dominio.com -d www.seu-dominio.com

# Auto-renewal
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
```

### **10. Backup Automático**

```bash
# Criar script de backup
sudo nano /usr/local/bin/backup-frota.sh

#!/bin/bash
BACKUP_DIR="/backups/frota"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup PostgreSQL
pg_dump -U frota -h localhost frota_globo | gzip > $BACKUP_DIR/db_$DATE.sql.gz

# Backup arquivos
tar -czf $BACKUP_DIR/app_$DATE.tar.gz /var/www/frota-globo

# Remover backups antigos (>30 dias)
find $BACKUP_DIR -type f -mtime +30 -delete

# Upload para S3 (opcional)
# aws s3 sync $BACKUP_DIR s3://seu-bucket/backups/

# Tornar executável
sudo chmod +x /usr/local/bin/backup-frota.sh

# Agendar cron (2am diário)
sudo crontab -e
# 0 2 * * * /usr/local/bin/backup-frota.sh
```

---

## 🟠 OPÇÃO 2: Docker Kubernetes (Produção Enterprise)

### **1. Deploy no Kubernetes**

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: frota-globo
  labels:
    app: frota-globo
spec:
  replicas: 3  # 3 instâncias para HA
  selector:
    matchLabels:
      app: frota-globo
  template:
    metadata:
      labels:
        app: frota-globo
    spec:
      containers:
      - name: frota-globo
        image: seu-registry/frota-globo:latest
        ports:
        - containerPort: 5000
        env:
        - name: FLASK_ENV
          value: "production"
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: frota-secrets
              key: database-url
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: frota-secrets
              key: redis-url
        livenessProbe:
          httpGet:
            path: /health
            port: 5000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 5000
          initialDelaySeconds: 5
          periodSeconds: 5
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
---
# service.yaml
apiVersion: v1
kind: Service
metadata:
  name: frota-globo-service
spec:
  type: LoadBalancer
  ports:
  - port: 80
    targetPort: 5000
  selector:
    app: frota-globo
```

Aplicar:
```bash
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
```

---

## 🔵 OPÇÃO 3: Heroku (Mais Simples)

### **1. Setup Heroku**

```bash
# Instalar Heroku CLI
# https://devcenter.heroku.com/articles/heroku-cli

# Login
heroku login

# Criar app
heroku create frota-globo

# Adicionar PostgreSQL
heroku addons:create heroku-postgresql:standard-0

# Adicionar Redis
heroku addons:create heroku-redis:premium-0

# Secrets
heroku config:set FLASK_ENV=production
heroku config:set SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')
```

### **2. Procfile**

```
# Procfile
web: gunicorn -w 4 app:app
worker: celery -A celery_app worker
release: python app.py db upgrade
```

### **3. Deploy**

```bash
# Commit mudanças
git add .
git commit -m "Deploy para produção"

# Push para Heroku
git push heroku main

# Abrir app
heroku open
```

---

## 🟡 OPÇÃO 4: DigitalOcean App Platform

```bash
# 1. Conectar GitHub
# 2. Selecionar repositório
# 3. Configurar variáveis de ambiente
# 4. Conectar PostgreSQL managed
# 5. Deploy automático

# .do/app.yaml
name: frota-globo
services:
- name: api
  github:
    repo: seu-usuario/frota-globo
    branch: main
  build_command: pip install -r requirements.txt
  run_command: gunicorn -w 4 app:app
  envs:
  - key: FLASK_ENV
    value: production
  http_port: 5000
```

---

## 🔐 CHECKLIST DE SEGURANÇA

- [ ] `SECRET_KEY` alterada
- [ ] `DEBUG = False` em produção
- [ ] HTTPS/SSL configurado
- [ ] PostgreSQL com senha forte
- [ ] Redis com requirepass
- [ ] Firewall habilitado (porta 22, 80, 443 apenas)
- [ ] SQL Injection prevention (ORM protege)
- [ ] CSRF protection ativado
- [ ] Rate limiting configurado
- [ ] Logs auditados
- [ ] Backups automatizados
- [ ] Monitoring ativado

---

## 📊 MONITORAMENTO PRODUÇÃO

```bash
# Alertas com Sentry
pip install sentry-sdk
```

```python
# app.py
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

sentry_sdk.init(
    dsn="https://seu-dsn@sentry.io/seu-project",
    integrations=[FlaskIntegration()]
)
```

```bash
# New Relic
pip install newrelic
newrelic-admin run-program gunicorn app:app
```

---

## 🚨 Troubleshooting Produção

### **App não responde**
```bash
# Verificar status
systemctl status frota-globo

# Ver logs
journalctl -u frota-globo -f

# Reiniciar
systemctl restart frota-globo
```

### **Database connection failed**
```bash
# Testar conexão
psql -U frota -h localhost -d frota_globo -c "SELECT 1;"

# Verificar DATABASE_URL
echo $DATABASE_URL
```

### **Redis não responde**
```bash
# Teste
redis-cli -a sua-senha ping

# Restart
systemctl restart redis-server
```

---

## 📈 Performance Produção

**Recomendações:**
- Gunicorn: 4-8 workers (2-4x núcleos CPU)
- PostgreSQL: max_connections = 200
- Redis: maxmemory = 25% RAM
- Nginx: worker_processes = auto
- Cache: TTL = 300s para queries

---

**Status:** ✅ Pronto para Produção  
**Próximo:** Escolher opção de deployment conforme infraestrutura
