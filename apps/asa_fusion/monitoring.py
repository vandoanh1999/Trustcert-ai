"""
ASA-Fusion v2.0 - Performance Monitoring and Tracing
Real-time performance monitoring and distributed tracing.
"""

import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from contextlib import contextmanager
import threading
from collections import defaultdict


@dataclass
class PerformanceMetrics:
    """Performance metrics for an operation."""
    operation_name: str
    start_time: float
    end_time: Optional[float] = None
    duration_ms: Optional[float] = None
    success: bool = True
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def complete(self, success: bool = True, error_message: Optional[str] = None):
        """Mark operation as complete."""
        self.end_time = time.time()
        self.duration_ms = (self.end_time - self.start_time) * 1000
        self.success = success
        self.error_message = error_message


@dataclass
class TraceSpan:
    """Distributed tracing span."""
    trace_id: str
    span_id: str
    parent_span_id: Optional[str]
    operation_name: str
    start_time: float
    end_time: Optional[float] = None
    duration_ms: Optional[float] = None
    tags: Dict[str, Any] = field(default_factory=dict)
    logs: List[Dict[str, Any]] = field(default_factory=list)
    
    def finish(self):
        """Finish the span."""
        self.end_time = time.time()
        self.duration_ms = (self.end_time - self.start_time) * 1000
    
    def add_tag(self, key: str, value: Any):
        """Add a tag to the span."""
        self.tags[key] = value
    
    def log_event(self, event: str, metadata: Optional[Dict[str, Any]] = None):
        """Log an event in the span."""
        self.logs.append({
            "timestamp": time.time(),
            "event": event,
            "metadata": metadata or {}
        })


class PerformanceMonitor:
    """Real-time performance monitoring system."""
    
    def __init__(self):
        self._metrics: List[PerformanceMetrics] = []
        self._lock = threading.Lock()
        self._operation_stats = defaultdict(lambda: {
            "count": 0,
            "total_duration_ms": 0.0,
            "success_count": 0,
            "error_count": 0
        })
    
    @contextmanager
    def measure(self, operation_name: str, metadata: Optional[Dict[str, Any]] = None):
        """
        Context manager to measure operation performance.
        
        Args:
            operation_name: Name of the operation
            metadata: Optional metadata
            
        Yields:
            PerformanceMetrics object
        """
        metrics = PerformanceMetrics(
            operation_name=operation_name,
            start_time=time.time(),
            metadata=metadata or {}
        )
        
        try:
            yield metrics
            metrics.complete(success=True)
        except Exception as e:
            metrics.complete(success=False, error_message=str(e))
            raise
        finally:
            self._record_metrics(metrics)
    
    def _record_metrics(self, metrics: PerformanceMetrics):
        """Record metrics internally."""
        with self._lock:
            self._metrics.append(metrics)
            
            # Update operation statistics
            stats = self._operation_stats[metrics.operation_name]
            stats["count"] += 1
            if metrics.duration_ms:
                stats["total_duration_ms"] += metrics.duration_ms
            if metrics.success:
                stats["success_count"] += 1
            else:
                stats["error_count"] += 1
    
    def get_metrics(self, operation_name: Optional[str] = None) -> List[PerformanceMetrics]:
        """
        Get recorded metrics.
        
        Args:
            operation_name: Optional operation name to filter by
            
        Returns:
            List of PerformanceMetrics
        """
        with self._lock:
            if operation_name:
                return [m for m in self._metrics if m.operation_name == operation_name]
            return list(self._metrics)
    
    def get_statistics(self, operation_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get aggregated statistics.
        
        Args:
            operation_name: Optional operation name to filter by
            
        Returns:
            Dictionary of statistics
        """
        with self._lock:
            if operation_name:
                stats = self._operation_stats.get(operation_name, {})
                if not stats:
                    return {}
                
                avg_duration = (
                    stats["total_duration_ms"] / stats["count"] 
                    if stats["count"] > 0 else 0
                )
                
                return {
                    "operation": operation_name,
                    "total_calls": stats["count"],
                    "successful_calls": stats["success_count"],
                    "failed_calls": stats["error_count"],
                    "average_duration_ms": round(avg_duration, 2),
                    "success_rate": (
                        stats["success_count"] / stats["count"] 
                        if stats["count"] > 0 else 0
                    )
                }
            
            # Return all statistics
            all_stats = {}
            for op_name, stats in self._operation_stats.items():
                avg_duration = (
                    stats["total_duration_ms"] / stats["count"] 
                    if stats["count"] > 0 else 0
                )
                
                all_stats[op_name] = {
                    "total_calls": stats["count"],
                    "successful_calls": stats["success_count"],
                    "failed_calls": stats["error_count"],
                    "average_duration_ms": round(avg_duration, 2),
                    "success_rate": (
                        stats["success_count"] / stats["count"] 
                        if stats["count"] > 0 else 0
                    )
                }
            
            return all_stats
    
    def reset(self):
        """Reset all metrics."""
        with self._lock:
            self._metrics.clear()
            self._operation_stats.clear()


class DistributedTracer:
    """Distributed tracing system."""
    
    def __init__(self):
        self._spans: Dict[str, List[TraceSpan]] = defaultdict(list)
        self._lock = threading.Lock()
        self._span_counter = 0
    
    def start_trace(self, operation_name: str, trace_id: Optional[str] = None) -> TraceSpan:
        """
        Start a new trace.
        
        Args:
            operation_name: Name of the operation
            trace_id: Optional trace ID (generated if not provided)
            
        Returns:
            TraceSpan
        """
        if not trace_id:
            trace_id = f"trace_{int(time.time() * 1000000)}"
        
        span_id = self._generate_span_id()
        span = TraceSpan(
            trace_id=trace_id,
            span_id=span_id,
            parent_span_id=None,
            operation_name=operation_name,
            start_time=time.time()
        )
        
        self._record_span(span)
        return span
    
    def start_span(
        self,
        operation_name: str,
        trace_id: str,
        parent_span_id: str
    ) -> TraceSpan:
        """
        Start a child span.
        
        Args:
            operation_name: Name of the operation
            trace_id: Trace ID from parent
            parent_span_id: Parent span ID
            
        Returns:
            TraceSpan
        """
        span_id = self._generate_span_id()
        span = TraceSpan(
            trace_id=trace_id,
            span_id=span_id,
            parent_span_id=parent_span_id,
            operation_name=operation_name,
            start_time=time.time()
        )
        
        self._record_span(span)
        return span
    
    def _generate_span_id(self) -> str:
        """Generate unique span ID."""
        with self._lock:
            self._span_counter += 1
            return f"span_{self._span_counter}"
    
    def _record_span(self, span: TraceSpan):
        """Record span internally."""
        with self._lock:
            self._spans[span.trace_id].append(span)
    
    def get_trace(self, trace_id: str) -> List[TraceSpan]:
        """
        Get all spans for a trace.
        
        Args:
            trace_id: Trace ID
            
        Returns:
            List of TraceSpan
        """
        with self._lock:
            return list(self._spans.get(trace_id, []))
    
    def get_all_traces(self) -> Dict[str, List[TraceSpan]]:
        """Get all traces."""
        with self._lock:
            return {k: list(v) for k, v in self._spans.items()}


# Global instances
_monitor = PerformanceMonitor()
_tracer = DistributedTracer()


def get_monitor() -> PerformanceMonitor:
    """Get global performance monitor instance."""
    return _monitor


def get_tracer() -> DistributedTracer:
    """Get global distributed tracer instance."""
    return _tracer
