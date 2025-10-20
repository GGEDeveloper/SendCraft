"""
Modelo base e mixins para SendCraft.
Fornece funcionalidades comuns para todos os modelos.
"""
from datetime import datetime
from typing import Dict, Any, Optional, TypeVar, Type
from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.ext.declarative import declared_attr

from ..extensions import db
from ..utils.logging import get_logger

logger = get_logger(__name__)

T = TypeVar('T', bound='BaseModel')


class TimestampMixin:
    """Mixin para timestamps automáticos."""
    
    created_at = Column(
        DateTime, 
        default=datetime.utcnow, 
        nullable=False,
        doc="Data e hora de criação do registro"
    )
    updated_at = Column(
        DateTime, 
        default=datetime.utcnow, 
        onupdate=datetime.utcnow, 
        nullable=False,
        doc="Data e hora da última atualização"
    )


class BaseModel(db.Model):
    """
    Modelo base para todos os modelos SendCraft.
    Fornece funcionalidades CRUD comuns e métodos utilitários.
    """
    
    __abstract__ = True
    
    id = Column(
        Integer, 
        primary_key=True,
        doc="Identificador único do registro"
    )
    
    def to_dict(self, include_relationships: bool = False) -> Dict[str, Any]:
        """
        Converte modelo para dicionário.
        
        Args:
            include_relationships: Se deve incluir relacionamentos
        
        Returns:
            Dicionário com os dados do modelo
        """
        result = {}
        
        # Incluir colunas
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            
            # Serializar datetime
            if isinstance(value, datetime):
                value = value.isoformat()
            
            result[column.name] = value
        
        # Incluir relacionamentos se solicitado
        if include_relationships:
            # Será implementado quando os modelos tiverem relacionamentos
            pass
        
        return result
    
    def update_from_dict(self, data: Dict[str, Any], skip_none: bool = True) -> None:
        """
        Atualiza modelo a partir de dicionário.
        
        Args:
            data: Dicionário com os dados
            skip_none: Se deve ignorar valores None
        """
        for key, value in data.items():
            # Verificar se o atributo existe e é uma coluna
            if hasattr(self, key) and key in self.__table__.columns:
                if value is not None or not skip_none:
                    setattr(self, key, value)
    
    @classmethod
    def create(cls: Type[T], commit: bool = True, **kwargs) -> T:
        """
        Cria e salva nova instância.
        
        Args:
            commit: Se deve fazer commit da transação
            **kwargs: Atributos do modelo
        
        Returns:
            Nova instância criada
        """
        try:
            instance = cls(**kwargs)
            db.session.add(instance)
            
            if commit:
                db.session.commit()
            else:
                db.session.flush()
            
            logger.info(f'Created {cls.__name__} with id {instance.id}')
            return instance
            
        except Exception as e:
            db.session.rollback()
            logger.error(f'Failed to create {cls.__name__}: {e}')
            raise
    
    def save(self, commit: bool = True) -> 'BaseModel':
        """
        Salva instância atual.
        
        Args:
            commit: Se deve fazer commit da transação
        
        Returns:
            Self para method chaining
        """
        try:
            db.session.add(self)
            
            if commit:
                db.session.commit()
            else:
                db.session.flush()
            
            logger.debug(f'Saved {self.__class__.__name__} with id {self.id}')
            return self
            
        except Exception as e:
            db.session.rollback()
            logger.error(f'Failed to save {self.__class__.__name__}: {e}')
            raise
    
    def delete(self, commit: bool = True) -> None:
        """
        Deleta instância atual.
        
        Args:
            commit: Se deve fazer commit da transação
        """
        try:
            db.session.delete(self)
            
            if commit:
                db.session.commit()
            else:
                db.session.flush()
            
            logger.info(f'Deleted {self.__class__.__name__} with id {self.id}')
            
        except Exception as e:
            db.session.rollback()
            logger.error(f'Failed to delete {self.__class__.__name__}: {e}')
            raise
    
    @classmethod
    def get_by_id(cls: Type[T], id: int) -> Optional[T]:
        """
        Busca registro por ID.
        
        Args:
            id: ID do registro
        
        Returns:
            Instância encontrada ou None
        """
        return cls.query.get(id)
    
    @classmethod
    def get_or_404(cls: Type[T], id: int) -> T:
        """
        Busca registro por ID ou retorna 404.
        
        Args:
            id: ID do registro
        
        Returns:
            Instância encontrada
        
        Raises:
            404 se não encontrado
        """
        return cls.query.get_or_404(id)
    
    @classmethod
    def get_all(cls: Type[T], **filters) -> list[T]:
        """
        Retorna todos os registros com filtros opcionais.
        
        Args:
            **filters: Filtros para aplicar na query
        
        Returns:
            Lista de instâncias
        """
        query = cls.query
        
        for key, value in filters.items():
            if hasattr(cls, key):
                query = query.filter(getattr(cls, key) == value)
        
        return query.all()
    
    @classmethod
    def count(cls: Type[T], **filters) -> int:
        """
        Conta registros com filtros opcionais.
        
        Args:
            **filters: Filtros para aplicar na query
        
        Returns:
            Número de registros
        """
        query = cls.query
        
        for key, value in filters.items():
            if hasattr(cls, key):
                query = query.filter(getattr(cls, key) == value)
        
        return query.count()
    
    def __repr__(self) -> str:
        """Representação string do modelo."""
        return f'<{self.__class__.__name__} {self.id}>'


def init_db() -> None:
    """
    Inicializa base de dados criando todas as tabelas.
    """
    try:
        # Importar todos os modelos para registrar com SQLAlchemy
        # Será expandido na FASE 2
        # from . import domain, account, template, log
        
        # Criar todas as tabelas
        db.create_all()
        
        logger.info('Database initialized successfully')
        
    except Exception as e:
        logger.error(f'Failed to initialize database: {e}')
        raise