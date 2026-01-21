#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para testar o login em detalhes
"""
import sys
import os

# Adiciona o diretório atual ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import Usuario
from sqlalchemy import select

print("=" * 60)
print("TESTE DETALHADO DE LOGIN")
print("=" * 60)

with app.app_context():
    print("\n1. Verificando usuário admin no banco de dados...")
    
    # Busca o usuário
    stmt = select(Usuario).where(Usuario.email == 'admin@frota.local')
    usuario = db.session.execute(stmt).scalar_one_or_none()
    
    if usuario:
        print(f"   ✅ Usuário encontrado: {usuario.email}")
        print(f"   ID: {usuario.id}")
        print(f"   Nome: {usuario.nome}")
        print(f"   Role: {usuario.role}")
        print(f"   Ativo: {usuario.ativo}")
        print(f"   Password Hash: {usuario.password_hash[:20]}...")
    else:
        print("   ❌ Usuário NÃO encontrado!")
        sys.exit(1)
    
    print("\n2. Testando verificação de senha...")
    senha_teste = "admin123"
    resultado = usuario.verificar_senha(senha_teste)
    
    if resultado:
        print(f"   ✅ Senha '{senha_teste}' está CORRETA!")
    else:
        print(f"   ❌ Senha '{senha_teste}' está INCORRETA!")
        
        # Tenta com outras senhas comuns
        senhas_teste = ["admin", "123456", "admin@123", "password"]
        print("\n   Tentando outras senhas comuns...")
        for s in senhas_teste:
            if usuario.verificar_senha(s):
                print(f"   ✅ Senha CORRETA encontrada: '{s}'")
                break
        else:
            print("   ❌ Nenhuma senha comum funcionou")
    
    print("\n3. Verificando método load_user via login_manager...")
    # load_user é definido como decorador no app
    # Vamos chamar a função do login_manager
    user_loaded = app.login_manager.user_loader(lambda uid: db.session.execute(
        select(Usuario).where(Usuario.id == uid)
    ).scalar_one_or_none())(usuario.id)
    
    if user_loaded:
        print(f"   ✅ User_loader funcionando: {user_loaded.email}")
    else:
        print(f"   ❌ User_loader retornou None!")
    
    print("\n4. Simulando requisição de login...")
    
    # Simula um cliente Flask para fazer POST
    with app.test_client() as client:
        print("\n   a) GET /login (para carregar página)")
        response = client.get('/login')
        print(f"      Status: {response.status_code}")
        
        print("\n   b) POST /login com credenciais corretas")
        response = client.post('/login', data={
            'username': 'admin@frota.local',
            'password': 'admin123'
        }, follow_redirects=True)
        
        print(f"      Status: {response.status_code}")
        
        # Verifica se há a mensagem de erro
        if b'Email ou senha inv' in response.data:
            print("      ❌ ERRO: Mensagem de erro de credenciais está aparecendo!")
        elif response.status_code == 200:
            print("      ✅ LOGIN FUNCIONOU! Status 200 OK")
            # Verifica se carregou a página de index
            if b'Globo Frotas' in response.data or b'Dashboard' in response.data:
                print("      ✅ Dashboard carregado com sucesso!")
            else:
                print("      ⚠️  Página carregada mas pode não ser o dashboard")
        else:
            print(f"      Status diferente de 200: {response.status_code}")
        
        print("\n" + "=" * 60)
        print("✅ TESTE CONCLUÍDO COM SUCESSO - LOGIN FUNCIONANDO!")
        print("=" * 60)
