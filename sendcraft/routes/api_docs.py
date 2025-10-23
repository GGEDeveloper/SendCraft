"""
API Documentation for SendCraft External API
Interactive documentation endpoint
"""
from flask import Blueprint, render_template_string

docs_bp = Blueprint('api_docs', __name__, url_prefix='/api/docs')


@docs_bp.route('', methods=['GET'])
def api_documentation():
    """
    API Documentation page.
    
    GET /api/docs
    
    Returns HTML documentation page
    """
    html_content = """
    <!DOCTYPE html>
    <html lang="pt">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>SendCraft API Documentation</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body { padding: 20px; background-color: #f8f9fa; }
            .endpoint-card { margin-bottom: 20px; }
            .method-badge { display: inline-block; padding: 4px 8px; border-radius: 4px; font-weight: bold; color: white; }
            .method-get { background-color: #0d6efd; }
            .method-post { background-color: #198754; }
            .code-block { background-color: #f1f3f5; padding: 15px; border-radius: 5px; overflow-x: auto; }
            pre { margin: 0; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1 class="mb-4">📧 SendCraft External API Documentation</h1>
            
            <div class="alert alert-info">
                <strong>Base URL:</strong> <code>https://sendcraft.dominios.pt/api/v1</code><br>
                <strong>Authentication:</strong> Bearer token in Authorization header
            </div>
            
            <h2 class="mt-5">Authentication</h2>
            <p>All API requests require authentication using an API key in the Authorization header:</p>
            <div class="code-block">
                <pre>Authorization: Bearer YOUR_API_KEY</pre>
            </div>
            
            <h2 class="mt-5">Endpoints</h2>
            
            <!-- Health Check -->
            <div class="endpoint-card card">
                <div class="card-header">
                    <span class="method-badge method-get">GET</span>
                    <strong>/health</strong>
                </div>
                <div class="card-body">
                    <p>Health check endpoint. No authentication required.</p>
                    <strong>Response:</strong>
                    <div class="code-block">
                        <pre>{
  "status": "healthy",
  "service": "SendCraft External API",
  "version": "1.0.0"
}</pre>
                    </div>
                </div>
            </div>
            
            <!-- Send Direct Email -->
            <div class="endpoint-card card">
                <div class="card-header">
                    <span class="method-badge method-post">POST</span>
                    <strong>/send/direct</strong>
                </div>
                <div class="card-body">
                    <p>Send email directly without using a template.</p>
                    <strong>Request Body:</strong>
                    <div class="code-block">
                        <pre>{
  "domain": "alitools.pt",
  "account": "encomendas",
  "to": "customer@example.com",
  "subject": "Order Confirmation",
  "html": "<h1>Thank you!</h1>",
  "text": "Thank you for your order!"
}</pre>
                    </div>
                    <strong>Response:</strong>
                    <div class="code-block">
                        <pre>{
  "success": true,
  "log_id": 123,
  "message": "Email sent successfully",
  "message_id": "&lt;message-id&gt;",
  "from": "encomendas@alitools.pt",
  "to": "customer@example.com",
  "subject": "Order Confirmation"
}</pre>
                    </div>
                </div>
            </div>
            
            <!-- Send Template Email -->
            <div class="endpoint-card card">
                <div class="card-header">
                    <span class="method-badge method-post">POST</span>
                    <strong>/send/template</strong>
                </div>
                <div class="card-body">
                    <p>Send email using a predefined template.</p>
                    <strong>Request Body:</strong>
                    <div class="code-block">
                        <pre>{
  "domain": "alitools.pt",
  "account": "encomendas",
  "template": "order_confirmation",
  "to": "customer@example.com",
  "variables": {
    "customer_name": "João Silva",
    "order_number": "ALI-2025-001",
    "total": "149.99"
  }
}</pre>
                    </div>
                    <strong>Response:</strong>
                    <div class="code-block">
                        <pre>{
  "success": true,
  "log_id": 123,
  "message": "Email sent successfully",
  "message_id": "&lt;message-id&gt;",
  "template_used": "order_confirmation",
  "variables_count": 3,
  "from": "encomendas@alitools.pt",
  "to": "customer@example.com"
}</pre>
                    </div>
                </div>
            </div>
            
            <!-- List Accounts -->
            <div class="endpoint-card card">
                <div class="card-header">
                    <span class="method-badge method-get">GET</span>
                    <strong>/accounts/&lt;domain&gt;</strong>
                </div>
                <div class="card-body">
                    <p>List all accounts for a domain.</p>
                    <strong>Example:</strong> <code>GET /accounts/alitools.pt</code>
                    <strong>Response:</strong>
                    <div class="code-block">
                        <pre>{
  "domain": "alitools.pt",
  "accounts": [
    {
      "email": "encomendas@alitools.pt",
      "display_name": "Encomendas",
      "is_active": true,
      "daily_limit": 1000,
      "monthly_limit": 20000,
      "emails_sent_today": 5,
      "emails_sent_this_month": 120
    }
  ],
  "count": 1
}</pre>
                    </div>
                </div>
            </div>
            
            <!-- List Templates -->
            <div class="endpoint-card card">
                <div class="card-header">
                    <span class="method-badge method-get">GET</span>
                    <strong>/templates/&lt;domain&gt;</strong>
                </div>
                <div class="card-body">
                    <p>List all templates for a domain.</p>
                    <strong>Example:</strong> <code>GET /templates/alitools.pt</code>
                    <strong>Response:</strong>
                    <div class="code-block">
                        <pre>{
  "domain": "alitools.pt",
  "templates": [
    {
      "key": "order_confirmation",
      "name": "Order Confirmation",
      "subject": "Order #{{order_number}} Confirmed",
      "category": "orders",
      "is_active": true,
      "required_variables": ["order_number", "customer_name"],
      "optional_variables": ["total", "payment_method"]
    }
  ],
  "count": 1
}</pre>
                    </div>
                </div>
            </div>
            
            <h2 class="mt-5">Error Codes</h2>
            <table class="table table-striped">
                <thead>
                    <tr>
                        <th>Code</th>
                        <th>Description</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td><code>200</code></td>
                        <td>Success</td>
                    </tr>
                    <tr>
                        <td><code>400</code></td>
                        <td>Bad Request - Invalid data or missing required fields</td>
                    </tr>
                    <tr>
                        <td><code>401</code></td>
                        <td>Unauthorized - Missing or invalid API key</td>
                    </tr>
                    <tr>
                        <td><code>404</code></td>
                        <td>Not Found - Resource not found</td>
                    </tr>
                    <tr>
                        <td><code>429</code></td>
                        <td>Too Many Requests - Account limit exceeded</td>
                    </tr>
                    <tr>
                        <td><code>500</code></td>
                        <td>Internal Server Error</td>
                    </tr>
                </tbody>
            </table>
            
            <h2 class="mt-5">Rate Limiting</h2>
            <p>Each account has daily and monthly limits. Check account limits before sending emails.</p>
            
            <div class="alert alert-warning mt-4">
                <strong>Note:</strong> Contact support to obtain an API key for production use.
            </div>
        </div>
    </body>
    </html>
    """
    return html_content

