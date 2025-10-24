# 🚀 SendCraft Phase 17: Prompt Executivo - E-commerce Integration

**Você é um arquiteto de software sênior responsável por criar a integração definitiva entre SendCraft e sistemas de e-commerce. Sua missão é construir um simulador completo que demonstre o valor real da API SendCraft em cenários de e-commerce.**

## 🎯 OBJETIVO EXECUTIVO
Criar um **E-commerce Simulator completo** que integra com a API SendCraft para demonstrar:
- ✅ Confirmações de encomenda com faturas PDF
- ✅ Notificações de envio com tracking  
- ✅ Campanhas de marketing em bulk
- ✅ Sistema de webhooks em tempo real
- ✅ Dashboard com métricas de engagement

## 📂 CONTEXTO TÉCNICO
- **SendCraft API:** 100% pronta (Phase 16 completa)
- **Base URL:** http://localhost:5000/api/v1
- **Conta de teste:** geral@artnshine.pt
- **Endpoints:** `/send`, `/send/{id}/status`, `/attachments/upload`
- **Branch:** main (commit 26c43462 - Phase 16 success)

---

## 📋 EXECUÇÃO PASSO-A-PASSO

### 🛠️ **FASE 1: SETUP DO PROJETO E-COMMERCE (45 min)**

#### 1.1 Criar Estrutura do Simulador
```bash
# No diretório principal (fora de SendCraft)
mkdir -p ecommerce_simulator
cd ecommerce_simulator

# Criar estrutura completa
mkdir -p {templates/{shop,emails},static/{css,js,assets,uploads},models,services,config}
mkdir -p docs/integration

# Estrutura de arquivos
touch app.py requirements.txt config.py
touch models/{__init__.py,order.py,product.py,customer.py}
touch services/{__init__.py,sendcraft_client.py,pdf_generator.py,webhook_receiver.py}
touch templates/shop/{index.html,checkout.html,dashboard.html}
touch templates/emails/{order_confirmation.html,shipping_notification.html,newsletter.html}

echo "✅ Estrutura criada"
```

#### 1.2 Configurar Ambiente Python
```bash
# Criar requirements.txt
cat > requirements.txt << 'EOF'
Flask==2.3.2
Flask-SQLAlchemy==3.0.5
requests==2.31.0
reportlab==4.0.4
Pillow==10.0.0
python-dotenv==1.0.0
Faker==19.3.0
Jinja2==3.1.2
Werkzeug==2.3.6
EOF

# Instalar dependências
python -m venv venv
source venv/bin/activate  # ou venv\Scripts\activate no Windows
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
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'ecommerce-simulator-secret-key-2025'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///ecommerce.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # SendCraft API
    SENDCRAFT_API_BASE = os.environ.get('SENDCRAFT_API_BASE') or 'http://localhost:5000/api/v1'
    SENDCRAFT_API_KEY = os.environ.get('SENDCRAFT_API_KEY') or 'YOUR_API_KEY_HERE'
    SENDCRAFT_DOMAIN = os.environ.get('SENDCRAFT_DOMAIN') or 'artnshine.pt'
    SENDCRAFT_ACCOUNT = os.environ.get('SENDCRAFT_ACCOUNT') or 'geral'
    
    # E-commerce Settings
    COMPANY_NAME = 'TechStore Simulator'
    COMPANY_EMAIL = 'geral@artnshine.pt'
    COMPANY_PHONE = '+351 123 456 789'
    COMPANY_ADDRESS = 'Rua da Inovação, 123, Lisboa, Portugal'
    
    # File Upload
    UPLOAD_FOLDER = 'static/uploads'
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
```

---

### 🏪 **FASE 2: MODELOS E DATABASE (30 min)**

#### 2.1 Modelos de Dados
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
    email = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(50))
    address = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    orders = db.relationship('Order', backref='customer', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'address': self.address,
            'created_at': self.created_at.isoformat() if self.created_at else None
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
            'stock': self.stock,
            'image_url': self.image_url,
            'created_at': self.created_at.isoformat() if self.created_at else None
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
    
    # Order details
    total_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), default='pending')  # pending, confirmed, shipped, delivered, cancelled
    
    # Email tracking
    confirmation_email_sent = db.Column(db.Boolean, default=False)
    confirmation_message_id = db.Column(db.String(100))
    shipping_email_sent = db.Column(db.Boolean, default=False)
    shipping_message_id = db.Column(db.String(100))
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    shipped_at = db.Column(db.DateTime)
    delivered_at = db.Column(db.DateTime)
    
    # Relationships
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')
    
    def generate_order_number(self):
        """Gerar número de encomenda único"""
        prefix = datetime.utcnow().strftime('%Y%m')
        suffix = str(uuid.uuid4())[:8].upper()
        return f"TS-{prefix}-{suffix}"
    
    def calculate_total(self):
        """Calcular total da encomenda"""
        return sum(item.quantity * item.price for item in self.items)
    
    def to_dict(self):
        return {
            'id': self.id,
            'order_number': self.order_number,
            'customer': self.customer.to_dict() if self.customer else None,
            'total_amount': self.total_amount,
            'status': self.status,
            'items': [item.to_dict() for item in self.items],
            'confirmation_email_sent': self.confirmation_email_sent,
            'shipping_email_sent': self.shipping_email_sent,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'shipped_at': self.shipped_at.isoformat() if self.shipped_at else None,
            'delivered_at': self.delivered_at.isoformat() if self.delivered_at else None
        }

class OrderItem(db.Model):
    __tablename__ = 'order_items'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)  # Preço no momento da compra
    
    # Relationships
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

