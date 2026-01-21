#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para testar permissões da conta de serviço no Google Sheets
"""

import gspread
from oauth2client.service_account import ServiceAccountCredentials
import sys

print("=" * 70)
print("🔍 TESTE DE PERMISSÕES - GOOGLE SHEETS")
print("=" * 70)

try:
    # Configurar credenciais
    scope = ['https://www.googleapis.com/auth/spreadsheets', 
             'https://www.googleapis.com/auth/drive']
    
    print("\n1️⃣ Carregando credentials.json...")
    creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
    print("   ✅ Credenciais carregadas com sucesso!")
    
    print("\n2️⃣ Conectando ao Google Sheets...")
    client = gspread.authorize(creds)
    print("   ✅ Autorização bem-sucedida!")
    
    print("\n3️⃣ Abrindo planilha...")
    spreadsheet = client.open_by_key('1ZjTYIRF_n91JSCI1OytRYaRFiGkZX2JgoqB0eRIwu8I')
    print(f"   ✅ Planilha aberta: '{spreadsheet.title}'")
    
    print("\n4️⃣ Testando LEITURA das worksheets...")
    sheets = {
        'DB_Viagens': None,
        'DB_Motoristas': None,
        'DB_Veiculos': None,
        'DB_Usuarios': None,
        'DB_Agendamentos': None
    }
    
    for sheet_name in sheets.keys():
        try:
            sheet = spreadsheet.worksheet(sheet_name)
            dados = sheet.get_all_records()
            sheets[sheet_name] = True
            print(f"   ✅ {sheet_name}: {len(dados)} registros encontrados")
        except Exception as e:
            sheets[sheet_name] = False
            print(f"   ❌ {sheet_name}: ERRO - {str(e)[:50]}")
    
    print("\n5️⃣ Testando ESCRITA (append) em DB_Agendamentos...")
    try:
        agendamentos_sheet = spreadsheet.worksheet("DB_Agendamentos")
        
        # Tenta adicionar uma linha de teste
        teste_linha = ['TESTE', 'TESTE_ESCRITA', 'TESTE', 'TESTE', 'TESTE', 
                       'TESTE', 'TESTE', 'TESTE', 'TESTE', 'TESTE', 
                       'TESTE', 'TESTE', 'TESTE', 'TESTE', 'TESTE', 'TESTE']
        
        print("   📝 Tentando adicionar linha de teste...")
        agendamentos_sheet.append_row(teste_linha, value_input_option='RAW')
        print("   ✅ ESCRITA FUNCIONOU! Permissão OK!")
        
        # Remove a linha de teste
        print("   🧹 Removendo linha de teste...")
        all_values = agendamentos_sheet.get_all_values()
        last_row = len(all_values)
        if all_values[-1][0] == 'TESTE':
            agendamentos_sheet.delete_rows(last_row)
            print("   ✅ Linha de teste removida!")
        
    except gspread.exceptions.APIError as e:
        print(f"   ❌ ERRO DE PERMISSÃO: {e}")
        print("\n" + "=" * 70)
        print("🚨 SOLUÇÃO NECESSÁRIA:")
        print("=" * 70)
        print("\n1. Abra a planilha no navegador:")
        print("   https://docs.google.com/spreadsheets/d/1ZjTYIRF_n91JSCI1OytRYaRFiGkZX2JgoqB0eRIwu8I")
        print("\n2. Clique em 'Compartilhar' (canto superior direito)")
        print("\n3. Adicione este email com permissão de EDITOR:")
        print("   📧 frotaglobo@gen-lang-client-0063703030.iam.gserviceaccount.com")
        print("\n4. Desmarque 'Notificar pessoas'")
        print("\n5. Clique em 'Compartilhar'")
        print("\n" + "=" * 70)
        sys.exit(1)
    
    except Exception as e:
        print(f"   ❌ ERRO DESCONHECIDO: {e}")
        sys.exit(1)
    
    print("\n" + "=" * 70)
    print("✅ TODOS OS TESTES PASSARAM!")
    print("=" * 70)
    print("\n✨ A aplicação está pronta para funcionar!")
    print("   Execute: python app.py")
    print("\n" + "=" * 70)

except FileNotFoundError:
    print("\n❌ ERRO: Arquivo 'credentials.json' não encontrado!")
    print("   Certifique-se de que o arquivo está na pasta raiz do projeto.")
    sys.exit(1)

except Exception as e:
    print(f"\n❌ ERRO GERAL: {e}")
    print("\n💡 Verifique se:")
    print("   1. O arquivo credentials.json está correto")
    print("   2. A planilha existe e está acessível")
    print("   3. Você tem conexão com a internet")
    sys.exit(1)
