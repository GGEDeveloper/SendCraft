"""Routes para gestão de templates de email."""
from flask import render_template, request, redirect, url_for, flash, jsonify
import json
from . import web_bp
from ..models import Domain, EmailTemplate, EmailLog
from ..services.template_service import TemplateService
from ..extensions import db
from ..utils.logging import get_logger

logger = get_logger(__name__)


@web_bp.route('/templates')
def templates_list():
    """Lista todos os templates."""
    try:
        # Filtrar por domínio se especificado
        domain_id = request.args.get('domain_id', type=int)
        category = request.args.get('category')
        
        query = EmailTemplate.query
        
        if domain_id:
            domain = Domain.query.get_or_404(domain_id)
            query = query.filter_by(domain_id=domain_id)
            title = f"Templates de {domain.name}"
        else:
            title = "Todos os Templates"
            domain = None
        
        if category:
            query = query.filter_by(category=category)
        
        templates = query.all()
        
        # Adicionar estatísticas para cada template
        templates_data = []
        for template in templates:
            # Contar uso do template
            usage_count = EmailLog.query.filter_by(template_id=template.id).count()
            
            templates_data.append({
                'id': template.id,
                'template_key': template.template_key,
                'template_name': template.template_name,
                'domain_name': template.domain.name,
                'category': template.category,
                'version': template.version,
                'is_active': template.is_active,
                'variables_required': template.variables_required,
                'variables_optional': template.variables_optional,
                'usage_count': usage_count,
                'created_at': template.created_at,
                'updated_at': template.updated_at
            })
        
        # Categorias únicas para filtro
        categories = db.session.query(EmailTemplate.category).distinct().all()
        categories = [c[0] for c in categories if c[0]]
        
        return render_template('templates/list.html',
                             templates=templates_data,
                             title=title,
                             domain=domain,
                             categories=categories,
                             current_category=category)
    
    except Exception as e:
        logger.error(f"Error listing templates: {e}", exc_info=True)
        flash('Erro ao carregar templates', 'danger')
        return redirect(url_for('web.dashboard'))


@web_bp.route('/templates/<int:template_id>')
def template_detail(template_id):
    """Detalhes de um template."""
    try:
        template = EmailTemplate.query.get_or_404(template_id)
        
        # Extrair variáveis usadas
        variables_detected = template.extract_variables()
        
        # Contar uso do template
        usage_count = EmailLog.query.filter_by(template_id=template.id).count()
        
        # Logs recentes que usaram este template
        recent_logs = EmailLog.query.filter_by(
            template_id=template_id
        ).order_by(EmailLog.created_at.desc()).limit(10).all()
        
        return render_template('templates/detail.html',
                             template=template,
                             variables_detected=variables_detected,
                             usage_count=usage_count,
                             recent_logs=recent_logs)
    
    except Exception as e:
        logger.error(f"Error loading template {template_id}: {e}", exc_info=True)
        flash('Erro ao carregar detalhes do template', 'danger')
        return redirect(url_for('web.templates_list'))


@web_bp.route('/templates/new', methods=['GET', 'POST'])
def template_new():
    """Criar novo template."""
    # Buscar domínios para o select
    domains = Domain.query.filter_by(is_active=True).all()
    
    if request.method == 'POST':
        try:
            domain_id = request.form.get('domain_id', type=int)
            template_key = request.form.get('template_key', '').strip()
            template_name = request.form.get('template_name', '').strip()
            description = request.form.get('description', '').strip()
            category = request.form.get('category', 'general').strip()
            subject_template = request.form.get('subject_template', '').strip()
            html_template = request.form.get('html_template', '').strip()
            text_template = request.form.get('text_template', '').strip()
            
            # Variáveis
            variables_required = request.form.get('variables_required', '').strip()
            variables_optional = request.form.get('variables_optional', '').strip()
            
            # Converter variáveis para lista
            if variables_required:
                variables_required = [v.strip() for v in variables_required.split(',')]
            else:
                variables_required = []
            
            if variables_optional:
                variables_optional = [v.strip() for v in variables_optional.split(',')]
            else:
                variables_optional = []
            
            # Validações
            if not domain_id or not template_key or not template_name or not subject_template:
                flash('Campos obrigatórios: domínio, chave, nome e assunto', 'danger')
                return render_template('templates/form.html', template=None, domains=domains)
            
            domain = Domain.query.get(domain_id)
            if not domain:
                flash('Domínio inválido', 'danger')
                return render_template('templates/form.html', template=None, domains=domains)
            
            # Verificar se já existe
            if EmailTemplate.get_by_key(domain_id, template_key):
                flash(f'Template {template_key} já existe para este domínio', 'danger')
                return render_template('templates/form.html', template=None, domains=domains)
            
            # Criar template usando o serviço
            template_service = TemplateService()
            success, message, template = template_service.create_template(
                domain_name=domain.name,
                template_key=template_key,
                template_name=template_name,
                subject_template=subject_template,
                html_template=html_template,
                text_template=text_template,
                description=description,
                category=category,
                variables_required=variables_required,
                variables_optional=variables_optional
            )
            
            if success:
                flash(f'Template {template_name} criado com sucesso!', 'success')
                logger.info(f"Template {template_key} created with ID {template.id}")
                return redirect(url_for('web.template_detail', template_id=template.id))
            else:
                flash(f'Erro ao criar template: {message}', 'danger')
                return render_template('templates/form.html', template=None, domains=domains)
            
        except Exception as e:
            logger.error(f"Error creating template: {e}", exc_info=True)
            flash('Erro ao criar template', 'danger')
            db.session.rollback()
    
    return render_template('templates/form.html', template=None, domains=domains)