#### 2.2 Inicializar Base de Dados
```python
# Adicionar ao app.py (início)
from flask import Flask
from config import config
from models import db, Customer, Product, Order, OrderItem

def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    
    return app

def init_db():
    """Inicializar BD com dados de exemplo"""
    db.create_all()
    
    # Produtos de exemplo
    if Product.query.count() == 0:
        products = [
            Product(name='Smartphone XYZ', description='Smartphone de última geração', price=599.99, category='Tecnologia', stock=50),
            Product(name='Laptop Pro 15"', description='Laptop profissional 15 polegadas', price=1299.99, category='Tecnologia', stock=25),
            Product(name='Headphones Wireless', description='Auscultadores sem fios com cancelamento de ruído', price=199.99, category='Áudio', stock=100),
            Product(name='Smartwatch Sport', description='Relógio inteligente para desporto', price=299.99, category='Wearables', stock=75),
            Product(name='Tablet 10"', description='Tablet de 10 polegadas para trabalho e lazer', price=399.99, category='Tecnologia', stock=30),
        ]
        
        for product in products:
            db.session.add(product)
        
        db.session.commit()
        print("✅ Produtos de exemplo criados")
    
    print("✅ Base de dados inicializada")
```

---

### 📧 **FASE 3: CLIENTE SENDCRAFT API (45 min)**

