#!/usr/bin/env python3
"""
Script para testar API v1 do SendCraft end-to-end.
Testa geração de API key via UI e envio de email via API.

Uso: python3 scripts/test_e2e_api.py
"""
import requests
import json
import time
from datetime import datetime

# Configurações do teste
BASE_URL = "http://localhost:5000"
TEST_ACCOUNT_EMAIL = "geral@artnshine.pt"
TEST_RECIPIENT = "mmelo.deb@gmail.com"
API_KEY = None  # Será obtida via UI/Playwright

def print_test_header(test_name: str):
    """Imprimir header de teste."""
    print(f"\n{'='*60}")
    print(f"🧪 {test_name}")
    print(f"{'='*60}")

def print_test_result(test_name: str, success: bool, details: str = ""):
    """Imprimir resultado do teste."""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} {test_name}")
    if details:
        print(f"    {details}")

def test_api_health():
    """Testar endpoint de health da API."""
    print_test_header("API Health Check")
    
    try:
        response = requests.get(f"{BASE_URL}/api/v1/health", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print_test_result("API Health", True, f"Status: {data.get('status', 'OK')}")
                return True
            else:
                print_test_result("API Health", False, "Response success=false")
                return False
        else:
            print_test_result("API Health", False, f"HTTP {response.status_code}")
            return False
    except Exception as e:
        print_test_result("API Health", False, str(e))
        return False

def test_api_without_auth():
    """Testar que endpoints protegidos retornam 401 sem auth."""
    print_test_header("API Authentication Protection")
    
    endpoints = [
        {
            'method': 'POST',
            'url': f"{BASE_URL}/api/v1/send",
            'data': {'to': ['test@test.com'], 'subject': 'test', 'html': 'test'}
        },
        {
            'method': 'GET', 
            'url': f"{BASE_URL}/api/v1/send/MSG-000001/status",
            'data': None
        },
        {
            'method': 'POST',
            'url': f"{BASE_URL}/api/v1/attachments/upload",
            'data': {'filename': 'test.txt', 'content': 'dGVzdA==', 'content_type': 'text/plain'}
        }
    ]
    
    all_protected = True
    
    for endpoint in endpoints:
        try:
            if endpoint['method'] == 'POST':
                response = requests.post(
                    endpoint['url'], 
                    json=endpoint['data'],
                    timeout=10
                )
            else:
                response = requests.get(endpoint['url'], timeout=10)
            
            if response.status_code == 401:
                print_test_result(f"Endpoint Protected: {endpoint['url']}", True, "401 Unauthorized")
            else:
                print_test_result(f"Endpoint Protected: {endpoint['url']}", False, f"HTTP {response.status_code}")
                all_protected = False
                
        except Exception as e:
            print_test_result(f"Endpoint Test: {endpoint['url']}", False, str(e))
            all_protected = False
    
    return all_protected

def test_api_with_auth(api_key: str):
    """Testar API com autenticação válida."""
    print_test_header("API with Valid Authentication")
    
    if not api_key:
        print_test_result("API Authentication", False, "API key not provided")
        return False
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    # Test 1: Send email
    print("\n📧 Testing email send...")
    
    email_payload = {
        'to': [TEST_RECIPIENT],
        'subject': f'SendCraft E2E API Test - {datetime.now().strftime("%Y-%m-%d %H:%M")}',
        'html': '''
        <h2>SendCraft API Test Email</h2>
        <p>Este email foi enviado via API v1 do SendCraft para testar a integração e2e.</p>
        <ul>
            <li><strong>Data:</strong> {timestamp}</li>
            <li><strong>Conta:</strong> {account}</li>
            <li><strong>Endpoint:</strong> POST /api/v1/send</li>
        </ul>
        <p>Se recebeu este email, o sistema está funcional! 🎉</p>
        '''.format(
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            account=TEST_ACCOUNT_EMAIL
        ),
        'text': f'''SendCraft API Test Email\n\nEste email foi enviado via API v1 do SendCraft.\n\nData: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\nConta: {TEST_ACCOUNT_EMAIL}\nEndpoint: POST /api/v1/send\n\nSe recebeu este email, o sistema está funcional!''',
        'from_name': 'SendCraft E2E Test'
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/send",
            json=email_payload,
            headers=headers,
            timeout=30  # SMTP pode demorar
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                message_id = data.get('message_id')
                print_test_result("Email Send", True, f"Message ID: {message_id}")
                
                # Test 2: Check status
                print("\n📊 Testing email status...")
                time.sleep(2)  # Aguardar log ser criado
                
                status_response = requests.get(
                    f"{BASE_URL}/api/v1/send/{message_id}/status",
                    headers=headers,
                    timeout=10
                )
                
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    email_status = status_data.get('status', 'unknown')
                    print_test_result("Email Status", True, f"Status: {email_status}")
                    
                    # Print detailed status
                    print(f"\n📈 Email Status Details:")
                    print(f"    Message ID: {status_data.get('message_id')}")
                    print(f"    Status: {email_status}")
                    print(f"    Created: {status_data.get('created_at')}")
                    print(f"    Recipients: {len(status_data.get('recipients', []))}")
                    
                    return True
                else:
                    print_test_result("Email Status", False, f"HTTP {status_response.status_code}")
                    return False
            else:
                print_test_result("Email Send", False, data.get('message', 'Unknown error'))
                return False
        else:
            print_test_result("Email Send", False, f"HTTP {response.status_code}: {response.text}")
            return False
            
    except requests.Timeout:
        print_test_result("Email Send", False, "Timeout - SMTP pode estar lento (normal)")
        return False
    except Exception as e:
        print_test_result("Email Send", False, str(e))
        return False

def test_api_attachment_upload(api_key: str):
    """Testar upload de anexos."""
    print_test_header("API Attachment Upload")
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    # Criar anexo de teste (base64 encoded)
    import base64
    test_content = "Este é um anexo de teste do SendCraft E2E.\n\nData: " + datetime.now().isoformat()
    test_content_b64 = base64.b64encode(test_content.encode()).decode()
    
    attachment_payload = {
        'filename': 'sendcraft-test.txt',
        'content_type': 'text/plain',
        'content': test_content_b64
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/attachments/upload",
            json=attachment_payload,
            headers=headers,
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                attachment_id = data.get('attachment_id')
                file_size = data.get('size_mb')
                print_test_result("Attachment Upload", True, f"ID: {attachment_id}, Size: {file_size}MB")
                return attachment_id
            else:
                print_test_result("Attachment Upload", False, data.get('message', 'Upload failed'))
                return None
        else:
            print_test_result("Attachment Upload", False, f"HTTP {response.status_code}: {response.text}")
            return None
            
    except Exception as e:
        print_test_result("Attachment Upload", False, str(e))
        return None

def test_web_interface():
    """Testar que interface web carrega."""
    print_test_header("Web Interface Connectivity")
    
    pages = [
        {'url': '/', 'name': 'Homepage'},
        {'url': '/accounts', 'name': 'Accounts List'},
        {'url': '/domains', 'name': 'Domains List'},
        {'url': '/emails/inbox', 'name': 'Email Inbox'},
        {'url': '/logs', 'name': 'Logs'}
    ]
    
    all_working = True
    
    for page in pages:
        try:
            response = requests.get(f"{BASE_URL}{page['url']}", timeout=10)
            
            if response.status_code == 200:
                print_test_result(f"Page: {page['name']}", True, f"HTTP 200")
            else:
                print_test_result(f"Page: {page['name']}", False, f"HTTP {response.status_code}")
                all_working = False
                
        except Exception as e:
            print_test_result(f"Page: {page['name']}", False, str(e))
            all_working = False
    
    return all_working

def validate_account_configuration():
    """Validar configuração da conta de teste."""
    print_test_header("Account Configuration Validation")
    
    try:
        # Verificar conta via API interna (sem auth)
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        from sendcraft import create_app
        from sendcraft.models.account import EmailAccount
        
        app = create_app('development')
        with app.app_context():
            account = EmailAccount.query.filter_by(email_address=TEST_ACCOUNT_EMAIL).first()
            
            if not account:
                print_test_result("Account Exists", False, f"Account {TEST_ACCOUNT_EMAIL} not found")
                return False
            
            print_test_result("Account Exists", True, f"Found: {account.email_address}")
            
            # Verificar configuração SMTP
            config = account.get_smtp_config(app.config.get('SECRET_KEY', ''))
            print_test_result("SMTP Config", True, f"Server: {config.get('server')}, Port: {config.get('port')}")
            
            # Verificar API enabled
            if account.api_enabled and account.api_key_hash:
                print_test_result("API Enabled", True, "Account has API access")
            else:
                print_test_result("API Enabled", False, "Account needs API key generation via UI")
                
            # Verificar limites
            within_limits, limit_msg = account.is_within_limits()
            print_test_result("Account Limits", within_limits, limit_msg)
            
            return True
            
    except Exception as e:
        print_test_result("Account Validation", False, str(e))
        return False

def main():
    """Executar todos os testes."""
    print("🏁 SENDCRAFT E2E API TESTING")
    print(f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Base URL: {BASE_URL}")
    print(f"Test Account: {TEST_ACCOUNT_EMAIL}")
    print(f"Test Recipient: {TEST_RECIPIENT}")
    
    # Fase 1: Testes básicos
    print("\n📊 Fase 1: Basic Connectivity Tests")
    test_results = {
        'web_interface': test_web_interface(),
        'api_health': test_api_health(),
        'api_protection': test_api_without_auth(),
        'account_config': validate_account_configuration()
    }
    
    # Fase 2: Testes com autenticação (requer API key)
    print("\n🔑 Fase 2: Authenticated API Tests")
    print("⚠️  Para testes completos, gere API key via UI:")
    print(f"    1. Aceda a {BASE_URL}/accounts")
    print(f"    2. Edite conta {TEST_ACCOUNT_EMAIL}")
    print(f"    3. Vá para API → Ativar API → Gerar Primeira Chave")
    print(f"    4. Copie a chave gerada")
    print(f"    5. Execute: python3 scripts/test_e2e_api.py --api-key SC_...")
    
    # Verificar se API key foi fornecida como argumento
    import sys
    if len(sys.argv) > 2 and sys.argv[1] == '--api-key':
        api_key = sys.argv[2]
        print(f"\n🔑 Using API Key: {api_key[:15]}...")
        
        test_results.update({
            'api_send_email': test_api_with_auth(api_key),
            'api_attachment_upload': test_api_attachment_upload(api_key) is not None
        })
    else:
        print("\n🔑 API key not provided - skipping authenticated tests")
        test_results.update({
            'api_send_email': None,  # Skipped
            'api_attachment_upload': None  # Skipped
        })
    
    # Resumo final
    print(f"\n{'='*60}")
    print("📈 RESUMO DOS TESTES")
    print(f"{'='*60}")
    
    passed = sum(1 for result in test_results.values() if result is True)
    failed = sum(1 for result in test_results.values() if result is False)
    skipped = sum(1 for result in test_results.values() if result is None)
    total = len(test_results)
    
    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {failed}/{total}")
    print(f"⏭️ Skipped: {skipped}/{total}")
    
    # Detalhe por teste
    for test_name, result in test_results.items():
        if result is True:
            print(f"  ✅ {test_name}")
        elif result is False:
            print(f"  ❌ {test_name}")
        else:
            print(f"  ⏭️ {test_name} (skipped)")
    
    # Conclusion
    if failed == 0:
        if skipped == 0:
            print("\n🎉 TODOS OS TESTES PASSARAM - SENDCRAFT PRODUCTION READY!")
        else:
            print(f"\n✅ TESTES CORE PASSARAM - {skipped} teste(s) requer(em) API key")
        return True
    else:
        print(f"\n❌ {failed} TESTE(S) FALHARAM - Corrigir antes do deploy")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
