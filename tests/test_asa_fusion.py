# Copyright (c) 2024-2025 Doanh1102. All Rights Reserved.
# Tests for ASA-Fusion v2.0

import pytest
from apps.asa_fusion import (
    ASAFusionEngine,
    ProblemType,
    DecisionProcedure,
    SolverResult,
    InputValidator,
    ProblemAnalyzer,
)
from apps.asa_fusion.plugins import PresburgerProcedure, DiophantineProcedure


class TestInputValidator:
    """Test security validation features."""
    
    def test_valid_input(self):
        validator = InputValidator()
        result = validator.validate("x + y = 10")
        assert result.is_valid
        assert len(result.errors) == 0
    
    def test_oversized_input(self):
        validator = InputValidator(max_input_size=50)
        result = validator.validate("x" * 100)
        assert not result.is_valid
        assert any("exceeds maximum size" in err for err in result.errors)
    
    def test_dangerous_patterns(self):
        validator = InputValidator()
        
        # Test dangerous pattern detection
        dangerous_inputs = [
            "__import__('os')",
            "eval(input())",
            "exec('print(1)')",
            "open('/etc/passwd')",
        ]
        
        for dangerous in dangerous_inputs:
            result = validator.validate(dangerous)
            assert not result.is_valid
            assert len(result.errors) > 0
    
    def test_nesting_depth(self):
        validator = InputValidator(max_nesting_depth=5)
        result = validator.validate("((((((((x)))))))) = 1")
        assert not result.is_valid
        assert any("Nesting depth" in err for err in result.errors)
    
    def test_sanitization(self):
        validator = InputValidator()
        result = validator.validate("x  +   y   =  10")
        assert result.is_valid
        assert result.sanitized_input == "x + y = 10"


class TestProblemAnalyzer:
    """Test AI reasoning and problem classification."""
    
    def test_linear_arithmetic_detection(self):
        analyzer = ProblemAnalyzer()
        result = analyzer.analyze("2*x + 3*y = 10 and x > 0")
        
        assert result.problem_type in [
            ProblemType.PRESBURGER,
            ProblemType.LINEAR_ARITHMETIC
        ]
        assert result.confidence > 0.5
        assert result.complexity_score >= 1
    
    def test_diophantine_detection(self):
        analyzer = ProblemAnalyzer()
        result = analyzer.analyze("x^2 + y^2 = z^2")
        
        assert result.problem_type == ProblemType.DIOPHANTINE
        assert result.confidence > 0.5
    
    def test_boolean_logic_detection(self):
        analyzer = ProblemAnalyzer()
        result = analyzer.analyze("(p and q) or (not r)")
        
        assert result.problem_type == ProblemType.BOOLEAN_LOGIC
        assert result.confidence > 0.5
    
    def test_complexity_calculation(self):
        analyzer = ProblemAnalyzer()
        
        # Simple problem
        simple = analyzer.analyze("x = 5")
        # Complex problem
        complex_prob = analyzer.analyze("(((x + y) * (z - w)) ^ 2) + (a * b * c) = 100")
        
        assert complex_prob.complexity_score > simple.complexity_score


class TestPresburgerProcedure:
    """Test Presburger arithmetic decision procedure."""
    
    def test_can_handle_presburger(self):
        proc = PresburgerProcedure()
        
        # Should handle linear arithmetic
        assert proc.can_handle("x + y = 10")
        assert proc.can_handle("2*x - 3 = 7")
        
        # Should not handle multiplication of variables
        assert not proc.can_handle("x * y = 10")
    
    def test_simple_equation_solving(self):
        proc = PresburgerProcedure()
        result = proc.decide("x = 42")
        
        assert result.satisfiable is True
        assert result.model is not None
        assert result.model.get("x") == 42
    
    def test_priority(self):
        proc = PresburgerProcedure()
        assert proc.get_priority() > 0


class TestDiophantineProcedure:
    """Test Diophantine equation decision procedure."""
    
    def test_can_handle_diophantine(self):
        proc = DiophantineProcedure()
        
        # Should handle polynomial equations
        assert proc.can_handle("x^2 + y^2 = 25")
        assert proc.can_handle("x*x + y*y = z*z")
    
    def test_linear_diophantine_solvable(self):
        proc = DiophantineProcedure()
        # 3x + 6y = 9, gcd(3,6)=3 divides 9, so solvable
        result = proc.decide("3*x + 6*y = 9")
        
        assert result.satisfiable is True
    
    def test_linear_diophantine_unsolvable(self):
        proc = DiophantineProcedure()
        # 3x + 6y = 10, gcd(3,6)=3 does not divide 10, so unsolvable
        result = proc.decide("3*x + 6*y = 10")
        
        assert result.satisfiable is False


