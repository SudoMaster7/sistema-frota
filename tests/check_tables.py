from app import db, app
from sqlalchemy import text

app.app_context().push()

# Listar tabelas
result = db.session.execute(text("SELECT tablename FROM pg_tables WHERE schemaname = 'public'"))
tables = [r[0] for r in result]
print(f"Tabelas no banco: {tables}")

if not tables:
    print("\nNenhuma tabela encontrada. Criando...")
    db.create_all()
    result = db.session.execute(text("SELECT tablename FROM pg_tables WHERE schemaname = 'public'"))
    tables = [r[0] for r in result]
    print(f"Tabelas criadas: {tables}")
