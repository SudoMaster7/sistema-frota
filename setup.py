#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
🚀 Script de Setup - Sprint 1: PostgreSQL Migration

Execução: python setup.py
"""

import os
import sys
import subprocess
import json
from pathlib import Path

class Setup:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.venv_path = self.project_root / 'venv'
        
    def print_banner(self, text):
        """Imprime banner colorido"""
        print("\n" + "="*70)
        print(f"  {text}")
        print("="*70 + "\n")
    
    def step(self, number, title):
        """Imprime número do passo"""
        print(f"\n{number}️⃣  {title}")
        print("-" * 70)
    
    def run_command(self, cmd, description=""):
        """Executa comando e retorna sucesso/falha"""
        if description:
            print(f"   📝 {description}...")
        try:
            subprocess.run(cmd, shell=True, check=True, capture_output=True)
            print(f"   ✅ Sucesso!")
            return True
        except subprocess.CalledProcessError as e:
            print(f"   ❌ Erro: {e.stderr.decode()}")
            return False
    
    def setup(self):
        """Executa setup completo"""
        
        self.print_banner("🚀 SETUP SPRINT 1: MIGRAÇÃO POSTGRESQL")
        
        # Passo 1: Verificar Python
        self.step(1, "Verificar Python")
        python_version = subprocess.run(
            ["python", "--version"],
            capture_output=True,
            text=True
        ).stdout.strip()
        print(f"   ✅ {python_version} detectado")
        
        # Passo 2: Criar/Ativar venv
        self.step(2, "Configurar Virtual Environment")
        
        if not self.venv_path.exists():
            print(f"   📝 Criando venv em {self.venv_path}...")
            subprocess.run(
                ["python", "-m", "venv", str(self.venv_path)],
                check=True
            )
            print(f"   ✅ venv criado!")
        else:
            print(f"   ℹ️  venv já existe em {self.venv_path}")
        
        # Passo 3: Instalar dependências
        self.step(3, "Instalar Dependências")
        
        pip_path = self.venv_path / ('Scripts' if sys.platform == 'win32' else 'bin') / 'pip'
        
        print("   📝 Atualizando pip...")
        subprocess.run(
            [str(pip_path), "install", "--upgrade", "pip"],
            check=True,
            capture_output=True
        )
        
        print("   📝 Instalando dependências...")
        subprocess.run(
            [str(pip_path), "install", "-r", "requirements.txt"],
            check=True,
            capture_output=True
        )
        print("   ✅ Dependências instaladas!")
        
        # Passo 4: Verificar Docker
        self.step(4, "Verificar Docker")
        
        try:
            subprocess.run(
                ["docker", "--version"],
                capture_output=True,
                check=True
            )
            docker_version = subprocess.run(
                ["docker", "--version"],
                capture_output=True,
                text=True
            ).stdout.strip()
            print(f"   ✅ {docker_version} detectado")
            
            # Iniciar Docker Compose
            print("\n   📝 Iniciando Docker Compose...")
            subprocess.run(
                ["docker-compose", "up", "-d"],
                cwd=str(self.project_root),
                capture_output=True
            )
            print("   ✅ Containers iniciados!")
            print("\n   🌐 Acessar interfaces:")
            print("      - pgAdmin: http://localhost:5050")
            print("      - Redis Commander: http://localhost:8081")
            
        except FileNotFoundError:
            print("   ⚠️  Docker não está instalado")
            print("      Instale do: https://www.docker.com/products/docker-desktop")
            return False
        
        # Passo 5: Criar arquivo .env
        self.step(5, "Criar arquivo .env")
        
        env_file = self.project_root / '.env'
        if not env_file.exists():
            env_content = """# Desenvolvimento
FLASK_ENV=development
FLASK_DEBUG=1
SECRET_KEY=sua-chave-secreta-aqui

# Database PostgreSQL
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/frota_globo

# Cache Redis
REDIS_URL=redis://:redis_password@localhost:6379/0

# Email (opcional)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=seu-email@gmail.com
MAIL_PASSWORD=sua-senha-app

# Google Sheets (para migração)
GOOGLE_SHEETS_ID=1ZjTYIRF_n91JSCI1OytRYaRFiGkZX2JgoqB0eRIwu8I
"""
            with open(env_file, 'w') as f:
                f.write(env_content)
            print("   ✅ Arquivo .env criado!")
            print("      Edite com suas credenciais no arquivo .env")
        else:
            print("   ℹ️  Arquivo .env já existe")
        
        # Passo 6: Inicializar banco de dados
        self.step(6, "Inicializar Banco de Dados")
        
        print("   📝 Aguardando PostgreSQL estar pronto...")
        import time
        time.sleep(5)
        
        print("   📝 Criando tabelas...")
        try:
            from models import db
            from config import config
            from app import app
            
            with app.app_context():
                db.create_all()
            print("   ✅ Tabelas criadas!")
        except Exception as e:
            print(f"   ⚠️  Erro ao criar tabelas: {e}")
        
        # Passo 7: Resumo final
        self.print_banner("✅ SETUP CONCLUÍDO COM SUCESSO!")
        
        print("📋 Próximos passos:\n")
        print("1. Edite o arquivo .env com suas credenciais")
        print("2. Execute a migração de dados do Google Sheets:")
        print("   python migrations/migrate_from_sheets.py")
        print("3. Inicie a aplicação:")
        print("   python app.py")
        print("\n🌐 Acessar aplicação em: http://localhost:5000")
        print("\n📚 Documentação: SPRINT1_MIGRACAO_POSTGRESQL.md")
        
        return True

if __name__ == '__main__':
    setup = Setup()
    
    try:
        success = setup.setup()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Erro durante setup: {e}")
        sys.exit(1)
