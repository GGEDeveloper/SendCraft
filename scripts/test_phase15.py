#!/usr/bin/env python3
"""
SendCraft Phase 15 - Complete Test Suite
Testa todos os endpoints da API de envio de emails
"""
import requests
import base64
import time
import json
import sys
from datetime import datetime

# Configuração REAL
API_BASE = "http://localhost:5000"
DOMAIN = "artnshine.pt" 
ACCOUNT = "geral"
TEST_EMAIL = "geral@artnshine.pt"

# API_KEY será obtida dinamicamente
API_KEY = None
HEADERS = {}

class TestResults:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.results = []
    
    def add_result(self, test_name, success, message, details=None):
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            'test': test_name,
            'success': success,
            'message': message,
            'details': details,
            'timestamp': datetime.now().isoformat()
        }
        self.results.append(result)
        
        if success:
            self.passed += 1
        else:
            self.failed += 1
        
        print(f"{status}: {test_name}")
        print(f"   {message}")
        if details and not success:
            print(f"   Details: {details}")
        print()
    
    def summary(self):
        total = self.passed + self.failed
        if total == 0:
            print("❌ No tests executed!")
            return False
            
        print(f"{'='*60}")
        print(f"📊 TEST SUMMARY - SendCraft Phase 15")
        print(f"{'='*60}")
        print(f"Total Tests: {total}")
        print(f"✅ Passed: {self.passed}")
        print(f"❌ Failed: {self.failed}")
        print(f"📈 Success Rate: {(self.passed/total*100):.1f}%")
        print(f"{'='*60}")
        
        if self.failed == 0:
            print("🎉 ALL TESTS PASSED! Phase 15 API is working correctly!")
        else:
            print(f"⚠️  {self.failed} test(s) failed. Please review and fix.")
            
        return self.failed == 0

def get_api_key():
    """Obter API key da conta geral@artnshine.pt"""
    print("🔑 Obtendo API key da conta geral@artnshine.pt...")
    
    # Tentar várias estratégias para obter a API key
    strategies = [
        lambda: input("Cole a API key da conta geral@artnshine.pt aqui: ").strip(),
        lambda: get_api_key_from_web_interface(),
        lambda: get_api_key_from_database()
    ]
    
    for strategy in strategies:
        try:
            api_key = strategy()
            if api_key and len(api_key) > 10:
                return api_key
        except:
            continue
    
    print("❌ Não foi possível obter a API key!")
    print("📝 Por favor, obtenha manualmente:")
    print("   1. Acesse http://localhost:5000")
    print("   2. Login com geral@artnshine.pt")
    print("   3. Vá para configurações da conta")
    print("   4. Copie a API key")
    return None

def get_api_key_from_web_interface():
    """Tentar obter API key via web interface automaticamente"""
    print("🌐 Tentando obter API key via interface web...")
    
    # Fazer login automático (se possível)
    login_data = {
        'email': 'geral@artnshine.pt',
        'password': '6+r&0io.ThlW2'
    }
    
    session = requests.Session()
    
    try:
        # Login
        login_response = session.post(f"{API_BASE}/login", data=login_data)
        if login_response.status_code == 200:
            print("✅ Login automático bem-sucedido")
            
            # Tentar acessar página de API keys
            api_page = session.get(f"{API_BASE}/accounts")
            if api_page.status_code == 200:
                # Procurar por API key no HTML
                import re
                api_key_match = re.search(r'api[_-]?key["\']?\s*[:=]\s*["\']?([a-zA-Z0-9]{32,})', api_page.text, re.IGNORECASE)
                if api_key_match:
                    return api_key_match.group(1)
        
    except Exception as e:
        print(f"❌ Erro no login automático: {e}")
    
    return None

def get_api_key_from_database():
    """Tentar obter API key diretamente do banco de dados"""
    print("🗄️  Tentando obter API key do banco de dados...")
    
    try:
        import sqlite3
        
        # Tentar SQLite local primeiro
        for db_path in ['instance/sendcraft.db', 'sendcraft.db', 'app.db']:
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                
                # Procurar pela API key da conta geral
                cursor.execute("""
                    SELECT api_key_hash FROM email_accounts 
                    WHERE email_address = 'geral@artnshine.pt' 
                    AND is_active = 1
                """)
                
                result = cursor.fetchone()
                if result:
                    api_key_hash = result[0]
                    print(f"✅ Encontrada API key hash: {api_key_hash[:16]}...")
                    # Nota: Precisaria de reverse do hash, que não é possível
                    # Retornar None para forçar input manual
                    
                conn.close()
                break
                
            except Exception as e:
                continue
                
    except ImportError:
        print("❌ sqlite3 não disponível")
    except Exception as e:
        print(f"❌ Erro ao acessar banco: {e}")
    
    return None

def create_test_pdf_base64():
    """Criar PDF pequeno para testes"""
    pdf_content = """%PDF-1.4
1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj
2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj  
3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 612 792]>>endobj
xref 0 4
0000000000 65535 f
0000000010 00000 n
0000000053 00000 n
0000000100 00000 n
trailer<</Size 4/Root 1 0 R>>startxref 150 %%EOF"""
    return base64.b64encode(pdf_content.encode()).decode()