@web_bp.route('/templates/<int:template_id>/edit', methods=['GET', 'POST'])
def template_edit(template_id):
    """Editar template."""
    template = EmailTemplate.query.get_or_404(template_id)
    domains = Domain.query.filter_by(is_active=True).all()
    
    if request.method == 'POST':
        try:
            template.template_name = request.form.get('template_name', '').strip()
            template.description = request.form.get('description', '').strip()
            template.category = request.form.get('category', 'general').strip()
            template.subject_template = request.form.get('subject_template', '').strip()
            template.html_template = request.form.get('html_template', '').strip()
            template.text_template = request.form.get('text_template', '').strip()
            template.is_active = request.form.get('is_active') == 'on'
            
            # Variáveis
            variables_required = request.form.get('variables_required', '').strip()
            variables_optional = request.form.get('variables_optional', '').strip()
            
            # Converter variáveis para lista
            if variables_required:
                template.variables_required = [v.strip() for v in variables_required.split(',')]
            else:
                template.variables_required = []
            
            if variables_optional:
                template.variables_optional = [v.strip() for v in variables_optional.split(',')]
            else:
                template.variables_optional = []
            
            # Incrementar versão
            template.version += 1
            
            template.save()
            
            flash('Template atualizado com sucesso!', 'success')
            logger.info(f"Template {template.template_key} updated to version {template.version}")
            return redirect(url_for('web.template_detail', template_id=template.id))
            
        except Exception as e:
            logger.error(f"Error updating template {template_id}: {e}", exc_info=True)
            flash('Erro ao atualizar template', 'danger')
            db.session.rollback()
    
    return render_template('templates/form.html', template=template, domains=domains)


@web_bp.route('/templates/<int:template_id>/preview', methods=['GET', 'POST'])
def template_preview(template_id):
    """Preview de template com variáveis de teste."""
    template = EmailTemplate.query.get_or_404(template_id)
    
    if request.method == 'POST':
        try:
            # Obter variáveis do formulário
            variables = {}
            for key in request.form:
                if key.startswith('var_'):
                    var_name = key[4:]  # Remove 'var_' prefix
                    variables[var_name] = request.form[key]
            
            # Renderizar template
            try:
                rendered_subject = template.render_subject(variables)
                rendered_html = template.render_html(variables)
                rendered_text = template.render_text(variables)
                
                return jsonify({
                    'success': True,
                    'rendered': {
                        'subject': rendered_subject,
                        'html': rendered_html,
                        'text': rendered_text
                    }
                })
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': str(e)
                })
            
        except Exception as e:
            logger.error(f"Error previewing template {template_id}: {e}")
            return jsonify({
                'success': False,
                'error': 'Erro ao renderizar template'
            })
    
    # GET request - mostrar formulário de preview
    return render_template('templates/preview.html', template=template)


@web_bp.route('/templates/<int:template_id>/clone', methods=['POST'])
def template_clone(template_id):
    """Clonar template."""
    try:
        template = EmailTemplate.query.get_or_404(template_id)
        
        # Gerar nova chave
        new_key = f"{template.template_key}_copy"
        counter = 1
        while EmailTemplate.get_by_key(template.domain_id, new_key):
            new_key = f"{template.template_key}_copy{counter}"
            counter += 1
        
        # Usar serviço para clonar
        template_service = TemplateService()
        success, message, cloned = template_service.clone_template(
            domain_name=template.domain.name,
            template_key=template.template_key,
            new_key=new_key,
            new_name=f"{template.template_name} (Cópia)"
        )
        
        if success:
            flash(f'Template clonado com sucesso!', 'success')
            logger.info(f"Template {template.template_key} cloned to {new_key}")
            return redirect(url_for('web.template_detail', template_id=cloned.id))
        else:
            flash(f'Erro ao clonar template: {message}', 'danger')
            
    except Exception as e:
        logger.error(f"Error cloning template {template_id}: {e}", exc_info=True)
        flash('Erro ao clonar template', 'danger')
    
    return redirect(url_for('web.template_detail', template_id=template_id))


@web_bp.route('/templates/<int:template_id>/delete', methods=['POST'])
def template_delete(template_id):
    """Deletar template."""
    try:
        template = EmailTemplate.query.get_or_404(template_id)
        template_name = template.template_name
        domain_id = template.domain_id
        
        # Verificar se tem logs
        if template.logs.count() > 0:
            flash('Não é possível deletar template que já foi usado', 'warning')
            return redirect(url_for('web.template_detail', template_id=template_id))
        
        template.delete()
        
        flash(f'Template {template_name} deletado com sucesso!', 'success')
        logger.info(f"Template {template_name} deleted")
        return redirect(url_for('web.templates_list', domain_id=domain_id))
        
    except Exception as e:
        logger.error(f"Error deleting template {template_id}: {e}", exc_info=True)
        flash('Erro ao deletar template', 'danger')
        db.session.rollback()
        return redirect(url_for('web.template_detail', template_id=template_id))