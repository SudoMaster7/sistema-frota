#!/usr/bin/env python3
"""
Script para inicializar o banco de dados e criar usuário admin
"""
import os
import sys
from getpass import getpass

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import app, db
from models import Usuario
from datetime import datetime
from zoneinfo import ZoneInfo

TZ = ZoneInfo('America/Sao_Paulo')


def criar_tabelas():
    """Criar todas as tabelas"""
    print('\n📦 Criando tabelas do banco de dados...')
    with app.app_context():
        db.create_all()
        print('✅ Tabelas criadas com sucesso!')


def criar_usuario_admin():
    """Criar usuário administrador"""
    print('\n👤 Criar Usuário Administrador')
    print('=' * 50)
    
    with app.app_context():
        email = input('📧 Email: ').strip()
        
        # Verificar se já existe
        if Usuario.query.filter_by(email=email).first():
            print(f'⚠️  Usuário {email} já existe!')
            return
        
        nome = input('👤 Nome completo: ').strip()
        
        # Solicitar senha
        while True:
            senha = getpass('🔐 Senha: ')
            senha_confirmacao = getpass('🔐 Confirmar senha: ')
            
            if senha == senha_confirmacao and len(senha) >= 6:
                break
            else:
                print('❌ Senhas não correspondem ou muito curtas (mín. 6 caracteres)')
        
        # Criar usuário
        usuario = Usuario(
            email=email,
            nome=nome,
            role='Admin',
            ativo=True,
            data_criacao=datetime.now(TZ)
        )
        usuario.set_senha(senha)
        
        db.session.add(usuario)
        db.session.commit()
        
        print('\n✅ Usuário administrador criado com sucesso!')
        print(f'   Email: {email}')
        print(f'   Função: Admin')
        print('\n💡 Você pode fazer login em http://localhost:5000')


def main():
    print('\n' + '='*50)
    print('🚀 INICIALIZAÇÃO FROTA GLOBO')
    print('='*50)
    
    # Verificar conexão com banco
    try:
        with app.app_context():
            db.session.execute('SELECT 1')
            print('✅ Conexão com banco de dados OK')
    except Exception as e:
        print(f'❌ Erro ao conectar com banco: {str(e)}')
        print('\n💡 Dicas:')
        print('   1. PostgreSQL está rodando?')
        print('   2. Variável DATABASE_URL está correta em .env?')
        print('   3. Se usar Docker: docker-compose up -d')
        return
    
    # Criar tabelas
    criar_tabelas()
    
    # Criar usuário admin
    criar_usuario_admin()
    
    print('\n' + '='*50)
    print('✅ INICIALIZAÇÃO COMPLETA!')
    print('='*50)
    print('\n🎯 Próximos passos:')
    print('   1. Executar: python migrations/migrate_from_sheets.py')
    print('   2. Ou iniciar a aplicação: python app.py')


if __name__ == '__main__':
    main()
