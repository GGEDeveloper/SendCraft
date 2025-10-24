# 🚀 SendCraft Phase 17A: Development - E-commerce Integration

**Você é um desenvolvedor full-stack sênior responsável por criar o E-commerce Simulator que integra com a API SendCraft. Sua missão é construir toda a infraestrutura backend, frontend e serviços de integração.**

## 🎯 OBJETIVO PHASE 17A
Desenvolver o **E-commerce Simulator completo** sem testes de browser. Foco na **implementação, integração API e funcionalidades core**.

## 📂 CONTEXTO TÉCNICO
- **SendCraft API:** Production-ready em `http://localhost:5000/api/v1`
- **Conta SendCraft:** geral@artnshine.pt
- **Phase 16:** 100% completa (API testada e validada)
- **Target Port:** 5001 (para não conflitar com SendCraft:5000)

---

## 📋 EXECUÇÃO PHASE 17A

### 🛠️ **FASE 1: SETUP DO PROJETO (30 min)**

#### 1.1 Criar Estrutura Completa
```bash
# Criar projeto fora do SendCraft
mkdir -p ecommerce_simulator
cd ecommerce_simulator

# Estrutura de diretórios
mkdir -p {models,services,templates/shop,static/{css,js,assets}}
mkdir -p docs/integration

# Arquivos principais
touch app.py config.py requirements.txt .env
touch models/{__init__.py,customer.py,product.py,order.py}
touch services/{__init__.py,sendcraft_client.py,pdf_generator.py}
touch templates/shop/{base.html,index.html,dashboard.html,marketing.html}

echo "✅ Estrutura do projeto criada"
```

#### 1.2 Dependências e Ambiente
```bash
# requirements.txt
cat > requirements.txt << 'EOF'
Flask==2.3.2
Flask-SQLAlchemy==3.0.5
requests==2.31.0
reportlab==4.0.4
Faker==19.3.0
python-dotenv==1.0.0
Jinja2==3.1.2
Werkzeug==2.3.6
EOF

# Ambiente virtual
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

echo "✅ Ambiente Python configurado"
```

#### 1.3 Configuração Base
```python
# config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'ecommerce-simulator-2025'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///ecommerce.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # SendCraft Integration
    SENDCRAFT_API_BASE = 'http://localhost:5000/api/v1'
    SENDCRAFT_API_KEY = 'YOUR_API_KEY_HERE'  # Será obtida depois
    SENDCRAFT_DOMAIN = 'artnshine.pt'
    SENDCRAFT_ACCOUNT = 'geral'
    
    # E-commerce
    COMPANY_NAME = 'TechStore Demo'
    COMPANY_EMAIL = 'geral@artnshine.pt'
    SHOP_PORT = 5001

# .env (template)
cat > .env << 'EOF'
SECRET_KEY=ecommerce-simulator-secret-2025
SENDCRAFT_API_KEY=your_sendcraft_api_key_here
DATABASE_URL=sqlite:///ecommerce.db
FLASK_ENV=development
EOF
```

---

### 🗄️ **FASE 2: MODELOS DE DADOS (45 min)**

#### 2.1 Base de Dados
```python
# models/__init__.py
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# models/customer.py
from . import db
from datetime import datetime

class Customer(db.Model):
    __tablename__ = 'customers'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), nullable=False, unique=True)
    phone = db.Column(db.String(50))
    address = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    orders = db.relationship('Order', backref='customer', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'address': self.address
        }

# models/product.py
from . import db
from datetime import datetime

class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(100))
    stock = db.Column(db.Integer, default=0)
    image_url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'category': self.category,
            'stock': self.stock
        }

# models/order.py
from . import db
from datetime import datetime
import uuid

class Order(db.Model):
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(50), unique=True, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), default='pending')
    
    # Email tracking
    confirmation_email_sent = db.Column(db.Boolean, default=False)
    confirmation_message_id = db.Column(db.String(100))
    shipping_email_sent = db.Column(db.Boolean, default=False)
    shipping_message_id = db.Column(db.String(100))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    shipped_at = db.Column(db.DateTime)
    
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')
    
    @classmethod
    def generate_order_number(cls):
        prefix = datetime.utcnow().strftime('%Y%m%d')
        suffix = str(uuid.uuid4())[:8].upper()
        return f"TS-{prefix}-{suffix}"
    
    def calculate_total(self):
        return sum(item.quantity * item.price for item in self.items)
    
    def to_dict(self):
        return {
            'id': self.id,
            'order_number': self.order_number,
            'customer': self.customer.to_dict() if self.customer else None,
            'total_amount': self.total_amount,
            'status': self.status,
            'items': [item.to_dict() for item in self.items],
            'created_at': self.created_at.isoformat(),
            'confirmation_email_sent': self.confirmation_email_sent,
            'shipping_email_sent': self.shipping_email_sent
        }

class OrderItem(db.Model):
    __tablename__ = 'order_items'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    
    product = db.relationship('Product')
    
    def to_dict(self):
        return {
            'id': self.id,
            'product': self.product.to_dict() if self.product else None,
            'quantity': self.quantity,
            'price': self.price,
            'subtotal': self.quantity * self.price
        }
```

---

### 📧 **FASE 3: CLIENTE SENDCRAFT API (60 min)**

