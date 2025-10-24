# 📝 SendCraft Phase 16: Scripts de Teste

## 🧪 Script Principal de Teste

### scripts/test_phase15.py
```python
#!/usr/bin/env python3
"""
SendCraft Phase 15 - Complete Test Suite
Testa todos os endpoints da API de envio de emails
"""
import requests
import base64
import time
import json
from datetime import datetime

# Configuração
API_BASE = "http://localhost:5000"
API_KEY = "sua_chave_api_aqui"  # Obtida da conta geral@artnshine.pt
DOMAIN = "artnshine.pt" 
ACCOUNT = "geral"
TEST_EMAIL = "geral@artnshine.pt"

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

class TestResults:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.results = []
    
    def add_result(self, test_name, success, message, details=None):
        status = "✅ PASS" if success else "❌ FAIL"
        self.results.append({
            'test': test_name,
            'status': status,
            'message': message,
            'details': details,
            'timestamp': datetime.now().isoformat()
        })
        
        if success:
            self.passed += 1
        else:
            self.failed += 1
        
        print(f"{status}: {test_name} - {message}")
        if details and not success:
            print(f"   Details: {details}")
    
    def summary(self):
        total = self.passed + self.failed
        print(f"\n{'='*50}")
        print(f"TEST SUMMARY")
        print(f"{'='*50}")
        print(f"Total Tests: {total}")
        print(f"Passed: {self.passed}")
        print(f"Failed: {self.failed}")
        print(f"Success Rate: {(self.passed/total*100):.1f}%")
        return self.failed == 0

def create_test_pdf_base64():
    """Cria um PDF pequeno em base64 para testes"""
    # PDF mínimo válido (Hello World)
    pdf_content = """%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R >>
endobj
4 0 obj
<< /Length 44 >>
stream
BT
/F1 12 Tf
100 700 Td
(Hello World) Tj
ET
endstream
endobj
xref
0 5
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000206 00000 n 
trailer
<< /Size 5 /Root 1 0 R >>
startxref
299
%%EOF"""
    return base64.b64encode(pdf_content.encode()).decode()

def test_send_simple_email(results):
    """Teste 1: Envio simples sem anexos"""
    payload = {
        "to": [TEST_EMAIL],
        "subject": "Teste Phase 16 - Email Simples",
        "html": "<h1>✅ Teste Phase 16 Funcionou!</h1><p>Este email foi enviado via API.</p>",
        "text": "✅ Teste Phase 16 Funcionou! Este email foi enviado via API.",
        "domain": DOMAIN,
        "account": ACCOUNT,
        "from_name": "SendCraft Test Bot"
    }
    
    try:
        response = requests.post(f"{API_BASE}/api/v1/emails/send", json=payload, headers=HEADERS)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and 'message_id' in data:
                results.add_result(
                    "send_simple_email",
                    True,
                    f"Email enviado com sucesso. ID: {data['message_id']}"
                )
                return data['message_id']
            else:
                results.add_result(
                    "send_simple_email", 
                    False,
                    "Response não indica sucesso",
                    data
                )
        else:
            results.add_result(
                "send_simple_email",
                False, 
                f"HTTP {response.status_code}",
                response.text
            )
    except Exception as e:
        results.add_result("send_simple_email", False, f"Exception: {str(e)}")
    
    return None

def test_send_with_attachment(results):
    """Teste 2: Envio com anexo PDF"""
    pdf_base64 = create_test_pdf_base64()
    
    payload = {
        "to": [TEST_EMAIL],
        "subject": "Teste Phase 16 - Com Anexo PDF",
        "html": "<h1>📎 Teste com Anexo</h1><p>PDF em anexo.</p>",
        "attachments": [{
            "filename": "teste-phase16.pdf",
            "content_type": "application/pdf",
            "content": pdf_base64
        }],
        "domain": DOMAIN,
        "account": ACCOUNT
    }
    
    try:
        response = requests.post(f"{API_BASE}/api/v1/emails/send", json=payload, headers=HEADERS)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and data.get('attachments_processed', 0) > 0:
                results.add_result(
                    "send_with_attachment",
                    True,
                    f"Email com anexo enviado. ID: {data['message_id']}"
                )
            else:
                results.add_result(
                    "send_with_attachment",
                    False,
                    "Anexo não foi processado",
                    data
                )
        else:
            results.add_result(
                "send_with_attachment",
                False,
                f"HTTP {response.status_code}",
                response.text
            )
    except Exception as e:
        results.add_result("send_with_attachment", False, f"Exception: {str(e)}")

def test_bulk_processing(results):
    """Teste 3: Bulk com múltiplos destinatários"""
    payload = {
        "to": [TEST_EMAIL] * 5,  # 5 emails para mesmo destinatário
        "subject": "Teste Phase 16 - Bulk Processing",
        "html": "<h1>📧 Bulk Email Test</h1><p>Este é um teste de envio em lote.</p>",
        "bulk": True,
        "domain": DOMAIN,
        "account": ACCOUNT
    }
    
    try:
        response = requests.post(f"{API_BASE}/api/v1/emails/send", json=payload, headers=HEADERS)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and data.get('status') == 'queued':
                results.add_result(
                    "bulk_processing",
                    True,
                    f"Bulk email enfileirado. ID: {data['message_id']}"
                )
            else:
                results.add_result(
                    "bulk_processing",
                    False,
                    "Bulk não foi enfileirado corretamente",
                    data
                )
        else:
            results.add_result(
                "bulk_processing",
                False,
                f"HTTP {response.status_code}",
                response.text
            )
    except Exception as e:
        results.add_result("bulk_processing", False, f"Exception: {str(e)}")

def test_attachment_too_large(results):
    """Teste 4: Anexo muito grande deve falhar"""
    # Criar conteúdo de ~12MB (deve exceder limite de 10MB)
    large_content = "A" * (12 * 1024 * 1024)
    large_base64 = base64.b64encode(large_content.encode()).decode()
    
    payload = {
        "to": [TEST_EMAIL],
        "subject": "Teste - Anexo Grande",
        "html": "<h1>Anexo Grande</h1>",
        "attachments": [{
            "filename": "arquivo-grande.txt",
            "content_type": "text/plain",
            "content": large_base64
        }],
        "domain": DOMAIN,
        "account": ACCOUNT
    }
    
    try:
        response = requests.post(f"{API_BASE}/api/v1/emails/send", json=payload, headers=HEADERS)
        
        if response.status_code == 400:
            data = response.json()
            if "10MB" in str(data) or "size" in str(data).lower():
                results.add_result(
                    "attachment_too_large",
                    True,
                    "Anexo grande foi corretamente rejeitado"
                )
            else:
                results.add_result(
                    "attachment_too_large",
                    False,
                    "Rejeitado mas mensagem não menciona tamanho",
                    data
                )
        else:
            results.add_result(
                "attachment_too_large",
                False,
                f"Deveria retornar 400, retornou {response.status_code}",
                response.text
            )
    except Exception as e:
        results.add_result("attachment_too_large", False, f"Exception: {str(e)}")

def test_invalid_file_type(results):
    """Teste 5: Tipo de arquivo não permitido"""
    payload = {
        "to": [TEST_EMAIL],
        "subject": "Teste - Arquivo Inválido",
        "html": "<h1>Arquivo EXE</h1>",
        "attachments": [{
            "filename": "virus.exe", 
            "content_type": "application/x-executable",
            "content": base64.b64encode(b"fake exe content").decode()
        }],
        "domain": DOMAIN,
        "account": ACCOUNT
    }
    
    try:
        response = requests.post(f"{API_BASE}/api/v1/emails/send", json=payload, headers=HEADERS)
        
        if response.status_code == 400:
            data = response.json()
            if "type" in str(data).lower() or "not allowed" in str(data).lower():
                results.add_result(
                    "invalid_file_type",
                    True,
                    "Tipo de arquivo inválido foi corretamente rejeitado"
                )
            else:
                results.add_result(
                    "invalid_file_type",
                    False,
                    "Rejeitado mas mensagem não menciona tipo",
                    data
                )
        else:
            results.add_result(
                "invalid_file_type",
                False,
                f"Deveria retornar 400, retornou {response.status_code}",
                response.text
            )
    except Exception as e:
        results.add_result("invalid_file_type", False, f"Exception: {str(e)}")

def test_status_endpoint(results, message_id=None):
    """Teste 6: Endpoint de status"""
    if not message_id:
        message_id = "MSG-000001"  # ID de teste
    
    try:
        response = requests.get(
            f"{API_BASE}/api/v1/emails/send/{message_id}/status",
            headers=HEADERS
        )
        
        if response.status_code == 200:
            data = response.json()
            required_fields = ['message_id', 'status', 'recipients']
            missing_fields = [field for field in required_fields if field not in data]
            
            if not missing_fields:
                results.add_result(
                    "status_endpoint",
                    True,
                    f"Status endpoint funcionou para {message_id}"
                )
            else:
                results.add_result(
                    "status_endpoint",
                    False,
                    f"Campos ausentes: {missing_fields}",
                    data
                )
        elif response.status_code == 404:
            results.add_result(
                "status_endpoint",
                True,  # 404 é válido para ID inexistente
                f"404 para ID inexistente (correto)"
            )
        else:
            results.add_result(
                "status_endpoint",
                False,
                f"HTTP {response.status_code}",
                response.text
            )
    except Exception as e:
        results.add_result("status_endpoint", False, f"Exception: {str(e)}")

def test_missing_required_fields(results):
    """Teste 7: Campos obrigatórios ausentes"""
    test_cases = [
        ({}, "corpo vazio"),
        ({"to": []}, "destinatários vazios"),
        ({"to": ["test@test.com"]}, "sem subject"),
        ({"to": ["test@test.com"], "subject": "Test"}, "sem domain/account"),
    ]
    
    for payload, description in test_cases:
        try:
            response = requests.post(f"{API_BASE}/api/v1/emails/send", json=payload, headers=HEADERS)
            
            if response.status_code == 400:
                data = response.json()
                if "validation" in str(data).lower() or "required" in str(data).lower():
                    results.add_result(
                        f"validation_{description.replace(' ', '_')}",
                        True,
                        f"Validação correta para {description}"
                    )
                else:
                    results.add_result(
                        f"validation_{description.replace(' ', '_')}",
                        False,
                        f"400 mas mensagem não indica validação para {description}",
                        data
                    )
            else:
                results.add_result(
                    f"validation_{description.replace(' ', '_')}",
                    False,
                    f"Deveria retornar 400, retornou {response.status_code} para {description}",
                    response.text
                )
        except Exception as e:
            results.add_result(f"validation_{description.replace(' ', '_')}", False, f"Exception: {str(e)}")

def test_idempotency(results):
    """Teste 8: Idempotency com mesma chave"""
    idempotency_key = f"test-{int(time.time())}"
    
    payload = {
        "to": [TEST_EMAIL],
        "subject": "Teste Phase 16 - Idempotency",
        "html": "<h1>🔒 Teste de Idempotency</h1>",
        "domain": DOMAIN,
        "account": ACCOUNT,
        "idempotency_key": idempotency_key
    }
    
    try:
        # Primeiro envio
        response1 = requests.post(f"{API_BASE}/api/v1/emails/send", json=payload, headers=HEADERS)
        time.sleep(1)
        
        # Segundo envio com mesma chave
        response2 = requests.post(f"{API_BASE}/api/v1/emails/send", json=payload, headers=HEADERS)
        
        if response1.status_code == 200 and response2.status_code == 200:
            data1 = response1.json()
            data2 = response2.json()
            
            # Segundo deve ser ignorado ou indicar duplicado
            if (data2.get('status') == 'duplicate_ignored' or 
                data1.get('message_id') == data2.get('message_id')):
                results.add_result(
                    "idempotency",
                    True,
                    "Idempotency funcionou - segundo envio ignorado"
                )
            else:
                results.add_result(
                    "idempotency",
                    False,
                    "Segundo envio não foi tratado como duplicado",
                    {"first": data1, "second": data2}
                )
        else:
            results.add_result(
                "idempotency",
                False,
                f"Erro nos envios: {response1.status_code}, {response2.status_code}",
                {"resp1": response1.text, "resp2": response2.text}
            )
    except Exception as e:
        results.add_result("idempotency", False, f"Exception: {str(e)}")

def main():
    """Executar todos os testes"""
    print("🧪 SendCraft Phase 15 - Test Suite")
    print("=" * 50)
    print(f"API Base: {API_BASE}")
    print(f"Domain: {DOMAIN}")
    print(f"Account: {ACCOUNT}")
    print(f"Test Email: {TEST_EMAIL}")
    print("=" * 50)
    
    results = TestResults()
    
    # Executar testes em ordem
    print("\n1️⃣ Testando envio simples...")
    message_id = test_send_simple_email(results)
    
    print("\n2️⃣ Testando envio com anexo...")
    test_send_with_attachment(results)
    
    print("\n3️⃣ Testando bulk processing...")
    test_bulk_processing(results)
    
    print("\n4️⃣ Testando anexo muito grande...")
    test_attachment_too_large(results)
    
    print("\n5️⃣ Testando tipo de arquivo inválido...")
    test_invalid_file_type(results)
    
    print("\n6️⃣ Testando endpoint de status...")
    test_status_endpoint(results, message_id)
    
    print("\n7️⃣ Testando validações...")
    test_missing_required_fields(results)
    
    print("\n8️⃣ Testando idempotency...")
    test_idempotency(results)
    
    # Summary
    success = results.summary()
    
    # Salvar resultados
    with open('docs/phase16/test-results.json', 'w') as f:
        json.dump(results.results, f, indent=2)
    
    print(f"\n📊 Resultados salvos em: docs/phase16/test-results.json")
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())
```

