from app import app, db
from models import Usuario
from sqlalchemy import select

app.app_context().push()

print("=== DEBUG LOGIN ===\n")

# 1. Procurar usuário
email_teste = 'admin@frota.local'
print(f"1️⃣ Buscando usuário com email: {email_teste}")

stmt = select(Usuario).where(Usuario.email == email_teste)
usuario = db.session.execute(stmt).scalar_one_or_none()

if not usuario:
    print("❌ Usuário não encontrado!")
    print("\nListando todos os usuários:")
    stmt_all = select(Usuario)
    todos = db.session.execute(stmt_all).scalars().all()
    for u in todos:
        print(f"  - {u.email} (ID: {u.id})")
else:
    print(f"✅ Usuário encontrado: {usuario.email}")
    print(f"   ID: {usuario.id}")
    print(f"   Nome: {usuario.nome}")
    print(f"   Ativo: {usuario.ativo}")
    print(f"   Role: {usuario.role}")
    
    # 2. Testar senha
    print(f"\n2️⃣ Testando verificação de senha")
    senha_teste = 'admin123'
    resultado = usuario.verificar_senha(senha_teste)
    print(f"   Senha '{senha_teste}': {resultado}")
    
    if not resultado:
        print("   ❌ Senha não combina!")
        print("   Resetando senha...")
        usuario.set_senha('admin123')
        db.session.commit()
        
        resultado2 = usuario.verificar_senha('admin123')
        print(f"   Após reset: {resultado2}")
    
    # 3. Testar load_user
    print(f"\n3️⃣ Testando load_user()")
    try:
        usuario_loaded = app.blueprints.get('__main__')  # Tentar carregar
        # Reimplementar localmente
        from sqlalchemy import select
        stmt = select(Usuario).where(Usuario.id == usuario.id)
        loaded = db.session.execute(stmt).scalar_one_or_none()
        
        if loaded:
            print(f"   ✅ load_user funcionou: {loaded.email}")
        else:
            print(f"   ❌ load_user retornou None")
    except Exception as e:
        print(f"   ❌ Erro em load_user: {e}")
    
    # 4. Teste completo de login
    print(f"\n4️⃣ Simulando fluxo de login completo")
    print(f"   Email: {email_teste}")
    print(f"   Senha: {senha_teste}")
    
    # Procurar
    stmt_login = select(Usuario).where(Usuario.email == email_teste)
    usuario_login = db.session.execute(stmt_login).scalar_one_or_none()
    
    if usuario_login:
        print(f"   ✅ Usuário encontrado")
        
        # Verificar senha
        if usuario_login.verificar_senha(senha_teste):
            print(f"   ✅ Senha correta")
            
            # Verificar ativo
            if usuario_login.ativo:
                print(f"   ✅ Usuário ativo")
                print(f"\n   🎉 LOGIN DEVERIA FUNCIONAR!")
            else:
                print(f"   ❌ Usuário não está ativo")
        else:
            print(f"   ❌ Senha incorreta")
    else:
        print(f"   ❌ Usuário não encontrado")

print("\n=== FIM DEBUG ===")