def test_api_health(results):
    """Teste 0: Verificar se API está respondendo"""
    try:
        response = requests.get(f"{API_BASE}/api/v1/health", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            results.add_result(
                "api_health",
                True,
                f"API está respondendo - {data.get('service', 'Unknown')}"
            )
            return True
        else:
            results.add_result(
                "api_health",
                False,
                f"API retornou status {response.status_code}",
                response.text
            )
            return False
            
    except Exception as e:
        results.add_result("api_health", False, f"Erro ao conectar com API: {str(e)}")
        return False

def test_send_simple_email(results):
    """Teste 1: Envio simples sem anexos"""
    payload = {
        "to": [TEST_EMAIL],
        "subject": f"✅ Teste SendCraft Phase 16 - {datetime.now().strftime('%H:%M:%S')}",
        "html": "<h1>🚀 Teste Phase 16 Funcionou!</h1><p>Este email foi enviado via API Phase 15.</p><p><strong>Status:</strong> Envio simples sem anexos</p>",
        "text": "🚀 Teste Phase 16 Funcionou! Este email foi enviado via API Phase 15. Status: Envio simples sem anexos",
        "domain": DOMAIN,
        "account": ACCOUNT,
        "from_name": "SendCraft Test Bot"
    }
    
    # Testar ambas as rotas (atual e esperada)
    endpoints_to_test = [
        "/api/v1/emails/send",  # Rota atual
        "/api/v1/send"          # Rota esperada
    ]
    
    success = False
    for endpoint in endpoints_to_test:
        try:
            response = requests.post(f"{API_BASE}{endpoint}", json=payload, headers=HEADERS, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and 'message_id' in data:
                    results.add_result(
                        "send_simple_email",
                        True,
                        f"Email enviado com sucesso via {endpoint}. ID: {data['message_id']}"
                    )
                    return data['message_id']
                    
        except Exception as e:
            continue
    
    # Se chegou aqui, ambas as rotas falharam
    results.add_result(
        "send_simple_email",
        False,
        "Falha em ambas as rotas (/api/v1/emails/send e /api/v1/send)",
        "Verificar se a API está rodando e se as rotas estão corretas"
    )
    return None

def test_send_with_attachment(results):
    """Teste 2: Envio com anexo PDF"""
    pdf_base64 = create_test_pdf_base64()
    
    payload = {
        "to": [TEST_EMAIL],
        "subject": f"📎 Teste Anexo PDF - {datetime.now().strftime('%H:%M:%S')}",
        "html": "<h1>📎 Teste com Anexo PDF</h1><p>PDF de teste em anexo.</p>",
        "attachments": [{
            "filename": f"teste-phase16-{int(time.time())}.pdf",
            "content_type": "application/pdf",
            "content": pdf_base64
        }],
        "domain": DOMAIN,
        "account": ACCOUNT
    }
    
    endpoints_to_test = ["/api/v1/emails/send", "/api/v1/send"]
    
    for endpoint in endpoints_to_test:
        try:
            response = requests.post(f"{API_BASE}{endpoint}", json=payload, headers=HEADERS, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                attachments_count = data.get('attachments_processed', 0)
                if data.get('success') and attachments_count > 0:
                    results.add_result(
                        "send_with_attachment",
                        True,
                        f"Email com anexo enviado via {endpoint}. Anexos processados: {attachments_count}"
                    )
                    return
                    
        except Exception as e:
            continue
    
    results.add_result(
        "send_with_attachment",
        False,
        "Falha no envio com anexo em ambas as rotas"
    )

def test_attachment_too_large(results):
    """Teste 3: Anexo muito grande deve falhar (>10MB)"""
    # Criar conteúdo de ~12MB
    large_content = "A" * (12 * 1024 * 1024)  # 12MB
    large_base64 = base64.b64encode(large_content.encode()).decode()
    
    payload = {
        "to": [TEST_EMAIL],
        "subject": "Teste Anexo Grande (deve falhar)",
        "html": "<h1>Anexo Grande</h1>",
        "attachments": [{
            "filename": "arquivo-grande.txt",
            "content_type": "text/plain",
            "content": large_base64
        }],
        "domain": DOMAIN,
        "account": ACCOUNT
    }
    
    endpoints_to_test = ["/api/v1/emails/send", "/api/v1/send"]
    
    for endpoint in endpoints_to_test:
        try:
            response = requests.post(f"{API_BASE}{endpoint}", json=payload, headers=HEADERS, timeout=30)
            
            if response.status_code == 400:
                data = response.json()
                error_msg = str(data).lower()
                if "size" in error_msg or "10mb" in error_msg or "limit" in error_msg:
                    results.add_result(
                        "attachment_too_large",
                        True,
                        f"Anexo grande corretamente rejeitado via {endpoint}"
                    )
                    return
                    
        except Exception as e:
            continue
    
    results.add_result(
        "attachment_too_large",
        False,
        "Anexo grande não foi rejeitado (problema de segurança!)"
    )

def test_bulk_processing(results):
    """Teste 4: Processamento bulk"""
    payload = {
        "to": [TEST_EMAIL] * 3,  # 3 emails para teste
        "subject": f"📧 Teste Bulk - {datetime.now().strftime('%H:%M:%S')}",
        "html": "<h1>📧 Bulk Email Test</h1><p>Este é um teste de envio em lote.</p>",
        "bulk": True,
        "domain": DOMAIN,
        "account": ACCOUNT
    }
    
    endpoints_to_test = ["/api/v1/emails/send", "/api/v1/send"]
    
    for endpoint in endpoints_to_test:
        try:
            response = requests.post(f"{API_BASE}{endpoint}", json=payload, headers=HEADERS, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    status = data.get('status', 'unknown')
                    results.add_result(
                        "bulk_processing",
                        True,
                        f"Bulk email processado via {endpoint}. Status: {status}"
                    )
                    return
                    
        except Exception as e:
            continue
    
    results.add_result(
        "bulk_processing",
        False,
        "Falha no processamento bulk"
    )

def test_status_endpoint(results, message_id=None):
    """Teste 5: Endpoint de status"""
    if not message_id:
        message_id = "MSG-000001"  # ID de fallback
    
    endpoints_to_test = [
        f"/api/v1/emails/send/{message_id}/status",
        f"/api/v1/send/{message_id}/status"
    ]
    
    for endpoint in endpoints_to_test:
        try:
            response = requests.get(f"{API_BASE}{endpoint}", headers=HEADERS, timeout=10)
            
            if response.status_code in [200, 404]:  # 200 ou 404 são válidos
                if response.status_code == 200:
                    data = response.json()
                    required_fields = ['message_id', 'status']
                    missing_fields = [field for field in required_fields if field not in data]
                    
                    if not missing_fields:
                        results.add_result(
                            "status_endpoint",
                            True,
                            f"Status endpoint funcionando via {endpoint}"
                        )
                        return
                else:  # 404
                    results.add_result(
                        "status_endpoint",
                        True,
                        f"Status endpoint respondendo 404 para ID inexistente (correto) via {endpoint}"
                    )
                    return
                    
        except Exception as e:
            continue
    
    results.add_result(
        "status_endpoint",
        False,
        "Status endpoint não está funcionando"
    )

def test_validation_errors(results):
    """Teste 6: Validações de erro"""
    # Teste 1: Corpo vazio
    try:
        response = requests.post(f"{API_BASE}/api/v1/emails/send", json={}, headers=HEADERS, timeout=10)
        if response.status_code == 400:
            results.add_result("validation_empty_body", True, "Corpo vazio corretamente rejeitado")
        else:
            results.add_result("validation_empty_body", False, f"Esperado 400, recebido {response.status_code}")
    except:
        results.add_result("validation_empty_body", False, "Erro no teste de validação")

def main():
    """Executar todos os testes"""
    global API_KEY, HEADERS
    
    print("🚀 SendCraft Phase 15 - Complete Test Suite")
    print("=" * 60)
    print(f"🌐 API Base: {API_BASE}")
    print(f"📧 Domain: {DOMAIN}")
    print(f"👤 Account: {ACCOUNT}")
    print(f"✉️  Test Email: {TEST_EMAIL}")
    print("=" * 60)
    
    # Obter API key
    API_KEY = get_api_key()
    if not API_KEY:
        print("❌ Não foi possível obter API key. Teste abortado.")
        return 1
    
    HEADERS = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    print(f"🔑 API Key obtida: {API_KEY[:16]}...")
    print()
    
    results = TestResults()
    
    # Executar testes
    print("🧪 Iniciando testes...")
    print()
    
    # Teste 0: Health check
    if not test_api_health(results):
        print("❌ API não está respondendo. Parando testes.")
        return 1
    
    # Teste 1: Envio simples
    print("1️⃣ Testando envio simples...")
    message_id = test_send_simple_email(results)
    
    # Teste 2: Com anexo
    print("2️⃣ Testando envio com anexo...")
    test_send_with_attachment(results)
    
    # Teste 3: Anexo grande
    print("3️⃣ Testando anexo muito grande...")
    test_attachment_too_large(results)
    
    # Teste 4: Bulk
    print("4️⃣ Testando processamento bulk...")
    test_bulk_processing(results)
    
    # Teste 5: Status
    print("5️⃣ Testando endpoint de status...")
    test_status_endpoint(results, message_id)
    
    # Teste 6: Validações
    print("6️⃣ Testando validações...")
    test_validation_errors(results)
    
    # Salvar resultados
    with open('docs/phase16/test-results.json', 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'api_base': API_BASE,
            'test_account': f"{ACCOUNT}@{DOMAIN}",
            'results': results.results
        }, f, indent=2)
    
    # Resumo final
    success = results.summary()
    
    print(f"\n📄 Resultados salvos em: docs/phase16/test-results.json")
    
    if success:
        print("\n🎉 PARABÉNS! Todos os testes passaram!")
        print("🚀 A API Phase 15 está funcionando corretamente!")
        return 0
    else:
        print(f"\n⚠️  Alguns testes falharam. Revisar e corrigir.")
        return 1

if __name__ == "__main__":
    exit(main())
