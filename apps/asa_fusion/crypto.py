import hashlib
import json
import time
import platform
import sys
from dataclasses import dataclass
from typing import Dict, Any, Optional, List


class ValidationError(Exception): ...
class CertificateError(Exception): ...


def runtime_fingerprint() -> str:
    payload = {
        "python": sys.version,
        "abi": sys.abiflags,
        "platform": platform.platform(),
        "machine": platform.machine(),
    }
    return hashlib.sha3_256(
        json.dumps(payload, sort_keys=True).encode()
    ).hexdigest()


@dataclass(frozen=True)
class Certificate:
    data_hash: str
    timestamp: float
    signature: str
    height: int


class ASAFusionLocalChain:
    """
    Machine-bound tamper-evident audit log.
    NOT portable. NOT distributed.
    """

    def __init__(self):
        self.runtime_id = runtime_fingerprint()
        self.chain: List[Certificate] = []

    def _hash(self, s: str) -> str:
        return hashlib.sha3_256(s.encode()).hexdigest()

    def _derive(self, data_hash: str, ts: float, prev_sig: str, height: int) -> str:
        payload = f"{data_hash}|{ts}|{prev_sig}|{height}|{self.runtime_id}"
        return self._hash(payload)

    def append(self, data: str) -> Certificate:
        if not data:
            raise ValidationError("Empty data")

        data_hash = self._hash(data)
        ts = time.time()

        if self.chain:
            prev = self.chain[-1]
            if ts <= prev.timestamp:
                raise ValidationError("Timestamp must be strictly increasing")
            prev_sig = prev.signature
            height = prev.height + 1
        else:
            prev_sig = "GENESIS"
            height = 1

        sig = self._derive(data_hash, ts, prev_sig, height)
        cert = Certificate(data_hash, ts, sig, height)
        self.chain.append(cert)
        return cert

    def verify_chain(self) -> bool:
        prev_sig = "GENESIS"
        for i, cert in enumerate(self.chain, start=1):
            expected = self._derive(
                cert.data_hash,
                cert.timestamp,
                prev_sig,
                i
            )
            if cert.signature != expected or cert.height != i:
                return False
            prev_sig = cert.signature
        return True