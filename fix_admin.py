"""
Fix existing admin user to have admin role
"""

from supabase_db import SupabaseDB

db = SupabaseDB()

print("Updating existing admin user...")

# Update the existing admin user
response = db.client.table('usuarios').update({
    'role': 'admin'
}).eq('email', 'admin@frota.globo').execute()

if response.data:
    print(f"✓ Admin role updated!")
    print(f"\nLogin credentials:")
    print(f"  Email: admin@frota.globo")
    print(f"  Senha: admin123")
    print(f"  Role: admin")
else:
    print(f"✗ Failed to update")

print("\nAll users:")
users = db.get_users()
for user in users:
    print(f"  - {user.get('nome')} ({user.get('email')}) - Role: {user.get('role')}")