#### 3.1 Cliente API SendCraft
```python
# services/sendcraft_client.py
import requests
import base64
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple

class SendCraftClient:
    """Cliente para integração com SendCraft API"""
    
    def __init__(self, api_key: str, base_url: str, domain: str, account: str):
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.domain = domain
        self.account = account
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
    
    def _make_request(self, method: str, endpoint: str, data: dict = None) -> Tuple[bool, dict]:
        """Fazer requisição à API SendCraft"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method.upper() == 'POST':
                response = requests.post(url, headers=self.headers, json=data, timeout=30)
            elif method.upper() == 'GET':
                response = requests.get(url, headers=self.headers, timeout=30)
            else:
                return False, {'error': 'Método não suportado'}
            
            response.raise_for_status()
            return True, response.json()
            
        except requests.exceptions.RequestException as e:
            return False, {'error': str(e), 'status_code': getattr(e.response, 'status_code', 0)}
    
    def send_order_confirmation(self, order_data: dict, pdf_content: bytes = None) -> Tuple[bool, dict]:
        """Enviar confirmação de encomenda"""
        
        # Preparar anexos se houver PDF
        attachments = []
        if pdf_content:
            pdf_base64 = base64.b64encode(pdf_content).decode('utf-8')
            attachments.append({
                'filename': f"fatura-{order_data['order_number']}.pdf",
                'content_type': 'application/pdf',
                'content': pdf_base64
            })
        
        # Preparar dados do email
        email_data = {
            'to': [order_data['customer_email']],
            'subject': f"✅ Confirmação de Encomenda {order_data['order_number']}",
            'html': self._render_order_confirmation_html(order_data),
            'text': self._render_order_confirmation_text(order_data),
            'domain': self.domain,
            'account': self.account,
            'from_name': 'TechStore',
            'attachments': attachments,
            'idempotency_key': f"order-confirmation-{order_data['order_number']}"
        }
        
        success, result = self._make_request('POST', '/send', email_data)
        return success, result
    
    def send_shipping_notification(self, order_data: dict, tracking_number: str) -> Tuple[bool, dict]:
        """Enviar notificação de envio"""
        
        email_data = {
            'to': [order_data['customer_email']],
            'subject': f"📦 Encomenda {order_data['order_number']} Enviada - Tracking: {tracking_number}",
            'html': self._render_shipping_notification_html(order_data, tracking_number),
            'text': self._render_shipping_notification_text(order_data, tracking_number),
            'domain': self.domain,
            'account': self.account,
            'from_name': 'TechStore Envios',
            'idempotency_key': f"shipping-notification-{order_data['order_number']}"
        }
        
        success, result = self._make_request('POST', '/send', email_data)
        return success, result
    
    def send_marketing_campaign(self, recipients: List[str], campaign_data: dict) -> Tuple[bool, dict]:
        """Enviar campanha de marketing"""
        
        email_data = {
            'to': recipients,
            'subject': campaign_data.get('subject', '🎯 Oferta Especial TechStore'),
            'html': self._render_marketing_html(campaign_data),
            'text': self._render_marketing_text(campaign_data),
            'domain': self.domain,
            'account': self.account,
            'from_name': 'TechStore Marketing',
            'bulk': len(recipients) > 1,
            'idempotency_key': f"campaign-{campaign_data.get('campaign_id', datetime.now().isoformat())}"
        }
        
        success, result = self._make_request('POST', '/send', email_data)
        return success, result
    
    def get_email_status(self, message_id: str) -> Tuple[bool, dict]:
        """Verificar status de email"""
        success, result = self._make_request('GET', f'/send/{message_id}/status')
        return success, result
    
    def _render_order_confirmation_html(self, order_data: dict) -> str:
        """Renderizar HTML da confirmação de encomenda"""
        items_html = ""
        for item in order_data['items']:
            items_html += f"""
            <tr>
                <td style="padding: 10px; border-bottom: 1px solid #eee;">
                    {item['product_name']}
                </td>
                <td style="padding: 10px; border-bottom: 1px solid #eee; text-align: center;">
                    {item['quantity']}
                </td>
                <td style="padding: 10px; border-bottom: 1px solid #eee; text-align: right;">
                    €{item['price']:.2f}
                </td>
                <td style="padding: 10px; border-bottom: 1px solid #eee; text-align: right;">
                    €{item['subtotal']:.2f}
                </td>
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
            <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                
                <div style="text-align: center; margin-bottom: 30px;">
                    <h1 style="color: #333; margin: 0;">TechStore</h1>
                    <p style="color: #666; margin: 5px 0 0 0;">Tecnologia de Confiança</p>
                </div>
                
                <div style="background-color: #4CAF50; color: white; padding: 15px; text-align: center; border-radius: 5px; margin-bottom: 20px;">
                    <h2 style="margin: 0;">✅ Encomenda Confirmada!</h2>
                </div>
                
                <p>Olá <strong>{order_data['customer_name']}</strong>,</p>
                
                <p>Obrigado pela sua compra! A sua encomenda foi confirmada e está a ser processada.</p>
                
                <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <h3 style="margin: 0 0 10px 0; color: #333;">Detalhes da Encomenda</h3>
                    <p style="margin: 5px 0;"><strong>Número:</strong> {order_data['order_number']}</p>
                    <p style="margin: 5px 0;"><strong>Data:</strong> {order_data['order_date']}</p>
                    <p style="margin: 5px 0;"><strong>Total:</strong> €{order_data['total']:.2f}</p>
                </div>
                
                <h3 style="color: #333;">Items da Encomenda</h3>
                <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px;">
                    <thead>
                        <tr style="background-color: #f8f9fa;">
                            <th style="padding: 10px; text-align: left; border-bottom: 2px solid #ddd;">Produto</th>
                            <th style="padding: 10px; text-align: center; border-bottom: 2px solid #ddd;">Qtd</th>
                            <th style="padding: 10px; text-align: right; border-bottom: 2px solid #ddd;">Preço</th>
                            <th style="padding: 10px; text-align: right; border-bottom: 2px solid #ddd;">Subtotal</th>
                        </tr>
                    </thead>
                    <tbody>
                        {items_html}
                    </tbody>
                    <tfoot>
                        <tr style="background-color: #f8f9fa; font-weight: bold;">
                            <td colspan="3" style="padding: 15px; text-align: right; border-top: 2px solid #ddd;">TOTAL:</td>
                            <td style="padding: 15px; text-align: right; border-top: 2px solid #ddd;">€{order_data['total']:.2f}</td>
                        </tr>
                    </tfoot>
                </table>
                
                <div style="background-color: #e3f2fd; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <h3 style="margin: 0 0 10px 0; color: #1976d2;">📦 Próximos Passos</h3>
                    <p style="margin: 5px 0;">1. Processamento da encomenda (1-2 dias úteis)</p>
                    <p style="margin: 5px 0;">2. Preparação e embalamento</p>
                    <p style="margin: 5px 0;">3. Envio com número de tracking</p>
                    <p style="margin: 5px 0;">4. Entrega no endereço indicado</p>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <p style="color: #666;">Em caso de dúvidas, contacte-nos:</p>
                    <p style="color: #666;">📧 geral@artnshine.pt | 📞 +351 123 456 789</p>
                </div>
                
                <div style="border-top: 1px solid #eee; padding-top: 20px; text-align: center; color: #666; font-size: 14px;">
                    <p>TechStore - Tecnologia de Confiança</p>
                    <p>Rua da Inovação, 123, Lisboa, Portugal</p>
                </div>
                
            </div>
        </body>
        </html>
        """
    
    def _render_order_confirmation_text(self, order_data: dict) -> str:
        """Renderizar texto da confirmação de encomenda"""
        items_text = ""
        for item in order_data['items']:
            items_text += f"- {item['product_name']} x{item['quantity']} - €{item['subtotal']:.2f}\\n"
        
        return f"""
✅ ENCOMENDA CONFIRMADA!

Olá {order_data['customer_name']},

Obrigado pela sua compra! A sua encomenda foi confirmada e está a ser processada.

DETALHES DA ENCOMENDA:
- Número: {order_data['order_number']}
- Data: {order_data['order_date']}
- Total: €{order_data['total']:.2f}

ITEMS:
{items_text}

PRÓXIMOS PASSOS:
1. Processamento da encomenda (1-2 dias úteis)
2. Preparação e embalamento
3. Envio com número de tracking
4. Entrega no endereço indicado

Em caso de dúvidas, contacte-nos:
📧 geral@artnshine.pt | 📞 +351 123 456 789

TechStore - Tecnologia de Confiança
Rua da Inovação, 123, Lisboa, Portugal
        """
    
    def _render_shipping_notification_html(self, order_data: dict, tracking_number: str) -> str:
        """Renderizar HTML da notificação de envio"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Encomenda Enviada</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; margin: 0; padding: 20px; background-color: #f4f4f4;">
            <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                
                <div style="text-align: center; margin-bottom: 30px;">
                    <h1 style="color: #333; margin: 0;">TechStore</h1>
                    <p style="color: #666; margin: 5px 0 0 0;">Envios Rápidos</p>
                </div>
                
                <div style="background-color: #2196F3; color: white; padding: 15px; text-align: center; border-radius: 5px; margin-bottom: 20px;">
                    <h2 style="margin: 0;">📦 Encomenda Enviada!</h2>
                </div>
                
                <p>Olá <strong>{order_data['customer_name']}</strong>,</p>
                
                <p>Ótimas notícias! A sua encomenda <strong>{order_data['order_number']}</strong> foi enviada e está a caminho.</p>
                
                <div style="background-color: #e8f5e8; padding: 20px; border-radius: 5px; margin: 20px 0; text-align: center;">
                    <h3 style="margin: 0 0 10px 0; color: #2e7d32;">📍 Número de Tracking</h3>
                    <div style="background-color: white; padding: 15px; border-radius: 5px; font-family: monospace; font-size: 18px; font-weight: bold; color: #2e7d32; letter-spacing: 2px;">
                        {tracking_number}
                    </div>
                </div>
                
                <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <h3 style="margin: 0 0 10px 0; color: #333;">🚚 Informações de Envio</h3>
                    <p style="margin: 5px 0;"><strong>Transportadora:</strong> CTT Express</p>
                    <p style="margin: 5px 0;"><strong>Prazo de entrega:</strong> 2-3 dias úteis</p>
                    <p style="margin: 5px 0;"><strong>Método:</strong> Entrega ao domicílio</p>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="https://track.ctt.pt/feapl_2/app/open/ctt/objectSearch/objectSearch.jspx?objects={tracking_number}" 
                       style="background-color: #4CAF50; color: white; padding: 15px 25px; text-decoration: none; border-radius: 5px; font-weight: bold; display: inline-block;">
                        🔍 Acompanhar Encomenda
                    </a>
                </div>
                
                <div style="background-color: #fff3cd; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <h3 style="margin: 0 0 10px 0; color: #856404;">💡 Dicas Importantes</h3>
                    <p style="margin: 5px 0;">• Certifique-se que alguém estará presente no endereço de entrega</p>
                    <p style="margin: 5px 0;">• Tenha um documento de identificação à mão</p>
                    <p style="margin: 5px 0;">• Guarde o número de tracking para referência</p>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <p style="color: #666;">Alguma dúvida sobre a sua encomenda?</p>
                    <p style="color: #666;">📧 geral@artnshine.pt | 📞 +351 123 456 789</p>
                </div>
                
                <div style="border-top: 1px solid #eee; padding-top: 20px; text-align: center; color: #666; font-size: 14px;">
                    <p>TechStore - Tecnologia de Confiança</p>
                    <p>Obrigado por escolher a TechStore!</p>
                </div>
                
            </div>
        </body>
        </html>
        """
    
    def _render_shipping_notification_text(self, order_data: dict, tracking_number: str) -> str:
        """Renderizar texto da notificação de envio"""
        return f"""
📦 ENCOMENDA ENVIADA!

Olá {order_data['customer_name']},

Ótimas notícias! A sua encomenda {order_data['order_number']} foi enviada e está a caminho.

NÚMERO DE TRACKING: {tracking_number}

INFORMAÇÕES DE ENVIO:
- Transportadora: CTT Express
- Prazo de entrega: 2-3 dias úteis
- Método: Entrega ao domicílio

Acompanhe a sua encomenda em:
https://track.ctt.pt/feapl_2/app/open/ctt/objectSearch/objectSearch.jspx?objects={tracking_number}

DICAS IMPORTANTES:
• Certifique-se que alguém estará presente no endereço de entrega
• Tenha um documento de identificação à mão
• Guarde o número de tracking para referência

Alguma dúvida sobre a sua encomenda?
📧 geral@artnshine.pt | 📞 +351 123 456 789

TechStore - Tecnologia de Confiança
Obrigado por escolher a TechStore!
        """
    
    def _render_marketing_html(self, campaign_data: dict) -> str:
        """Renderizar HTML da campanha de marketing"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{campaign_data.get('title', 'Oferta Especial TechStore')}</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; margin: 0; padding: 20px; background-color: #f4f4f4;">
            <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                
                <div style="text-align: center; margin-bottom: 30px;">
                    <h1 style="color: #333; margin: 0;">TechStore</h1>
                    <p style="color: #666; margin: 5px 0 0 0;">Ofertas Imperdíveis</p>
                </div>
                
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; text-align: center; border-radius: 10px; margin-bottom: 20px;">
                    <h2 style="margin: 0; font-size: 24px;">🎯 {campaign_data.get('title', 'Oferta Especial!')}</h2>
                    <p style="margin: 10px 0 0 0; opacity: 0.9;">{campaign_data.get('subtitle', 'Não perca esta oportunidade única!')}</p>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <div style="background-color: #ff4444; color: white; padding: 20px; border-radius: 10px; display: inline-block; transform: rotate(-2deg);">
                        <div style="font-size: 24px; font-weight: bold; margin-bottom: 5px;">DESCONTO</div>
                        <div style="font-size: 36px; font-weight: bold;">{campaign_data.get('discount', '20')}%</div>
                        <div style="font-size: 14px;">EM PRODUTOS SELECIONADOS</div>
                    </div>
                </div>
                
                <p>{campaign_data.get('description', 'Aproveite esta oferta limitada e renove a sua tecnologia com os melhores preços!')}</p>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{campaign_data.get('cta_link', '#')}" 
                       style="background: linear-gradient(135deg, #ff6b6b, #ee5a24); color: white; padding: 15px 30px; text-decoration: none; border-radius: 25px; font-weight: bold; display: inline-block; box-shadow: 0 4px 15px rgba(238, 90, 36, 0.3);">
                        🛒 {campaign_data.get('cta_text', 'Ver Ofertas')}
                    </a>
                </div>
                
                <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0; text-align: center;">
                    <p style="margin: 0; color: #666; font-size: 14px;">
                        ⏰ <strong>Oferta válida até:</strong> {campaign_data.get('valid_until', '31 de Dezembro')}
                    </p>
                </div>
                
                <div style="border-top: 1px solid #eee; padding-top: 20px; text-align: center; color: #666; font-size: 14px;">
                    <p>TechStore - Tecnologia de Confiança</p>
                    <p style="font-size: 12px;">Se não deseja receber estes emails, <a href="#">clique aqui para cancelar</a></p>
                </div>
                
            </div>
        </body>
        </html>
        """
    
    def _render_marketing_text(self, campaign_data: dict) -> str:
        """Renderizar texto da campanha de marketing"""
        return f"""
🎯 {campaign_data.get('title', 'OFERTA ESPECIAL TECHSTORE!')}

{campaign_data.get('description', 'Aproveite esta oferta limitada e renove a sua tecnologia com os melhores preços!')}

🔥 DESCONTO DE {campaign_data.get('discount', '20')}% EM PRODUTOS SELECIONADOS!

Visite a nossa loja online: {campaign_data.get('cta_link', 'https://techstore.exemplo.com')}

⏰ Oferta válida até: {campaign_data.get('valid_until', '31 de Dezembro')}

TechStore - Tecnologia de Confiança
Se não deseja receber estes emails, contacte-nos.
        """
```

