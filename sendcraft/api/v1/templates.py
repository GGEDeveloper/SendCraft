"""Endpoints de gestão de templates."""
from flask import Blueprint, jsonify, request

from ...models import Domain, EmailTemplate
from ...services.auth_service import require_api_key
from ...utils.logging import get_logger

bp = Blueprint('templates', __name__, url_prefix='/templates')
logger = get_logger(__name__)


@bp.route('/<domain>', methods=['GET'])
@require_api_key
def list_templates(domain: str):
    """
    Lista templates de um domínio.
    
    Args:
        domain: Nome do domínio
    
    Query Parameters:
        category: Filtrar por categoria
        active_only: Se deve retornar apenas templates ativos (default: false)
    
    Returns:
        JSON response with list of templates
    """
    try:
        # Buscar domínio
        domain_obj = Domain.get_by_name(domain)
        if not domain_obj:
            return jsonify({
                'error': 'Domain not found',
                'message': f"Domain '{domain}' not found",
                'domain': domain,
                'templates': []
            }), 404
        
        # Parâmetros de query
        category_filter = request.args.get('category')
        active_only = request.args.get('active_only', 'false').lower() == 'true'
        
        # Construir query
        query = EmailTemplate.query.filter_by(domain_id=domain_obj.id)
        
        if category_filter:
            query = query.filter_by(category=category_filter)
        
        if active_only:
            query = query.filter_by(is_active=True)
        
        templates = query.all()
        
        # Serializar templates
        templates_data = []
        for tpl in templates:
            try:
                # Extrair variáveis usadas
                extracted_vars = tpl.extract_variables()
                all_vars = set()
                for var_list in extracted_vars.values():
                    all_vars.update(var_list)
                
                template_dict = {
                    'id': tpl.id,
                    'template_key': tpl.template_key,
                    'template_name': tpl.template_name,
                    'description': tpl.description,
                    'category': tpl.category,
                    'version': tpl.version,
                    'is_active': tpl.is_active,
                    'variables_required': tpl.variables_required,
                    'variables_optional': tpl.variables_optional,
                    'variables_detected': list(all_vars),
                    'created_at': tpl.created_at.isoformat() + 'Z',
                    'updated_at': tpl.updated_at.isoformat() + 'Z'
                }
                templates_data.append(template_dict)
            except Exception as e:
                logger.error(f"Error serializing template {tpl.id}: {e}")
                continue
        
        logger.info(f"Listed {len(templates_data)} templates for domain {domain}")
        
        return jsonify({
            'domain': domain,
            'domain_active': domain_obj.is_active,
            'total_templates': len(templates_data),
            'filters': {
                'category': category_filter,
                'active_only': active_only
            },
            'templates': templates_data
        })
        
    except Exception as e:
        logger.error(f"Error listing templates for domain {domain}: {e}", exc_info=True)
        return jsonify({
            'error': 'Internal server error',
            'message': 'Failed to retrieve templates'
        }), 500


@bp.route('/<domain>/<template_key>', methods=['GET'])
@require_api_key
def get_template(domain: str, template_key: str):
    """
    Obtém detalhes de um template específico.
    
    Args:
        domain: Nome do domínio
        template_key: Chave única do template
    
    Query Parameters:
        include_content: Se deve incluir o conteúdo dos templates (default: true)
    
    Returns:
        JSON response with template details
    """
    try:
        # Buscar domínio
        domain_obj = Domain.get_by_name(domain)
        if not domain_obj:
            return jsonify({
                'error': 'Domain not found',
                'message': f"Domain '{domain}' not found"
            }), 404
        
        # Buscar template
        template = EmailTemplate.get_by_key(domain_obj.id, template_key)
        if not template:
            return jsonify({
                'error': 'Template not found',
                'message': f"Template '{template_key}' not found for domain '{domain}'"
            }), 404
        
        # Verificar se deve incluir conteúdo
        include_content = request.args.get('include_content', 'true').lower() == 'true'
        
        # Extrair variáveis
        extracted_vars = template.extract_variables()
        all_vars = set()
        for var_list in extracted_vars.values():
            all_vars.update(var_list)
        
        # Serializar template
        template_data = {
            'id': template.id,
            'template_key': template.template_key,
            'template_name': template.template_name,
            'description': template.description,
            'category': template.category,
            'version': template.version,
            'is_active': template.is_active,
            'variables_required': template.variables_required,
            'variables_optional': template.variables_optional,
            'variables_detected': list(all_vars),
            'variables_by_section': extracted_vars,
            'domain': {
                'id': template.domain.id,
                'name': template.domain.name,
                'is_active': template.domain.is_active
            },
            'created_at': template.created_at.isoformat() + 'Z',
            'updated_at': template.updated_at.isoformat() + 'Z'
        }
        
        # Incluir conteúdo se solicitado
        if include_content:
            template_data['subject_template'] = template.subject_template
            template_data['html_template'] = template.html_template
            template_data['text_template'] = template.text_template
        
        logger.info(f"Retrieved template {template_key} for domain {domain}")
        
        return jsonify(template_data)
        
    except Exception as e:
        logger.error(f"Error getting template {template_key} for domain {domain}: {e}", exc_info=True)
        return jsonify({
            'error': 'Internal server error',
            'message': 'Failed to retrieve template details'
        }), 500


