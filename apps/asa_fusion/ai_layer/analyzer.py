# Copyright (c) 2024-2025 Doanh1102. All Rights Reserved.
# This file is part of ASA-Fusion v2.0 - Proprietary Software
# Unauthorized copying, modification, or distribution is strictly prohibited.

"""
AI-powered problem analysis and strategy recommendation.
"""

import re
from dataclasses import dataclass
from typing import List, Optional

from apps.asa_fusion.core import ProblemType


@dataclass
class AnalysisResult:
    """Result of AI problem analysis."""
    problem_type: ProblemType
    confidence: float  # 0.0 to 1.0
    complexity_score: int  # 1-10, where 10 is most complex
    recommended_solver: Optional[str] = None
    suggested_transformations: List[str] = None
    reasoning: str = ""
    
    def __post_init__(self):
        if self.suggested_transformations is None:
            self.suggested_transformations = []


class ProblemAnalyzer:
    """
    AI-powered analyzer that examines problems and recommends solving strategies.
    
    This is a rule-based implementation. In production, this could be enhanced with:
    - Machine learning models (e.g., transformer-based classifiers)
    - LLM integration for complex problem understanding
    - Historical performance data for adaptive recommendations
    """
    
    def analyze(self, problem: str) -> AnalysisResult:
        """
        Analyze a problem and determine its type and characteristics.
        
        Args:
            problem: The problem statement to analyze
            
        Returns:
            AnalysisResult with problem classification and recommendations
        """
        # Rule-based heuristics for problem classification
        problem_lower = problem.lower()
        
        # Check for different problem types
        is_boolean = self._is_boolean_logic(problem)
        is_linear = self._is_linear_arithmetic(problem)
        is_nonlinear = self._is_nonlinear_arithmetic(problem)
        is_diophantine = self._is_diophantine(problem)
        is_presburger = self._is_presburger(problem)
        
        # Determine primary type and confidence (check Diophantine first)
        if is_diophantine:
            problem_type = ProblemType.DIOPHANTINE
            confidence = 0.75
            recommended_solver = "diophantine"
            reasoning = "Detected polynomial equation with integer constraints"
        elif is_presburger:
            problem_type = ProblemType.PRESBURGER
            confidence = 0.8
            recommended_solver = "presburger"
            reasoning = "Detected linear integer arithmetic without multiplication"
        elif is_nonlinear:
            problem_type = ProblemType.NONLINEAR_ARITHMETIC
            confidence = 0.7
            recommended_solver = "z3"
            reasoning = "Detected nonlinear arithmetic, recommend SMT solver"
        elif is_linear:
            problem_type = ProblemType.LINEAR_ARITHMETIC
            confidence = 0.85
            recommended_solver = "presburger"
            reasoning = "Detected linear arithmetic"
        elif is_boolean:
            problem_type = ProblemType.BOOLEAN_LOGIC
            confidence = 0.9
            recommended_solver = "z3"
            reasoning = "Detected boolean/propositional logic"
        else:
            problem_type = ProblemType.UNKNOWN
            confidence = 0.5
            recommended_solver = "z3"
            reasoning = "Unknown problem type, recommend general solver"
        
        # Calculate complexity
        complexity = self._calculate_complexity(problem)
        
        # Suggest transformations
        transformations = self._suggest_transformations(problem, problem_type)
        
        return AnalysisResult(
            problem_type=problem_type,
            confidence=confidence,
            complexity_score=complexity,
            recommended_solver=recommended_solver,
            suggested_transformations=transformations,
            reasoning=reasoning
        )
    
    def _is_boolean_logic(self, problem: str) -> bool:
        """Check if problem is boolean logic."""
        boolean_keywords = ['and', 'or', 'not', 'true', 'false', 'implies']
        has_boolean = any(kw in problem.lower() for kw in boolean_keywords)
        has_arithmetic = bool(re.search(r'[+\-*/]', problem))
        return has_boolean and not has_arithmetic
    
    def _is_linear_arithmetic(self, problem: str) -> bool:
        """Check if problem involves linear arithmetic."""
        has_addition = bool(re.search(r'[+\-]', problem))
        has_comparison = bool(re.search(r'[<>=!]=?', problem))
        has_multiplication = bool(re.search(r'\*|/', problem))
        
        # Linear if has arithmetic and comparison, but multiplication is only with constants
        return has_addition and has_comparison
    
    def _is_nonlinear_arithmetic(self, problem: str) -> bool:
        """Check if problem involves nonlinear arithmetic."""
        has_power = bool(re.search(r'\^|\*\*|pow', problem.lower()))
        has_var_mult = bool(re.search(r'[a-z]\s*\*\s*[a-z]', problem.lower()))
        return has_power or has_var_mult
    
    def _is_presburger(self, problem: str) -> bool:
        """Check if problem is Presburger arithmetic."""
        has_arithmetic = bool(re.search(r'[+\-]', problem))
        # Presburger allows multiplication by constants but not variables
        has_var_mult = bool(re.search(r'[a-z]\s*\*\s*[a-z]', problem.lower()))
        has_power = bool(re.search(r'\^|\*\*|pow', problem.lower()))
        # Not Presburger if has powers or variable multiplication
        return has_arithmetic and not has_var_mult and not has_power
    
    def _is_diophantine(self, problem: str) -> bool:
        """Check if problem is a Diophantine equation."""
        has_power = bool(re.search(r'\^2|\*\*2|x\*x|y\*y', problem))
        has_equals = '=' in problem
        has_integer_hint = 'int' in problem.lower() or 'integer' in problem.lower()
        return (has_power or has_integer_hint) and has_equals
    
    def _calculate_complexity(self, problem: str) -> int:
        """
        Calculate problem complexity score (1-10).
        
        Factors:
        - Length of problem
        - Number of variables
        - Nesting depth
        - Operator types
        """
        score = 1
        
        # Length factor
        if len(problem) > 100:
            score += 2
        elif len(problem) > 50:
            score += 1
        
        # Variable count
        variables = set(re.findall(r'\b[a-z]\b', problem.lower()))
        score += min(len(variables), 3)
        
        # Nesting depth
        depth = 0
        max_depth = 0
        for char in problem:
            if char in '([{':
                depth += 1
                max_depth = max(max_depth, depth)
            elif char in ')]}':
                depth -= 1
        score += min(max_depth // 2, 2)
        
        # Nonlinear operators
        if re.search(r'\^|\*\*|pow', problem.lower()):
            score += 2
        
        return min(score, 10)
    
    def _suggest_transformations(
        self, 
        problem: str, 
        problem_type: ProblemType
    ) -> List[str]:
        """Suggest helpful transformations for the problem."""
        suggestions = []
        
        # Check if problem could be simplified
        if len(problem) > 100:
            suggestions.append("Consider breaking into smaller sub-problems")
        
        # Type-specific suggestions
        if problem_type == ProblemType.NONLINEAR_ARITHMETIC:
            suggestions.append("Try linearization if applicable")
            suggestions.append("Consider bounds on variables to simplify search")
        
        if problem_type == ProblemType.DIOPHANTINE:
            suggestions.append("Check if problem can be reduced modulo small primes")
        
        return suggestions