---

### 📄 **FASE 4: GERADOR DE PDFs (30 min)**

#### 4.1 Serviço de Geração de PDFs
```python
# services/pdf_generator.py
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch, cm
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from datetime import datetime
import io
import os

class PDFGenerator:
    """Gerador de PDFs para faturas"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Configurar estilos personalizados"""
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
        
        # Criar buffer para o PDF
        buffer = io.BytesIO()
        
        # Criar documento
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        # Lista de elementos do PDF
        elements = []
        
        # Cabeçalho
        elements.append(Paragraph("TechStore", self.styles['CustomTitle']))
        elements.append(Paragraph("Tecnologia de Confiança", self.styles['Normal']))
        elements.append(Paragraph("Rua da Inovação, 123, Lisboa, Portugal", self.styles['Normal']))
        elements.append(Paragraph("NIF: 123456789 | Email: geral@artnshine.pt", self.styles['Normal']))
        elements.append(Spacer(1, 0.5*inch))
        
        # Título da fatura
        elements.append(Paragraph(f"FATURA - {order_data['order_number']}", self.styles['CustomHeading']))
        elements.append(Spacer(1, 0.3*inch))
        
        # Informações do cliente e da fatura
        info_data = [
            ['Data da Fatura:', order_data['order_date']],
            ['Cliente:', order_data['customer_name']],
            ['Email:', order_data['customer_email']],
            ['Morada:', order_data.get('customer_address', 'N/A')],
        ]
        
        info_table = Table(info_data, colWidths=[4*cm, 8*cm])
        info_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ]))
        
        elements.append(info_table)
        elements.append(Spacer(1, 0.5*inch))
        
        # Tabela de produtos
        elements.append(Paragraph("Detalhes da Encomenda", self.styles['CustomHeading']))
        
        # Cabeçalho da tabela
        table_data = [['Produto', 'Quantidade', 'Preço Unitário', 'Subtotal']]
        
        # Items da encomenda
        for item in order_data['items']:
            table_data.append([
                item['product_name'],
                str(item['quantity']),
                f"€{item['price']:.2f}",
                f"€{item['subtotal']:.2f}"
            ])
        
        # Total
        table_data.append(['', '', 'TOTAL:', f"€{order_data['total']:.2f}"])
        
        # Criar tabela
        items_table = Table(table_data, colWidths=[8*cm, 2*cm, 3*cm, 3*cm])
        items_table.setStyle(TableStyle([
            # Cabeçalho
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            
            # Dados
            ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -2), 10),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
            ('ALIGN', (2, 1), (-1, -1), 'RIGHT'),
            
            # Total
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#ecf0f1')),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, -1), (-1, -1), 12),
            ('ALIGN', (2, -1), (-1, -1), 'RIGHT'),
            
            # Bordas
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        elements.append(items_table)
        elements.append(Spacer(1, 0.5*inch))
        
        # Informações de pagamento
        elements.append(Paragraph("Informações de Pagamento", self.styles['CustomHeading']))
        elements.append(Paragraph("Método: Transferência Bancária", self.styles['Normal']))
        elements.append(Paragraph("IBAN: PT50 0000 0000 0000 0000 0000 0", self.styles['Normal']))
        elements.append(Paragraph("Referência: " + order_data['order_number'], self.styles['Normal']))
        elements.append(Spacer(1, 0.3*inch))
        
        # Rodapé
        elements.append(Paragraph("Obrigado pela sua preferência!", self.styles['Normal']))
        elements.append(Paragraph("TechStore - A sua tecnologia de confiança", self.styles['Normal']))
        
        # Gerar PDF
        doc.build(elements)
        
        # Obter conteúdo do buffer
        pdf_content = buffer.getvalue()
        buffer.close()
        
        return pdf_content
```

