from dotenv import load_dotenv
from sheets_db import SheetsDB
import sys
sys.path.insert(0, '.')

load_dotenv()

# Import the SheetsUser class
from app_sheets import SheetsUser

db = SheetsDB()

# Test login
print("Testando login...")
user_data = db.get_user_by_email('admin@frota.globo')

if user_data:
    print(f"✅ Usuário encontrado: {user_data}")
    user = SheetsUser(user_data)
    print(f"\nUser object created:")
    print(f"  - ID: {user.id}")
    print(f"  - Email: {user.email}")
    print(f"  - Nome: {user.nome}")
    print(f"  - Role: {user.role}")
    print(f"  - Ativo: {user.ativo}")
    print(f"  - Password: {user.password}")
    
    # Test password verification
    print(f"\nTestando senha 'admin123'...")
    if user.verificar_senha('admin123'):
        print("✅ Senha CORRETA!")
    else:
        print("❌ Senha INCORRETA!")
    
    print(f"\nTestando ativo...")
    if user.ativo:
        print("✅ Usuário ATIVO!")
    else:
        print("❌ Usuário INATIVO!")
else:
    print("❌ Usuário não encontrado!")