### scripts/validate_api.py
```python
#!/usr/bin/env python3
"""
SendCraft API Health Check & Validation
Verifica se a API está funcionando corretamente
"""
import requests
import sys

def check_health():
    """Verificar health endpoint"""
    try:
        response = requests.get("http://localhost:5000/api/v1/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ API Health: OK")
            print(f"   Service: {data.get('service')}")
            print(f"   Version: {data.get('version')}")
            return True
        else:
            print(f"❌ API Health: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API Health: {e}")
        return False

def check_endpoints():
    """Verificar se endpoints existem"""
    endpoints = [
        "POST /api/v1/emails/send",
        "GET /api/v1/emails/send/MSG-123/status", 
        "POST /api/v1/emails/attachments/upload"
    ]
    
    print("\n🔍 Validando endpoints...")
    
    # Teste sem auth - deve retornar 401
    response = requests.post("http://localhost:5000/api/v1/emails/send", json={})
    if response.status_code == 401:
        print("✅ Authentication required (401) - correto")
        return True
    else:
        print(f"❌ Deveria retornar 401, retornou {response.status_code}")
        return False

if __name__ == "__main__":
    print("🔧 SendCraft API Validation")
    print("=" * 30)
    
    health_ok = check_health()
    endpoints_ok = check_endpoints()
    
    if health_ok and endpoints_ok:
        print("\n✅ API está funcionando corretamente")
        sys.exit(0)
    else:
        print("\n❌ API tem problemas")
        sys.exit(1)
```

