# 🚀 CHECKLIST RÁPIDO - SPRINT 1 IMPLEMENTAÇÃO

## Status: EM PROGRESSO

---

## ✅ FASE 1: PREPARAÇÃO (5-10 min)

- [ ] **1.1** Abrir PowerShell/Terminal no diretório do projeto
  ```bash
  cd "c:\Users\leosc\OneDrive\Área de Trabalho\Frota Globo\sistema-frota-fundec"
  ```

- [ ] **1.2** Ativar virtual environment
  ```bash
  .\venv\Scripts\activate.bat
  ```

- [ ] **1.3** Verificar Python
  ```bash
  python --version
  ```
  ✅ Esperado: Python 3.10+

---

## 📦 FASE 2: DEPENDÊNCIAS (5 min)

- [ ] **2.1** Instalar requirements
  ```bash
  pip install -r requirements.txt
  ```
  ✅ Esperado: 40+ pacotes instalados

- [ ] **2.2** Verificar instalação
  ```bash
  pip list | findstr "Flask SQLAlchemy psycopg2"
  ```

---

## 🐘 FASE 3: BANCO DE DADOS (10-15 min)

### Opção A: Docker (RECOMENDADO)
- [ ] **3A.1** Verificar Docker instalado
  ```bash
  docker --version
  docker-compose --version
  ```

- [ ] **3A.2** Iniciar containers
  ```bash
  docker-compose up -d
  ```
  ✅ Esperado: 4 containers iniciados (postgres, redis, pgadmin, redis-commander)

- [ ] **3A.3** Verificar status
  ```bash
  docker-compose ps
  ```

### Opção B: PostgreSQL Local
- [ ] **3B.1** PostgreSQL está rodando?
  - Windows: Verificar em Services (postgresql-x64-15)
  - Linux/Mac: `sudo systemctl status postgresql`

- [ ] **3B.2** Criar banco de dados
  ```bash
  psql -U postgres -c "CREATE DATABASE frota_globo;"
  ```

---

## ⚙️ FASE 4: CONFIGURAÇÃO (5 min)

- [ ] **4.1** .env já foi criado? ✅ (automático)
  ```bash
  type .env
  ```

- [ ] **4.2** Atualizar .env se necessário
  - Editar `.env`
  - Verificar `DATABASE_URL` (se Docker: já está correto)
  - Se PostgreSQL local: ajustar password e port

---

## 🗄️ FASE 5: INICIALIZAR BANCO (5-10 min)

- [ ] **5.1** Criar tabelas e usuário admin
  ```bash
  python init_db.py
  ```
  ✅ Seguir prompts (email, nome, senha)

- [ ] **5.2** Verificar tabelas criadas
  ```bash
  # No PostgreSQL:
  psql -U postgres -d frota_globo -c "\dt"
  ```

---

## 📊 FASE 6: MIGRAÇÃO DE DADOS (10-15 min) [OPCIONAL]

- [ ] **6.1** Se tem dados em Google Sheets:
  ```bash
  python migrations/migrate_from_sheets.py
  ```

- [ ] **6.2** Verificar migração
  ```bash
  # Deve mostrar: "✅ TOTAL MIGRADO: XXX registros"
  ```

- [ ] **6.3** Se erro:
  ```bash
  # Verificar GOOGLE_SHEETS_ID em .env
  # Verificar credentials.json compartilhado
  # Ver SOLUCAO_ERRO_403.md
  ```

---

## 🎬 FASE 7: INICIAR APLICAÇÃO (2 min)

- [ ] **7.1** Executar aplicação
  ```bash
  python app.py
  ```
  ✅ Esperado: "Running on http://localhost:5000"

- [ ] **7.2** Abrir no navegador
  - URL: `http://localhost:5000`
  - Login: (email e senha que criou em 5.1)

---

## ✔️ FASE 8: VALIDAÇÃO (5-10 min)

- [ ] **8.1** Login funciona?
  - [ ] Página de login carrega
  - [ ] Consegue fazer login
  - [ ] Dashboard aparece

- [ ] **8.2** Verificar dados
  - [ ] Clique em "Agendamentos"
  - [ ] Se migrou dados: aparecem na lista
  - [ ] Se vazio: é normal (sem dados migrados)

- [ ] **8.3** Testar funcionalidades básicas
  - [ ] Agendar veículo (agendar_veiculo)
  - [ ] Visualizar agendamentos
  - [ ] Logout funciona

---

## 🔧 TROUBLESHOOTING RÁPIDO

### Erro: "ModuleNotFoundError"
```bash
# Solução: Reinstalar requirements
pip install -r requirements.txt --force-reinstall
```

### Erro: "connection refused" (banco)
```bash
# Se Docker:
docker-compose ps  # Verificar se rodando
docker-compose logs postgres  # Ver logs

# Se PostgreSQL local:
# Verificar se está rodando em Services
# Ou: sudo systemctl start postgresql
```

### Erro: "GOOGLE_SHEETS_ID not configured"
```bash
# Solução: Editar .env
# Adicionar sua ID da planilha
GOOGLE_SHEETS_ID=seu-id-aqui
```

### Erro: "Permission denied" (migrate_from_sheets)
```bash
# Solução: Compartilhar Google Sheets com email em credentials.json
# Ver: SOLUCAO_ERRO_403.md
```

---

## 📚 RECURSOS

- 📖 **Detalhes Técnicos**: [SPRINT1_MIGRACAO_POSTGRESQL.md](SPRINT1_MIGRACAO_POSTGRESQL.md)
- 🎯 **Início Rápido Completo**: [INICIO_RAPIDO_SPRINT1.md](INICIO_RAPIDO_SPRINT1.md)
- 🚀 **Deploy em Produção**: [DEPLOYMENT_PRODUCAO.md](DEPLOYMENT_PRODUCAO.md)
- 📊 **Status Projeto**: [STATUS_PROJETO.md](STATUS_PROJETO.md)

---

## ⏱️ TEMPO TOTAL ESPERADO: 45-60 minutos

| Fase | Tempo | Status |
|------|-------|--------|
| 1. Preparação | 5-10 min | ⏳ |
| 2. Dependências | 5 min | ⏳ |
| 3. Banco de Dados | 10-15 min | ⏳ |
| 4. Configuração | 5 min | ⏳ |
| 5. Inicializar | 5-10 min | ⏳ |
| 6. Migração | 10-15 min | ⏳ (opcional) |
| 7. Iniciar App | 2 min | ⏳ |
| 8. Validação | 5-10 min | ⏳ |
| **TOTAL** | **45-60 min** | **⏳** |

---

## ✨ SE TER SUCESSO EM TUDO:

```
✅ Virtual environment ativo
✅ Todas as dependências instaladas
✅ PostgreSQL/Redis rodando
✅ Banco de dados criado
✅ Usuário admin criado
✅ Dados migrados (opcional)
✅ Aplicação rodando em localhost:5000
✅ Login e dashboard funcionando
```

**🎉 PARABÉNS! Sprint 1 implementada com sucesso!**

---

## 🚀 PRÓXIMAS ETAPAS:

1. Testar todas as rotas
2. Validar integridade dos dados
3. Documentar customizações
4. Começar Sprint 2 (Logs, Cache, Validações)

---

**Data de início**: [TODAY]  
**Status**: EM PROGRESSO  
**Responsável**: Você! 💪
