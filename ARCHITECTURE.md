# ASA-Fusion v2.0 - Architecture Documentation

## 📐 System Overview

ASA-Fusion v2.0 is a breakthrough modular framework for automated theorem proving and SMT solving. It combines:
- **Plugin Architecture:** Dynamic solver loading
- **AI Reasoning:** Intelligent problem classification
- **Hybrid Solving:** Multiple decision procedures with fallback
- **Security:** Validation, sandboxing, and resource control

## 🏗️ High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    ASA-Fusion Engine                        │
│  (Orchestration, Strategy, Execution)                       │
└─────────────────────────────────────────────────────────────┘
           │                    │                    │
           ▼                    ▼                    ▼
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│   AI Analyzer    │  │   Validator      │  │  Sandbox         │
│  (Classification)│  │  (Security)      │  │  (Isolation)     │
└──────────────────┘  └──────────────────┘  └──────────────────┘
                              │
                              ▼
                   ┌──────────────────┐
                   │ Procedure Registry│
                   │  (Plugin Manager) │
                   └──────────────────┘
                              │
          ┌───────────────────┼───────────────────┐
          ▼                   ▼                   ▼
    ┌──────────┐       ┌──────────┐       ┌──────────┐
    │Presburger│       │Diophantine│      │ Z3 Solver│
    │Procedure │       │Procedure  │      │(Fallback)│
    └──────────┘       └──────────┘       └──────────┘
```

## 🔧 Core Components

### 1. Core Module (`apps/asa_fusion/core/`)

#### `interfaces.py`
Defines the standard interfaces for the framework:

```python
class DecisionProcedure(ABC):
    """Base interface for all decision procedures."""
    
    @abstractmethod
    def name(self) -> str:
        """Unique identifier for this procedure."""
    
    @abstractmethod
    def can_handle(self, problem, problem_type) -> bool:
        """Determine if this procedure can solve the problem."""
    
    @abstractmethod
    def decide(self, problem, timeout_ms) -> SolverResult:
        """Attempt to solve the problem."""
    
    @abstractmethod
    def explain(self, result) -> str:
        """Generate human-readable explanation."""
```

**Key Classes:**
- `DecisionProcedure`: Abstract base for all solvers
- `SolverResult`: Standard result format
- `ProblemType`: Enum of problem categories

#### `registry.py`
Manages the plugin system:

```python
class ProcedureRegistry:
    """Central registry for decision procedures."""
    
    def register(self, procedure: DecisionProcedure)
    def find_capable_procedures(self, problem) -> List[DecisionProcedure]
    def solve(self, problem, problem_type, timeout_ms) -> SolverResult
```

**Features:**
- Dynamic procedure registration
- Priority-based solver selection
- Automatic fallback on failure
- Thread-safe operation

### 2. AI Layer (`apps/asa_fusion/ai_layer/`)

#### `analyzer.py`
Implements AI-powered problem classification:

```python
class ProblemAnalyzer:
    """Analyzes problems and recommends strategies."""
    
    def analyze(self, problem: str) -> AnalysisResult:
        """Classify problem and suggest approach."""
```

**Classification Heuristics:**
- Pattern matching for problem types
- Complexity scoring (1-10 scale)
- Confidence estimation
- Optimization suggestions

**Supported Types:**
- Presburger arithmetic
- Diophantine equations
- Linear/nonlinear arithmetic
- Boolean logic
- General SMT problems

### 3. Security Module (`apps/asa_fusion/security/`)

#### `validator.py`
Input validation and sanitization:

```python
class InputValidator:
    """Validates and sanitizes input."""
    
    def validate(self, input_str: str) -> ValidationResult:
        """Check for security issues."""
```

**Protection Against:**
- Code injection (eval, exec, import)
- Path traversal attacks
- XSS attempts
- DoS via oversized input
- Excessive nesting depth

#### `sandbox.py`
Resource-limited execution:

```python
def execute_sandboxed(func, config: SandboxConfig):
    """Execute function with resource limits."""
```

**Limits:**
- Execution timeout (signal-based)
- Memory limits (via resource module)
- CPU time limits
- No network access by default

### 4. Plugins (`apps/asa_fusion/plugins/`)

Built-in decision procedures:

#### `presburger.py`
Handles Presburger arithmetic:
- Linear integer arithmetic
- Addition and subtraction
- No multiplication of variables
- Comparison operators

#### `diophantine.py`
Handles Diophantine equations:
- Integer polynomial equations
- GCD-based solvability check
- Linear Diophantine solver

**Plugin Interface:**
Every plugin implements `DecisionProcedure`:
1. Declares supported problem types
2. Implements `can_handle()` check
3. Provides `decide()` solver
4. Offers `explain()` for results

### 5. Solvers (`apps/asa_fusion/solvers/`)

#### `z3_solver.py`
Integration with Z3 SMT solver:

```python
class Z3Solver(DecisionProcedure):
    """Fallback to Microsoft Z3 SMT solver."""
```

**Features:**
- Handles general SMT problems
- Low priority (fallback)
- Timeout support
- Optional (requires z3-solver package)

### 6. Engine (`apps/asa_fusion/engine.py`)

Main orchestration engine:

```python
class ASAFusionEngine:
    """Main engine coordinating all components."""
    
    def solve(self, problem, problem_type, timeout_ms) -> dict:
        """End-to-end problem solving."""