#### 3.1 Integração Completa SendCraft
```python
# services/sendcraft_client.py
import requests
import base64
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class SendCraftClient:
    """Cliente robusto para SendCraft API"""
    
    def __init__(self, api_key: str, base_url: str, domain: str, account: str):
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.domain = domain
        self.account = account
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        self.timeout = 30
    
    def _make_request(self, method: str, endpoint: str, data: dict = None) -> Tuple[bool, dict]:
        """Fazer requisição com retry logic"""
        url = f"{self.base_url}{endpoint}"
        
        for attempt in range(3):  # 3 tentativas
            try:
                if method.upper() == 'POST':
                    response = requests.post(url, headers=self.headers, json=data, timeout=self.timeout)
                elif method.upper() == 'GET':
                    response = requests.get(url, headers=self.headers, timeout=self.timeout)
                else:
                    return False, {'error': f'Método {method} não suportado'}
                
                response.raise_for_status()
                return True, response.json()
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"Tentativa {attempt + 1} falhou: {e}")
                if attempt == 2:  # Última tentativa
                    return False, {
                        'error': str(e),
                        'status_code': getattr(e.response, 'status_code', 0),
                        'attempts': 3
                    }
        
        return False, {'error': 'Máximo de tentativas excedido'}
    
    def test_connection(self) -> Tuple[bool, dict]:
        """Testar conectividade com SendCraft"""
        try:
            # Testar health endpoint primeiro
            health_url = self.base_url.replace('/api/v1', '/api/v1/health')
            response = requests.get(health_url, timeout=10)
            
            if response.status_code == 200:
                return True, {'message': 'Conexão com SendCraft OK', 'health': response.json()}
            else:
                return False, {'error': f'Health check falhou: {response.status_code}'}
                
        except Exception as e:
            return False, {'error': f'Erro de conectividade: {str(e)}'}
    
    def send_order_confirmation(self, order_data: dict, pdf_content: bytes = None) -> Tuple[bool, dict]:
        """Enviar confirmação de encomenda com fatura PDF"""
        
        # Preparar anexos
        attachments = []
        if pdf_content:
            pdf_base64 = base64.b64encode(pdf_content).decode('utf-8')
            attachments.append({
                'filename': f"fatura-{order_data['order_number']}.pdf",
                'content_type': 'application/pdf',
                'content': pdf_base64
            })
        
        # Preparar email
        email_data = {
            'to': [order_data['customer_email']],
            'subject': f"✅ Confirmação Encomenda {order_data['order_number']} - TechStore",
            'html': self._render_order_confirmation_html(order_data),
            'text': self._render_order_confirmation_text(order_data),
            'domain': self.domain,
            'account': self.account,
            'from_name': 'TechStore',
            'attachments': attachments,
            'idempotency_key': f"order-confirmation-{order_data['order_number']}"
        }
        
        logger.info(f"Enviando confirmação de encomenda {order_data['order_number']} para {order_data['customer_email']}")
        success, result = self._make_request('POST', '/send', email_data)
        
        if success:
            logger.info(f"Email de confirmação enviado com sucesso: {result.get('message_id')}")
        else:
            logger.error(f"Falha no envio da confirmação: {result}")
        
        return success, result
    
    def send_shipping_notification(self, order_data: dict, tracking_number: str) -> Tuple[bool, dict]:
        """Enviar notificação de envio com tracking"""
        
        email_data = {
            'to': [order_data['customer_email']],
            'subject': f"📦 Encomenda {order_data['order_number']} Enviada - Tracking: {tracking_number}",
            'html': self._render_shipping_html(order_data, tracking_number),
            'text': self._render_shipping_text(order_data, tracking_number),
            'domain': self.domain,
            'account': self.account,
            'from_name': 'TechStore Envios',
            'idempotency_key': f"shipping-{order_data['order_number']}-{tracking_number}"
        }
        
        logger.info(f"Enviando notificação de envio {order_data['order_number']} - tracking: {tracking_number}")
        success, result = self._make_request('POST', '/send', email_data)
        
        if success:
            logger.info(f"Email de envio enviado com sucesso: {result.get('message_id')}")
        else:
            logger.error(f"Falha no envio da notificação: {result}")
        
        return success, result
    
    def send_marketing_campaign(self, recipients: List[str], campaign_data: dict) -> Tuple[bool, dict]:
        """Enviar campanha de marketing em bulk"""
        
        email_data = {
            'to': recipients,
            'subject': campaign_data.get('subject', '🎯 Oferta Especial TechStore'),
            'html': self._render_marketing_html(campaign_data),
            'text': self._render_marketing_text(campaign_data),
            'domain': self.domain,
            'account': self.account,
            'from_name': 'TechStore Marketing',
            'bulk': True,
            'idempotency_key': f"campaign-{campaign_data.get('campaign_id', datetime.now().isoformat())}"
        }
        
        logger.info(f"Enviando campanha para {len(recipients)} destinatários")
        success, result = self._make_request('POST', '/send', email_data)
        
        if success:
            logger.info(f"Campanha enviada com sucesso: {result.get('message_id')}")
        else:
            logger.error(f"Falha no envio da campanha: {result}")
        
        return success, result
    
    def get_email_status(self, message_id: str) -> Tuple[bool, dict]:
        """Verificar status de email"""
        success, result = self._make_request('GET', f'/send/{message_id}/status')
        return success, result
    
    def _render_order_confirmation_html(self, order_data: dict) -> str:
        """HTML da confirmação de encomenda"""
        items_html = ""
        for item in order_data['items']:
            items_html += f"""
            <tr>
                <td style="padding: 10px; border-bottom: 1px solid #eee;">{item['product_name']}</td>
                <td style="padding: 10px; border-bottom: 1px solid #eee; text-align: center;">{item['quantity']}</td>
                <td style="padding: 10px; border-bottom: 1px solid #eee; text-align: right;">€{item['price']:.2f}</td>
                <td style="padding: 10px; border-bottom: 1px solid #eee; text-align: right;">€{item['subtotal']:.2f}</td>
            </tr>
            """
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Confirmação de Encomenda</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; margin: 0; padding: 20px; background-color: #f4f4f4;">
            <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 8px;">
                
                <div style="text-align: center; margin-bottom: 30px;">
                    <h1 style="color: #333; margin: 0;">TechStore</h1>
                    <p style="color: #666;">Tecnologia de Confiança</p>
                </div>
                
                <div style="background-color: #4CAF50; color: white; padding: 15px; text-align: center; border-radius: 5px; margin-bottom: 20px;">
                    <h2 style="margin: 0;">✅ Encomenda Confirmada!</h2>
                </div>
                
                <p>Olá <strong>{order_data['customer_name']}</strong>,</p>
                <p>Obrigado pela sua compra! A sua encomenda foi confirmada e está a ser processada.</p>
                
                <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <h3 style="margin: 0 0 10px 0;">Detalhes da Encomenda</h3>
                    <p><strong>Número:</strong> {order_data['order_number']}</p>
                    <p><strong>Data:</strong> {order_data['order_date']}</p>
                    <p><strong>Total:</strong> €{order_data['total']:.2f}</p>
                </div>
                
                <h3>Items da Encomenda</h3>
                <table style="width: 100%; border-collapse: collapse;">
                    <thead>
                        <tr style="background-color: #f8f9fa;">
                            <th style="padding: 10px; text-align: left;">Produto</th>
                            <th style="padding: 10px; text-align: center;">Qtd</th>
                            <th style="padding: 10px; text-align: right;">Preço</th>
                            <th style="padding: 10px; text-align: right;">Subtotal</th>
                        </tr>
                    </thead>
                    <tbody>
                        {items_html}
                    </tbody>
                    <tfoot>
                        <tr style="background-color: #f8f9fa; font-weight: bold;">
                            <td colspan="3" style="padding: 15px; text-align: right;">TOTAL:</td>
                            <td style="padding: 15px; text-align: right;">€{order_data['total']:.2f}</td>
                        </tr>
                    </tfoot>
                </table>
                
                <div style="background-color: #e3f2fd; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <h3>📦 Próximos Passos</h3>
                    <p>1. Processamento da encomenda (1-2 dias úteis)</p>
                    <p>2. Preparação e embalamento</p>
                    <p>3. Envio com número de tracking</p>
                    <p>4. Entrega no endereço indicado</p>
                </div>
                
                <div style="text-align: center; margin: 30px 0; color: #666;">
                    <p>Em caso de dúvidas: geral@artnshine.pt | +351 123 456 789</p>
                </div>
                
            </div>
        </body>
        </html>
        """
    
    def _render_order_confirmation_text(self, order_data: dict) -> str:
        """Texto da confirmação"""
        items_text = "\\n".join([
            f"- {item['product_name']} x{item['quantity']} - €{item['subtotal']:.2f}"
            for item in order_data['items']
        ])
        
        return f"""
✅ ENCOMENDA CONFIRMADA!

Olá {order_data['customer_name']},

Obrigado pela sua compra! A sua encomenda {order_data['order_number']} foi confirmada.

DETALHES:
- Número: {order_data['order_number']}
- Data: {order_data['order_date']}
- Total: €{order_data['total']:.2f}

ITEMS:
{items_text}

PRÓXIMOS PASSOS:
1. Processamento (1-2 dias úteis)
2. Preparação e embalamento
3. Envio com tracking
4. Entrega

Contactos: geral@artnshine.pt | +351 123 456 789

TechStore - Tecnologia de Confiança
        """
    
    def _render_shipping_html(self, order_data: dict, tracking_number: str) -> str:
        """HTML da notificação de envio"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Encomenda Enviada</title>
        </head>
        <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 8px;">
                
                <div style="text-align: center; margin-bottom: 30px;">
                    <h1 style="color: #333;">TechStore</h1>
                </div>
                
                <div style="background-color: #2196F3; color: white; padding: 15px; text-align: center; border-radius: 5px;">
                    <h2 style="margin: 0;">📦 Encomenda Enviada!</h2>
                </div>
                
                <p>Olá <strong>{order_data['customer_name']}</strong>,</p>
                <p>A sua encomenda <strong>{order_data['order_number']}</strong> foi enviada!</p>
                
                <div style="background-color: #e8f5e8; padding: 20px; border-radius: 5px; text-align: center; margin: 20px 0;">
                    <h3>📍 Número de Tracking</h3>
                    <div style="font-family: monospace; font-size: 18px; font-weight: bold; color: #2e7d32;">
                        {tracking_number}
                    </div>
                </div>
                
                <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px;">
                    <h3>🚚 Informações de Envio</h3>
                    <p><strong>Transportadora:</strong> CTT Express</p>
                    <p><strong>Prazo:</strong> 2-3 dias úteis</p>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="https://track.ctt.pt/tracking?number={tracking_number}" 
                       style="background-color: #4CAF50; color: white; padding: 15px 25px; text-decoration: none; border-radius: 5px;">
                        🔍 Acompanhar Encomenda
                    </a>
                </div>
                
            </div>
        </body>
        </html>
        """
    
    def _render_shipping_text(self, order_data: dict, tracking_number: str) -> str:
        """Texto da notificação de envio"""
        return f"""
📦 ENCOMENDA ENVIADA!

Olá {order_data['customer_name']},

A sua encomenda {order_data['order_number']} foi enviada!

TRACKING: {tracking_number}

Transportadora: CTT Express
Prazo: 2-3 dias úteis

Acompanhe: https://track.ctt.pt/tracking?number={tracking_number}

TechStore - Tecnologia de Confiança
        """
    
    def _render_marketing_html(self, campaign_data: dict) -> str:
        """HTML da campanha de marketing"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>{campaign_data.get('title', 'Oferta TechStore')}</title>
        </head>
        <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 8px;">
                
                <div style="text-align: center; margin-bottom: 30px;">
                    <h1 style="color: #333;">TechStore</h1>
                </div>
                
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; text-align: center; border-radius: 10px;">
                    <h2 style="margin: 0;">🎯 {campaign_data.get('title', 'Oferta Especial!')}</h2>
                    <p style="margin: 10px 0 0 0;">{campaign_data.get('subtitle', 'Não perca!')}</p>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <div style="background-color: #ff4444; color: white; padding: 20px; border-radius: 10px; display: inline-block;">
                        <div style="font-size: 24px; font-weight: bold;">DESCONTO</div>
                        <div style="font-size: 36px; font-weight: bold;">{campaign_data.get('discount', '20')}%</div>
                    </div>
                </div>
                
                <p>{campaign_data.get('description', 'Aproveite esta oferta limitada!')}</p>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{campaign_data.get('cta_link', '#')}" 
                       style="background: #ff6b6b; color: white; padding: 15px 30px; text-decoration: none; border-radius: 25px;">
                        🛒 {campaign_data.get('cta_text', 'Ver Ofertas')}
                    </a>
                </div>
                
            </div>
        </body>
        </html>
        """
    
    def _render_marketing_text(self, campaign_data: dict) -> str:
        """Texto da campanha"""
        return f"""
🎯 {campaign_data.get('title', 'OFERTA TECHSTORE!')}

{campaign_data.get('description', 'Aproveite esta oferta limitada!')}

🔥 DESCONTO DE {campaign_data.get('discount', '20')}%!

{campaign_data.get('cta_link', 'Visite nossa loja')}

TechStore - Tecnologia de Confiança
        """
```

