import os
from dotenv import load_dotenv
from sheets_db import SheetsDB

# Load environment variables
load_dotenv()

def create_admin_user():
    print("Connecting to database...")
    db = SheetsDB()
    
    # Check/Create 'Usuários' worksheet
    print("Checking 'Usuários' worksheet...")
    ws = db._get_worksheet('Usuários')
    
    if not ws:
        print("'Usuários' worksheet not found. Creating...")
        try:
            if db.spreadsheet:
                ws = db.spreadsheet.add_worksheet(title="Usuários", rows=1000, cols=10)
                # Add header based on sheets_db.py usage and common sense
                # Columns: Email, Nome, Cargo, Telefone, Ativo, Senha
                ws.append_row(['Email', 'Nome', 'Cargo', 'Telefone', 'Ativo', 'Senha'])
                print("'Usuários' worksheet created.")
            else:
                print("Error: Could not access spreadsheet instance.")
                return
        except Exception as e:
            print(f"Error creating worksheet: {e}")
            return
            
    # Check if admin already exists
    users = ws.get_all_records()
    admin_email = "admin@frota.globo"
    
    for user in users:
        if user.get('Email') == admin_email:
            print(f"User {admin_email} already exists.")
            return

    # Create Admin User
    print(f"Creating user {admin_email}...")
    # Row structure matches sheets_db.py create_user roughly, but explicit here
    # ['Email', 'Nome', 'Cargo', 'Telefone', 'Ativo', 'Senha']
    row = [
        admin_email,
        "Administrador",
        "admin",
        "00000000000",
        "Sim",
        "admin123"
    ]
    
    ws.append_row(row)
    print("Admin user created successfully!")
    print(f"Login: {admin_email}")
    print(f"Password: admin123")

if __name__ == "__main__":
    create_admin_user()
