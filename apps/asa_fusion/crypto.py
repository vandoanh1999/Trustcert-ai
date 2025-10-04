"""
ASA-Fusion v2.0 - Quantum-Resistant Cryptography
SHA3-256 based certificate generation and validation.
"""

import hashlib
import json
import time
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict

from .exceptions import CertificateError, ValidationError


@dataclass
class Certificate:
    """Quantum-resistant certificate using SHA3-256."""
    data: str
    timestamp: float
    signature: str
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert certificate to dictionary."""
        return asdict(self)
    
    def to_json(self) -> str:
        """Convert certificate to JSON string."""
        return json.dumps(self.to_dict())


class SHA3CertificateManager:
    """Manages quantum-resistant SHA3-256 certificates."""
    
    def __init__(self, salt: Optional[str] = None):
        """
        Initialize certificate manager.
        
        Args:
            salt: Optional salt for additional security
        """
        self.salt = salt or "ASA-FUSION-V2"
    
    def generate_signature(self, data: str, timestamp: float) -> str:
        """
        Generate SHA3-256 signature for data.
        
        Args:
            data: Data to sign
            timestamp: Timestamp for signature
            
        Returns:
            Hexadecimal signature string
            
        Raises:
            ValidationError: If data is invalid
        """
        if not data:
            raise ValidationError("Data cannot be empty for signature generation")
        
        # Combine data with timestamp and salt for quantum-resistant signature
        combined = f"{data}|{timestamp}|{self.salt}".encode('utf-8')
        signature = hashlib.sha3_256(combined).hexdigest()
        return signature
    
    def create_certificate(self, data: str, metadata: Optional[Dict[str, Any]] = None) -> Certificate:
        """
        Create a new quantum-resistant certificate.
        
        Args:
            data: Data to certify
            metadata: Optional metadata
            
        Returns:
            Certificate object
            
        Raises:
            ValidationError: If data is invalid
        """
        if not data:
            raise ValidationError("Data cannot be empty for certificate creation")
        
        timestamp = time.time()
        signature = self.generate_signature(data, timestamp)
        
        return Certificate(
            data=data,
            timestamp=timestamp,
            signature=signature,
            metadata=metadata or {}
        )
    
    def verify_certificate(self, cert: Certificate) -> bool:
        """
        Verify certificate signature.
        
        Args:
            cert: Certificate to verify
            
        Returns:
            True if valid, False otherwise
            
        Raises:
            CertificateError: If certificate structure is invalid
        """
        if not cert.data or not cert.signature:
            raise CertificateError("Invalid certificate structure")
        
        try:
            expected_signature = self.generate_signature(cert.data, cert.timestamp)
            return expected_signature == cert.signature
        except Exception as e:
            raise CertificateError(f"Certificate verification failed: {str(e)}")
    
    def verify_certificate_dict(self, cert_dict: Dict[str, Any]) -> bool:
        """
        Verify certificate from dictionary.
        
        Args:
            cert_dict: Certificate dictionary
            
        Returns:
            True if valid, False otherwise
        """
        cert = Certificate(**cert_dict)
        return self.verify_certificate(cert)