---

### 📄 **FASE 4: GERADOR DE PDF (30 min)**

#### 4.1 Serviço PDF Completo
```python
# services/pdf_generator.py
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from datetime import datetime
import io

class PDFGenerator:
    """Gerador de PDFs para faturas e documentos"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_styles()
    
    def _setup_styles(self):
        """Configurar estilos customizados"""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            textColor=colors.HexColor('#2c3e50'),
            alignment=TA_CENTER
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceAfter=12,
            textColor=colors.HexColor('#34495e')
        ))
    
    def generate_invoice(self, order_data: dict) -> bytes:
        """Gerar fatura em PDF"""
        buffer = io.BytesIO()
        
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        elements = []
        
        # Cabeçalho
        elements.append(Paragraph("TechStore", self.styles['CustomTitle']))
        elements.append(Paragraph("Tecnologia de Confiança", self.styles['Normal']))
        elements.append(Paragraph("Rua da Inovação, 123, Lisboa, Portugal", self.styles['Normal']))
        elements.append(Paragraph("NIF: 123456789 | geral@artnshine.pt", self.styles['Normal']))
        elements.append(Spacer(1, 1*cm))
        
        # Título da fatura
        elements.append(Paragraph(f"FATURA - {order_data['order_number']}", self.styles['CustomHeading']))
        elements.append(Spacer(1, 0.5*cm))
        
        # Informações
        info_data = [
            ['Data:', order_data['order_date']],
            ['Cliente:', order_data['customer_name']],
            ['Email:', order_data['customer_email']],
        ]
        
        info_table = Table(info_data, colWidths=[4*cm, 8*cm])
        info_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ]))
        
        elements.append(info_table)
        elements.append(Spacer(1, 1*cm))
        
        # Tabela de produtos
        elements.append(Paragraph("Detalhes da Encomenda", self.styles['CustomHeading']))
        
        table_data = [['Produto', 'Qtd', 'Preço', 'Subtotal']]
        
        for item in order_data['items']:
            table_data.append([
                item['product_name'],
                str(item['quantity']),
                f"€{item['price']:.2f}",
                f"€{item['subtotal']:.2f}"
            ])
        
        table_data.append(['', '', 'TOTAL:', f"€{order_data['total']:.2f}"])
        
        items_table = Table(table_data, colWidths=[8*cm, 2*cm, 3*cm, 3*cm])
        items_table.setStyle(TableStyle([
            # Cabeçalho
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            
            # Dados
            ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
            ('ALIGN', (2, 1), (-1, -1), 'RIGHT'),
            
            # Total
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#ecf0f1')),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('ALIGN', (2, -1), (-1, -1), 'RIGHT'),
            
            # Bordas
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        elements.append(items_table)
        elements.append(Spacer(1, 1*cm))
        
        # Informações de pagamento
        elements.append(Paragraph("Informações de Pagamento", self.styles['CustomHeading']))
        elements.append(Paragraph("Método: Transferência Bancária", self.styles['Normal']))
        elements.append(Paragraph("IBAN: PT50 0000 0000 0000 0000 0000 0", self.styles['Normal']))
        elements.append(Paragraph(f"Referência: {order_data['order_number']}", self.styles['Normal']))
        elements.append(Spacer(1, 0.5*cm))
        
        # Rodapé
        elements.append(Paragraph("Obrigado pela sua preferência!", self.styles['Normal']))
        elements.append(Paragraph("TechStore - A sua tecnologia de confiança", self.styles['Normal']))
        
        # Gerar PDF
        doc.build(elements)
        
        pdf_content = buffer.getvalue()
        buffer.close()
        
        return pdf_content
```

