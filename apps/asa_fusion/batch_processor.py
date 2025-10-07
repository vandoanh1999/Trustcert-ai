"""
ASA-Fusion v2.0 - Async/Await Multi-Threaded Batch Processing
High-performance batch processing with async/await support.
"""

import asyncio
from typing import List, Callable, Any, Dict, Optional, TypeVar, Coroutine
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
import time

from .exceptions import BatchProcessingError, TimeoutError as ASATimeoutError


T = TypeVar('T')
R = TypeVar('R')


@dataclass
class BatchResult:
    """Result of batch processing operation."""
    total: int
    successful: int
    failed: int
    results: List[Any]
    errors: List[Dict[str, Any]]
    duration_seconds: float


class BatchProcessor:
    """Async/await batch processor with timeout protection."""
    
    def __init__(self, max_workers: int = 4, default_timeout: float = 30.0):
        """
        Initialize batch processor.
        
        Args:
            max_workers: Maximum number of worker threads
            default_timeout: Default timeout in seconds
        """
        self.max_workers = max_workers
        self.default_timeout = default_timeout
        self._executor = ThreadPoolExecutor(max_workers=max_workers)
    
    async def process_batch_async(
        self,
        items: List[T],
        processor: Callable[[T], R],
        timeout: Optional[float] = None
    ) -> BatchResult:
        """
        Process batch of items asynchronously.
        
        Args:
            items: Items to process
            processor: Processing function
            timeout: Timeout per item in seconds
            
        Returns:
            BatchResult
            
        Raises:
            BatchProcessingError: If batch processing fails
        """
        if not items:
            raise BatchProcessingError("Cannot process empty batch")
        
        timeout = timeout or self.default_timeout
        start_time = time.time()
        
        results = []
        errors = []
        successful = 0
        failed = 0
        
        # Create tasks for all items
        tasks = []
        for idx, item in enumerate(items):
            task = self._process_item_with_timeout(idx, item, processor, timeout)
            tasks.append(task)
        
        # Wait for all tasks to complete
        completed = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        for idx, result in enumerate(completed):
            if isinstance(result, Exception):
                failed += 1
                errors.append({
                    "index": idx,
                    "item": str(items[idx]),
                    "error": str(result)
                })
                results.append(None)
            else:
                successful += 1
                results.append(result)
        
        duration = time.time() - start_time
        
        return BatchResult(
            total=len(items),
            successful=successful,
            failed=failed,
            results=results,
            errors=errors,
            duration_seconds=duration
        )
    
    async def _process_item_with_timeout(
        self,
        idx: int,
        item: T,
        processor: Callable[[T], R],
        timeout: float
    ) -> R:
        """
        Process single item with timeout protection.
        
        Args:
            idx: Item index
            item: Item to process
            processor: Processing function
            timeout: Timeout in seconds
            
        Returns:
            Processed result
            
        Raises:
            ASATimeoutError: If processing exceeds timeout
        """
        try:
            # Run processor in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            result = await asyncio.wait_for(
                loop.run_in_executor(self._executor, processor, item),
                timeout=timeout
            )
            return result
        except asyncio.TimeoutError:
            raise ASATimeoutError(
                f"Processing item {idx} exceeded timeout of {timeout}s",
                timeout
            )
    
    async def process_batch_concurrent(
        self,
        items: List[T],
        processor: Callable[[T], Coroutine[Any, Any, R]],
        max_concurrent: int = 10,
        timeout: Optional[float] = None
    ) -> BatchResult:
        """
        Process batch with concurrency limit (for async processors).
        
        Args:
            items: Items to process
            processor: Async processing function
            max_concurrent: Maximum concurrent operations
            timeout: Timeout per item in seconds
            
        Returns:
            BatchResult
        """
        if not items:
            raise BatchProcessingError("Cannot process empty batch")
        
        timeout = timeout or self.default_timeout
        start_time = time.time()
        
        results = []
        errors = []
        successful = 0
        failed = 0
        
        # Use semaphore to limit concurrency
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def process_with_semaphore(idx: int, item: T) -> Any:
            async with semaphore:
                try:
                    result = await asyncio.wait_for(processor(item), timeout=timeout)
                    return result
                except asyncio.TimeoutError:
                    raise ASATimeoutError(
                        f"Processing item {idx} exceeded timeout of {timeout}s",
                        timeout
                    )
        
        # Create and gather tasks
        tasks = [process_with_semaphore(idx, item) for idx, item in enumerate(items)]
        completed = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        for idx, result in enumerate(completed):
            if isinstance(result, Exception):
                failed += 1
                errors.append({
                    "index": idx,
                    "item": str(items[idx]),
                    "error": str(result)
                })
                results.append(None)
            else:
                successful += 1
                results.append(result)
        
        duration = time.time() - start_time
        
        return BatchResult(
            total=len(items),
            successful=successful,
            failed=failed,
            results=results,
            errors=errors,
            duration_seconds=duration
        )
    
    def shutdown(self):
        """Shutdown the executor."""
        self._executor.shutdown(wait=True)
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.shutdown()
