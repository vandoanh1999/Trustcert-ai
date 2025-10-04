#!/usr/bin/env python3
# Copyright (c) 2024-2025 Doanh1102. All Rights Reserved.
# ASA-Fusion v2.0 Demo - Showcasing breakthrough features

"""
ASA-Fusion v2.0 Demo
====================

This demo showcases the key features of ASA-Fusion:
- Plugin architecture with multiple decision procedures
- AI-powered problem classification
- Security validation and sandboxing
- Hybrid solver fallback
"""

from apps.asa_fusion import ASAFusionEngine, ProblemType


def print_section(title):
    """Print a formatted section header."""
    print("\n" + "=" * 70)
    print(f" {title}")
    print("=" * 70)


def demo_basic_solving():
    """Demonstrate basic problem solving."""
    print_section("1. Basic Problem Solving")
    
    engine = ASAFusionEngine()
    
    problems = [
        ("x = 42", "Simple assignment"),
        ("x + y = 10", "Linear equation"),
        ("3*x + 6*y = 9", "Linear Diophantine (solvable)"),
        ("3*x + 6*y = 10", "Linear Diophantine (unsolvable)"),
    ]
    
    for problem, description in problems:
        print(f"\n📝 Problem: {problem}")
        print(f"   Description: {description}")
        
        result = engine.solve(problem)
        
        print(f"   ✓ Success: {result['success']}")
        print(f"   ✓ Satisfiable: {result['satisfiable']}")
        print(f"   ✓ Solver: {result['solver']}")
        print(f"   ✓ Time: {result['execution_time_ms']:.2f}ms")
        
        if result.get('model'):
            print(f"   ✓ Model: {result['model']}")
        
        if result.get('explanation'):
            print(f"   ℹ Explanation: {result['explanation']}")


def demo_ai_analysis():
    """Demonstrate AI-powered problem analysis."""
    print_section("2. AI-Powered Problem Classification")
    
    engine = ASAFusionEngine()
    
    problems = [
        "x + y = 10 and x > 0",
        "x^2 + y^2 = 25",
        "(p and q) or (not r)",
        "2*x - 3*y = 7",
    ]
    
    for problem in problems:
        print(f"\n🤖 Analyzing: {problem}")
        
        result = engine.solve(problem, use_ai=True)
        
        if 'ai_analysis' in result:
            analysis = result['ai_analysis']
            print(f"   • Problem Type: {analysis['problem_type']}")
            print(f"   • Confidence: {analysis['confidence']:.0%}")
            print(f"   • Complexity: {analysis['complexity_score']}/10")
            print(f"   • Reasoning: {analysis['reasoning']}")
            
            if analysis['recommendations']:
                print(f"   • Recommendations:")
                for rec in analysis['recommendations']:
                    print(f"     - {rec}")


def demo_security():
    """Demonstrate security features."""
    print_section("3. Security Validation & Protection")
    
    engine = ASAFusionEngine()
    
    # Safe inputs
    print("\n✅ Testing safe inputs:")
    safe_problems = [
        "x + y = 10",
        "2*x - 3 = 7",
    ]
    
    for problem in safe_problems:
        result = engine.solve(problem, validate=True)
        print(f"   • '{problem}' → VALID")
    
    # Dangerous inputs
    print("\n🚫 Testing dangerous inputs:")
    dangerous_problems = [
        "eval(x + y)",
        "__import__('os').system('ls')",
        "open('/etc/passwd').read()",
        "x" * 15000,  # Too large
    ]
    
    for problem in dangerous_problems:
        result = engine.solve(problem, validate=True)
        display_problem = problem[:50] + "..." if len(problem) > 50 else problem
        
        if not result['success']:
            print(f"   • '{display_problem}' → BLOCKED")
            if 'validation_errors' in result:
                for error in result['validation_errors'][:1]:  # Show first error
                    print(f"     Reason: {error}")


def demo_plugin_system():
    """Demonstrate plugin architecture."""
    print_section("4. Plugin Architecture & Solver Registry")
    
    engine = ASAFusionEngine()
    
    print("\n📦 Registered Solvers:")
    solvers = engine.list_solvers()
    for solver in solvers:
        print(f"   • {solver}")
    
    print("\n🔧 Engine Information:")
    info = engine.get_info()
    print(f"   • Version: {info['version']}")
    print(f"   • Author: {info['author']}")
    
    print("\n✨ Features:")
    for feature, enabled in info['features'].items():
        status = "✓" if enabled else "✗"
        print(f"   {status} {feature.replace('_', ' ').title()}")
    
    print(f"\n📜 License: {info['license']}")


def demo_custom_procedure():
    """Demonstrate adding a custom decision procedure."""
    print_section("5. Custom Decision Procedure")
    
    from apps.asa_fusion.core import DecisionProcedure, SolverResult, ProblemType
    
    class SimpleBooleanProcedure(DecisionProcedure):
        """A simple custom procedure for boolean logic."""
        
        @property
        def name(self):
            return "simple_boolean"
        
        @property
        def supported_types(self):
            return [ProblemType.BOOLEAN_LOGIC]
        
        def can_handle(self, problem, problem_type=None):
            return 'true' in problem.lower() or 'false' in problem.lower()
        
        def decide(self, problem, timeout_ms=5000):
            # Simplified: always return SAT for demo
            return SolverResult(
                satisfiable=True,
                explanation="Custom boolean solver (demo)",
                solver_name=self.name
            )
        
        def explain(self, result):
            return "Boolean formula is satisfiable (custom solver)"
    
    # Create engine and register custom procedure
    engine = ASAFusionEngine(auto_register_builtin=False)
    custom_proc = SimpleBooleanProcedure()
    engine.registry.register(custom_proc)
    
    print("\n✨ Created custom SimpleBooleanProcedure")
    print("   Registered solvers:", engine.list_solvers())
    
    # Test it
    result = engine.solve("true and false", use_ai=False)
    print(f"\n📝 Test: 'true and false'")
    print(f"   • Solver: {result['solver']}")
    print(f"   • Satisfiable: {result['satisfiable']}")


def main():
    """Run all demos."""
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║              ASA-Fusion v2.0 - Interactive Demo                      ║
║                                                                      ║
║  Copyright (c) 2024-2025 Doanh1102. All Rights Reserved.            ║
║  Proprietary Software - Unauthorized use prohibited                 ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
    """)
    
    try:
        demo_basic_solving()
        demo_ai_analysis()
        demo_security()
        demo_plugin_system()
        demo_custom_procedure()
        
        print_section("Demo Complete! ✨")
        print("\n🎉 ASA-Fusion v2.0 showcases:")
        print("   ✓ Modular plugin architecture")
        print("   ✓ AI-powered problem classification")
        print("   ✓ Security validation and sandboxing")
        print("   ✓ Multiple decision procedures")
        print("   ✓ Hybrid solver fallback")
        
        print("\n📞 For commercial licensing and premium features:")
        print("   Contact: phamvandoanh9@gmail.com")
        print("   GitHub: https://github.com/vandoanh1999")
        print()
        
    except Exception as e:
        print(f"\n❌ Error running demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