---

### 🌐 **FASE 5: APLICAÇÃO FLASK (90 min)**

#### 5.1 App Principal com Rotas
```python
# app.py
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from datetime import datetime, timedelta
import uuid
import logging
from faker import Faker

from config import Config
from models import db, Customer, Product, Order, OrderItem
from services.sendcraft_client import SendCraftClient
from services.pdf_generator import PDFGenerator

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

fake = Faker('pt_PT')

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    
    # Initialize services
    sendcraft = SendCraftClient(
        api_key=app.config['SENDCRAFT_API_KEY'],
        base_url=app.config['SENDCRAFT_API_BASE'],
        domain=app.config['SENDCRAFT_DOMAIN'],
        account=app.config['SENDCRAFT_ACCOUNT']
    )
    
    pdf_generator = PDFGenerator()
    
    @app.before_first_request
    def init_database():
        """Inicializar BD na primeira requisição"""
        db.create_all()
        
        # Criar produtos de exemplo
        if Product.query.count() == 0:
            products = [
                Product(name='Smartphone XYZ Pro', description='Smartphone de última geração', price=699.99, category='Smartphones', stock=25),
                Product(name='Laptop Gaming Elite', description='Laptop gaming RTX 4070', price=1899.99, category='Laptops', stock=10),
                Product(name='Headphones ANC Premium', description='Auscultadores noise cancelling', price=299.99, category='Áudio', stock=50),
                Product(name='Smartwatch Pro Sport', description='Relógio inteligente GPS', price=399.99, category='Wearables', stock=30),
                Product(name='Tablet Ultra 12"', description='Tablet 12 polegadas 4K', price=799.99, category='Tablets', stock=20),
                Product(name='Webcam 4K Ultra', description='Webcam profissional 4K', price=199.99, category='Acessórios', stock=40),
                Product(name='Teclado Mecânico RGB', description='Teclado gaming RGB', price=149.99, category='Acessórios', stock=60),
                Product(name='Monitor 27" 4K', description='Monitor profissional 4K', price=499.99, category='Monitores', stock=15),
            ]
            
            for product in products:
                db.session.add(product)
            
            db.session.commit()
            logger.info("Produtos de exemplo criados")
    
    @app.route('/')
    def index():
        """Página principal da loja"""
        products = Product.query.all()
        
        # Testar conexão com SendCraft
        connection_ok, connection_info = sendcraft.test_connection()
        
        return render_template('shop/index.html', 
                             products=products,
                             sendcraft_status=connection_ok,
                             sendcraft_info=connection_info)
    
    @app.route('/api/products')
    def api_products():
        """API para listar produtos"""
        products = Product.query.all()
        return jsonify([product.to_dict() for product in products])
    
    @app.route('/checkout', methods=['POST'])
    def checkout():
        """Processar checkout e criar encomenda"""
        try:
            data = request.get_json()
            
            # Validar dados
            if not data.get('customer') or not data.get('items'):
                return jsonify({'success': False, 'error': 'Dados incompletos'}), 400
            
            # Criar ou encontrar cliente
            customer_data = data['customer']
            customer = Customer.query.filter_by(email=customer_data['email']).first()
            
            if not customer:
                customer = Customer(
                    name=customer_data['name'],
                    email=customer_data['email'],
                    phone=customer_data.get('phone'),
                    address=customer_data.get('address')
                )
                db.session.add(customer)
                db.session.flush()
            
            # Criar encomenda
            order = Order(
                order_number=Order.generate_order_number(),
                customer_id=customer.id,
                total_amount=0,
                status='confirmed'
            )
            db.session.add(order)
            db.session.flush()
            
            # Adicionar items
            total = 0
            for item_data in data['items']:
                product = Product.query.get(item_data['product_id'])
                if not product:
                    continue
                
                # Verificar stock
                if product.stock < item_data['quantity']:
                    return jsonify({
                        'success': False, 
                        'error': f'Stock insuficiente para {product.name}'
                    }), 400
                
                item = OrderItem(
                    order_id=order.id,
                    product_id=product.id,
                    quantity=item_data['quantity'],
                    price=product.price
                )
                db.session.add(item)
                total += item.quantity * item.price
                
                # Atualizar stock
                product.stock -= item_data['quantity']
            
            order.total_amount = total
            db.session.commit()
            
            # Enviar email de confirmação
            email_success = send_order_confirmation_email(order, sendcraft, pdf_generator)
            
            logger.info(f"Encomenda {order.order_number} criada com sucesso")
            
            return jsonify({
                'success': True,
                'order_id': order.id,
                'order_number': order.order_number,
                'total': order.total_amount,
                'email_sent': email_success
            })
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erro no checkout: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/order/<int:order_id>')
    def order_detail(order_id):
        """Detalhes da encomenda"""
        order = Order.query.get_or_404(order_id)
        return render_template('shop/order_detail.html', order=order)
    
    @app.route('/order/<int:order_id>/ship', methods=['POST'])
    def ship_order(order_id):
        """Marcar encomenda como enviada"""
        try:
            order = Order.query.get_or_404(order_id)
            
            if order.status != 'confirmed':
                flash('Encomenda deve estar confirmada para ser enviada', 'warning')
                return redirect(url_for('dashboard'))
            
            # Gerar tracking
            tracking_number = f"CT{datetime.now().strftime('%Y%m%d')}{str(uuid.uuid4())[:6].upper()}"
            
            # Atualizar status
            order.status = 'shipped'
            order.shipped_at = datetime.utcnow()
            
            # Enviar email de notificação
            email_success = send_shipping_notification_email(order, tracking_number, sendcraft)
            
            if email_success:
                order.shipping_email_sent = True
                flash(f'Encomenda enviada! Email de notificação enviado com tracking: {tracking_number}', 'success')
            else:
                flash(f'Encomenda marcada como enviada, mas falha no email. Tracking: {tracking_number}', 'warning')
            
            db.session.commit()
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erro ao enviar encomenda: {e}")
            flash(f'Erro: {str(e)}', 'danger')
        
        return redirect(url_for('dashboard'))
    
    @app.route('/dashboard')
    def dashboard():
        """Dashboard administrativo"""
        # Estatísticas
        total_orders = Order.query.count()
        total_revenue = db.session.query(db.func.sum(Order.total_amount)).scalar() or 0
        pending_orders = Order.query.filter_by(status='confirmed').count()
        shipped_orders = Order.query.filter_by(status='shipped').count()
        
        # Encomendas recentes
        orders = Order.query.order_by(Order.created_at.desc()).limit(20).all()
        
        # Produtos com stock baixo
        low_stock_products = Product.query.filter(Product.stock < 10).all()
        
        stats = {
            'total_orders': total_orders,
            'total_revenue': total_revenue,
            'pending_orders': pending_orders,
            'shipped_orders': shipped_orders,
            'customers_count': Customer.query.count(),
            'products_count': Product.query.count()
        }
        
        # Testar SendCraft
        sendcraft_ok, sendcraft_info = sendcraft.test_connection()
        
        return render_template('shop/dashboard.html', 
                             orders=orders, 
                             stats=stats,
                             low_stock_products=low_stock_products,
                             sendcraft_status=sendcraft_ok,
                             sendcraft_info=sendcraft_info)
    
    @app.route('/marketing', methods=['GET', 'POST'])
    def marketing():
        """Campanhas de marketing"""
        if request.method == 'GET':
            customers_count = Customer.query.count()
            return render_template('shop/marketing.html', customers_count=customers_count)
        
        try:
            data = request.get_json()
            
            # Obter emails de clientes
            customers = Customer.query.all()
            if not customers:
                return jsonify({'success': False, 'error': 'Nenhum cliente encontrado'}), 400
            
            recipient_emails = [customer.email for customer in customers]
            
            # Preparar campanha
            campaign_data = {
                'campaign_id': str(uuid.uuid4()),
                'title': data.get('title', 'Oferta Especial TechStore'),
                'subtitle': data.get('subtitle', 'Não perca esta oportunidade!'),
                'description': data.get('description', 'Aproveite descontos incríveis em tecnologia!'),
                'discount': data.get('discount', '20'),
                'cta_text': data.get('cta_text', 'Ver Ofertas'),
                'cta_link': data.get('cta_link', 'http://localhost:5001'),
                'valid_until': data.get('valid_until', '31 de Dezembro')
            }
            
            # Enviar campanha
            success, result = sendcraft.send_marketing_campaign(recipient_emails, campaign_data)
            
            if success:
                message = f'Campanha enviada com sucesso para {len(recipient_emails)} clientes!'
                logger.info(f"Campanha enviada: {result.get('message_id')}")
            else:
                message = f'Falha no envio da campanha: {result.get("error", "Erro desconhecido")}'
                logger.error(f"Falha na campanha: {result}")
            
            return jsonify({
                'success': success,
                'message': message,
                'recipients_count': len(recipient_emails),
                'details': result
            })
            
        except Exception as e:
            logger.error(f"Erro na campanha de marketing: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/generate-test-data')
    def generate_test_data():
        """Gerar clientes de teste"""
        try:
            # Gerar 15 clientes fake
            for _ in range(15):
                customer = Customer(
                    name=fake.name(),
                    email=fake.email(),
                    phone=fake.phone_number(),
                    address=fake.address()
                )
                db.session.add(customer)
            
            db.session.commit()
            flash(f'15 clientes de teste gerados com sucesso!', 'success')
            logger.info("Dados de teste gerados")
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erro ao gerar dados: {e}")
            flash(f'Erro: {str(e)}', 'danger')
        
        return redirect(url_for('dashboard'))
    
    @app.route('/api/sendcraft/test')
    def test_sendcraft():
        """Testar conexão com SendCraft"""
        success, info = sendcraft.test_connection()
        return jsonify({
            'success': success,
            'info': info,
            'config': {
                'api_base': app.config['SENDCRAFT_API_BASE'],
                'domain': app.config['SENDCRAFT_DOMAIN'],
                'account': app.config['SENDCRAFT_ACCOUNT']
            }
        })
    
    def send_order_confirmation_email(order, sendcraft_client, pdf_gen):
        """Enviar email de confirmação com PDF"""
        try:
            order_data = {
                'order_number': order.order_number,
                'order_date': order.created_at.strftime('%d/%m/%Y %H:%M'),
                'customer_name': order.customer.name,
                'customer_email': order.customer.email,
                'total': order.total_amount,
                'items': [
                    {
                        'product_name': item.product.name,
                        'quantity': item.quantity,
                        'price': item.price,
                        'subtotal': item.quantity * item.price
                    }
                    for item in order.items
                ]
            }
            
            # Gerar PDF
            pdf_content = pdf_gen.generate_invoice(order_data)
            
            # Enviar email
            success, result = sendcraft_client.send_order_confirmation(order_data, pdf_content)
            
            if success:
                order.confirmation_email_sent = True
                order.confirmation_message_id = result.get('message_id')
                db.session.commit()
            
            return success
            
        except Exception as e:
            logger.error(f"Erro no email de confirmação: {e}")
            return False
    
    def send_shipping_notification_email(order, tracking_number, sendcraft_client):
        """Enviar email de notificação de envio"""
        try:
            order_data = {
                'order_number': order.order_number,
                'customer_name': order.customer.name,
                'customer_email': order.customer.email,
                'total': order.total_amount
            }
            
            success, result = sendcraft_client.send_shipping_notification(order_data, tracking_number)
            
            if success:
                order.shipping_message_id = result.get('message_id')
                db.session.commit()
            
            return success
            
        except Exception as e:
            logger.error(f"Erro no email de envio: {e}")
            return False
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5001)
```

