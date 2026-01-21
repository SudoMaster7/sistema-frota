"""
Script de Inicialização - Usando SQLite para desenvolvimento rápido
"""
import os
import sys
from datetime import datetime
from zoneinfo import ZoneInfo

# Adicionar projeto ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ['FLASK_ENV'] = 'development'

from app import app, db
from models import Usuario

TZ = ZoneInfo('America/Sao_Paulo')

def criar_tabelas():
    """Criar todas as tabelas"""
    print('\n📦 Criando tabelas do banco de dados...')
    with app.app_context():
        try:
            db.create_all()
            print('✅ Tabelas criadas com sucesso!')
            return True
        except Exception as e:
            print(f'❌ Erro ao criar tabelas: {str(e)}')
            return False

def criar_usuario_admin():
    """Criar usuário administrador padrão"""
    print('\n👤 Criando usuário admin padrão...')
    
    with app.app_context():
        # Verificar se já existe
        from sqlalchemy import select
        stmt = select(Usuario).where(Usuario.email == 'admin@frota.local')
        admin = db.session.execute(stmt).scalar_one_or_none()
        if admin:
            print('⚠️  Usuário admin já existe!')
            return
        
        # Criar admin - gerar ID único
        import uuid
        usuario_id = str(uuid.uuid4())[:8].upper()
        
        usuario = Usuario(
            id=usuario_id,
            email='admin@frota.local',
            nome='Administrador',
            role='Admin',
            ativo=True,
            data_criacao=datetime.now(TZ)
        )
        usuario.set_senha('admin123')  # Senha padrão para demo
        
        db.session.add(usuario)
        db.session.commit()
        
        print('✅ Usuário admin criado!')
        print('   📧 Email: admin@frota.local')
        print('   🔐 Senha: admin123')


def main():
    print('\n' + '='*50)
    print('🚀 INICIALIZAÇÃO FROTA GLOBO - SPRINT 1')
    print('='*50)
    
    # Criar tabelas
    if not criar_tabelas():
        return
    
    # Criar usuário admin
    criar_usuario_admin()
    
    print('\n' + '='*50)
    print('✅ INICIALIZAÇÃO COMPLETA!')
    print('='*50)
    print('\n🎯 Próximas ações:')
    print('   1. Iniciar a aplicação: python app.py')
    print('   2. Acessar: http://localhost:5000')
    print('   3. Login com:')
    print('      📧 admin@frota.local')
    print('      🔐 admin123')


if __name__ == '__main__':
    main()
