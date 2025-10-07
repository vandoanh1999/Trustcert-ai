# Copyright (c) 2024-2025 Doanh1102. All Rights Reserved.
# This file is part of ASA-Fusion v2.0 - Proprietary Software
# Unauthorized copying, modification, or distribution is strictly prohibited.

"""
ASA-Fusion v2.0 - Breakthrough Modular SMT Framework

A super-modular framework for AI reasoning and automated theorem proving.
Supports plugin architecture, external solver integration, and AI-powered problem analysis.

Key Features:
- Plugin architecture for decision procedures
- AI reasoning layer for problem classification and strategy recommendation
- Hybrid solver fallback to Z3/CVC5
- Security features: input validation, sandboxing, timeouts
- High-performance multi-threaded execution

Author: Doanh1102
License: Proprietary (see LICENSE file)
Contact: phamvandoanh9@gmail.com
"""

__version__ = "2.0.0"
__author__ = "Doanh1102"
__copyright__ = "Copyright (c) 2024-2025 Doanh1102. All Rights Reserved."

from .core import (
    DecisionProcedure,
    SolverResult,
    ProblemType,
    ProcedureRegistry,
)
from .ai_layer import ProblemAnalyzer, AnalysisResult
from .security import InputValidator, ValidationResult, SandboxConfig, execute_sandboxed
from .engine import ASAFusionEngine

__all__ = [
    # Core
    'DecisionProcedure',
    'SolverResult',
    'ProblemType',
    'ProcedureRegistry',
    
    # AI Layer
    'ProblemAnalyzer',
    'AnalysisResult',
    
    # Security
    'InputValidator',
    'ValidationResult',
    'SandboxConfig',
    'execute_sandboxed',
    
    # Engine
    'ASAFusionEngine',
]