---

### 🎨 **FASE 6: TEMPLATES HTML BÁSICOS (45 min)**

#### 6.1 Template Base
```html
<!-- templates/shop/base.html -->
<!DOCTYPE html>
<html lang="pt">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}TechStore - E-commerce Simulator{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css" rel="stylesheet">
    <style>
        .product-card:hover { transform: translateY(-5px); transition: transform 0.2s; }
        .stats-card { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
        .sendcraft-status { position: fixed; bottom: 20px; right: 20px; z-index: 1000; }
    </style>
</head>
<body>
    <!-- Navigation -->
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container">
            <a class="navbar-brand fw-bold" href="{{ url_for('index') }}">
                <i class="bi bi-laptop"></i> TechStore
            </a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link" href="{{ url_for('index') }}"><i class="bi bi-shop"></i> Loja</a>
                <a class="nav-link" href="{{ url_for('dashboard') }}"><i class="bi bi-graph-up"></i> Dashboard</a>
                <a class="nav-link" href="{{ url_for('marketing') }}"><i class="bi bi-megaphone"></i> Marketing</a>
            </div>
        </div>
    </nav>

    <!-- Flash Messages -->
    {% with messages = get_flashed_messages(with_categories=true) %}
        {% if messages %}
            <div class="container mt-3">
                {% for category, message in messages %}
                    <div class="alert alert-{{ 'danger' if category == 'error' else category }} alert-dismissible fade show">
                        {{ message }}
                        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                    </div>
                {% endfor %}
            </div>
        {% endif %}
    {% endwith %}

    <!-- Main Content -->
    <main>{% block content %}{% endblock %}</main>

    <!-- SendCraft Status -->
    <div class="sendcraft-status">
        {% if sendcraft_status is defined %}
            <div class="alert alert-{{ 'success' if sendcraft_status else 'danger' }} alert-dismissible">
                <small>
                    <i class="bi bi-{{ 'check-circle' if sendcraft_status else 'x-circle' }}"></i>
                    SendCraft: {{ 'OK' if sendcraft_status else 'Falha' }}
                </small>
                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="alert"></button>
            </div>
        {% endif %}
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    {% block scripts %}{% endblock %}
</body>
</html>
```

