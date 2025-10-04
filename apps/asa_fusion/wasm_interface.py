"""
ASA-Fusion v2.0 - WebAssembly Interface
WebAssembly-ready design with interface definitions for WASM integration.
"""

from typing import Any, Dict, List, Optional
from abc import ABC, abstractmethod
from dataclasses import dataclass
import json


@dataclass
class WasmModule:
    """WebAssembly module metadata."""
    name: str
    version: str
    functions: List[str]
    memory_pages: int
    max_memory_pages: int


class WasmSerializable(ABC):
    """Base class for WebAssembly-serializable objects."""
    
    @abstractmethod
    def to_wasm_bytes(self) -> bytes:
        """Convert to bytes for WASM."""
        pass
    
    @abstractmethod
    def from_wasm_bytes(self, data: bytes) -> 'WasmSerializable':
        """Create from bytes from WASM."""
        pass


class WasmInterface:
    """
    Interface for WebAssembly integration.
    
    This provides a bridge between Python and WebAssembly modules,
    enabling ASA-Fusion to run in browser environments and edge computing.
    """
    
    def __init__(self):
        self._modules: Dict[str, WasmModule] = {}
    
    def register_module(self, module: WasmModule) -> None:
        """
        Register a WASM module.
        
        Args:
            module: WasmModule to register
        """
        self._modules[module.name] = module
    
    def get_module(self, name: str) -> Optional[WasmModule]:
        """
        Get registered WASM module.
        
        Args:
            name: Module name
            
        Returns:
            WasmModule or None
        """
        return self._modules.get(name)
    
    def list_modules(self) -> List[WasmModule]:
        """List all registered WASM modules."""
        return list(self._modules.values())
    
    @staticmethod
    def serialize_for_wasm(data: Any) -> bytes:
        """
        Serialize Python data for WASM consumption.
        
        Args:
            data: Data to serialize
            
        Returns:
            Serialized bytes
        """
        if isinstance(data, bytes):
            return data
        
        # Convert to JSON and then to bytes
        json_str = json.dumps(data, default=str)
        return json_str.encode('utf-8')
    
    @staticmethod
    def deserialize_from_wasm(data: bytes) -> Any:
        """
        Deserialize data from WASM.
        
        Args:
            data: Bytes from WASM
            
        Returns:
            Deserialized Python object
        """
        if not data:
            return None
        
        try:
            json_str = data.decode('utf-8')
            return json.loads(json_str)
        except (UnicodeDecodeError, json.JSONDecodeError):
            # Return raw bytes if not JSON
            return data
    
    def create_wasm_context(self, memory_pages: int = 1) -> Dict[str, Any]:
        """
        Create a context for WASM execution.
        
        Args:
            memory_pages: Number of 64KB memory pages
            
        Returns:
            Context dictionary
        """
        return {
            "memory_pages": memory_pages,
            "memory_size_bytes": memory_pages * 65536,
            "stack_size": 1024 * 1024,  # 1MB stack
            "heap_size": memory_pages * 65536 - 1024 * 1024
        }


class WasmCertificate(WasmSerializable):
    """WebAssembly-compatible certificate."""
    
    def __init__(self, data: str, signature: str, timestamp: float):
        self.data = data
        self.signature = signature
        self.timestamp = timestamp
    
    def to_wasm_bytes(self) -> bytes:
        """Convert certificate to bytes for WASM."""
        cert_dict = {
            "data": self.data,
            "signature": self.signature,
            "timestamp": self.timestamp
        }
        return WasmInterface.serialize_for_wasm(cert_dict)
    
    def from_wasm_bytes(self, data: bytes) -> 'WasmCertificate':
        """Create certificate from WASM bytes."""
        cert_dict = WasmInterface.deserialize_from_wasm(data)
        return WasmCertificate(
            data=cert_dict["data"],
            signature=cert_dict["signature"],
            timestamp=cert_dict["timestamp"]
        )


class WasmExportable:
    """
    Mixin for classes that can be exported to WebAssembly.
    
    This enables ASA-Fusion components to be compiled and run in WASM environments,
    supporting browser-based verification and edge computing deployments.
    """
    
    @staticmethod
    def get_wasm_exports() -> List[str]:
        """
        Get list of functions exported to WASM.
        
        Returns:
            List of function names
        """
        return [
            "validate_input",
            "generate_certificate",
            "verify_certificate",
            "check_satisfiability",
            "process_batch"
        ]
    
    @staticmethod
    def get_wasm_imports() -> List[str]:
        """
        Get list of functions imported from WASM host.
        
        Returns:
            List of function names
        """
        return [
            "console_log",
            "get_timestamp",
            "random_bytes"
        ]
    
    @staticmethod
    def get_wasm_memory_config() -> Dict[str, int]:
        """
        Get WASM memory configuration.
        
        Returns:
            Memory configuration dictionary
        """
        return {
            "initial_pages": 16,  # 1MB initial
            "max_pages": 256,     # 16MB maximum
            "stack_size": 65536   # 64KB stack
        }


# Global WASM interface instance
_wasm_interface = WasmInterface()


def get_wasm_interface() -> WasmInterface:
    """Get global WASM interface instance."""
    return _wasm_interface
