"""
Tests for ASA-Fusion v2.0 features.
"""

import pytest
import asyncio
import time
from apps.asa_fusion import (
    # Exceptions
    ASAFusionError,
    ValidationError,
    SecurityError,
    TimeoutError,
    CertificateError,
    PluginError,
    # Crypto
    Certificate,
    SHA3CertificateManager,
    # Plugins
    DecisionResult,
    Z3Plugin,
    CVC5Plugin,
    PluginRegistry,
    # Batch Processing
    BatchProcessor,
    # Validation
    InputValidator,
    # Monitoring
    get_monitor,
    get_tracer,
    # WASM
    get_wasm_interface,
    WasmModule,
    WasmCertificate,
)


class TestExceptions:
    """Test custom exception hierarchy."""
    
    def test_base_exception(self):
        """Test base ASAFusionError."""
        error = ASAFusionError("Test error", "TEST_CODE")
        assert error.message == "Test error"
        assert error.error_code == "TEST_CODE"
        assert str(error) == "Test error"
    
    def test_validation_error(self):
        """Test ValidationError."""
        error = ValidationError("Invalid input")
        assert error.error_code == "VALIDATION_ERROR"
    
    def test_security_error(self):
        """Test SecurityError."""
        error = SecurityError("Security threat")
        assert error.error_code == "SECURITY_ERROR"
    
    def test_timeout_error(self):
        """Test TimeoutError."""
        error = TimeoutError("Timeout", 30.0)
        assert error.error_code == "TIMEOUT_ERROR"
        assert error.timeout_seconds == 30.0


class TestCrypto:
    """Test quantum-resistant cryptography."""
    
    def test_certificate_creation(self):
        """Test certificate creation."""
        manager = SHA3CertificateManager()
        cert = manager.create_certificate("test data", {"key": "value"})
        
        assert cert.data == "test data"
        assert cert.signature is not None
        assert len(cert.signature) == 64  # SHA3-256 hex length
        assert cert.timestamp > 0
        assert cert.metadata == {"key": "value"}
    
    def test_certificate_verification(self):
        """Test certificate verification."""
        manager = SHA3CertificateManager()
        cert = manager.create_certificate("test data")
        
        # Valid certificate should verify
        assert manager.verify_certificate(cert) is True
        
        # Tampered certificate should fail
        cert.data = "tampered data"
        assert manager.verify_certificate(cert) is False
    
    def test_certificate_to_dict(self):
        """Test certificate serialization."""
        manager = SHA3CertificateManager()
        cert = manager.create_certificate("test data")
        cert_dict = cert.to_dict()
        
        assert "data" in cert_dict
        assert "signature" in cert_dict
        assert "timestamp" in cert_dict
    
    def test_empty_data_validation(self):
        """Test empty data validation."""
        manager = SHA3CertificateManager()
        
        with pytest.raises(ValidationError):
            manager.create_certificate("")


class TestPlugins:
    """Test plugin-based decision procedures."""
    
    def test_z3_plugin(self):
        """Test Z3 plugin."""
        plugin = Z3Plugin()
        assert plugin.name == "Z3"
        assert plugin.version == "4.0"
        assert plugin.enabled is True
    
    def test_cvc5_plugin(self):
        """Test CVC5 plugin."""
        plugin = CVC5Plugin()
        assert plugin.name == "CVC5"
        assert plugin.version == "1.0"
    
    def test_plugin_validation(self):
        """Test plugin input validation."""
        plugin = Z3Plugin()
        
        # Valid input
        assert plugin.validate_input("(and p q)") is True
        
        # Invalid input
        with pytest.raises(ValidationError):
            plugin.validate_input("")
        
        with pytest.raises(ValidationError):
            plugin.validate_input("x" * 2000000)  # Too large
    
    def test_plugin_registry(self):
        """Test plugin registry."""
        registry = PluginRegistry()
        
        z3 = Z3Plugin()
        cvc5 = CVC5Plugin()
        
        registry.register_plugin(z3)
        registry.register_plugin(cvc5)
        
        # Should have 2 plugins
        plugins = registry.list_plugins()
        assert len(plugins) == 2
        
        # Get specific plugin
        retrieved = registry.get_plugin("Z3")
        assert retrieved.name == "Z3"
    
    def test_duplicate_plugin_registration(self):
        """Test duplicate plugin registration fails."""
        registry = PluginRegistry()
        plugin = Z3Plugin()
        
        registry.register_plugin(plugin)
        
        with pytest.raises(PluginError):
            registry.register_plugin(plugin)
    
    def test_plugin_not_found(self):
        """Test getting non-existent plugin."""
        registry = PluginRegistry()
        
        with pytest.raises(PluginError):
            registry.get_plugin("NonExistent")