#### 6.2 Página Principal
```html
<!-- templates/shop/index.html -->
{% extends "shop/base.html" %}
{% block content %}
<div class="container my-5">
    <!-- Hero -->
    <div class="bg-primary text-white rounded-3 p-5 text-center mb-5">
        <h1 class="display-4">🚀 TechStore</h1>
        <p class="lead">E-commerce Simulator + SendCraft Integration</p>
        <p>Demonstração completa de emails transacionais</p>
    </div>

    <!-- Products -->
    <h2 class="mb-4"><i class="bi bi-laptop"></i> Produtos Disponíveis</h2>
    <div class="row" id="products-container">
        {% for product in products %}
        <div class="col-md-6 col-lg-4 mb-4">
            <div class="card product-card h-100 shadow-sm">
                <div class="card-body">
                    <h5 class="card-title">{{ product.name }}</h5>
                    <p class="card-text text-muted">{{ product.description }}</p>
                    <div class="d-flex justify-content-between mb-2">
                        <span class="h5 text-primary">€{{ "%.2f"|format(product.price) }}</span>
                        <span class="badge bg-secondary">{{ product.category }}</span>
                    </div>
                    <div class="d-flex justify-content-between align-items-center">
                        <small>Stock: {{ product.stock }}</small>
                        <button class="btn btn-primary btn-sm" onclick="addToCart({{ product.id }})">
                            <i class="bi bi-cart-plus"></i> Adicionar
                        </button>
                    </div>
                </div>
            </div>
        </div>
        {% endfor %}
    </div>

    <!-- Cart -->
    <div class="card mt-5">
        <div class="card-header bg-success text-white">
            <h4><i class="bi bi-cart"></i> Carrinho <span id="cart-count" class="badge bg-light text-dark">0</span></h4>
        </div>
        <div class="card-body">
            <div id="cart-items">
                <p class="text-muted text-center">Carrinho vazio</p>
            </div>
            <div id="cart-total" class="d-none">
                <hr>
                <div class="d-flex justify-content-between">
                    <h5>Total: <span id="total-amount">€0.00</span></h5>
                    <button class="btn btn-success" onclick="proceedToCheckout()">
                        <i class="bi bi-credit-card"></i> Finalizar Compra
                    </button>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block scripts %}
<script>
let cart = [];
let products = {{ products|tojsonfilter }};

function addToCart(productId) {
    const product = products.find(p => p.id === productId);
    if (!product) return;
    
    const existingItem = cart.find(item => item.product_id === productId);
    if (existingItem) {
        existingItem.quantity += 1;
    } else {
        cart.push({product_id: productId, product: product, quantity: 1});
    }
    updateCartDisplay();
}

function updateCartDisplay() {
    const cartItems = document.getElementById('cart-items');
    const cartCount = document.getElementById('cart-count');
    const cartTotal = document.getElementById('cart-total');
    const totalAmount = document.getElementById('total-amount');
    
    cartCount.textContent = cart.length;
    
    if (cart.length === 0) {
        cartItems.innerHTML = '<p class="text-muted text-center">Carrinho vazio</p>';
        cartTotal.classList.add('d-none');
        return;
    }
    
    let total = 0;
    let html = '';
    
    cart.forEach(item => {
        const subtotal = item.quantity * item.product.price;
        total += subtotal;
        html += `
            <div class="d-flex justify-content-between align-items-center mb-2">
                <div>
                    <strong>${item.product.name}</strong><br>
                    <small>€${item.product.price.toFixed(2)} × ${item.quantity}</small>
                </div>
                <div class="text-end">
                    <div>€${subtotal.toFixed(2)}</div>
                    <button class="btn btn-outline-danger btn-sm" onclick="removeFromCart(${item.product_id})">
                        <i class="bi bi-trash"></i>
                    </button>
                </div>
            </div>
        `;
    });
    
    cartItems.innerHTML = html;
    totalAmount.textContent = `€${total.toFixed(2)}`;
    cartTotal.classList.remove('d-none');
}

function removeFromCart(productId) {
    cart = cart.filter(item => item.product_id !== productId);
    updateCartDisplay();
}

function proceedToCheckout() {
    if (cart.length === 0) {
        alert('Carrinho vazio!');
        return;
    }
    
    const customerName = prompt('Nome do cliente:') || 'Cliente Teste';
    const customerEmail = prompt('Email do cliente:') || 'geral@artnshine.pt';
    
    if (!customerEmail) {
        alert('Email é obrigatório!');
        return;
    }
    
    const orderData = {
        customer: {
            name: customerName,
            email: customerEmail,
            phone: '+351 123 456 789',
            address: 'Rua Teste, 123, Lisboa'
        },
        items: cart.map(item => ({
            product_id: item.product_id,
            quantity: item.quantity
        }))
    };
    
    fetch('/checkout', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(orderData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert(`Encomenda ${data.order_number} criada! ${data.email_sent ? 'Email enviado.' : 'Falha no email.'}`);
            cart = [];
            updateCartDisplay();
            setTimeout(() => window.location.href = '/dashboard', 2000);
        } else {
            alert(`Erro: ${data.error}`);
        }
    })
    .catch(error => alert(`Erro: ${error.message}`));
}
</script>
{% endblock %}
```