---

### 🌐 **FASE 5: APLICAÇÃO FLASK PRINCIPAL (60 min)**

#### 5.1 App Principal
```python
# app.py
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, send_file
from datetime import datetime, timedelta
import uuid
import io
from faker import Faker

from config import config
from models import db, Customer, Product, Order, OrderItem
from services.sendcraft_client import SendCraftClient
from services.pdf_generator import PDFGenerator

fake = Faker('pt_PT')

def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
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
    
    @app.route('/')
    def index():
        """Página principal da loja"""
        products = Product.query.all()
        return render_template('shop/index.html', products=products)
    
    @app.route('/api/products')
    def api_products():
        """API para listar produtos"""
        products = Product.query.all()
        return jsonify([product.to_dict() for product in products])
    
    @app.route('/checkout', methods=['GET', 'POST'])
    def checkout():
        """Processo de checkout"""
        if request.method == 'GET':
            products = Product.query.all()
            return render_template('shop/checkout.html', products=products)
        
        # Processar encomenda
        try:
            data = request.get_json()
            
            # Criar cliente
            customer = Customer(
                name=data['customer']['name'],
                email=data['customer']['email'],
                phone=data['customer'].get('phone'),
                address=data['customer'].get('address')
            )
            db.session.add(customer)
            db.session.flush()  # Para obter o ID
            
            # Criar encomenda
            order = Order(
                order_number=f"TS-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}",
                customer_id=customer.id,
                total_amount=0,
                status='confirmed'
            )
            db.session.add(order)
            db.session.flush()  # Para obter o ID
            
            # Adicionar items
            total = 0
            for item_data in data['items']:
                product = Product.query.get(item_data['product_id'])
                if not product:
                    continue
                
                item = OrderItem(
                    order_id=order.id,
                    product_id=product.id,
                    quantity=item_data['quantity'],
                    price=product.price
                )
                db.session.add(item)
                total += item.quantity * item.price
            
            order.total_amount = total
            db.session.commit()
            
            # Enviar email de confirmação
            success = send_order_confirmation_email(order, sendcraft, pdf_generator)
            
            return jsonify({
                'success': True,
                'order_id': order.id,
                'order_number': order.order_number,
                'email_sent': success
            })
            
        except Exception as e:
            db.session.rollback()
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
            
            # Gerar número de tracking
            tracking_number = f"CT{datetime.now().strftime('%Y%m%d')}{str(uuid.uuid4())[:6].upper()}"
            
            # Atualizar status
            order.status = 'shipped'
            order.shipped_at = datetime.utcnow()
            
            # Enviar email de envio
            success = send_shipping_notification_email(order, tracking_number, sendcraft)
            
            if success:
                order.shipping_email_sent = True
                flash(f'Encomenda marcada como enviada. Email de notificação enviado.', 'success')
            else:
                flash(f'Encomenda marcada como enviada, mas falha no envio do email.', 'warning')
            
            db.session.commit()
            
            return redirect(url_for('dashboard'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao processar envio: {str(e)}', 'error')
            return redirect(url_for('dashboard'))
    
    @app.route('/dashboard')
    def dashboard():
        """Dashboard administrativo"""
        orders = Order.query.order_by(Order.created_at.desc()).limit(50).all()
        
        # Estatísticas básicas
        total_orders = Order.query.count()
        total_revenue = db.session.query(db.func.sum(Order.total_amount)).scalar() or 0
        pending_orders = Order.query.filter_by(status='confirmed').count()
        shipped_orders = Order.query.filter_by(status='shipped').count()
        
        stats = {
            'total_orders': total_orders,
            'total_revenue': total_revenue,
            'pending_orders': pending_orders,
            'shipped_orders': shipped_orders
        }
        
        return render_template('shop/dashboard.html', orders=orders, stats=stats)
    
    @app.route('/marketing', methods=['GET', 'POST'])
    def marketing():
        """Campanhas de marketing"""
        if request.method == 'GET':
            return render_template('shop/marketing.html')
        
        try:
            data = request.get_json()
            
            # Obter emails de clientes
            customers = Customer.query.all()
            recipient_emails = [customer.email for customer in customers]
            
            if not recipient_emails:
                return jsonify({'success': False, 'error': 'Nenhum cliente encontrado'})
            
            # Enviar campanha
            campaign_data = {
                'campaign_id': str(uuid.uuid4()),
                'title': data.get('title', 'Oferta Especial TechStore'),
                'subtitle': data.get('subtitle', 'Não perca esta oportunidade!'),
                'description': data.get('description', 'Aproveite descontos incríveis!'),
                'discount': data.get('discount', '20'),
                'cta_text': data.get('cta_text', 'Ver Ofertas'),
                'cta_link': data.get('cta_link', 'https://techstore.exemplo.com'),
                'valid_until': data.get('valid_until', '31 de Dezembro')
            }
            
            success, result = sendcraft.send_marketing_campaign(recipient_emails, campaign_data)
            
            return jsonify({
                'success': success,
                'message': 'Campanha enviada com sucesso!' if success else 'Falha no envio da campanha',
                'details': result,
                'recipients_count': len(recipient_emails)
            })
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/generate-test-data')
    def generate_test_data():
        """Gerar dados de teste"""
        try:
            # Gerar clientes fake
            for _ in range(10):
                customer = Customer(
                    name=fake.name(),
                    email=fake.email(),
                    phone=fake.phone_number(),
                    address=fake.address()
                )
                db.session.add(customer)
            
            db.session.commit()
            flash('Dados de teste gerados com sucesso!', 'success')
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao gerar dados: {str(e)}', 'error')
        
        return redirect(url_for('dashboard'))
    
    def send_order_confirmation_email(order, sendcraft_client, pdf_gen):
        """Enviar email de confirmação de encomenda"""
        try:
            # Preparar dados da encomenda
            order_data = {
                'order_number': order.order_number,
                'order_date': order.created_at.strftime('%d/%m/%Y'),
                'customer_name': order.customer.name,
                'customer_email': order.customer.email,
                'customer_address': order.customer.address,
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
            
            # Gerar PDF da fatura
            pdf_content = pdf_gen.generate_invoice(order_data)
            
            # Enviar email
            success, result = sendcraft_client.send_order_confirmation(order_data, pdf_content)
            
            if success:
                order.confirmation_email_sent = True
                order.confirmation_message_id = result.get('message_id')
                db.session.commit()
            
            return success
            
        except Exception as e:
            print(f"Erro ao enviar email de confirmação: {e}")
            return False
    
    def send_shipping_notification_email(order, tracking_number, sendcraft_client):
        """Enviar email de notificação de envio"""
        try:
            # Preparar dados da encomenda
            order_data = {
                'order_number': order.order_number,
                'customer_name': order.customer.name,
                'customer_email': order.customer.email,
                'total': order.total_amount
            }
            
            # Enviar email
            success, result = sendcraft_client.send_shipping_notification(order_data, tracking_number)
            
            if success:
                order.shipping_email_sent = True
                order.shipping_message_id = result.get('message_id')
                db.session.commit()
            
            return success
            
        except Exception as e:
            print(f"Erro ao enviar email de envio: {e}")
            return False
    
    @app.before_first_request
    def init_db():
        """Inicializar BD na primeira requisição"""
        db.create_all()
        
        # Produtos de exemplo
        if Product.query.count() == 0:
            products = [
                Product(name='Smartphone XYZ Pro', description='Smartphone de última geração com câmara de 108MP', price=699.99, category='Smartphones', stock=25),
                Product(name='Laptop Gaming Elite', description='Laptop gaming com RTX 4070 e 32GB RAM', price=1899.99, category='Laptops', stock=10),
                Product(name='Headphones ANC Premium', description='Auscultadores com cancelamento ativo de ruído', price=299.99, category='Áudio', stock=50),
                Product(name='Smartwatch Pro Sport', description='Relógio inteligente com GPS e monitor cardíaco', price=399.99, category='Wearables', stock=30),
                Product(name='Tablet Ultra 12"', description='Tablet de 12 polegadas para criatividade', price=799.99, category='Tablets', stock=20),
                Product(name='Webcam 4K Ultra', description='Webcam profissional 4K para streaming', price=199.99, category='Acessórios', stock=40),
                Product(name='Teclado Mecânico RGB', description='Teclado mecânico gaming com iluminação RGB', price=149.99, category='Acessórios', stock=60),
                Product(name='Monitor 27" 4K', description='Monitor profissional 4K IPS de 27 polegadas', price=499.99, category='Monitores', stock=15),
            ]
            
            for product in products:
                db.session.add(product)
            
            db.session.commit()
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5001)  # Porta diferente do SendCraft
```