class TestBatchProcessor:
    """Test async/await batch processing."""
    
    @pytest.mark.asyncio
    async def test_batch_processing_async(self):
        """Test async batch processing."""
        processor = BatchProcessor(max_workers=2)
        
        def square(x):
            return x * x
        
        items = [1, 2, 3, 4, 5]
        result = await processor.process_batch_async(items, square, timeout=1.0)
        
        assert result.total == 5
        assert result.successful == 5
        assert result.failed == 0
        assert result.results == [1, 4, 9, 16, 25]
    
    @pytest.mark.asyncio
    async def test_batch_processing_with_errors(self):
        """Test batch processing with errors."""
        processor = BatchProcessor(max_workers=2)
        
        def faulty_processor(x):
            if x == 3:
                raise ValueError("Error on 3")
            return x * 2
        
        items = [1, 2, 3, 4, 5]
        result = await processor.process_batch_async(items, faulty_processor, timeout=1.0)
        
        assert result.total == 5
        assert result.successful == 4
        assert result.failed == 1
        assert len(result.errors) == 1
    
    @pytest.mark.asyncio
    async def test_batch_processing_timeout(self):
        """Test batch processing timeout."""
        processor = BatchProcessor(max_workers=2)
        
        def slow_processor(x):
            time.sleep(2)
            return x
        
        items = [1, 2]
        result = await processor.process_batch_async(items, slow_processor, timeout=0.5)
        
        # Should timeout
        assert result.failed > 0
    
    @pytest.mark.asyncio
    async def test_empty_batch_error(self):
        """Test empty batch raises error."""
        processor = BatchProcessor()
        
        with pytest.raises(Exception):
            await processor.process_batch_async([], lambda x: x)


class TestValidation:
    """Test input validation and security."""
    
    def test_string_validation(self):
        """Test string validation."""
        validator = InputValidator()
        
        # Valid string
        result = validator.validate_string("test", min_length=1, max_length=10)
        assert result == "test"
        
        # Too short
        with pytest.raises(ValidationError):
            validator.validate_string("", min_length=1)
        
        # Too long
        with pytest.raises(ValidationError):
            validator.validate_string("x" * 20, max_length=10)
    
    def test_number_validation(self):
        """Test number validation."""
        validator = InputValidator()
        
        # Valid number
        result = validator.validate_number(5, min_value=0, max_value=10)
        assert result == 5
        
        # Too small
        with pytest.raises(ValidationError):
            validator.validate_number(-1, min_value=0)
        
        # Too large
        with pytest.raises(ValidationError):
            validator.validate_number(11, max_value=10)
    
    def test_list_validation(self):
        """Test list validation."""
        validator = InputValidator()
        
        # Valid list
        result = validator.validate_list([1, 2, 3], min_items=1, max_items=5)
        assert result == [1, 2, 3]
        
        # Too few items
        with pytest.raises(ValidationError):
            validator.validate_list([], min_items=1)
        
        # Too many items
        with pytest.raises(ValidationError):
            validator.validate_list([1, 2, 3], max_items=2)
    
    def test_security_sql_injection(self):
        """Test SQL injection detection."""
        validator = InputValidator()
        
        with pytest.raises(SecurityError):
            validator.check_security_threats("SELECT * FROM users")
    
    def test_security_xss(self):
        """Test XSS detection."""
        validator = InputValidator()
        
        with pytest.raises(SecurityError):
            validator.check_security_threats("<script>alert('xss')</script>")
    
    def test_security_path_traversal(self):
        """Test path traversal detection."""
        validator = InputValidator()
        
        with pytest.raises(SecurityError):
            validator.check_security_threats("../../etc/passwd")
    
    def test_sanitize_string(self):
        """Test string sanitization."""
        validator = InputValidator()
        
        result = validator.sanitize_string("  test\x00data  ")
        assert result == "testdata"  # Null byte removed, spaces stripped


