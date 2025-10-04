# Copyright (c) 2024-2025 Doanh1102. All Rights Reserved.
# This file is part of ASA-Fusion v2.0 - Proprietary Software
# Unauthorized copying, modification, or distribution is strictly prohibited.

"""
Input validation and security checks for ASA-Fusion.
"""

import re
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class ValidationResult:
    """Result of input validation."""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    sanitized_input: Optional[str] = None


class InputValidator:
    """
    Validates and sanitizes input to prevent malicious queries.
    Implements hardened parsing and validation.
    """
    
    # Maximum allowed input size (characters)
    MAX_INPUT_SIZE = 10000
    
    # Maximum nesting depth for expressions
    MAX_NESTING_DEPTH = 50
    
    # Dangerous patterns to check for
    DANGEROUS_PATTERNS = [
        r'__import__',  # Python imports
        r'eval\s*\(',   # Eval calls
        r'exec\s*\(',   # Exec calls
        r'compile\s*\(',  # Compile calls
        r'open\s*\(',   # File operations
        r'system\s*\(',  # System calls
        r'subprocess',  # Subprocess
        r'\.\./',       # Path traversal
        r'<script',     # XSS attempts
    ]
    
    def __init__(
        self,
        max_input_size: int = MAX_INPUT_SIZE,
        max_nesting_depth: int = MAX_NESTING_DEPTH
    ):
        self.max_input_size = max_input_size
        self.max_nesting_depth = max_nesting_depth
    
    def validate(self, input_str: str) -> ValidationResult:
        """
        Validate input and check for security issues.
        
        Args:
            input_str: The input string to validate
            
        Returns:
            ValidationResult with validation status and any errors/warnings
        """
        errors = []
        warnings = []
        
        # Check input size
        if len(input_str) > self.max_input_size:
            errors.append(
                f"Input exceeds maximum size of {self.max_input_size} characters"
            )
        
        # Check for null bytes
        if '\x00' in input_str:
            errors.append("Input contains null bytes")
        
        # Check nesting depth
        depth = self._check_nesting_depth(input_str)
        if depth > self.max_nesting_depth:
            errors.append(
                f"Nesting depth {depth} exceeds maximum of {self.max_nesting_depth}"
            )
        
        # Check for dangerous patterns
        for pattern in self.DANGEROUS_PATTERNS:
            if re.search(pattern, input_str, re.IGNORECASE):
                errors.append(f"Dangerous pattern detected: {pattern}")
        
        # Check for excessive repetition (potential DoS)
        if self._has_excessive_repetition(input_str):
            warnings.append("Input contains excessive repetition (potential DoS)")
        
        # Sanitize input if no critical errors
        sanitized = None
        if not errors:
            sanitized = self._sanitize(input_str)
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            sanitized_input=sanitized
        )
    
    def _check_nesting_depth(self, input_str: str) -> int:
        """Calculate maximum nesting depth of parentheses/brackets."""
        max_depth = 0
        current_depth = 0
        
        for char in input_str:
            if char in '([{':
                current_depth += 1
                max_depth = max(max_depth, current_depth)
            elif char in ')]}':
                current_depth = max(0, current_depth - 1)
        
        return max_depth
    
    def _has_excessive_repetition(self, input_str: str, threshold: int = 1000) -> bool:
        """Check if input has excessive character repetition."""
        if len(input_str) < threshold:
            return False
        
        # Look for any character repeated more than threshold times
        from collections import Counter
        counts = Counter(input_str)
        return any(count > threshold for count in counts.values())
    
    def _sanitize(self, input_str: str) -> str:
        """
        Sanitize input by removing/escaping dangerous characters.
        
        Args:
            input_str: Input to sanitize
            
        Returns:
            Sanitized string
        """
        # Remove control characters except whitespace
        sanitized = ''.join(
            char for char in input_str 
            if char.isprintable() or char.isspace()
        )
        
        # Normalize whitespace
        sanitized = ' '.join(sanitized.split())
        
        return sanitized
