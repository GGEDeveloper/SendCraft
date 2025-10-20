"""Utilitários de criptografia para SendCraft."""
from cryptography.fernet import Fernet
import base64
import hashlib
import secrets
from typing import Optional


class AESCipher:
    """Cipher AES-256 para encriptação simétrica."""
    
    def __init__(self, key: str):
        """
        Inicializa cipher com chave.
        
        Args:
            key: Chave de encriptação (será derivada para 32 bytes)
        """
        # Deriva chave de 32 bytes usando SHA-256
        key_bytes = key.encode('utf-8')
        digest = hashlib.sha256(key_bytes).digest()
        self.fernet = Fernet(base64.urlsafe_b64encode(digest))
    
    def encrypt(self, plaintext: str) -> str:
        """
        Encripta texto plano.
        
        Args:
            plaintext: Texto a encriptar
            
        Returns:
            Texto encriptado em base64
        """
        if not plaintext:
            return ''
        
        plaintext_bytes = plaintext.encode('utf-8')
        encrypted_bytes = self.fernet.encrypt(plaintext_bytes)
        return encrypted_bytes.decode('utf-8')
    
    def decrypt(self, ciphertext: str) -> str:
        """
        Decripta texto encriptado.
        
        Args:
            ciphertext: Texto encriptado em base64
            
        Returns:
            Texto plano decriptado
            
        Raises:
            ValueError: Se não conseguir decriptar
        """
        if not ciphertext:
            return ''
        
        try:
            ciphertext_bytes = ciphertext.encode('utf-8')
            decrypted_bytes = self.fernet.decrypt(ciphertext_bytes)
            return decrypted_bytes.decode('utf-8')
        except Exception as e:
            raise ValueError(f"Erro ao decriptar: {e}")

    @classmethod
    def generate_key(cls) -> str:
        """Gera chave aleatória segura."""
        return secrets.token_urlsafe(32)


def hash_api_key(api_key: str) -> str:
    """
    Cria hash seguro de API key.
    
    Args:
        api_key: API key em texto plano
        
    Returns:
        Hash SHA-256 da chave
    """
    return hashlib.sha256(api_key.encode('utf-8')).hexdigest()


def generate_api_key(prefix: str = 'SC') -> str:
    """
    Gera API key segura.
    
    Args:
        prefix: Prefixo da chave
        
    Returns:
        API key formatada
    """
    random_part = secrets.token_urlsafe(48)  # Gerar mais caracteres para ter 64 no total
    return f"{prefix}_{random_part}"


def verify_api_key(api_key: str, hashed_key: str) -> bool:
    """
    Verifica se API key corresponde ao hash.
    
    Args:
        api_key: API key em texto plano
        hashed_key: Hash armazenado
        
    Returns:
        True se a chave é válida
    """
    return hash_api_key(api_key) == hashed_key