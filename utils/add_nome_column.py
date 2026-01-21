from app import db, app
from sqlalchemy import text

app.app_context().push()

# Adicionar coluna nome se não existir
try:
    db.session.execute(text("ALTER TABLE usuarios ADD COLUMN nome VARCHAR(100)"))
    db.session.commit()
    print("✅ Coluna 'nome' adicionada à tabela usuarios")
except Exception as e:
    print(f"ℹ️  Coluna 'nome' já existe ou erro: {e}")
    db.session.rollback()
