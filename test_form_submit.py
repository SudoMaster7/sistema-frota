import requests

# Test form submission
url = "http://127.0.0.1:5000/registrar-saida"

# First, we need to get a session with login
session = requests.Session()

# Login
login_data = {
    'email': 'admin@frota.globo',
    'senha': 'admin123'
}
login_response = session.post('http://127.0.0.1:5000/login', data=login_data)
print(f"Login status: {login_response.status_code}")

# Now try to submit the form
form_data = {
    'agendamento_id': '1',
    'motorista_id': 'motorista1@frota.globo',
    'km_inicial': '50000',
    'observacoes': 'Teste automático'
}

print("\n" + "="*60)
print("Submitting form data:")
for key, value in form_data.items():
    print(f"  {key} = '{value}'")
print("="*60)

response = session.post(url, data=form_data, allow_redirects=False)
print(f"\nResponse status: {response.status_code}")
print(f"Redirect location: {response.headers.get('Location', 'None')}")

if 'Set-Cookie' in response.headers:
    # Flash message might be in cookies
    print(f"Cookies: {response.headers['Set-Cookie'][:200]}")