class TestMonitoring:
    """Test performance monitoring and tracing."""
    
    def test_performance_monitor(self):
        """Test performance monitoring."""
        monitor = get_monitor()
        monitor.reset()
        
        with monitor.measure("test_operation"):
            time.sleep(0.01)
        
        stats = monitor.get_statistics("test_operation")
        assert stats["total_calls"] == 1
        assert stats["successful_calls"] == 1
        assert stats["average_duration_ms"] > 0
    
    def test_performance_monitor_with_error(self):
        """Test performance monitoring with error."""
        monitor = get_monitor()
        monitor.reset()
        
        try:
            with monitor.measure("failing_operation"):
                raise ValueError("Test error")
        except ValueError:
            pass
        
        stats = monitor.get_statistics("failing_operation")
        assert stats["total_calls"] == 1
        assert stats["failed_calls"] == 1
    
    def test_distributed_tracer(self):
        """Test distributed tracing."""
        tracer = get_tracer()
        
        span = tracer.start_trace("test_trace")
        assert span.trace_id is not None
        assert span.span_id is not None
        
        span.add_tag("key", "value")
        span.log_event("test_event", {"data": "test"})
        span.finish()
        
        assert span.duration_ms is not None
        assert "key" in span.tags
        assert len(span.logs) == 1


class TestWasmInterface:
    """Test WebAssembly interface."""
    
    def test_wasm_module_registration(self):
        """Test WASM module registration."""
        interface = get_wasm_interface()
        
        module = WasmModule(
            name="test_module",
            version="1.0",
            functions=["func1", "func2"],
            memory_pages=1,
            max_memory_pages=10
        )
        
        interface.register_module(module)
        retrieved = interface.get_module("test_module")
        
        assert retrieved is not None
        assert retrieved.name == "test_module"
    
    def test_wasm_serialization(self):
        """Test WASM serialization."""
        interface = get_wasm_interface()
        
        data = {"key": "value", "number": 42}
        serialized = interface.serialize_for_wasm(data)
        
        assert isinstance(serialized, bytes)
        
        deserialized = interface.deserialize_from_wasm(serialized)
        assert deserialized == data
    
    def test_wasm_certificate(self):
        """Test WASM certificate."""
        cert = WasmCertificate(
            data="test data",
            signature="abc123",
            timestamp=time.time()
        )
        
        # Serialize
        wasm_bytes = cert.to_wasm_bytes()
        assert isinstance(wasm_bytes, bytes)
        
        # Deserialize
        restored = cert.from_wasm_bytes(wasm_bytes)
        assert restored.data == "test data"
        assert restored.signature == "abc123"


class TestIntegration:
    """Integration tests for ASA-Fusion v2.0."""
    
    @pytest.mark.asyncio
    async def test_end_to_end_workflow(self):
        """Test complete workflow with monitoring."""
        monitor = get_monitor()
        monitor.reset()
        
        # Create certificate
        with monitor.measure("certificate_creation"):
            manager = SHA3CertificateManager()
            cert = manager.create_certificate("test data")
        
        # Verify certificate
        with monitor.measure("certificate_verification"):
            is_valid = manager.verify_certificate(cert)
        
        assert is_valid is True
        
        # Check statistics
        stats = monitor.get_statistics()
        assert "certificate_creation" in stats
        assert "certificate_verification" in stats
    
    @pytest.mark.asyncio
    async def test_batch_certificate_processing(self):
        """Test batch certificate creation."""
        processor = BatchProcessor(max_workers=4)
        manager = SHA3CertificateManager()
        
        data_items = [f"data_{i}" for i in range(10)]
        
        def create_cert(data):
            return manager.create_certificate(data)
        
        result = await processor.process_batch_async(data_items, create_cert, timeout=5.0)
        
        assert result.total == 10
        assert result.successful == 10
        assert len(result.results) == 10
        
        # Verify all certificates
        for cert in result.results:
            assert manager.verify_certificate(cert) is True
