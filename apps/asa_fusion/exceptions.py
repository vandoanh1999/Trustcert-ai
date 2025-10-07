"""
ASA-Fusion v2.0 - Custom Exception Hierarchy
Production-grade error handling for all ASA-Fusion operations.
"""


class ASAFusionError(Exception):
    """Base exception for all ASA-Fusion errors."""
    def __init__(self, message: str, error_code: str = "ASA_ERROR"):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class ValidationError(ASAFusionError):
    """Raised when input validation fails."""
    def __init__(self, message: str):
        super().__init__(message, "VALIDATION_ERROR")


class SecurityError(ASAFusionError):
    """Raised when security checks fail."""
    def __init__(self, message: str):
        super().__init__(message, "SECURITY_ERROR")


class TimeoutError(ASAFusionError):
    """Raised when operation exceeds timeout limit."""
    def __init__(self, message: str, timeout_seconds: float):
        self.timeout_seconds = timeout_seconds
        super().__init__(message, "TIMEOUT_ERROR")


class CertificateError(ASAFusionError):
    """Raised when certificate operations fail."""
    def __init__(self, message: str):
        super().__init__(message, "CERTIFICATE_ERROR")


class PluginError(ASAFusionError):
    """Raised when plugin operations fail."""
    def __init__(self, message: str, plugin_name: str = None):
        self.plugin_name = plugin_name
        super().__init__(message, "PLUGIN_ERROR")


class SolverError(ASAFusionError):
    """Raised when solver operations fail."""
    def __init__(self, message: str, solver_name: str = None):
        self.solver_name = solver_name
        super().__init__(message, "SOLVER_ERROR")


class BatchProcessingError(ASAFusionError):
    """Raised when batch processing operations fail."""
    def __init__(self, message: str, failed_items: int = 0):
        self.failed_items = failed_items
        super().__init__(message, "BATCH_PROCESSING_ERROR")
