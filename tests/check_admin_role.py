#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para verificar o role do usuário admin
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import Usuario
from sqlalchemy import select

with app.app_context():
    print("=" * 60)
    print("VERIFICANDO ROLE DO USUÁRIO ADMIN")
    print("=" * 60)
    
    # Busca o usuário admin
    stmt = select(Usuario).where(Usuario.email == 'admin@frota.local')
    usuario = db.session.execute(stmt).scalar_one_or_none()
    
    if usuario:
        print(f"\n✅ Usuário encontrado: {usuario.email}")
        print(f"   ID: {usuario.id}")
        print(f"   Nome: {usuario.nome}")
        print(f"   Role: '{usuario.role}'")
        print(f"   Role type: {type(usuario.role)}")
        print(f"   Ativo: {usuario.ativo}")
        print(f"   is_authenticated: {usuario.is_authenticated}")
        
        # Verifica se o role é 'admin'
        if usuario.role == 'admin' or usuario.role == 'Admin':
            print(f"\n✅ ROLE CORRETO: {usuario.role}")
        else:
            print(f"\n❌ ROLE INCORRETO: '{usuario.role}' (esperado 'admin' ou 'Admin')")
            print(f"   Atualizando para 'admin'...")
            usuario.role = 'admin'
            db.session.commit()
            print(f"   ✅ Role atualizado!")
    else:
        print("❌ Usuário NÃO encontrado!")
    
    print("\n" + "=" * 60)