#### 6.3 Dashboard
```html
<!-- templates/shop/dashboard.html -->
{% extends "shop/base.html" %}
{% block content %}
<div class="container my-4">
    <h1><i class="bi bi-graph-up"></i> Dashboard TechStore</h1>
    
    <!-- Stats Cards -->
    <div class="row mb-4">
        <div class="col-md-3 mb-3">
            <div class="card stats-card text-center p-3">
                <h3>{{ stats.total_orders }}</h3>
                <p class="mb-0">Encomendas</p>
            </div>
        </div>
        <div class="col-md-3 mb-3">
            <div class="card stats-card text-center p-3">
                <h3>€{{ "%.2f"|format(stats.total_revenue) }}</h3>
                <p class="mb-0">Receita</p>
            </div>
        </div>
        <div class="col-md-3 mb-3">
            <div class="card stats-card text-center p-3">
                <h3>{{ stats.pending_orders }}</h3>
                <p class="mb-0">Pendentes</p>
            </div>
        </div>
        <div class="col-md-3 mb-3">
            <div class="card stats-card text-center p-3">
                <h3>{{ stats.customers_count }}</h3>
                <p class="mb-0">Clientes</p>
            </div>
        </div>
    </div>
    
    <!-- Actions -->
    <div class="row mb-4">
        <div class="col-md-6">
            <div class="card">
                <div class="card-body">
                    <h5>Ações Rápidas</h5>
                    <a href="{{ url_for('generate_test_data') }}" class="btn btn-primary me-2">
                        <i class="bi bi-people"></i> Gerar Clientes
                    </a>
                    <a href="{{ url_for('marketing') }}" class="btn btn-success">
                        <i class="bi bi-megaphone"></i> Nova Campanha
                    </a>
                </div>
            </div>
        </div>
        <div class="col-md-6">
            <div class="card">
                <div class="card-body">
                    <h5>SendCraft Status</h5>
                    <div class="d-flex align-items-center">
                        <i class="bi bi-{{ 'check-circle text-success' if sendcraft_status else 'x-circle text-danger' }} me-2"></i>
                        <span>{{ 'Conectado' if sendcraft_status else 'Desconectado' }}</span>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Orders Table -->
    <div class="card">
        <div class="card-header">
            <h5><i class="bi bi-list-ul"></i> Encomendas Recentes</h5>
        </div>
        <div class="card-body">
            {% if orders %}
            <div class="table-responsive">
                <table class="table">
                    <thead>
                        <tr>
                            <th>Nº Encomenda</th>
                            <th>Cliente</th>
                            <th>Total</th>
                            <th>Status</th>
                            <th>Data</th>
                            <th>Ações</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for order in orders %}
                        <tr>
                            <td>{{ order.order_number }}</td>
                            <td>{{ order.customer.name }}</td>
                            <td>€{{ "%.2f"|format(order.total_amount) }}</td>
                            <td>
                                <span class="badge bg-{{ 'warning' if order.status == 'confirmed' else 'primary' if order.status == 'shipped' else 'secondary' }}">
                                    {{ order.status }}
                                </span>
                            </td>
                            <td>{{ order.created_at.strftime('%d/%m/%Y %H:%M') }}</td>
                            <td>
                                {% if order.status == 'confirmed' %}
                                <form method="POST" action="{{ url_for('ship_order', order_id=order.id) }}" style="display: inline;">
                                    <button type="submit" class="btn btn-sm btn-primary" onclick="return confirm('Marcar como enviada?')">
                                        <i class="bi bi-truck"></i> Enviar
                                    </button>
                                </form>
                                {% endif %}
                                <a href="{{ url_for('order_detail', order_id=order.id) }}" class="btn btn-sm btn-outline-info">
                                    <i class="bi bi-eye"></i>
                                </a>
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
            {% else %}
            <p class="text-muted text-center">Nenhuma encomenda encontrada</p>
            {% endif %}
        </div>
    </div>
</div>
{% endblock %}
```

