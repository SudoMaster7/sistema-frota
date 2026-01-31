"""
Debug login - check what's happening
"""

from supabase_db import SupabaseDB

db = SupabaseDB()

email = 'admin@frota.globo'
senha = 'admin123'

print(f"Trying to login with: {email}")

# Get user
user_data = db.get_user_by_email(email)

if user_data:
    print(f"\nUser found!")
    print(f"  Data type: {type(user_data)}")
    print(f"  Keys: {user_data.keys() if isinstance(user_data, dict) else 'Not a dict'}")
    print(f"  Email: {user_data.get('email')}")
    print(f"  Senha from DB: '{user_data.get('senha')}'")
    print(f"  Senha trying: '{senha}'")
    print(f"  Match: {user_data.get('senha') == senha}")
    print(f"  Role: {user_data.get('role')}")
else:
    print(f"User NOT found!")

print("\n\nAll users:")
users = db.get_users()
for u in users:
    print(f"  {u.get('email')} - senha: '{u.get('senha')}' - role: {u.get('role')}")
