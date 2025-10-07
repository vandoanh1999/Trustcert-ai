"""
ASA-Fusion v2.0 - Input Validation and Security Hardening
Comprehensive input validation with security checks.
"""

import re
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass

from .exceptions import ValidationError, SecurityError


@dataclass
class ValidationRule:
    """Validation rule definition."""
    name: str
    rule_type: str
    params: Dict[str, Any]
    error_message: str


class InputValidator:
    """Comprehensive input validator with security hardening."""
    
    # Security patterns
    SQL_INJECTION_PATTERN = re.compile(
        r"(\bSELECT\b|\bUNION\b|\bINSERT\b|\bUPDATE\b|\bDELETE\b|\bDROP\b)",
        re.IGNORECASE
    )
    
    XSS_PATTERN = re.compile(
        r"<script|javascript:|onerror=|onload=",
        re.IGNORECASE
    )
    
    PATH_TRAVERSAL_PATTERN = re.compile(r"\.\./|\.\.\\")
    
    def __init__(self, max_input_size: int = 1048576):  # 1MB default
        """
        Initialize validator.
        
        Args:
            max_input_size: Maximum input size in bytes
        """
        self.max_input_size = max_input_size
    
    def validate_string(
        self,
        value: str,
        min_length: int = 0,
        max_length: Optional[int] = None,
        pattern: Optional[str] = None,
        field_name: str = "input"
    ) -> str:
        """
        Validate string input.
        
        Args:
            value: String to validate
            min_length: Minimum length
            max_length: Maximum length
            pattern: Optional regex pattern
            field_name: Field name for error messages
            
        Returns:
            Validated string
            
        Raises:
            ValidationError: If validation fails
        """
        if not isinstance(value, str):
            raise ValidationError(f"{field_name} must be a string")
        
        if len(value) < min_length:
            raise ValidationError(
                f"{field_name} must be at least {min_length} characters"
            )
        
        if max_length and len(value) > max_length:
            raise ValidationError(
                f"{field_name} must not exceed {max_length} characters"
            )
        
        if pattern and not re.match(pattern, value):
            raise ValidationError(
                f"{field_name} does not match required pattern"
            )
        
        return value
    
    def validate_number(
        self,
        value: Union[int, float],
        min_value: Optional[Union[int, float]] = None,
        max_value: Optional[Union[int, float]] = None,
        field_name: str = "input"
    ) -> Union[int, float]:
        """
        Validate numeric input.
        
        Args:
            value: Number to validate
            min_value: Minimum value
            max_value: Maximum value
            field_name: Field name for error messages
            
        Returns:
            Validated number
            
        Raises:
            ValidationError: If validation fails
        """
        if not isinstance(value, (int, float)):
            raise ValidationError(f"{field_name} must be a number")
        
        if min_value is not None and value < min_value:
            raise ValidationError(
                f"{field_name} must be at least {min_value}"
            )
        
        if max_value is not None and value > max_value:
            raise ValidationError(
                f"{field_name} must not exceed {max_value}"
            )
        
        return value
    
    def validate_list(
        self,
        value: List[Any],
        min_items: int = 0,
        max_items: Optional[int] = None,
        item_type: Optional[type] = None,
        field_name: str = "input"
    ) -> List[Any]:
        """
        Validate list input.
        
        Args:
            value: List to validate
            min_items: Minimum number of items
            max_items: Maximum number of items
            item_type: Expected type of items
            field_name: Field name for error messages
            
        Returns:
            Validated list
            
        Raises:
            ValidationError: If validation fails
        """
        if not isinstance(value, list):
            raise ValidationError(f"{field_name} must be a list")
        
        if len(value) < min_items:
            raise ValidationError(
                f"{field_name} must contain at least {min_items} items"
            )
        
        if max_items and len(value) > max_items:
            raise ValidationError(
                f"{field_name} must not contain more than {max_items} items"
            )
        
        if item_type:
            for idx, item in enumerate(value):
                if not isinstance(item, item_type):
                    raise ValidationError(
                        f"{field_name}[{idx}] must be of type {item_type.__name__}"
                    )
        
        return value
    
    def check_security_threats(self, value: str, field_name: str = "input") -> None:
        """
        Check for common security threats.
        
        Args:
            value: String to check
            field_name: Field name for error messages
            
        Raises:
            SecurityError: If security threat detected
        """
        if not isinstance(value, str):
            return
        
        # Check for SQL injection
        if self.SQL_INJECTION_PATTERN.search(value):
            raise SecurityError(
                f"Potential SQL injection detected in {field_name}"
            )
        
        # Check for XSS
        if self.XSS_PATTERN.search(value):
            raise SecurityError(
                f"Potential XSS attack detected in {field_name}"
            )
        
        # Check for path traversal
        if self.PATH_TRAVERSAL_PATTERN.search(value):
            raise SecurityError(
                f"Potential path traversal detected in {field_name}"
            )
        
        # Check input size
        if len(value.encode('utf-8')) > self.max_input_size:
            raise SecurityError(
                f"{field_name} exceeds maximum size of {self.max_input_size} bytes"
            )
    
    def validate_dict(
        self,
        value: Dict[str, Any],
        required_keys: Optional[List[str]] = None,
        field_name: str = "input"
    ) -> Dict[str, Any]:
        """
        Validate dictionary input.
        
        Args:
            value: Dictionary to validate
            required_keys: List of required keys
            field_name: Field name for error messages
            
        Returns:
            Validated dictionary
            
        Raises:
            ValidationError: If validation fails
        """
        if not isinstance(value, dict):
            raise ValidationError(f"{field_name} must be a dictionary")
        
        if required_keys:
            missing_keys = set(required_keys) - set(value.keys())
            if missing_keys:
                raise ValidationError(
                    f"{field_name} missing required keys: {', '.join(missing_keys)}"
                )
        
        return value
    
    def sanitize_string(self, value: str) -> str:
        """
        Sanitize string by removing potentially dangerous characters.
        
        Args:
            value: String to sanitize
            
        Returns:
            Sanitized string
        """
        if not isinstance(value, str):
            return value
        
        # Remove null bytes
        value = value.replace('\x00', '')
        
        # Remove control characters except newline and tab
        value = ''.join(char for char in value if char.isprintable() or char in '\n\t')
        
        return value.strip()