#### 6.4 Marketing
```html
<!-- templates/shop/marketing.html -->
{% extends "shop/base.html" %}
{% block content %}
<div class="container my-4">
    <h1><i class="bi bi-megaphone"></i> Campanhas de Marketing</h1>
    
    <div class="row">
        <div class="col-md-8">
            <div class="card">
                <div class="card-header">
                    <h5>Nova Campanha</h5>
                </div>
                <div class="card-body">
                    <form id="campaignForm">
                        <div class="mb-3">
                            <label class="form-label">Título da Campanha</label>
                            <input type="text" class="form-control" id="title" value="🎯 Oferta Especial TechStore">
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Subtítulo</label>
                            <input type="text" class="form-control" id="subtitle" value="Não perca esta oportunidade única!">
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Descrição</label>
                            <textarea class="form-control" id="description" rows="3">Aproveite descontos incríveis em toda nossa linha de tecnologia. Ofertas válidas por tempo limitado!</textarea>
                        </div>
                        <div class="row">
                            <div class="col-md-6 mb-3">
                                <label class="form-label">Desconto (%)</label>
                                <input type="number" class="form-control" id="discount" value="25">
                            </div>
                            <div class="col-md-6 mb-3">
                                <label class="form-label">Válido até</label>
                                <input type="text" class="form-control" id="validUntil" value="31 de Dezembro">
                            </div>
                        </div>
                        <div class="row">
                            <div class="col-md-6 mb-3">
                                <label class="form-label">Texto do Botão</label>
                                <input type="text" class="form-control" id="ctaText" value="Ver Ofertas">
                            </div>
                            <div class="col-md-6 mb-3">
                                <label class="form-label">Link do Botão</label>
                                <input type="url" class="form-control" id="ctaLink" value="http://localhost:5001">
                            </div>
                        </div>
                        <button type="submit" class="btn btn-success">
                            <i class="bi bi-send"></i> Enviar Campanha
                        </button>
                    </form>
                </div>
            </div>
        </div>
        
        <div class="col-md-4">
            <div class="card">
                <div class="card-header">
                    <h5>Informações</h5>
                </div>
                <div class="card-body">
                    <p><strong>Clientes registados:</strong> {{ customers_count }}</p>
                    <p><strong>SendCraft Status:</strong> 
                        <span class="badge bg-{{ 'success' if sendcraft_status else 'danger' }}">
                            {{ 'Online' if sendcraft_status else 'Offline' }}
                        </span>
                    </p>
                    <hr>
                    <h6>Como funciona:</h6>
                    <ol class="small">
                        <li>Preencha os dados da campanha</li>
                        <li>Clique em "Enviar Campanha"</li>
                        <li>Email será enviado para todos os clientes</li>
                        <li>Acompanhe os resultados no dashboard</li>
                    </ol>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block scripts %}
<script>
document.getElementById('campaignForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const campaignData = {
        title: document.getElementById('title').value,
        subtitle: document.getElementById('subtitle').value,
        description: document.getElementById('description').value,
        discount: document.getElementById('discount').value,
        valid_until: document.getElementById('validUntil').value,
        cta_text: document.getElementById('ctaText').value,
        cta_link: document.getElementById('ctaLink').value
    };
    
    fetch('/marketing', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(campaignData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert(`Campanha enviada com sucesso para ${data.recipients_count} clientes!`);
            setTimeout(() => window.location.href = '/dashboard', 2000);
        } else {
            alert(`Erro no envio: ${data.message || data.error}`);
        }
    })
    .catch(error => {
        alert(`Erro: ${error.message}`);
    });
});
</script>
{% endblock %}
```

---

## ✅ **ENTREGA PHASE 17A**

### **Resultados Esperados:**
1. **E-commerce Simulator** rodando em `http://localhost:5001`
2. **Integração SendCraft** funcional com a API
3. **Produtos, carrinho e checkout** operacionais
4. **Geração de PDFs** para faturas
5. **Dashboard administrativo** com estatísticas
6. **Sistema de marketing** para campanhas bulk
7. **Logging e error handling** adequados

### **Validação de Sucesso:**
```bash
# 1. Servidor rodando
python app.py
# → E-commerce acessível em http://localhost:5001

# 2. Integração OK
# → Status SendCraft verde na interface

# 3. Funcionalidades core
# → Adicionar produtos ao carrinho
# → Fazer checkout
# → Ver dashboard com estatísticas
# → Gerar clientes de teste
# → Enviar campanha de marketing

# 4. Logs no console
# → Confirmar tentativas de envio de email
# → Ver erros de integração (se houver)
```

**Phase 17A completa quando o e-commerce estiver 100% funcional e integrado, pronto para testes com Playwright na Phase 17B! 🚀**