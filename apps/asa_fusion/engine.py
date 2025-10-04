# Copyright (c) 2024-2025 Doanh1102. All Rights Reserved.
# This file is part of ASA-Fusion v2.0 - Proprietary Software
# Unauthorized copying, modification, or distribution is strictly prohibited.

"""
Main ASA-Fusion engine that orchestrates all components.
"""

from typing import Optional, List
import time

from .core import ProcedureRegistry, SolverResult, ProblemType
from .ai_layer import ProblemAnalyzer, AnalysisResult
from .security import InputValidator, ValidationResult, SandboxConfig, execute_sandboxed
from .plugins import PresburgerProcedure, DiophantineProcedure
from .solvers import Z3Solver


class ASAFusionEngine:
    """
    Main engine for ASA-Fusion v2.0.
    
    Orchestrates problem analysis, validation, solver selection, and execution.
    Implements hybrid solver fallback and AI-guided strategy selection.
    """
    
    def __init__(
        self,
        enable_ai_analysis: bool = True,
        enable_validation: bool = True,
        enable_sandbox: bool = True,
        auto_register_builtin: bool = True,
    ):
        """
        Initialize ASA-Fusion engine.
        
        Args:
            enable_ai_analysis: Use AI to analyze and classify problems
            enable_validation: Validate inputs for security
            enable_sandbox: Execute solvers in sandboxed environment
            auto_register_builtin: Automatically register built-in procedures
        """
        self.registry = ProcedureRegistry()
        self.analyzer = ProblemAnalyzer() if enable_ai_analysis else None
        self.validator = InputValidator() if enable_validation else None
        self.enable_sandbox = enable_sandbox
        
        # Register built-in procedures
        if auto_register_builtin:
            self._register_builtin_procedures()
    
    def _register_builtin_procedures(self):
        """Register built-in decision procedures."""
        self.registry.register(PresburgerProcedure())
        self.registry.register(DiophantineProcedure())
        
        # Register Z3 as fallback if available
        z3_solver = Z3Solver()
        if z3_solver.is_available():
            self.registry.register(z3_solver)
    
    def solve(
        self,
        problem: str,
        problem_type: Optional[ProblemType] = None,
        timeout_ms: int = 5000,
        validate: bool = True,
        use_ai: bool = True,
    ) -> dict:
        """
        Main entry point to solve a problem.
        
        Args:
            problem: Problem statement to solve
            problem_type: Optional hint about problem type
            timeout_ms: Timeout per solver in milliseconds
            validate: Whether to validate input
            use_ai: Whether to use AI analysis
            
        Returns:
            Dictionary with solution, analysis, and metadata
        """
        start_time = time.time()
        
        # Step 1: Validate input
        validation_result = None
        if validate and self.validator:
            validation_result = self.validator.validate(problem)
            if not validation_result.is_valid:
                return {
                    "success": False,
                    "error": "Input validation failed",
                    "validation_errors": validation_result.errors,
                    "warnings": validation_result.warnings,
                }
            problem = validation_result.sanitized_input or problem
        
        # Step 2: AI analysis
        analysis_result = None
        if use_ai and self.analyzer:
            analysis_result = self.analyzer.analyze(problem)
            # Use AI recommendation if no explicit type given
            if problem_type is None and analysis_result.problem_type != ProblemType.UNKNOWN:
                problem_type = analysis_result.problem_type
        
        # Step 3: Solve using registry
        if self.enable_sandbox:
            # Execute in sandbox
            sandbox_config = SandboxConfig(timeout_seconds=timeout_ms / 1000.0)
            try:
                result = execute_sandboxed(
                    lambda: self.registry.solve(problem, problem_type, timeout_ms),
                    sandbox_config
                )
            except Exception as e:
                result = SolverResult(
                    satisfiable=None,
                    explanation=f"Sandboxed execution failed: {str(e)}",
                    solver_name="sandbox",
                    metadata={"error": str(e)}
                )
        else:
            result = self.registry.solve(problem, problem_type, timeout_ms)
        
        # Step 4: Build response
        total_time = (time.time() - start_time) * 1000
        
        response = {
            "success": result.satisfiable is not None,
            "satisfiable": result.satisfiable,
            "solver": result.solver_name,
            "execution_time_ms": result.execution_time_ms,
            "total_time_ms": total_time,
            "explanation": result.explanation,
        }
        
        if result.model:
            response["model"] = result.model
        
        if analysis_result:
            response["ai_analysis"] = {
                "problem_type": analysis_result.problem_type.value,
                "confidence": analysis_result.confidence,
                "complexity_score": analysis_result.complexity_score,
                "reasoning": analysis_result.reasoning,
                "recommendations": analysis_result.suggested_transformations,
            }
        
        if validation_result and validation_result.warnings:
            response["warnings"] = validation_result.warnings
        
        response["metadata"] = result.metadata or {}
        
        return response
    
    def list_solvers(self) -> List[str]:
        """List all registered solvers."""
        return self.registry.list_procedures()
    
    def get_info(self) -> dict:
        """Get information about the engine and available solvers."""
        from . import __version__, __author__, __copyright__
        
        return {
            "version": __version__,
            "author": __author__,
            "copyright": __copyright__,
            "solvers": self.list_solvers(),
            "features": {
                "ai_analysis": self.analyzer is not None,
                "input_validation": self.validator is not None,
                "sandboxed_execution": self.enable_sandbox,
            },
            "license": "Proprietary - Contact phamvandoanh9@gmail.com for commercial use",
        }
