"""
SendCraft - Seed Data para Desenvolvimento Local
Cria dados realistas: domínios, contas, templates, logs
"""
import click
from flask.cli import with_appcontext
from flask import current_app
from datetime import datetime, timedelta
from sendcraft.extensions import db
from sendcraft.models import Domain, EmailAccount, EmailTemplate, EmailLog
from sendcraft.models.log import EmailStatus
import random


@click.command('seed-local-data')
@with_appcontext
def seed_local_data():
    """Popula base de dados com dados realistas para desenvolvimento"""
    
    click.echo('🔧 Criando dados seed para SendCraft...')
    
    # Limpar dados existentes (apenas se SQLite)
    database_url = current_app.config.get('SQLALCHEMY_DATABASE_URI', '')
    if 'sqlite' in database_url:
        click.echo('🗑️ Limpando dados SQLite existentes...')
        db.drop_all()
        db.create_all()
    else:
        click.echo('⚠️ MySQL detectado - mantendo dados existentes')
    
    # 1. CRIAR DOMÍNIOS
    domains_data = [
        {
            'name': 'alitools.pt',
            'description': 'Domínio principal AliTools B2B Ecommerce',
            'is_active': True
        },
        {
            'name': 'artnshine.pt',
            'description': 'Portfolio Art & Shine - Desenvolvimento Web',
            'is_active': True
        },
        {
            'name': 'sendcraft.local',
            'description': 'Domínio SendCraft para testes e demonstração',
            'is_active': True
        },
        {
            'name': 'test-domain.com',
            'description': 'Domínio de testes desativado',
            'is_active': False
        },
        {
            'name': 'cliente-exemplo.pt',
            'description': 'Exemplo cliente B2B - Ferramentas Industriais',
            'is_active': True
        }
    ]
    
    domains = []
    for data in domains_data:
        # Verificar se domínio já existe
        existing = Domain.query.filter_by(name=data['name']).first()
        if not existing:
            domain = Domain(**data)
            db.session.add(domain)
            domains.append(domain)
        else:
            domains.append(existing)
    
    db.session.commit()
    click.echo(f'   ✅ Domínios: {len(domains)} criados/verificados')
    
    # 2. CRIAR CONTAS DE EMAIL
    accounts_data = [
        {
            'domain_name': 'alitools.pt',
            'local_part': 'encomendas',
            'display_name': 'AliTools Encomendas',
            'smtp_server': 'smtp.gmail.com',
            'smtp_port': 587,
            'smtp_username': 'encomendas@alitools.pt',
            'use_tls': True,
            'use_ssl': False,
            'daily_limit': 1000,
            'monthly_limit': 20000,
            'is_active': True
        },
        {
            'domain_name': 'alitools.pt',
            'local_part': 'suporte',
            'display_name': 'AliTools Suporte Técnico',
            'smtp_server': 'smtp.gmail.com',
            'smtp_port': 587,
            'smtp_username': 'suporte@alitools.pt',
            'use_tls': True,
            'use_ssl': False,
            'daily_limit': 500,
            'monthly_limit': 10000,
            'is_active': True
        },
        {
            'domain_name': 'alitools.pt',
            'local_part': 'marketing',
            'display_name': 'AliTools Marketing',
            'smtp_server': 'smtp.antispamcloud.com',
            'smtp_port': 587,
            'smtp_username': 'marketing@alitools.pt',
            'use_tls': True,
            'use_ssl': False,
            'daily_limit': 2000,
            'monthly_limit': 50000,
            'is_active': True
        },
        {
            'domain_name': 'artnshine.pt',
            'local_part': 'info',
            'display_name': 'Art & Shine Portfolio',
            'smtp_server': 'mail.artnshine.pt',
            'smtp_port': 587,
            'smtp_username': 'info@artnshine.pt',
            'use_tls': True,
            'use_ssl': False,
            'daily_limit': 200,
            'monthly_limit': 5000,
            'is_active': True
        },
        {
            'domain_name': 'sendcraft.local',
            'local_part': 'demo',
            'display_name': 'SendCraft Demo Account',
            'smtp_server': 'localhost',
            'smtp_port': 1025,  # MailHog for testing
            'smtp_username': 'demo@sendcraft.local',
            'use_tls': False,
            'use_ssl': False,
            'daily_limit': 10000,
            'monthly_limit': 100000,
            'is_active': True
        },
        {
            'domain_name': 'cliente-exemplo.pt',
            'local_part': 'vendas',
            'display_name': 'Cliente Exemplo Vendas',
            'smtp_server': 'smtp.cliente-exemplo.pt',
            'smtp_port': 587,
            'smtp_username': 'vendas@cliente-exemplo.pt',
            'use_tls': True,
            'use_ssl': False,
            'daily_limit': 800,
            'monthly_limit': 15000,
            'is_active': False  # Conta inativa para testes
        }
    ]
    
    accounts = []
    for data in accounts_data:
        # Encontrar domínio
        domain = next((d for d in domains if d.name == data['domain_name']), None)
        if not domain:
            continue
        
        email_address = f"{data['local_part']}@{data['domain_name']}"
        
        # Verificar se conta já existe
        existing = EmailAccount.query.filter_by(email_address=email_address).first()
        if not existing:
            account_data = data.copy()
            account_data['domain_id'] = domain.id
            account_data['email_address'] = email_address
            del account_data['domain_name']
            
            account = EmailAccount(**account_data)
            # Set mock encrypted password
            account.smtp_password = 'mock_encrypted_password_for_development'
            db.session.add(account)
            accounts.append(account)
        else:
            accounts.append(existing)
    
    db.session.commit()
    click.echo(f'   ✅ Contas Email: {len(accounts)} criadas/verificadas')
    
    # 3. CRIAR TEMPLATES DE EMAIL
    templates_data = [
        {
            'domain_name': 'alitools.pt',
            'template_key': 'encomenda_confirmacao',
            'template_name': 'Confirmação de Encomenda',
            'subject': '✅ Encomenda #{encomenda_numero} Confirmada - AliTools',
            'html_body': '''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Confirmação de Encomenda</title>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; }
        .header { background: linear-gradient(135deg, #FFA500, #FF8C00); color: white; padding: 30px 20px; text-align: center; border-radius: 10px 10px 0 0; }
        .content { padding: 30px 20px; background: white; border: 1px solid #ddd; }
        .highlight { background: #fff3cd; padding: 15px; border-radius: 8px; border-left: 4px solid #FFA500; margin: 20px 0; }
        .footer { background: #f8f9fa; padding: 20px; text-align: center; font-size: 12px; color: #666; border-radius: 0 0 10px 10px; }
        .button { display: inline-block; background: #FFA500; color: white; padding: 12px 25px; text-decoration: none; border-radius: 6px; font-weight: bold; }
        .order-details { background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0; }
        .order-item { display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #eee; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🛠️ AliTools</h1>
        <p>Confirmação de Encomenda</p>
    </div>
    <div class="content">
        <h2>Olá {{cliente_nome}},</h2>
        <p>A sua encomenda foi <strong>confirmada com sucesso</strong> e está a ser processada!</p>
        
        <div class="highlight">
            <h3>📋 Detalhes da Encomenda:</h3>
            <div class="order-details">
                <div class="order-item">
                    <strong>Número da Encomenda:</strong>
                    <span>#{{encomenda_numero}}</span>
                </div>
                <div class="order-item">
                    <strong>Data:</strong>
                    <span>{{data}}</span>
                </div>
                <div class="order-item">
                    <strong>Total:</strong>
                    <span style="color: #FFA500; font-weight: bold;">€{{total}}</span>
                </div>
                <div class="order-item">
                    <strong>Pagamento:</strong>
                    <span>{{metodo_pagamento}}</span>
                </div>
                <div class="order-item">
                    <strong>Estado:</strong>
                    <span style="color: green;">✅ Confirmado</span>
                </div>
            </div>
        </div>
        
        <p>📦 <strong>Próximos passos:</strong></p>
        <ul>
            <li>Processamento: 1-2 dias úteis</li>
            <li>Envio: Receberá tracking por email</li>
            <li>Entrega: 3-5 dias úteis (Portugal Continental)</li>
        </ul>
        
        <div style="text-align: center; margin: 30px 0;">
            <a href="https://alitools.pt/encomendas/{{encomenda_numero}}" class="button">
                👀 Acompanhar Encomenda
            </a>
        </div>
        
        <hr>
        
        <p><strong>Precisa de ajuda?</strong></p>
        <p>📧 Email: <a href="mailto:suporte@alitools.pt">suporte@alitools.pt</a><br>
        📞 Telefone: +351 XXX XXX XXX<br>
        ⏰ Horário: 9h-18h (dias úteis)</p>
        
        <p>Obrigado pela sua confiança na AliTools!</p>
    </div>
    <div class="footer">
        <p>© 2025 AliTools - Ferramentas Profissionais para Profissionais</p>
        <p>Este email foi enviado para {{cliente_email}}</p>
        <p>🌐 <a href="https://alitools.pt">www.alitools.pt</a> | 📱 Siga-nos nas redes sociais</p>
    </div>
</body>
</html>''',
            'text_body': '''AliTools - Confirmação de Encomenda

Olá {{cliente_nome}},

A sua encomenda foi confirmada com sucesso!

Detalhes da Encomenda:
- Número: #{{encomenda_numero}}
- Data: {{data}}
- Total: €{{total}}
- Pagamento: {{metodo_pagamento}}
- Estado: ✅ Confirmado

Próximos passos:
- Processamento: 1-2 dias úteis
- Envio: Receberá tracking por email
- Entrega: 3-5 dias úteis

Acompanhar: https://alitools.pt/encomendas/{{encomenda_numero}}

Suporte: suporte@alitools.pt | +351 XXX XXX XXX

Obrigado pela sua confiança!
AliTools - Ferramentas Profissionais
www.alitools.pt''',
            'category': 'encomendas',
            'variables': 'cliente_nome,encomenda_numero,total,data,metodo_pagamento,cliente_email',
            'is_active': True,
            'version': 1
        },
        {
            'domain_name': 'alitools.pt',
            'template_key': 'boas_vindas_b2b',
            'template_name': 'Boas-vindas Cliente B2B',
            'subject': '🎉 Bem-vindo à AliTools, {{cliente_nome}}! Conta B2B Ativada',
            'html_body': '''<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; }
        .header { background: linear-gradient(135deg, #1E40AF, #3B82F6); color: white; padding: 40px 20px; text-align: center; }
        .content { padding: 30px 20px; }
        .benefits { background: #f0f7ff; padding: 20px; border-radius: 8px; margin: 20px 0; }
        .contact-box { background: #fff3cd; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #FFA500; }
        .cta-button { display: inline-block; background: #FFA500; color: white; padding: 15px 30px; text-decoration: none; border-radius: 6px; font-weight: bold; margin: 10px 5px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🎉 Bem-vindo à AliTools!</h1>
        <p>A sua parceria B2B começa agora</p>
    </div>
    <div class="content">
        <h2>Olá {{cliente_nome}},</h2>
        <p>É com grande prazer que damos as boas-vindas à <strong>AliTools</strong> - a sua nova parceria em ferramentas profissionais!</p>
        
        <div class="benefits">
            <h3>🚀 Benefícios da sua conta B2B:</h3>
            <ul>
                <li>✅ <strong>Preços especiais B2B</strong> - Descontos até 25%</li>
                <li>✅ <strong>Gestor de conta dedicado</strong> - Suporte personalizado</li>
                <li>✅ <strong>Condições de pagamento flexíveis</strong> - 30/60/90 dias</li>
                <li>✅ <strong>Entregas prioritárias</strong> - 24h em Lisboa/Porto</li>
                <li>✅ <strong>Catálogo B2B exclusivo</strong> - 5000+ produtos</li>
                <li>✅ <strong>Orçamentos personalizados</strong> - Para projetos grandes</li>
            </ul>
        </div>
        
        <h3>📋 Próximos Passos:</h3>
        <ol>
            <li><strong>Explore o catálogo B2B</strong> - Produtos exclusivos</li>
            <li><strong>Configure as suas preferências</strong> - Categorias favoritas</li>
            <li><strong>Contacte o seu gestor</strong> - Apresentação personalizada</li>
            <li><strong>Faça a primeira encomenda</strong> - Desconto 15% welcome</li>
        </ol>
        
        <div class="contact-box">
            <h4>👤 O seu Gestor de Conta:</h4>
            <p><strong>Nome:</strong> {{gestor_nome}}<br>
            <strong>Email:</strong> {{gestor_email}}<br>
            <strong>Telefone Direto:</strong> {{gestor_telefone}}<br>
            <strong>Horário:</strong> 9h-18h (dias úteis)</p>
        </div>
        
        <div style="text-align: center; margin: 30px 0;">
            <a href="{{link_catalogo_b2b}}" class="cta-button">
                🛒 Explorar Catálogo B2B
            </a>
            <a href="{{link_contacto_gestor}}" class="cta-button">
                📞 Contactar Gestor
            </a>
        </div>
        
        <p><strong>Oferta Especial de Boas-Vindas:</strong><br>
        🎁 Use o código <code style="background: #f0f7ff; padding: 2px 6px; border-radius: 4px;"><strong>WELCOME15</strong></code> 
        na sua primeira encomenda e tenha <strong>15% de desconto adicional</strong>!</p>
        
        <hr>
        
        <p>Estamos ansiosos por trabalhar consigo e contribuir para o sucesso dos seus projetos!</p>
        <p>Bem-vindo à família AliTools! 🛠️</p>
    </div>
</body>
</html>''',
            'text_body': '''Bem-vindo à AliTools, {{cliente_nome}}!

A sua conta B2B foi ativada com sucesso!

Benefícios B2B:
- Preços especiais com descontos até 25%
- Gestor de conta dedicado
- Condições de pagamento flexíveis
- Entregas prioritárias
- Catálogo B2B exclusivo

O seu Gestor de Conta:
Nome: {{gestor_nome}}
Email: {{gestor_email}}
Telefone: {{gestor_telefone}}

Oferta Welcome: Use WELCOME15 para 15% desconto!

Catálogo B2B: {{link_catalogo_b2b}}
Contacto Gestor: {{link_contacto_gestor}}

Bem-vindo à família AliTools!''',
            'category': 'marketing',
            'variables': 'cliente_nome,gestor_nome,gestor_email,gestor_telefone,link_catalogo_b2b,link_contacto_gestor',
            'is_active': True,
            'version': 1
        },
        {
            'domain_name': 'artnshine.pt',
            'template_key': 'portfolio_response',
            'template_name': 'Resposta Inquiry Portfolio',
            'subject': '🎨 Obrigado pelo interesse - {{projeto_tipo}}',
            'html_body': '''<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: 'Georgia', serif; line-height: 1.7; color: #444; max-width: 600px; margin: 0 auto; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px 20px; text-align: center; }
        .content { padding: 30px 20px; background: white; }
        .project-box { background: #f8f9fa; border-left: 4px solid #667eea; padding: 20px; margin: 20px 0; border-radius: 0 8px 8px 0; }
        .signature { margin-top: 40px; border-top: 2px solid #eee; padding-top: 20px; font-style: italic; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🎨 Art & Shine</h1>
        <p>Desenvolvimento Web & Design Criativo</p>
    </div>
    <div class="content">
        <h2>Olá {{cliente_nome}},</h2>
        
        <p>Muito obrigado pelo seu interesse no meu trabalho! É sempre um prazer receber propostas de projetos criativos.</p>
        
        <div class="project-box">
            <h3>📋 Projeto Solicitado:</h3>
            <p><strong>Tipo:</strong> {{projeto_tipo}}</p>
            <p><strong>Âmbito:</strong> {{projeto_ambito}}</p>
            <p><strong>Prazo desejado:</strong> {{projeto_prazo}}</p>
            <p><strong>Orçamento indicativo:</strong> {{projeto_orcamento}}</p>
        </div>
        
        <p>Vou analisar cuidadosamente os detalhes fornecidos e preparar uma <strong>proposta personalizada</strong> que atenda às suas necessidades específicas.</p>
        
        <h3>🚀 Próximos Passos:</h3>
        <ol>
            <li><strong>Análise detalhada</strong> - Estudo dos requisitos (24-48h)</li>
            <li><strong>Proposta técnica</strong> - Abordagem e cronograma</li>
            <li><strong>Orçamento final</strong> - Valores transparentes</li>
            <li><strong>Reunião de alinhamento</strong> - Esclarecimentos</li>
        </ol>
        
        <p>📞 <strong>Entretanto, se desejar esclarecer algum ponto:</strong></p>
        <ul>
            <li>📧 Email: info@artnshine.pt</li>
            <li>📱 WhatsApp: +351 XXX XXX XXX</li>
            <li>🌐 Portfolio: <a href="https://artnshine.pt">artnshine.pt</a></li>
        </ul>
        
        <p>Espero que possamos trabalhar juntos neste projeto! ✨</p>
        
        <div class="signature">
            <p>Com os melhores cumprimentos,<br>
            <strong>Art & Shine</strong><br>
            <em>Desenvolvimento Web & Design Criativo</em></p>
        </div>
    </div>
</body>
</html>''',
            'text_body': '''Olá {{cliente_nome}},

Obrigado pelo interesse no meu trabalho!

Projeto Solicitado:
- Tipo: {{projeto_tipo}}
- Âmbito: {{projeto_ambito}}
- Prazo: {{projeto_prazo}}
- Orçamento: {{projeto_orcamento}}

Próximos passos:
1. Análise detalhada (24-48h)
2. Proposta técnica
3. Orçamento final
4. Reunião de alinhamento

Contactos:
Email: info@artnshine.pt
WhatsApp: +351 XXX XXX XXX
Portfolio: https://artnshine.pt

Cumprimentos,
Art & Shine''',
            'category': 'portfolio',
            'variables': 'cliente_nome,projeto_tipo,projeto_ambito,projeto_prazo,projeto_orcamento',
            'is_active': True,
            'version': 1
        },
        {
            'domain_name': 'sendcraft.local',
            'template_key': 'teste_sendcraft',
            'template_name': 'Template Teste SendCraft',
            'subject': '🚀 SendCraft - Template de Teste {{nome_teste}}',
            'html_body': '''<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; color: #333; max-width: 600px; margin: 0 auto; }
        .header { background: #FFA500; color: white; padding: 20px; text-align: center; }
        .content { padding: 20px; }
        .test-box { background: #f0f7ff; padding: 15px; border-radius: 8px; margin: 15px 0; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 SendCraft Email Manager</h1>
        <p>Sistema de Gestão de Emails</p>
    </div>
    <div class="content">
        <h2>Template de Teste</h2>
        <p>Olá {{destinatario_nome}},</p>
        
        <div class="test-box">
            <h3>📋 Informações do Teste:</h3>
            <p><strong>Nome do Teste:</strong> {{nome_teste}}</p>
            <p><strong>Data/Hora:</strong> {{data_hora}}</p>
            <p><strong>Versão:</strong> {{versao_sendcraft}}</p>
            <p><strong>Ambiente:</strong> {{ambiente}}</p>
        </div>
        
        <p>Este é um email de teste gerado pelo SendCraft Email Manager para validar o funcionamento do sistema.</p>
        
        <p>✅ Se recebeu este email, significa que:</p>
        <ul>
            <li>A configuração SMTP está correta</li>
            <li>O template rendering funciona</li>
            <li>As variáveis são substituídas corretamente</li>
            <li>O sistema está operacional</li>
        </ul>
        
        <hr>
        <p><small>SendCraft Email Manager - Sistema de gestão de emails profissional</small></p>
    </div>
</body>
</html>''',
            'text_body': '''SendCraft Email Manager - Template de Teste

Olá {{destinatario_nome}},

Informações do Teste:
- Nome: {{nome_teste}}
- Data/Hora: {{data_hora}}
- Versão: {{versao_sendcraft}}
- Ambiente: {{ambiente}}

Este é um email de teste do SendCraft.

Se recebeu este email, o sistema está operacional!

SendCraft Email Manager''',
            'category': 'sistema',
            'variables': 'destinatario_nome,nome_teste,data_hora,versao_sendcraft,ambiente',
            'is_active': True,
            'version': 1
        }
    ]
    
    templates = []
    for data in templates_data:
        # Encontrar domínio
        domain = next((d for d in domains if d.name == data['domain_name']), None)
        if not domain:
            continue
        
        # Verificar se template já existe
        existing = EmailTemplate.query.filter_by(
            domain_id=domain.id, 
            template_key=data['template_key']
        ).first()
        
        if not existing:
            template_data = data.copy()
            template_data['domain_id'] = domain.id
            del template_data['domain_name']
            
            template = EmailTemplate(**template_data)
            db.session.add(template)
            templates.append(template)
        else:
            templates.append(existing)
    
    db.session.commit()
    click.echo(f'   ✅ Templates: {len(templates)} criados/verificados')
    
    # 4. CRIAR LOGS DE EXEMPLO (apenas para SQLite)
    if 'sqlite' in database_url:
        create_sample_logs(accounts, templates)
    else:
        click.echo('   ℹ️ Logs: Mantidos dados MySQL existentes')
    
    click.echo('\n🎉 Seed data concluído!')
    click.echo('=' * 50)
    click.echo(f'📊 Resumo:')
    click.echo(f'   • {len(domains)} domínios ({sum(1 for d in domains if d.is_active)} ativos)')
    click.echo(f'   • {len(accounts)} contas email ({sum(1 for a in accounts if a.is_active)} ativas)')
    click.echo(f'   • {len(templates)} templates ({sum(1 for t in templates if t.is_active)} ativos)')
    click.echo('=' * 50)
    click.echo('✅ SendCraft pronto para desenvolvimento!')