```

**Workflow:**
1. **Validate** input (if enabled)
2. **Analyze** with AI (if enabled)
3. **Select** capable procedures
4. **Execute** in sandbox (if enabled)
5. **Return** comprehensive result

## 🔄 Execution Flow

```
User Input
    ↓
[Input Validation]
    ↓
    ├─ Dangerous pattern? → REJECT
    ├─ Too large? → REJECT
    └─ Valid → Continue
    ↓
[AI Analysis]
    ↓
    ├─ Classify problem type
    ├─ Estimate complexity
    └─ Recommend solver
    ↓
[Procedure Selection]
    ↓
    ├─ Find capable procedures
    ├─ Sort by priority
    └─ Select top candidates
    ↓
[Sandboxed Execution]
    ↓
    ├─ Try procedure #1
    │   ├─ Success → Return result
    │   └─ Fail/Unknown → Try next
    ├─ Try procedure #2
    │   └─ ...
    └─ All failed → Return UNKNOWN
    ↓
Result + Metadata
```

## 🎯 Design Principles

### 1. Modularity
- Each component is independent
- Clear interfaces between modules
- Easy to add new procedures
- Plugin architecture

### 2. Security First
- Validation by default
- Sandboxed execution
- Resource limits
- No trust in user input

### 3. Intelligent Routing
- AI-guided solver selection
- Automatic fallback strategy
- Performance optimization
- Adaptive behavior

### 4. Extensibility
- Standard interfaces
- Plugin system
- Custom procedures
- Third-party integrations

### 5. Performance
- Priority-based selection
- Early rejection of incapable solvers
- Configurable timeouts
- Efficient pattern matching

## 📊 Data Flow

### Input Processing
```
Raw Problem String
    ↓ (validate)
Sanitized String
    ↓ (analyze)
AnalysisResult {
    problem_type,
    confidence,
    complexity,
    recommendations
}
```

### Solving Pipeline
```
Problem + Analysis
    ↓ (find_capable_procedures)
List[DecisionProcedure]
    ↓ (sort by priority)
Ordered Procedures
    ↓ (try each)
SolverResult {
    satisfiable,
    model,
    explanation,
    metadata
}
```

### Output Format
```python
{
    "success": bool,
    "satisfiable": bool | None,
    "solver": str,
    "execution_time_ms": float,
    "explanation": str,
    "model": dict | None,
    "ai_analysis": {
        "problem_type": str,
        "confidence": float,
        "complexity_score": int,
        "reasoning": str
    },
    "metadata": dict
}
```

## 🔌 Extension Points

### Adding a Custom Solver

1. **Implement Interface:**
```python
class MyCustomSolver(DecisionProcedure):
    @property
    def name(self):
        return "my_solver"
    
    def can_handle(self, problem, problem_type):
        # Return True if can solve
        return my_check(problem)
    
    def decide(self, problem, timeout_ms):
        # Solve and return SolverResult
        return SolverResult(...)
```

2. **Register:**
```python
engine = ASAFusionEngine(auto_register_builtin=False)
engine.registry.register(MyCustomSolver())
```

### Extending AI Analysis

Subclass `ProblemAnalyzer`:
```python
class MLProblemAnalyzer(ProblemAnalyzer):
    def __init__(self, model):
        super().__init__()
        self.ml_model = model
    
    def analyze(self, problem):
        # Use ML model for classification
        prediction = self.ml_model.predict(problem)
        return AnalysisResult(...)
```

### Custom Validation Rules

Extend `InputValidator`:
```python
class StrictValidator(InputValidator):
    def validate(self, input_str):
        result = super().validate(input_str)
        # Add custom checks
        if my_custom_check(input_str):
            result.errors.append("Custom validation failed")
        return result
```

## 🚀 Performance Considerations

### Optimization Strategies

1. **Early Rejection**
   - Quick `can_handle()` checks
   - Avoid expensive parsing if not capable

2. **Priority Ordering**
   - Fast solvers first
   - Specialized before general
   - Fallback last

3. **Caching** (Future)
   - Cache analysis results
   - Memoize problem classifications
   - Store successful strategies

4. **Parallelization** (Future)
   - Try multiple procedures in parallel
   - Race for first solution
   - Timeout management

### Scalability

**Current:**
- Single-threaded
- Sequential procedure trying
- Memory-resident only

**Future:**
- Multi-threaded execution
- Distributed solving
- Persistent cache
- Load balancing

## 🔐 Security Architecture

### Defense in Depth

1. **Layer 1: Input Validation**
   - Pattern matching for dangers
   - Size and complexity limits
   - Sanitization

2. **Layer 2: Sandboxing**
   - Resource limits
   - Timeout enforcement
   - Memory constraints

3. **Layer 3: Monitoring**
   - Execution metrics
   - Anomaly detection
   - Audit logging

### Threat Model

**Protected Against:**
- Code injection attacks
- Resource exhaustion (DoS)
- Path traversal
- Memory overflow
- Infinite loops

**Not Protected Against:**
- Sophisticated side-channel attacks
- Hardware-level vulnerabilities
- Social engineering
- Physical access

## 📚 Further Reading

- **SMT Solving:** [SMT-LIB Standard](http://smtlib.cs.uiowa.edu/)
- **Z3:** [Z3 Guide](https://microsoft.github.io/z3guide/)
- **Presburger Arithmetic:** [Wikipedia](https://en.wikipedia.org/wiki/Presburger_arithmetic)
- **Decision Procedures:** "Decision Procedures" by Kroening & Strichman

---

**Document Version:** 2.0  
**Last Updated:** January 2025  
**Author:** Doanh1102
