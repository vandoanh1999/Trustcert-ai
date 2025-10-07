# Copyright (c) 2024-2025 Doanh1102. All Rights Reserved.
# This file is part of ASA-Fusion v2.0 - Proprietary Software
# Unauthorized copying, modification, or distribution is strictly prohibited.

"""
Sandboxing utilities for safe execution of solver code.
"""

import signal
import time
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Any, Callable, Optional


@dataclass
class SandboxConfig:
    """Configuration for sandboxed execution."""
    timeout_seconds: float = 5.0
    max_memory_mb: Optional[int] = 512
    allow_network: bool = False


class TimeoutError(Exception):
    """Raised when execution times out."""
    pass


class MemoryLimitError(Exception):
    """Raised when memory limit is exceeded."""
    pass


def _timeout_handler(signum, frame):
    """Signal handler for timeout."""
    raise TimeoutError("Execution timed out")


@contextmanager
def timeout_context(seconds: float):
    """
    Context manager for execution timeout.
    
    Args:
        seconds: Maximum execution time
        
    Raises:
        TimeoutError: If execution exceeds timeout
    """
    # Set up the signal handler
    old_handler = signal.signal(signal.SIGALRM, _timeout_handler)
    
    # Set the alarm
    signal.setitimer(signal.ITIMER_REAL, seconds)
    
    try:
        yield
    finally:
        # Cancel the alarm and restore old handler
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, old_handler)


def execute_sandboxed(
    func: Callable[[], Any],
    config: SandboxConfig = None
) -> Any:
    """
    Execute a function in a sandboxed environment with resource limits.
    
    Args:
        func: The function to execute
        config: Sandbox configuration
        
    Returns:
        The result of the function
        
    Raises:
        TimeoutError: If execution exceeds timeout
        MemoryLimitError: If memory limit is exceeded
    """
    if config is None:
        config = SandboxConfig()
    
    # Apply resource limits
    try:
        import resource
        
        # Set memory limit if specified
        if config.max_memory_mb:
            max_memory_bytes = config.max_memory_mb * 1024 * 1024
            resource.setrlimit(
                resource.RLIMIT_AS,
                (max_memory_bytes, max_memory_bytes)
            )
    except (ImportError, ValueError, OSError):
        # Resource module not available or limit not supported
        pass
    
    # Execute with timeout
    try:
        with timeout_context(config.timeout_seconds):
            start_time = time.time()
            result = func()
            execution_time = time.time() - start_time
            
            return result
    except MemoryError:
        raise MemoryLimitError("Memory limit exceeded during execution")
    except TimeoutError:
        raise
    finally:
        # Reset resource limits
        try:
            import resource
            resource.setrlimit(resource.RLIMIT_AS, (resource.RLIM_INFINITY, resource.RLIM_INFINITY))
        except (ImportError, ValueError, OSError):
            pass
