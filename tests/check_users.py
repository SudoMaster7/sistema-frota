from app import app, db
from models import Usuario
from sqlalchemy import select

app.app_context().push()

# Verificar usuários existentes
stmt = select(Usuario)
usuarios = db.session.execute(stmt).scalars().all()

print("=== USUÁRIOS NO BANCO ===")
if usuarios:
    for u in usuarios:
        print(f"ID: {u.id}")
        print(f"Email: {u.email}")
        print(f"Nome: {u.nome}")
        print(f"Role: {u.role}")
        print(f"Ativo: {u.ativo}")
        print(f"Password Hash: {u.password_hash[:20]}...")
        print("---")
else:
    print("Nenhum usuário encontrado!")
    print("\nCriando usuário admin...")
    
    import uuid
    usuario_id = str(uuid.uuid4())[:8].upper()
    
    usuario = Usuario(
        id=usuario_id,
        email='admin@frota.local',
        nome='Administrador',
        role='Admin',
        ativo=True
    )
    usuario.set_senha('admin123')
    
    db.session.add(usuario)
    db.session.commit()
    
    print(f"✅ Usuário criado com sucesso!")
    print(f"ID: {usuario_id}")
    print(f"Email: admin@frota.local")
    print(f"Senha: admin123")
