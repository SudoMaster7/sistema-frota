from app import app, db
from models import Usuario
from sqlalchemy import select

app.app_context().push()

# Verificar o usuário
stmt = select(Usuario).where(Usuario.email == 'admin@frota.local')
usuario = db.session.execute(stmt).scalar_one_or_none()

if usuario:
    print(f"Usuário encontrado: {usuario.email}")
    print(f"Password Hash: {usuario.password_hash}")
    
    # Testar verificação de senha
    senha_teste = 'admin123'
    result = usuario.verificar_senha(senha_teste)
    
    print(f"\nTestando senha: '{senha_teste}'")
    print(f"Resultado: {result}")
    
    if result:
        print("✅ SENHA CORRETA!")
    else:
        print("❌ SENHA INCORRETA")
        
        # Tentar resetar a senha
        print("\nResetando senha...")
        usuario.set_senha('admin123')
        db.session.commit()
        
        # Testar novamente
        result = usuario.verificar_senha('admin123')
        print(f"Teste após reset: {result}")
        
        if result:
            print("✅ SENHA AGORA FUNCIONA!")
else:
    print("Usuário não encontrado!")
