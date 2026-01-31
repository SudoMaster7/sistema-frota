from dotenv import load_dotenv
from sheets_db import SheetsDB

load_dotenv()

db = SheetsDB()

# Test get admin user
print("Testando buscar usuário admin...")
user = db.get_user_by_email('admin@frota.globo')

if user:
    print("✅ Usuário encontrado!")
    print(f"Email: {user.get('Email')}")
    print(f"Nome: {user.get('Nome')}")
    print(f"Cargo: {user.get('Cargo')}")
    print(f"Senha: {user.get('Senha')}")
    print(f"Ativo: {user.get('Ativo')}")
else:
    print("❌ Usuário NÃO encontrado!")
    
# List all users
print("\n" + "="*50)
print("Todos os usuários na planilha:")
all_users = db.get_users()
for i, u in enumerate(all_users, 1):
    print(f"{i}. {u.get('Email')} - {u.get('Nome')} - Cargo: {u.get('Cargo')} - Senha: {u.get('Senha')}")
