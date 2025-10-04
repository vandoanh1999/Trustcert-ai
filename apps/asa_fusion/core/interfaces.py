# Copyright (c) 2024-2025 Doanh1102. All Rights Reserved.
# This file is part of ASA-Fusion v2.0 - Proprietary Software
# Unauthorized copying, modification, or distribution is strictly prohibited.

"""
Core interfaces for ASA-Fusion framework.
Defines the standard interface for decision procedures and solver results.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional


class ProblemType(Enum):
    """Types of problems that can be solved."""
    PRESBURGER = "presburger"
    DIOPHANTINE = "diophantine"
    LINEAR_ARITHMETIC = "linear_arithmetic"
    NONLINEAR_ARITHMETIC = "nonlinear_arithmetic"
    BOOLEAN_LOGIC = "boolean_logic"
    QUANTIFIER_FREE = "quantifier_free"
    GENERAL = "general"
    UNKNOWN = "unknown"


@dataclass
class SolverResult:
    """Result from a decision procedure or solver."""
    satisfiable: Optional[bool]  # True=SAT, False=UNSAT, None=UNKNOWN
    model: Optional[Dict[str, Any]] = None  # Variable assignments if SAT
    explanation: Optional[str] = None  # Human-readable explanation
    solver_name: str = "unknown"
    execution_time_ms: float = 0.0
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class DecisionProcedure(ABC):
    """
    Base interface for all decision procedures in ASA-Fusion.
    
    A decision procedure is a module that can solve a specific class of problems.
    It must implement three core methods: can_handle, decide, and explain.
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Return the name of this decision procedure."""
        pass
    
    @property
    @abstractmethod
    def supported_types(self) -> List[ProblemType]:
        """Return the types of problems this procedure can handle."""
        pass
    
    @abstractmethod
    def can_handle(self, problem: str, problem_type: Optional[ProblemType] = None) -> bool:
        """
        Determine if this procedure can handle the given problem.
        
        Args:
            problem: The problem statement (could be a formula, query, etc.)
            problem_type: Optional hint about the problem type
            
        Returns:
            True if this procedure can handle the problem, False otherwise
        """
        pass
    
    @abstractmethod
    def decide(self, problem: str, timeout_ms: int = 5000) -> SolverResult:
        """
        Attempt to solve the given problem.
        
        Args:
            problem: The problem statement to solve
            timeout_ms: Maximum time to spend in milliseconds
            
        Returns:
            SolverResult with the outcome and any relevant data
        """
        pass
    
    @abstractmethod
    def explain(self, result: SolverResult) -> str:
        """
        Generate a human-readable explanation of the result.
        
        Args:
            result: The solver result to explain
            
        Returns:
            Human-readable explanation string
        """
        pass
    
    def get_priority(self) -> int:
        """
        Return the priority of this procedure (higher = try first).
        Default is 0. Can be overridden by subclasses.
        """
        return 0