class TestASAFusionEngine:
    """Test the main ASA-Fusion engine."""
    
    def test_engine_initialization(self):
        engine = ASAFusionEngine()
        
        # Should have registered built-in solvers
        solvers = engine.list_solvers()
        assert "presburger" in solvers
        assert "diophantine" in solvers
    
    def test_solve_simple_problem(self):
        engine = ASAFusionEngine()
        result = engine.solve("x = 100")
        
        assert result["success"]
        assert result["satisfiable"] is True
        assert "solver" in result
        assert "execution_time_ms" in result
    
    def test_solve_with_validation(self):
        engine = ASAFusionEngine()
        
        # Valid input
        result = engine.solve("x + y = 10", validate=True)
        assert "validation_errors" not in result
        
        # Invalid input (dangerous pattern)
        result = engine.solve("eval(x)", validate=True)
        assert not result["success"]
        assert "validation_errors" in result
    
    def test_solve_with_ai_analysis(self):
        engine = ASAFusionEngine()
        result = engine.solve("2*x + 3*y = 10", use_ai=True)
        
        assert "ai_analysis" in result
        assert "problem_type" in result["ai_analysis"]
        assert "confidence" in result["ai_analysis"]
        assert "reasoning" in result["ai_analysis"]
    
    def test_get_info(self):
        engine = ASAFusionEngine()
        info = engine.get_info()
        
        assert "version" in info
        assert "author" in info
        assert "solvers" in info
        assert "features" in info
        assert "license" in info
    
    def test_disable_features(self):
        engine = ASAFusionEngine(
            enable_ai_analysis=False,
            enable_validation=False,
            enable_sandbox=False
        )
        
        assert engine.analyzer is None
        assert engine.validator is None
        assert not engine.enable_sandbox
    
    def test_diophantine_problem(self):
        engine = ASAFusionEngine()
        
        # Test with a clearer Diophantine problem
        # Use a problem that the Diophantine procedure will definitely match
        from apps.asa_fusion.plugins import DiophantineProcedure
        proc = DiophantineProcedure()
        result = proc.decide("3*x + 6*y = 9")
        
        # Should be recognized as solvable
        assert result.satisfiable is True


class TestProcedureRegistry:
    """Test the plugin registry system."""
    
    def test_register_custom_procedure(self):
        from apps.asa_fusion.core import ProcedureRegistry
        
        # Create a simple custom procedure
        class DummyProcedure(DecisionProcedure):
            @property
            def name(self):
                return "dummy"
            
            @property
            def supported_types(self):
                return [ProblemType.GENERAL]
            
            def can_handle(self, problem, problem_type=None):
                return "dummy" in problem.lower()
            
            def decide(self, problem, timeout_ms=5000):
                return SolverResult(
                    satisfiable=True,
                    explanation="Dummy solver always returns SAT",
                    solver_name=self.name
                )
            
            def explain(self, result):
                return result.explanation
        
        registry = ProcedureRegistry()
        dummy = DummyProcedure()
        registry.register(dummy)
        
        assert "dummy" in registry.list_procedures()
        assert registry.get_procedure("dummy") is dummy
    
    def test_duplicate_registration_fails(self):
        from apps.asa_fusion.core import ProcedureRegistry
        
        registry = ProcedureRegistry()
        proc = PresburgerProcedure()
        
        registry.register(proc)
        
        # Should raise error on duplicate
        with pytest.raises(ValueError):
            registry.register(proc)
    
    def test_find_capable_procedures(self):
        from apps.asa_fusion.core import ProcedureRegistry
        
        registry = ProcedureRegistry()
        registry.register(PresburgerProcedure())
        registry.register(DiophantineProcedure())
        
        # Linear problem should match Presburger
        capable = registry.find_capable_procedures("x + y = 10")
        assert len(capable) > 0
        assert any(p.name == "presburger" for p in capable)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
