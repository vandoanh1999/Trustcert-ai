# ASA-Fusion v2.0 Examples

This directory contains examples and demos for ASA-Fusion v2.0 features.

## Running the Demo

To run the comprehensive ASA-Fusion v2.0 demo:

```bash
PYTHONPATH=/path/to/Trustcert-ai python examples/asa_fusion_demo.py
```

Or from the project root:

```bash
cd Trustcert-ai
PYTHONPATH=. python examples/asa_fusion_demo.py
```

## What the Demo Shows

The demo demonstrates all revolutionary features of ASA-Fusion v2.0:

1. **Quantum-Resistant SHA3-256 Certificates**
   - Certificate creation with quantum-resistant signatures
   - Certificate verification
   - Tamper detection

2. **Plugin-Based Decision Procedures**
   - Plugin registration (Z3, CVC5)
   - Plugin management
   - Decision procedure execution

3. **Async/Await Multi-Threaded Batch Processing**
   - Batch certificate creation
   - Parallel processing
   - Performance metrics

4. **Input Validation & Security Hardening**
   - SQL injection detection
   - XSS attack prevention
   - Path traversal protection

5. **Performance Monitoring & Tracing**
   - Operation timing
   - Success rate tracking
   - Statistics aggregation

6. **WebAssembly-Ready Interface**
   - WASM module registration
   - Serialization/deserialization
   - Memory management

## Expected Output

The demo should output success messages for each feature, demonstrating:
- ✓ All certificates created and verified
- ✓ All plugins registered and working
- ✓ Batch processing completed successfully
- ✓ Security threats detected and blocked
- ✓ Performance metrics collected
- ✓ WASM interface functional

## Creating Your Own Examples

You can create your own examples by importing from `apps.asa_fusion`:

```python
from apps.asa_fusion import (
    SHA3CertificateManager,
    PluginRegistry,
    BatchProcessor,
    InputValidator,
    get_monitor,
)

# Your code here
```

Make sure to set PYTHONPATH or run from the project root.