def create_sample_logs(accounts, templates):
    """Cria logs de exemplo para os últimos 30 dias"""
    click.echo('📊 Criando logs de exemplo...')
    
    # Dados para logs realistas
    recipients = [
        'joao.silva@empresa.pt', 'maria.santos@loja.pt', 'admin@site.com',
        'cliente1@gmail.com', 'user@company.pt', 'test@domain.com',
        'pedro.costa@factory.pt', 'ana.ferreira@shop.pt', 'info@business.pt',
        'carlos.mendes@corp.com', 'rita.oliveira@store.pt', 'support@app.io'
    ]
    
    subjects_templates = {
        'encomenda_confirmacao': [
            'Encomenda #ALI-{} Confirmada - AliTools',
            'Confirmação Encomenda #{} - Processamento Iniciado'
        ],
        'boas_vindas_b2b': [
            'Bem-vindo à AliTools, {}!',
            'Conta B2B Ativada com Sucesso!'
        ],
        'portfolio_response': [
            'Obrigado pelo interesse - Website Corporativo',
            'Proposta Portfolio - Desenvolvimento E-commerce'
        ],
        'teste_sendcraft': [
            'SendCraft - Teste Sistema #{}',
            'Validação Template - SendCraft OK'
        ]
    }
    
    # Estatísticas realistas de status
    status_weights = {
        EmailStatus.SENT: 0.40,      # 40% sent
        EmailStatus.DELIVERED: 0.45, # 45% delivered  
        EmailStatus.OPENED: 0.10,    # 10% opened
        EmailStatus.FAILED: 0.03,    # 3% failed
        EmailStatus.BOUNCED: 0.02    # 2% bounced
    }
    
    statuses = list(status_weights.keys())
    weights = list(status_weights.values())
    
    logs_created = 0
    
    # Criar logs para últimos 30 dias
    for days_ago in range(30):
        # Número de emails por dia (variação realista)
        if days_ago < 7:  # Última semana - mais atividade
            emails_per_day = random.randint(10, 25)
        elif days_ago < 14: # Semana anterior
            emails_per_day = random.randint(5, 15)
        else: # Mais antigo
            emails_per_day = random.randint(2, 10)
        
        base_date = datetime.utcnow() - timedelta(days=days_ago)
        
        for _ in range(emails_per_day):
            # Data aleatória no dia
            hours = random.randint(8, 18)  # Horário comercial principalmente
            minutes = random.randint(0, 59)
            log_date = base_date.replace(hour=hours, minute=minutes, second=0, microsecond=0)
            
            # Selecionar conta aleatória (preferência pelas ativas)
            active_accounts = [a for a in accounts if a.is_active]
            if active_accounts and random.random() < 0.9:  # 90% emails de contas ativas
                account = random.choice(active_accounts)
            else:
                account = random.choice(accounts)
            
            # Template (70% com template, 30% sem)
            if templates and random.random() < 0.7:
                template = random.choice(templates)
                # Subject baseado no template
                template_subjects = subjects_templates.get(template.template_key, ['Email Genérico'])
                if '{}' in template_subjects[0]:
                    subject = template_subjects[0].format(random.randint(1000, 9999))
                else:
                    subject = random.choice(template_subjects)
            else:
                template = None
                generic_subjects = [
                    'Informação Importante', 'Newsletter Mensal', 'Atualização de Conta',
                    'Confirmação de Registo', 'Recuperação de Password', 'Notificação Sistema'
                ]
                subject = random.choice(generic_subjects)
            
            # Recipient e status
            recipient = random.choice(recipients)
            status = random.choices(statuses, weights=weights, k=1)[0]
            
            # SMTP response realista
            if status in [EmailStatus.SENT, EmailStatus.DELIVERED]:
                smtp_responses = ['250 OK', '250 Message accepted', '250 2.0.0 Ok: queued']
                smtp_response = random.choice(smtp_responses)
            elif status == EmailStatus.FAILED:
                smtp_responses = ['550 Mailbox unavailable', '553 Invalid recipient', '421 Service not available']
                smtp_response = random.choice(smtp_responses)
            elif status == EmailStatus.BOUNCED:
                smtp_responses = ['550 User unknown', '554 Delivery failed', '552 Message size exceeds limit']
                smtp_response = random.choice(smtp_responses)
            else:
                smtp_response = None
            
            # Criar log
            log = EmailLog(
                account_id=account.id,
                template_id=template.id if template else None,
                recipient_email=recipient,
                sender_email=account.email_address,
                subject=subject,
                status=status,
                message_id=f'msg-{logs_created+1}-{int(log_date.timestamp())}@{account.domain.name}',
                smtp_response=smtp_response,
                created_at=log_date,
                updated_at=log_date
            )
            
            db.session.add(log)
            logs_created += 1
    
    db.session.commit()
    click.echo(f'   ✅ Logs: {logs_created} emails de exemplo criados')