#!/usr/bin/env python3
"""
SendCraft Phase 16 - Basic API Test (No API Key Required)
Testa a estrutura básica da API sem autenticação
"""
import requests
import json
from datetime import datetime

# Configuração
API_BASE = "http://localhost:5000"

def test_health_endpoint():
    """Teste 1: Health endpoint"""
    print("1️⃣ Testando Health Endpoint...")
    try:
        response = requests.get(f"{API_BASE}/api/v1/health", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health OK: {data.get('service', 'Unknown')}")
            return True
        else:
            print(f"❌ Health falhou: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro no health: {e}")
        return False

def test_send_endpoint_structure():
    """Teste 2: Estrutura do endpoint de envio"""
    print("2️⃣ Testando Estrutura do Endpoint de Envio...")
    
    # Testar rota corrigida
    try:
        response = requests.post(f"{API_BASE}/api/v1/send", 
                               json={"test": "structure"}, 
                               timeout=10)
        
        if response.status_code in [200, 401]:
            data = response.json()
            if "API key" in data.get('message', '') or "API key required" in data.get('error', ''):
                print("✅ Rota /api/v1/send está funcionando (requer API key)")
                return True
        else:
            print(f"❌ Rota inesperada: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro na rota: {e}")
        return False

def test_old_route_compatibility():
    """Teste 3: Verificar se rota antiga foi removida (correto)"""
    print("3️⃣ Testando Remoção da Rota Antiga...")
    
    try:
        response = requests.post(f"{API_BASE}/api/v1/emails/send", 
                               json={"test": "compatibility"}, 
                               timeout=10)
        
        if response.status_code == 404:
            print("✅ Rota antiga /api/v1/emails/send foi corretamente removida")
            return True
        else:
            print(f"❌ Rota antiga ainda existe: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro na rota antiga: {e}")
        return False

def test_status_endpoint_structure():
    """Teste 4: Estrutura do endpoint de status"""
    print("4️⃣ Testando Estrutura do Endpoint de Status...")
    
    try:
        response = requests.get(f"{API_BASE}/api/v1/send/MSG-000001/status", timeout=10)
        
        if response.status_code in [200, 401]:
            data = response.json()
            if "API key" in data.get('message', '') or "API key required" in data.get('error', ''):
                print("✅ Endpoint de status está funcionando (requer API key)")
                return True
        else:
            print(f"❌ Status endpoint inesperado: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro no status endpoint: {e}")
        return False

def test_attachment_upload_structure():
    """Teste 5: Estrutura do endpoint de upload de anexos"""
    print("5️⃣ Testando Estrutura do Endpoint de Upload...")
    
    try:
        response = requests.post(f"{API_BASE}/api/v1/attachments/upload", 
                               json={"test": "upload"}, 
                               timeout=10)
        
        if response.status_code in [200, 401]:
            data = response.json()
            if "API key" in data.get('message', '') or "API key required" in data.get('error', ''):
                print("✅ Endpoint de upload está funcionando (requer API key)")
                return True
        else:
            print(f"❌ Upload endpoint inesperado: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro no upload endpoint: {e}")
        return False

def main():
    """Executar testes básicos da API"""
    print("🚀 SendCraft Phase 16 - Basic API Structure Test")
    print("=" * 60)
    print(f"🌐 API Base: {API_BASE}")
    print(f"📅 Timestamp: {datetime.now().isoformat()}")
    print("=" * 60)
    print()
    
    results = []
    
    # Executar testes
    results.append(("Health Endpoint", test_health_endpoint()))
    results.append(("Send Endpoint Structure", test_send_endpoint_structure()))
    results.append(("Old Route Compatibility", test_old_route_compatibility()))
    results.append(("Status Endpoint Structure", test_status_endpoint_structure()))
    results.append(("Upload Endpoint Structure", test_attachment_upload_structure()))
    
    # Resumo
    print()
    print("📊 RESUMO DOS TESTES")
    print("=" * 30)
    
    passed = 0
    failed = 0
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if success:
            passed += 1
        else:
            failed += 1
    
    print()
    print(f"Total: {len(results)}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📈 Success Rate: {(passed/len(results)*100):.1f}%")
    
    # Salvar resultados
    with open('docs/phase16/basic-test-results.json', 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'api_base': API_BASE,
            'results': results,
            'summary': {
                'total': len(results),
                'passed': passed,
                'failed': failed,
                'success_rate': passed/len(results)*100
            }
        }, f, indent=2)
    
    print(f"\n📄 Resultados salvos em: docs/phase16/basic-test-results.json")
    
    if failed == 0:
        print("\n🎉 TODOS OS TESTES BÁSICOS PASSARAM!")
        print("✅ A estrutura da API está funcionando corretamente!")
        print("🔑 Próximo passo: Obter API key para testes completos")
        return 0
    else:
        print(f"\n⚠️  {failed} teste(s) falharam.")
        print("🔧 Verificar configuração da API")
        return 1

if __name__ == "__main__":
    exit(main())