@bp.route('/<domain>/<template_key>/preview', methods=['POST'])
@require_api_key
def preview_template(domain: str, template_key: str):
    """
    Renderiza preview de um template com variáveis de teste.
    
    Args:
        domain: Nome do domínio
        template_key: Chave única do template
    
    JSON Body:
    {
        "variables": {
            "customer_name": "João Silva",
            "order_number": "#12345"
        }
    }
    
    Returns:
        JSON response with rendered template
    """
    try:
        # Buscar domínio
        domain_obj = Domain.get_by_name(domain)
        if not domain_obj:
            return jsonify({
                'error': 'Domain not found',
                'message': f"Domain '{domain}' not found"
            }), 404
        
        # Buscar template
        template = EmailTemplate.get_by_key(domain_obj.id, template_key)
        if not template:
            return jsonify({
                'error': 'Template not found',
                'message': f"Template '{template_key}' not found for domain '{domain}'"
            }), 404
        
        # Obter variáveis do body
        data = request.get_json() or {}
        variables = data.get('variables', {})
        
        # Validar variáveis
        is_valid, missing_vars = template.validate_variables(variables)
        
        # Renderizar template
        try:
            rendered_subject = template.render_subject(variables)
            rendered_html = template.render_html(variables)
            rendered_text = template.render_text(variables)
        except Exception as e:
            return jsonify({
                'error': 'Rendering error',
                'message': str(e)
            }), 400
        
        logger.info(f"Previewed template {template_key} for domain {domain}")
        
        return jsonify({
            'template_key': template_key,
            'template_name': template.template_name,
            'variables_provided': list(variables.keys()),
            'variables_required': template.variables_required,
            'variables_missing': missing_vars if not is_valid else [],
            'validation_passed': is_valid,
            'rendered': {
                'subject': rendered_subject,
                'html': rendered_html,
                'text': rendered_text
            }
        })
        
    except Exception as e:
        logger.error(f"Error previewing template {template_key}: {e}", exc_info=True)
        return jsonify({
            'error': 'Internal server error',
            'message': 'Failed to preview template'
        }), 500


@bp.route('', methods=['GET'])
@require_api_key
def list_all_templates():
    """
    Lista todos os templates do sistema.
    
    Query Parameters:
        domain: Filtrar por domínio
        category: Filtrar por categoria
        active_only: Se deve retornar apenas templates ativos (default: false)
        limit: Número máximo de resultados (default: 100)
        offset: Offset para paginação (default: 0)
    
    Returns:
        JSON response with list of all templates
    """
    try:
        # Parâmetros de query
        domain_filter = request.args.get('domain')
        category_filter = request.args.get('category')
        active_only = request.args.get('active_only', 'false').lower() == 'true'
        limit = min(int(request.args.get('limit', 100)), 500)  # Max 500
        offset = int(request.args.get('offset', 0))
        
        # Construir query
        query = EmailTemplate.query
        
        if domain_filter:
            domain_obj = Domain.get_by_name(domain_filter)
            if domain_obj:
                query = query.filter_by(domain_id=domain_obj.id)
        
        if category_filter:
            query = query.filter_by(category=category_filter)
        
        if active_only:
            query = query.filter_by(is_active=True)
        
        # Total antes de paginar
        total = query.count()
        
        # Aplicar paginação
        templates = query.limit(limit).offset(offset).all()
        
        # Serializar templates
        templates_data = []
        for tpl in templates:
            try:
                template_dict = {
                    'id': tpl.id,
                    'template_key': tpl.template_key,
                    'template_name': tpl.template_name,
                    'domain': tpl.domain.name,
                    'category': tpl.category,
                    'version': tpl.version,
                    'is_active': tpl.is_active,
                    'created_at': tpl.created_at.isoformat() + 'Z'
                }
                templates_data.append(template_dict)
            except Exception as e:
                logger.error(f"Error serializing template {tpl.id}: {e}")
                continue
        
        logger.info(f"Listed {len(templates_data)} templates (total: {total})")
        
        return jsonify({
            'total': total,
            'limit': limit,
            'offset': offset,
            'count': len(templates_data),
            'filters': {
                'domain': domain_filter,
                'category': category_filter,
                'active_only': active_only
            },
            'templates': templates_data
        })
        
    except ValueError as e:
        return jsonify({
            'error': 'Invalid parameters',
            'message': str(e)
        }), 400
        
    except Exception as e:
        logger.error(f"Error listing all templates: {e}", exc_info=True)
        return jsonify({
            'error': 'Internal server error',
            'message': 'Failed to retrieve templates'
        }), 500