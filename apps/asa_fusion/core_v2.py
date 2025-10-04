from enum import Enum
from dataclasses import dataclass

class Verdict(Enum):
    PASS = "pass"
    FAIL = "fail"
    UNSURE = "unsure"

@dataclass
class Certificate:
    name: str
    validity: bool

class ASAFusionEngine:
    @staticmethod
    def decide(cert: Certificate) -> Verdict:
        return Verdict.PASS if cert.validity else Verdict.FAIL

if __name__ == '__main__':
    # Test cases
    cert1 = Certificate(name="Valid Cert", validity=True)
    cert2 = Certificate(name="Invalid Cert", validity=False)
    
    print(f"{cert1.name}: {ASAFusionEngine.decide(cert1)}")  # Expected: PASS
    print(f"{cert2.name}: {ASAFusionEngine.decide(cert2)}")  # Expected: FAIL
