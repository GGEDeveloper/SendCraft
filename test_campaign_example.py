#!/usr/bin/env python3
"""
Exemplo Prático: Teste do Sistema de Campanhas
Demonstra:
- Criar campanha
- Adicionar recipients
- Iniciar envio
- Monitorar progresso
- Verificar métricas

Executar:
    python test_campaign_example.py
"""

import requests
import json
import time
from datetime import datetime

# Config
BASE_URL = "http://localhost:5000"
TOKEN = "test-token"  # Configure com seu token real
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {TOKEN}"
}

def print_section(title):
    """Imprime título de seção."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def print_response(label, response):
    """Imprime resposta formatada."""
    print(f"\n{label}")
    print(f"Status: {response.status_code}")
    try:
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2, ensure_ascii=False)}")
        return data
    except:
        print(f"Response: {response.text}")
        return None

def test_create_campaign():
    """Teste 1: Criar campanha."""
    print_section("TESTE 1: Criar Campanha")
    
    campaign_data = {
        "account_id": 1,
        "name": f"Campanha de Teste {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "description": "Campanha de teste do sistema de warm-up",
        "subject": "Olá {{ name }}, teste do SendCraft!",
        "html_content": """
            <html>
                <body>
                    <h1>Bem-vindo ao SendCraft!</h1>
                    <p>Olá {{ name }},</p>
                    <p>Este é um teste do sistema de envio em massa com warm-up.</p>
                    <p>Desconto especial: {{ discount }}% OFF</p>
                    <a href="https://example.com?code={{ coupon }}">Resgatar Desconto</a>
                </body>
            </html>
        """,
        "text_content": "Bem-vindo ao SendCraft! Ola {{ name }}, use o código {{ coupon }} para {{ discount }}% OFF",
        "from_name": "SendCraft Team",
        "reply_to": "support@example.com",
        "warmup_enabled": True,
        "delay_between_emails": 30,  # 30 segundos para teste rápido
        "batch_size": 5,
        "use_tracking_pixel": True,
        "use_click_tracking": True
    }
    
    response = requests.post(
        f"{BASE_URL}/api/campaigns",
        json=campaign_data,
        headers=HEADERS
    )
    
    data = print_response("POST /api/campaigns", response)
    return data["id"] if data else None

def test_add_recipients(campaign_id):
    """Teste 2: Adicionar recipients."""
    print_section("TESTE 2: Adicionar Recipients")
    
    # Gerar 20 recipients de teste
    recipients = [
        {
            "email": f"user{i:02d}@example.com",
            "name": f"Usuário {i}",
            "variables": {
                "discount": 10 + (i % 5) * 5,
                "coupon": f"SAVE{10 + (i % 5) * 5}"
            }
        }
        for i in range(1, 21)
    ]
    
    recipients_data = {"recipients": recipients}
    
    response = requests.post(
        f"{BASE_URL}/api/campaigns/{campaign_id}/recipients",
        json=recipients_data,
        headers=HEADERS
    )
    
    data = print_response(
        f"POST /api/campaigns/{campaign_id}/recipients",
        response
    )
    
    if data:
        print(f"\nResumo:")
        print(f"  Adicionados: {data['added']}")
        print(f"  Duplicados: {data['duplicates']}")
        print(f"  Total na campanha: {data['total_recipients']}")
    
    return data

def test_get_campaign(campaign_id):
    """Teste 3: Obter detalhes da campanha."""
    print_section("TESTE 3: Obter Detalhes da Campanha")
    
    response = requests.get(
        f"{BASE_URL}/api/campaigns/{campaign_id}",
        headers=HEADERS
    )
    
    data = print_response(
        f"GET /api/campaigns/{campaign_id}",
        response
    )
    
    if data:
        print(f"\nResumo:")
        print(f"  Status: {data['status']}")
        print(f"  Total recipients: {data['total_recipients']}")
        print(f"  Fase warm-up: {data['warmup_phase']}")
        print(f"  Limite diário: {data['daily_limit']} emails/dia")
    
    return data

def test_start_campaign(campaign_id):
    """Teste 4: Iniciar campanha."""
    print_section("TESTE 4: Iniciar Campanha")
    
    response = requests.post(
        f"{BASE_URL}/api/campaigns/{campaign_id}/start",
        headers=HEADERS
    )
    
    data = print_response(
        f"POST /api/campaigns/{campaign_id}/start",
        response
    )
    
    if data:
        print(f"\nCampanha iniciada com sucesso!")
        print(f"  Status: {data['status']}")
    
    return data

def test_monitor_campaign(campaign_id, duration_seconds=60):
    """Teste 5: Monitorar campanha em tempo real."""
    print_section("TESTE 5: Monitorar Campanha em Tempo Real")
    print(f"Monitorando por {duration_seconds} segundos...\n")
    
    start_time = time.time()
    last_sent = 0
    
    while time.time() - start_time < duration_seconds:
        response = requests.get(
            f"{BASE_URL}/api/campaigns/{campaign_id}/stats",
            headers=HEADERS
        )
        
        if response.status_code == 200:
            stats = response.json()
            
            # Mostrar progresso a cada mudanca
            if stats['sent'] != last_sent:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] "
                      f"Enviados: {stats['sent']}/{stats['total_recipients']} "
                      f"| Bounce: {stats['bounce_rate']} "
                      f"| Abertura: {stats['open_rate']} "
                      f"| Cliques: {stats['click_rate']}")
                last_sent = stats['sent']
            
            # Parar se completou
            if stats['status'] == 'completed':
                print(f"\n✅ Campanha concluída!")
                return stats
        
        time.sleep(5)
    
    # Obter stats finais
    response = requests.get(
        f"{BASE_URL}/api/campaigns/{campaign_id}/stats",
        headers=HEADERS
    )
    
    if response.status_code == 200:
        stats = response.json()
        print(f"\n[Monitoramento finalizado]")
        print(f"Status: {stats['status']}")
        return stats
    
    return None

def test_list_recipients(campaign_id, status='sent'):
    """Teste 6: Listar recipients com status."""
    print_section("TESTE 6: Listar Recipients")
    
    response = requests.get(
        f"{BASE_URL}/api/campaigns/{campaign_id}/recipients",
        params={
            "status": status,
            "limit": 10,
            "offset": 0
        },
        headers=HEADERS
    )
    
    data = print_response(
        f"GET /api/campaigns/{campaign_id}/recipients?status={status}",
        response
    )
    
    if data and data.get('recipients'):
        print(f"\nPrimeiros {len(data['recipients'])} recipients:")
        for r in data['recipients']:
            status_icon = "✅" if r['status'] == 'sent' else "❌"
            print(f"  {status_icon} {r['email']} - {r['status']} "
                  f"(Abertura: {r['opened']}, Clique: {r['clicked']})")
    
    return data

def test_pause_resume(campaign_id):
    """Teste 7: Pausar e retomar campanha."""
    print_section("TESTE 7: Pausar e Retomar")
    
    # Pausar
    print("\nPausando campanha...")
    response = requests.post(
        f"{BASE_URL}/api/campaigns/{campaign_id}/pause",
        headers=HEADERS
    )
    data_pause = print_response(
        f"POST /api/campaigns/{campaign_id}/pause",
        response
    )
    
    time.sleep(5)
    
    # Retomar
    print("\nRetomando campanha...")
    response = requests.post(
        f"{BASE_URL}/api/campaigns/{campaign_id}/resume",
        headers=HEADERS
    )
    data_resume = print_response(
        f"POST /api/campaigns/{campaign_id}/resume",
        response
    )
    
    return data_pause, data_resume

def test_list_campaigns():
    """Teste 8: Listar all campanhas."""
    print_section("TESTE 8: Listar Campanhas")
    
    response = requests.get(
        f"{BASE_URL}/api/campaigns",
        params={
            "account_id": 1,
            "limit": 10,
            "offset": 0
        },
        headers=HEADERS
    )
    
    data = print_response("GET /api/campaigns", response)
    
    if data and data.get('campaigns'):
        print(f"\nTotal de campanhas: {data['total']}\n")
        for campaign in data['campaigns']:
            print(f"  ID: {campaign['id']}")
            print(f"  Nome: {campaign['name']}")
            print(f"  Status: {campaign['status']}")
            print(f"  Recipients: {campaign['total_recipients']}")
            print(f"  Enviados: {campaign['sent']}/{campaign['total_recipients']}")
            print()
    
    return data

def main():
    """Executa todos os testes."""
    print("\n📧 Teste do Sistema de Campanhas do SendCraft")
    print(f"Base URL: {BASE_URL}")
    print(f"Token: {TOKEN[:20]}...\n")
    
    try:
        # Teste 1: Criar campanha
        campaign_id = test_create_campaign()
        if not campaign_id:
            print("\n❌ Falha ao criar campanha. Abortando.")
            return
        
        # Teste 2: Adicionar recipients
        test_add_recipients(campaign_id)
        
        # Teste 3: Obter detalhes
        test_get_campaign(campaign_id)
        
        # Teste 4: Iniciar
        test_start_campaign(campaign_id)
        
        # Teste 5: Monitorar
        test_monitor_campaign(campaign_id, duration_seconds=120)
        
        # Teste 6: Listar recipients enviados
        test_list_recipients(campaign_id, status='sent')
        
        # Teste 7: Pausar e retomar
        # test_pause_resume(campaign_id)  # Comentado para não interromper fluxo
        
        # Teste 8: Listar campanhas
        test_list_campaigns()
        
        print_section("RESUMO")
        print("✅ Todos os testes completados com sucesso!")
        print(f"\nPróximos passos:")
        print(f"1. Acesse a campanha: {BASE_URL}/dashboard/campaigns/{campaign_id}")
        print(f"2. Monitore as métricas em tempo real")
        print(f"3. Verifique se a campanha avançou de fase")
        
    except Exception as e:
        print(f"\n❌ Erro durante testes: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
