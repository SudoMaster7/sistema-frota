#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Debug script para verificar dados de motorista"""

from app import app, db
from models import Viagem, Usuario

with app.app_context():
    # Buscar viagens com motorista
    viagens = db.session.query(Viagem).all()
    print(f"Total de viagens: {len(viagens)}\n")
    
    for v in viagens[:3]:
        print(f"Viagem ID: {v.id}")
        print(f"  motorista_id: {v.motorista_id}")
        print(f"  placa: {v.placa}")
        print(f"  data_saida: {v.data_saida}")
        print(f"  Tentando acessar motorista...")
        try:
            if hasattr(v, 'motorista'):
                print(f"  motorista object: {v.motorista}")
                if v.motorista:
                    print(f"  motorista.nome: {v.motorista.nome}")
                    print(f"  motorista.email: {v.motorista.email}")
                    print(f"  motorista.role: {v.motorista.role}")
                else:
                    print("  motorista is None")
            else:
                print("  motorista property não existe")
        except Exception as e:
            print(f"  ERRO ao acessar motorista: {type(e).__name__}: {e}")
        print()
    
    # Buscar usuários
    print("\n=== USUÁRIOS NO BANCO ===")
    usuarios = db.session.query(Usuario).all()
    for u in usuarios:
        print(f"ID: {u.id}, Nome: {u.nome}, Email: {u.email}, Role: {u.role}")
