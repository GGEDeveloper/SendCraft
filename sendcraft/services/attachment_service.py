"""
Serviço de Gestão de Anexos para SendCraft Phase 15
Gerencia upload, validação e armazenamento de anexos
"""
import os
import base64
import uuid
import hashlib
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from pathlib import Path

from ..extensions import db
from ..utils.logging import get_logger

logger = get_logger(__name__)


class AttachmentService:
    """Serviço para gestão de anexos."""
    
    def __init__(self, upload_dir: str = None):
        """
        Inicializa serviço de anexos.
        
        Args:
            upload_dir: Diretório para uploads (opcional)
        """
        self.upload_dir = upload_dir or os.path.join(os.getcwd(), 'uploads', 'attachments')
        self._ensure_upload_dir()
    
    def _ensure_upload_dir(self) -> None:
        """Garante que o diretório de upload existe."""
        Path(self.upload_dir).mkdir(parents=True, exist_ok=True)
    
    def validate_attachment(self, attachment: Dict[str, Any]) -> Dict[str, Any]:
        """
        Valida um anexo individual.
        
        Args:
            attachment: Dados do anexo
            
        Returns:
            Dict com resultado da validação
        """
        # Configurações de validação
        max_file_size = 10 * 1024 * 1024  # 10MB
        allowed_types = [
            'application/pdf',
            'image/jpeg', 
            'image/png',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',  # DOCX
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',  # XLSX
            'text/plain'
        ]
        
        # Verificar campos obrigatórios
        required_fields = ['filename', 'content_type', 'content']
        missing_fields = [field for field in required_fields if not attachment.get(field)]
        
        if missing_fields:
            return {
                'valid': False,
                'message': f'Missing required fields: {", ".join(missing_fields)}',
                'details': {'missing_fields': missing_fields}
            }
        
        # Verificar tipo de conteúdo
        if attachment['content_type'] not in allowed_types:
            return {
                'valid': False,
                'message': f'Content type {attachment["content_type"]} not allowed',
                'details': {
                    'content_type': attachment['content_type'],
                    'allowed_types': allowed_types
                }
            }
        
        # Verificar tamanho do arquivo
        try:
            content_bytes = base64.b64decode(attachment['content'])
            size_bytes = len(content_bytes)
            size_mb = size_bytes / (1024 * 1024)
            
            if size_bytes > max_file_size:
                return {
                    'valid': False,
                    'message': f'Attachment exceeds {max_file_size // (1024*1024)}MB limit',
                    'details': {
                        'filename': attachment['filename'],
                        'size_mb': round(size_mb, 2),
                        'max_allowed_mb': max_file_size // (1024*1024)
                    }
                }
            
            return {
                'valid': True,
                'message': 'Attachment validated successfully',
                'details': {
                    'filename': attachment['filename'],
                    'content_type': attachment['content_type'],
                    'size_bytes': size_bytes,
                    'size_mb': round(size_mb, 2)
                }
            }
            
        except Exception as e:
            return {
                'valid': False,
                'message': f'Invalid base64 content: {str(e)}',
                'details': {'filename': attachment['filename']}
            }
    
    def validate_attachments(self, attachments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Valida lista de anexos.
        
        Args:
            attachments: Lista de anexos
            
        Returns:
            Dict com resultado da validação
        """
        if not isinstance(attachments, list):
            return {
                'valid': False,
                'message': 'Attachments must be an array',
                'details': {'type': type(attachments).__name__}
            }
        
        if len(attachments) == 0:
            return {'valid': True, 'message': 'No attachments to validate'}
        
        total_size = 0
        max_total_size = 50 * 1024 * 1024  # 50MB total
        
        for i, attachment in enumerate(attachments):
            result = self.validate_attachment(attachment)
            if not result['valid']:
                result['details']['attachment_index'] = i
                return result
            
            total_size += result['details']['size_bytes']
        
        if total_size > max_total_size:
            return {
                'valid': False,
                'message': f'Total attachment size exceeds {max_total_size // (1024*1024)}MB limit',
                'details': {
                    'total_size_mb': round(total_size / (1024*1024), 2),
                    'max_allowed_mb': max_total_size // (1024*1024)
                }
            }
        
        return {
            'valid': True,
            'message': f'All {len(attachments)} attachments validated successfully',
            'details': {
                'count': len(attachments),
                'total_size_mb': round(total_size / (1024*1024), 2)
            }
        }
    
    def upload_attachment(self, attachment: Dict[str, Any], expires_hours: int = 24) -> Dict[str, Any]:
        """
        Faz upload de um anexo.
        
        Args:
            attachment: Dados do anexo
            expires_hours: Horas até expirar
            
        Returns:
            Dict com resultado do upload
        """
        try:
            # Validar anexo
            validation = self.validate_attachment(attachment)
            if not validation['valid']:
                return {
                    'success': False,
                    'error': 'validation_failed',
                    'message': validation['message'],
                    'details': validation['details']
                }
            
            # Decodificar conteúdo
            content_bytes = base64.b64decode(attachment['content'])
            
            # Gerar ID único
            attachment_id = f"ATT-{int(datetime.utcnow().timestamp())}-{uuid.uuid4().hex[:6].upper()}"
            
            # Gerar hash para verificação de integridade
            content_hash = hashlib.sha256(content_bytes).hexdigest()
            
            # Criar nome de arquivo único
            file_extension = Path(attachment['filename']).suffix
            unique_filename = f"{attachment_id}{file_extension}"
            file_path = os.path.join(self.upload_dir, unique_filename)
            
            # Salvar arquivo
            with open(file_path, 'wb') as f:
                f.write(content_bytes)
            
            # Calcular expiração
            expires_at = datetime.utcnow() + timedelta(hours=expires_hours)
            
            # TODO: Salvar metadados no banco de dados
            # Por enquanto, retornar informações básicas
            
            logger.info(f"Attachment uploaded: {attachment_id} ({validation['details']['size_mb']:.2f}MB)")
            
            return {
                'success': True,
                'attachment_id': attachment_id,
                'filename': attachment['filename'],
                'size_mb': validation['details']['size_mb'],
                'expires_at': expires_at.isoformat() + 'Z',
                'file_path': file_path,
                'content_hash': content_hash
            }
            
        except Exception as e:
            logger.error(f"Attachment upload error: {e}", exc_info=True)
            return {
                'success': False,
                'error': 'upload_failed',
                'message': str(e)
            }
    
    def get_attachment(self, attachment_id: str) -> Optional[Dict[str, Any]]:
        """
        Recupera um anexo pelo ID.
        
        Args:
            attachment_id: ID do anexo
            
        Returns:
            Dict com dados do anexo ou None
        """
        try:
            # TODO: Implementar busca no banco de dados
            # Por enquanto, buscar por arquivo
            if not attachment_id.startswith('ATT-'):
                return None
            
            # Buscar arquivo no diretório
            for filename in os.listdir(self.upload_dir):
                if filename.startswith(attachment_id):
                    file_path = os.path.join(self.upload_dir, filename)
                    
                    if os.path.exists(file_path):
                        # Ler arquivo
                        with open(file_path, 'rb') as f:
                            content_bytes = f.read()
                        
                        # Codificar em base64
                        content_b64 = base64.b64encode(content_bytes).decode('utf-8')
                        
                        # Determinar content type
                        content_type = self._get_content_type(filename)
                        
                        return {
                            'attachment_id': attachment_id,
                            'filename': filename,
                            'content_type': content_type,
                            'content': content_b64,
                            'size_bytes': len(content_bytes),
                            'size_mb': len(content_bytes) / (1024 * 1024)
                        }
            
            return None
            
        except Exception as e:
            logger.error(f"Get attachment error: {e}", exc_info=True)
            return None
    
    def delete_attachment(self, attachment_id: str) -> bool:
        """
        Remove um anexo.
        
        Args:
            attachment_id: ID do anexo
            
        Returns:
            True se removido com sucesso
        """
        try:
            # TODO: Implementar remoção do banco de dados
            # Por enquanto, remover arquivo
            if not attachment_id.startswith('ATT-'):
                return False
            
            # Buscar e remover arquivo
            for filename in os.listdir(self.upload_dir):
                if filename.startswith(attachment_id):
                    file_path = os.path.join(self.upload_dir, filename)
                    
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        logger.info(f"Attachment deleted: {attachment_id}")
                        return True
            
            return False
            
        except Exception as e:
            logger.error(f"Delete attachment error: {e}", exc_info=True)
            return False
    
    def cleanup_expired_attachments(self) -> int:
        """
        Remove anexos expirados.
        
        Returns:
            Número de anexos removidos
        """
        try:
            # TODO: Implementar limpeza baseada em banco de dados
            # Por enquanto, limpar arquivos antigos (24h+)
            removed_count = 0
            cutoff_time = datetime.utcnow() - timedelta(hours=24)
            
            for filename in os.listdir(self.upload_dir):
                if filename.startswith('ATT-'):
                    file_path = os.path.join(self.upload_dir, filename)
                    
                    if os.path.exists(file_path):
                        file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                        
                        if file_time < cutoff_time:
                            os.remove(file_path)
                            removed_count += 1
                            logger.info(f"Expired attachment removed: {filename}")
            
            if removed_count > 0:
                logger.info(f"Cleaned up {removed_count} expired attachments")
            
            return removed_count
            
        except Exception as e:
            logger.error(f"Cleanup expired attachments error: {e}", exc_info=True)
            return 0
    
    def _get_content_type(self, filename: str) -> str:
        """
        Determina content type baseado na extensão.
        
        Args:
            filename: Nome do arquivo
            
        Returns:
            Content type
        """
        extension = Path(filename).suffix.lower()
        
        content_types = {
            '.pdf': 'application/pdf',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            '.txt': 'text/plain'
        }
        
        return content_types.get(extension, 'application/octet-stream')
    
    def prepare_attachments_for_smtp(self, attachments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Prepara anexos para envio SMTP.
        
        Args:
            attachments: Lista de anexos (pode incluir attachment_id ou content)
            
        Returns:
            Lista de anexos preparados para SMTP
        """
        prepared_attachments = []
        
        for attachment in attachments:
            try:
                # Se tem attachment_id, buscar anexo
                if 'attachment_id' in attachment:
                    stored_attachment = self.get_attachment(attachment['attachment_id'])
                    if stored_attachment:
                        prepared_attachments.append({
                            'filename': stored_attachment['filename'],
                            'content_type': stored_attachment['content_type'],
                            'content': base64.b64decode(stored_attachment['content'])
                        })
                    else:
                        logger.warning(f"Attachment not found: {attachment['attachment_id']}")
                
                # Se tem content direto, usar
                elif 'content' in attachment:
                    content_bytes = base64.b64decode(attachment['content'])
                    prepared_attachments.append({
                        'filename': attachment['filename'],
                        'content_type': attachment['content_type'],
                        'content': content_bytes
                    })
                
            except Exception as e:
                logger.warning(f"Failed to prepare attachment: {e}")
        
        return prepared_attachments
