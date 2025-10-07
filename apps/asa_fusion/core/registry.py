# Copyright (c) 2024-2025 Doanh1102. All Rights Reserved.
# This file is part of ASA-Fusion v2.0 - Proprietary Software
# Unauthorized copying, modification, or distribution is strictly prohibited.

"""
Procedure Registry for plugin architecture.
Manages registration and discovery of decision procedures.
"""

from typing import List, Optional, Type
from .interfaces import DecisionProcedure, ProblemType, SolverResult


class ProcedureRegistry:
    """
    Central registry for decision procedures.
    Implements a plugin architecture allowing dynamic registration of procedures.
    """
    
    def __init__(self):
        self._procedures: List[DecisionProcedure] = []
        self._procedures_by_name: dict[str, DecisionProcedure] = {}
    
    def register(self, procedure: DecisionProcedure) -> None:
        """
        Register a decision procedure.
        
        Args:
            procedure: The decision procedure instance to register
        """
        if procedure.name in self._procedures_by_name:
            raise ValueError(f"Procedure '{procedure.name}' is already registered")
        
        self._procedures.append(procedure)
        self._procedures_by_name[procedure.name] = procedure
        # Sort by priority (higher first)
        self._procedures.sort(key=lambda p: p.get_priority(), reverse=True)
    
    def unregister(self, procedure_name: str) -> None:
        """
        Unregister a decision procedure.
        
        Args:
            procedure_name: Name of the procedure to unregister
        """
        if procedure_name in self._procedures_by_name:
            procedure = self._procedures_by_name.pop(procedure_name)
            self._procedures.remove(procedure)
    
    def get_procedure(self, name: str) -> Optional[DecisionProcedure]:
        """
        Get a specific procedure by name.
        
        Args:
            name: Name of the procedure
            
        Returns:
            The procedure instance or None if not found
        """
        return self._procedures_by_name.get(name)
    
    def list_procedures(self) -> List[str]:
        """Return a list of all registered procedure names."""
        return list(self._procedures_by_name.keys())
    
    def find_capable_procedures(
        self, 
        problem: str, 
        problem_type: Optional[ProblemType] = None
    ) -> List[DecisionProcedure]:
        """
        Find all procedures that can handle the given problem.
        
        Args:
            problem: The problem statement
            problem_type: Optional hint about problem type
            
        Returns:
            List of capable procedures, sorted by priority
        """
        capable = []
        for procedure in self._procedures:
            if procedure.can_handle(problem, problem_type):
                capable.append(procedure)
        return capable
    
    def solve(
        self, 
        problem: str, 
        problem_type: Optional[ProblemType] = None,
        timeout_ms: int = 5000,
        fallback: bool = True
    ) -> SolverResult:
        """
        Attempt to solve a problem using registered procedures.
        
        Tries procedures in priority order until one succeeds or all fail.
        
        Args:
            problem: The problem statement
            problem_type: Optional hint about problem type
            timeout_ms: Timeout per procedure in milliseconds
            fallback: If True, try all capable procedures if first fails
            
        Returns:
            SolverResult from the first successful procedure
        """
        capable = self.find_capable_procedures(problem, problem_type)
        
        if not capable:
            return SolverResult(
                satisfiable=None,
                explanation="No capable decision procedure found for this problem",
                solver_name="registry",
                metadata={"error": "no_capable_procedure"}
            )
        
        last_result = None
        for procedure in capable:
            result = procedure.decide(problem, timeout_ms)
            
            # If we got a definitive answer (SAT or UNSAT), return it
            if result.satisfiable is not None:
                return result
            
            last_result = result
            
            # If not using fallback, return after first attempt
            if not fallback:
                break
        
        # All procedures failed or returned UNKNOWN
        return last_result or SolverResult(
            satisfiable=None,
            explanation="All procedures returned UNKNOWN or failed",
            solver_name="registry",
            metadata={"error": "all_failed"}
        )


# Global registry instance
_global_registry = ProcedureRegistry()


def get_global_registry() -> ProcedureRegistry:
    """Get the global procedure registry instance."""
    return _global_registry
