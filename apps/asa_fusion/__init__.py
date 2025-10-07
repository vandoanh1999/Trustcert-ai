"""
ASA-Fusion v2.0 - Revolutionary Breakthrough Features

This module implements a modular architecture for ASA-Fusion with:
- Plugin-based decision procedures for Z3/CVC5 integration
- Quantum-resistant SHA3-256 certificates
- Async/await multi-threaded batch processing
- Comprehensive input validation and security hardening
- Timeout protection mechanisms
- Performance monitoring and tracing
- Extensible solver architecture
- WebAssembly-ready design
- Production-grade error handling

Author: Doanh1102
Version: 2.0.0
"""

from .exceptions import (
    ASAFusionError,
    ValidationError,
    SecurityError,
    TimeoutError,
    CertificateError,
    PluginError,
    SolverError,
    BatchProcessingError
)

from .crypto import (
    Certificate,
    SHA3CertificateManager
)

from .plugins import (
    DecisionResult,
    DecisionPlugin,
    Z3Plugin,
    CVC5Plugin,
    PluginRegistry
)

from .batch_processor import (
    BatchResult,
    BatchProcessor
)

from .validation import (
    ValidationRule,
    InputValidator
)

from .monitoring import (
    PerformanceMetrics,
    TraceSpan,
    PerformanceMonitor,
    DistributedTracer,
    get_monitor,
    get_tracer
)

from .wasm_interface import (
    WasmModule,
    WasmSerializable,
    WasmInterface,
    WasmCertificate,
    WasmExportable,
    get_wasm_interface
)

__version__ = "2.0.0"
__author__ = "Doanh1102"

__all__ = [
    # Exceptions
    "ASAFusionError",
    "ValidationError",
    "SecurityError",
    "TimeoutError",
    "CertificateError",
    "PluginError",
    "SolverError",
    "BatchProcessingError",
    # Crypto
    "Certificate",
    "SHA3CertificateManager",
    # Plugins
    "DecisionResult",
    "DecisionPlugin",
    "Z3Plugin",
    "CVC5Plugin",
    "PluginRegistry",
    # Batch Processing
    "BatchResult",
    "BatchProcessor",
    # Validation
    "ValidationRule",
    "InputValidator",
    # Monitoring
    "PerformanceMetrics",
    "TraceSpan",
    "PerformanceMonitor",
    "DistributedTracer",
    "get_monitor",
    "get_tracer",
    # WASM
    "WasmModule",
    "WasmSerializable",
    "WasmInterface",
    "WasmCertificate",
    "WasmExportable",
    "get_wasm_interface",
]