---

### 🎨 **FASE 6: TEMPLATES HTML (45 min)**

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
        .navbar-brand {
            font-weight: bold;
            font-size: 1.5rem;
        }
        .product-card {
            transition: transform 0.2s;
        }
        .product-card:hover {
            transform: translateY(-5px);
        }
        .stats-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .order-status {
            font-size: 0.875rem;
            padding: 0.25rem 0.5rem;
            border-radius: 0.375rem;
        }
        .status-pending { background-color: #ffc107; color: #000; }
        .status-confirmed { background-color: #28a745; color: #fff; }
        .status-shipped { background-color: #007bff; color: #fff; }
        .status-delivered { background-color: #6f42c1; color: #fff; }
        .status-cancelled { background-color: #dc3545; color: #fff; }
    </style>
</head>
<body>
    <!-- Navigation -->
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container">
            <a class="navbar-brand" href="{{ url_for('index') }}">
                <i class="bi bi-laptop"></i> TechStore
            </a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav me-auto">
                    <li class="nav-item">
                        <a class="nav-link" href="{{ url_for('index') }}">
                            <i class="bi bi-shop"></i> Loja
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="{{ url_for('dashboard') }}">
                            <i class="bi bi-graph-up"></i> Dashboard
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="{{ url_for('marketing') }}">
                            <i class="bi bi-megaphone"></i> Marketing
                        </a>
                    </li>
                </ul>
                <ul class="navbar-nav">
                    <li class="nav-item">
                        <a class="nav-link" href="{{ url_for('generate_test_data') }}">
                            <i class="bi bi-database-add"></i> Gerar Dados
                        </a>
                    </li>
                </ul>
            </div>
        </div>
    </nav>

    <!-- Flash Messages -->
    {% with messages = get_flashed_messages(with_categories=true) %}
        {% if messages %}
            <div class="container mt-3">
                {% for category, message in messages %}
                    <div class="alert alert-{{ 'danger' if category == 'error' else category }} alert-dismissible fade show" role="alert">
                        {{ message }}
                        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                    </div>
                {% endfor %}
            </div>
        {% endif %}
    {% endwith %}

    <!-- Main Content -->
    <main>
        {% block content %}{% endblock %}
    </main>

    <!-- Footer -->
    <footer class="bg-dark text-light mt-5 py-4">
        <div class="container">
            <div class="row">
                <div class="col-md-6">
                    <h5>TechStore - E-commerce Simulator</h5>
                    <p>Demonstração de integração com SendCraft API</p>
                </div>
                <div class="col-md-6 text-md-end">
                    <p>Powered by SendCraft Email API</p>
                    <p><small>Phase 17 - Integration Showcase</small></p>
                </div>
            </div>
        </div>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // Global functions
        function showAlert(message, type = 'info') {
            const alertDiv = document.createElement('div');
            alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
            alertDiv.innerHTML = `
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            `;
            
            const container = document.querySelector('.container');
            if (container) {
                container.insertBefore(alertDiv, container.firstChild);
            }
            
            // Auto hide after 5 seconds
            setTimeout(() => {
                alertDiv.remove();
            }, 5000);
        }

        function formatPrice(price) {
            return new Intl.NumberFormat('pt-PT', {
                style: 'currency',
                currency: 'EUR'
            }).format(price);
        }
    </script>
    
    {% block scripts %}{% endblock %}
</body>
</html>
```

#### 6.2 Página Principal da Loja
```html
<!-- templates/shop/index.html -->
{% extends "shop/base.html" %}

{% block title %}TechStore - Loja Online{% endblock %}

{% block content %}
<div class="container my-5">
    <!-- Hero Section -->
    <div class="row mb-5">
        <div class="col-12">
            <div class="bg-primary text-white rounded-3 p-5 text-center">
                <h1 class="display-4 fw-bold">🚀 TechStore</h1>
                <p class="lead">E-commerce Simulator com Integração SendCraft</p>
                <p>Demonstração completa de emails transacionais e marketing</p>
                <a href="#produtos" class="btn btn-light btn-lg">
                    <i class="bi bi-arrow-down"></i> Ver Produtos
                </a>
            </div>
        </div>
    </div>

    <!-- Products Section -->
    <div id="produtos" class="row mb-5">
        <div class="col-12 mb-4">
            <h2 class="text-center mb-4">
                <i class="bi bi-laptop"></i> Nossos Produtos
            </h2>
        </div>
        
        {% for product in products %}
        <div class="col-md-6 col-lg-4 mb-4">
            <div class="card product-card h-100 shadow-sm">
                <div class="card-img-top bg-light d-flex align-items-center justify-content-center" style="height: 200px;">
                    <i class="bi bi-{{ 'phone' if 'Smartphone' in product.name else 'laptop' if 'Laptop' in product.name else 'headphones' if 'Headphones' in product.name else 'smartwatch' if 'Smartwatch' in product.name else 'tablet' if 'Tablet' in product.name else 'camera-video' if 'Webcam' in product.name else 'keyboard' if 'Teclado' in product.name else 'display' }} text-primary" style="font-size: 3rem;"></i>
                </div>
                <div class="card-body d-flex flex-column">
                    <h5 class="card-title">{{ product.name }}</h5>
                    <p class="card-text text-muted small flex-grow-1">{{ product.description }}</p>
                    <div class="d-flex justify-content-between align-items-center mb-2">
                        <span class="h5 text-primary mb-0">€{{ "%.2f"|format(product.price) }}</span>
                        <span class="badge bg-secondary">{{ product.category }}</span>
                    </div>
                    <div class="d-flex justify-content-between align-items-center">
                        <small class="text-muted">Stock: {{ product.stock }}</small>
                        <button class="btn btn-primary btn-sm" onclick="addToCart({{ product.id }})">
                            <i class="bi bi-cart-plus"></i> Adicionar
                        </button>
                    </div>
                </div>
            </div>
        </div>
        {% endfor %}
    </div>

    <!-- Cart Section -->
    <div class="row">
        <div class="col-12">
            <div class="card">
                <div class="card-header bg-success text-white">
                    <h4 class="mb-0">
                        <i class="bi bi-cart"></i> Carrinho de Compras
                        <span id="cart-count" class="badge bg-light text-dark ms-2">0</span>
                    </h4>
                </div>
                <div class="card-body">
                    <div id="cart-items">
                        <p class="text-muted text-center">Carrinho vazio</p>
                    </div>
                    <div id="cart-total" class="d-none">
                        <hr>
                        <div class="d-flex justify-content-between align-items-center">
                            <h5>Total: <span id="total-amount">€0.00</span></h5>
                            <button class="btn btn-success btn-lg" onclick="proceedToCheckout()">
                                <i class="bi bi-credit-card"></i> Finalizar Compra
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Integration Info -->
    <div class="row mt-5">
        <div class="col-12">
            <div class="alert alert-info">
                <h5><i class="bi bi-info-circle"></i> Como Funciona a Integração</h5>
                <p class="mb-2">Esta demonstração mostra como integrar o <strong>SendCraft</strong> num e-commerce real:</p>
                <ul class="mb-0">
                    <li><strong>Confirmação de Encomenda:</strong> Email automático com fatura PDF em anexo</li>
                    <li><strong>Notificação de Envio:</strong> Email com número de tracking</li>
                    <li><strong>Campanhas de Marketing:</strong> Newsletters em bulk para clientes</li>
                    <li><strong>Webhooks:</strong> Notificações real-time de eventos de email</li>
                </ul>
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
        cart.push({
            product_id: productId,
            product: product,
            quantity: 1
        });
    }
    
    updateCartDisplay();
    showAlert(`${product.name} adicionado ao carrinho!`, 'success');
}

function removeFromCart(productId) {
    cart = cart.filter(item => item.product_id !== productId);
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
    let html = '<div class="row">';
    
    cart.forEach(item => {
        const subtotal = item.quantity * item.product.price;
        total += subtotal;
        
        html += `
            <div class="col-12 mb-2">
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <strong>${item.product.name}</strong>
                        <br>
                        <small class="text-muted">€${item.product.price.toFixed(2)} × ${item.quantity}</small>
                    </div>
                    <div class="text-end">
                        <div>€${subtotal.toFixed(2)}</div>
                        <button class="btn btn-outline-danger btn-sm" onclick="removeFromCart(${item.product_id})">
                            <i class="bi bi-trash"></i>
                        </button>
                    </div>
                </div>
            </div>
        `;
    });
    
    html += '</div>';
    cartItems.innerHTML = html;
    totalAmount.textContent = formatPrice(total);
    cartTotal.classList.remove('d-none');
}

function proceedToCheckout() {
    if (cart.length === 0) {
        showAlert('Carrinho vazio!', 'warning');
        return;
    }
    
    // Simular processo de checkout
    const customerName = prompt('Nome do cliente:') || 'Cliente Teste';
    const customerEmail = prompt('Email do cliente:') || 'geral@artnshine.pt';
    
    if (!customerEmail) {
        showAlert('Email é obrigatório!', 'warning');
        return;
    }
    
    const orderData = {
        customer: {
            name: customerName,
            email: customerEmail,
            phone: '+351 123 456 789',
            address: 'Rua de Teste, 123, Lisboa, Portugal'
        },
        items: cart.map(item => ({
            product_id: item.product_id,
            quantity: item.quantity
        }))
    };
    
    // Enviar encomenda
    fetch('/checkout', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(orderData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showAlert(`Encomenda ${data.order_number} criada com sucesso! ${data.email_sent ? 'Email de confirmação enviado.' : 'Falha no envio do email.'}`, 'success');
            cart = [];
            updateCartDisplay();
            
            // Redirecionar para dashboard após 3 segundos
            setTimeout(() => {
                window.location.href = '/dashboard';
            }, 3000);
        } else {
            showAlert(`Erro ao criar encomenda: ${data.error}`, 'danger');
        }
    })
    .catch(error => {
        showAlert(`Erro: ${error.message}`, 'danger');
    });
}
</script>
{% endblock %}
```

---

## ✅ **CRITÉRIO DE SUCESSO FINAL**

A **Phase 17 está COMPLETA** quando:

1. **E-commerce Simulator rodando** em `http://localhost:5001`
2. **SendCraft API rodando** em `http://localhost:5000` 
3. **Encomenda criada** na loja gera email automático
4. **Email recebido** na caixa `geral@artnshine.pt`
5. **PDF da fatura** anexado corretamente
6. **Dashboard** mostra estatísticas reais
7. **Campanha de marketing** enviada em bulk

**🎯 Integration Showcase Complete! E-commerce + SendCraft = Success! 🚀**