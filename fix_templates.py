# Script to replace all .strftime() calls with |format_date filter in templates
import re
import os

templates_dir = r"c:\Users\leosc\OneDrive\Área de Trabalho\Frota Globo\sistema-frota-fundec\templates"

# Pattern to match: variable.strftime('format') if variable else 'default'
# Replace with: variable|format_date if variable else 'default'

files_to_fix = [
    'agendamentos.html',
    'cronograma.html',
    'historico.html',
    'index.html',
    'editar_perfil.html'
]

for filename in files_to_fix:
    filepath = os.path.join(templates_dir, filename)
    if not os.path.exists(filepath):
        print(f"❌ File not found: {filename}")
        continue
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Replace .strftime('%d/%m/%Y %H:%M:%S') with |format_date('%d/%m/%Y %H:%M:%S')
    # Replace .strftime('%d/%m/%Y %H:%M') with |format_date('%d/%m/%Y %H:%M')
    # Replace .strftime('%d/%m/%Y') with |format_date
    # Replace .strftime('%H:%M') with direct output (it's just a string already)
    # Replace .strftime('%d/%m %H:%M') with |format_date('%d/%m %H:%M')
    
    # Pattern 1: variable.strftime('anything') if variable else 'default'
    content = re.sub(
        r"(\w+(?:\.\w+)*)\.strftime\('([^']+)'\)\s+if\s+\1\s+else\s+'([^']+)'",
        r"\1|format_date('\2') if \1 else '\3'",
        content
    )
    
    # Pattern 2: variable.strftime('anything')
    content = re.sub(
        r"(\w+(?:\.\w+)*)\.strftime\('([^']+)'\)",
        r"\1|format_date('\2')",
        content
    )
    
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Fixed: {filename}")
    else:
        print(f"ℹ️  No changes: {filename}")

print("\n✅ All templates updated!")
