# Copyright (c) 2024-2025 Doanh1102. All Rights Reserved.
# This file is part of ASA-Fusion v2.0 - Proprietary Software
# Unauthorized copying, modification, or distribution is strictly prohibited.

"""
Presburger arithmetic decision procedure.
Handles linear integer arithmetic without multiplication.
"""

import re
import time
from typing import List, Optional

from apps.asa_fusion.core import DecisionProcedure, SolverResult, ProblemType


class PresburgerProcedure(DecisionProcedure):
    """
    Decision procedure for Presburger arithmetic.
    
    Presburger arithmetic is the first-order theory of natural numbers
    with addition and equality (no multiplication).
    """
    
    @property
    def name(self) -> str:
        return "presburger"
    
    @property
    def supported_types(self) -> List[ProblemType]:
        return [ProblemType.PRESBURGER, ProblemType.LINEAR_ARITHMETIC]
    
    def can_handle(self, problem: str, problem_type: Optional[ProblemType] = None) -> bool:
        """
        Check if this is a Presburger arithmetic problem.
        
        Presburger formulas contain:
        - Variables (x, y, z, etc.)
        - Integer constants
        - Addition and subtraction
        - Comparison operators (=, <, >, <=, >=, !=)
        - Logical connectives (and, or, not)
        - Multiplication by constants is OK
        - NO multiplication of variables
        """
        if problem_type == ProblemType.PRESBURGER:
            return True
        
        # Check for equals or other comparisons or arithmetic
        has_arithmetic = bool(re.search(r'[+\-=<>]', problem))
        
        # Must have variables
        has_variable = bool(re.search(r'\b[a-z]\b', problem.lower()))
        
        # Check for variable multiplication (not allowed)
        has_var_mult = bool(re.search(r'[a-z]\s*\*\s*[a-z]', problem.lower()))
        
        # Check for powers (not allowed)
        has_power = bool(re.search(r'\^|\*\*|pow', problem.lower()))
        
        return has_arithmetic and has_variable and not has_var_mult and not has_power
    
    def decide(self, problem: str, timeout_ms: int = 5000) -> SolverResult:
        """
        Attempt to solve the Presburger formula.
        
        This is a simplified implementation. A real implementation would:
        - Parse the formula into an AST
        - Apply quantifier elimination algorithms
        - Use Cooper's algorithm or Omega test
        """
        start_time = time.time()
        
        try:
            # Simplified: Try to solve basic linear equations
            # Example: "2*x + 3*y = 10 and x > 0 and y > 0"
            
            # For demonstration, handle simple equality
            match = re.match(r'(\w+)\s*=\s*(\d+)', problem.strip())
            if match:
                var_name = match.group(1)
                value = int(match.group(2))
                
                execution_time = (time.time() - start_time) * 1000
                
                return SolverResult(
                    satisfiable=True,
                    model={var_name: value},
                    explanation=f"Found solution: {var_name} = {value}",
                    solver_name=self.name,
                    execution_time_ms=execution_time
                )
            
            # More complex problems return UNKNOWN (would need full implementation)
            execution_time = (time.time() - start_time) * 1000
            
            return SolverResult(
                satisfiable=None,
                explanation="Problem requires full Presburger solver (not implemented)",
                solver_name=self.name,
                execution_time_ms=execution_time,
                metadata={"reason": "simplified_implementation"}
            )
            
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            
            return SolverResult(
                satisfiable=None,
                explanation=f"Error solving problem: {str(e)}",
                solver_name=self.name,
                execution_time_ms=execution_time,
                metadata={"error": str(e)}
            )
    
    def explain(self, result: SolverResult) -> str:
        """Generate explanation for the result."""
        if result.satisfiable is True:
            if result.model:
                assignments = ", ".join(f"{k}={v}" for k, v in result.model.items())
                return f"The formula is satisfiable with: {assignments}"
            return "The formula is satisfiable"
        elif result.satisfiable is False:
            return "The formula is unsatisfiable (no solution exists)"
        else:
            return result.explanation or "Unable to determine satisfiability"
    
    def get_priority(self) -> int:
        """Presburger has high priority for linear problems."""
        return 10