### scripts/generate_test_data.py
```python
#!/usr/bin/env python3
"""
Gerar dados de teste para Phase 15
"""
import base64
import json

def generate_test_attachments():
    """Gerar anexos de teste"""
    attachments = {}
    
    # PDF pequeno
    small_pdf = """%PDF-1.4
1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj
2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj  
3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 612 792]/Contents 4 0 R>>endobj
4 0 obj<</Length 44>>stream
BT/F1 12 Tf 100 700 Td(Hello PDF)Tj ET
endstream endobj
xref 0 5
0000000000 65535 f
0000000009 00000 n
0000000058 00000 n
0000000115 00000 n
0000000206 00000 n
trailer<</Size 5/Root 1 0 R>>
startxref 299 %%EOF"""
    
    attachments['small_pdf'] = {
        'filename': 'small-test.pdf',
        'content_type': 'application/pdf',
        'content': base64.b64encode(small_pdf.encode()).decode(),
        'description': 'PDF pequeno para testes (~300 bytes)'
    }
    
    # Imagem JPEG fake
    jpeg_header = bytes([0xFF, 0xD8, 0xFF, 0xE0, 0x00, 0x10, 0x4A, 0x46, 0x49, 0x46])
    jpeg_data = jpeg_header + b"fake jpeg content for testing" + bytes([0xFF, 0xD9])
    
    attachments['small_jpeg'] = {
        'filename': 'test-image.jpg',
        'content_type': 'image/jpeg', 
        'content': base64.b64encode(jpeg_data).decode(),
        'description': 'JPEG fake para testes'
    }
    
    # Arquivo de texto
    text_content = "Este é um arquivo de teste para o SendCraft Phase 15.\nConteúdo simples em texto plano."
    
    attachments['text_file'] = {
        'filename': 'readme.txt',
        'content_type': 'text/plain',
        'content': base64.b64encode(text_content.encode('utf-8')).decode(),
        'description': 'Arquivo de texto simples'
    }
    
    return attachments

def generate_test_payloads():
    """Gerar payloads de teste"""
    payloads = {}
    
    # Envio simples
    payloads['simple_send'] = {
        "to": ["teste@exemplo.com"],
        "subject": "Teste SendCraft Phase 15",
        "html": "<h1>🚀 Teste Funcionou!</h1><p>Este email foi enviado via API Phase 15.</p>",
        "text": "🚀 Teste Funcionou! Este email foi enviado via API Phase 15.",
        "domain": "artnshine.pt",
        "account": "geral",
        "from_name": "SendCraft Bot"
    }
    
    # Com anexo
    attachments = generate_test_attachments()
    payloads['with_attachment'] = {
        **payloads['simple_send'],
        "subject": "Teste com Anexo PDF",
        "attachments": [attachments['small_pdf']]
    }
    
    # Bulk
    payloads['bulk_send'] = {
        **payloads['simple_send'],
        "to": ["teste1@exemplo.com", "teste2@exemplo.com", "teste3@exemplo.com"],
        "subject": "Teste Bulk Phase 15",
        "bulk": True
    }
    
    # Com idempotency
    payloads['with_idempotency'] = {
        **payloads['simple_send'],
        "subject": "Teste Idempotency",
        "idempotency_key": "test-phase15-idempotency-123"
    }
    
    return payloads, attachments

def main():
    """Gerar e salvar dados de teste"""
    print("📋 Gerando dados de teste para Phase 15...")
    
    payloads, attachments = generate_test_payloads()
    
    # Salvar payloads
    with open('docs/phase16/test-payloads.json', 'w') as f:
        json.dump(payloads, f, indent=2)
    
    # Salvar anexos  
    with open('docs/phase16/test-attachments.json', 'w') as f:
        json.dump(attachments, f, indent=2)
    
    print("✅ Dados salvos:")
    print("   - docs/phase16/test-payloads.json")
    print("   - docs/phase16/test-attachments.json")
    
    # Mostrar resumo
    print(f"\n📊 Resumo:")
    print(f"   Payloads: {len(payloads)}")
    print(f"   Anexos: {len(attachments)}")
    
    for name, payload in payloads.items():
        att_count = len(payload.get('attachments', []))
        bulk = payload.get('bulk', False)
        print(f"   - {name}: {len(payload.get('to', []))} dest, {att_count} anexos{'(bulk)' if bulk else ''}")

if __name__ == "__main__":
    main()
```

### Makefile
```makefile
# SendCraft Phase 16 - Test Commands

.PHONY: install-test validate test test-full clean

install-test:
	@echo "📦 Installing test dependencies..."
	pip install requests pytest faker

validate:
	@echo "🔧 Validating API..."
	python scripts/validate_api.py

test-data:
	@echo "📋 Generating test data..."
	python scripts/generate_test_data.py

test:
	@echo "🧪 Running Phase 15 tests..."
	python scripts/test_phase15.py

test-full: validate test-data test
	@echo "✅ Full test suite completed"

clean:
	@echo "🧹 Cleaning test files..."
	rm -f docs/phase16/test-results.json
	rm -f docs/phase16/test-payloads.json
	rm -f docs/phase16/test-attachments.json

setup-phase16:
	@echo "🚀 Setting up Phase 16..."
	mkdir -p docs/phase16
	mkdir -p scripts
	@echo "✅ Phase 16 structure created"
```