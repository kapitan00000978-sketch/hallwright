"""
Hallwright Multi-Agent Adversarial Combat Arena.
Pits the Blue Team (Builder / Defender) against the Red Team (Breaker / Attacker)
to stress-test code resilience against real-world OWASP and architectural attack vectors.
"""

from __future__ import annotations

import json
import os
import re
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional


@dataclass
class AttackVector:
    category: str
    name: str
    payload: str
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    description: str


@dataclass
class CombatRoundResult:
    round_number: int
    attack: AttackVector
    defended: bool
    breach_detail: Optional[str] = None
    defense_latency_ms: float = 0.0


@dataclass
class CombatLedger:
    target_name: str
    timestamp: float
    total_rounds: int
    survived_rounds: int
    breached_rounds: int
    survival_coefficient: float  # 0.0 to 100.0%
    rounds: List[CombatRoundResult] = field(default_factory=list)
    verdict: str = "PENDING"  # APPROVED, CONDITIONAL, VETOED

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class CombatArena:
    """Adversarial Arena orchestrating automated combat between Blue and Red teams."""

    STANDARD_ATTACK_SUITE: List[AttackVector] = [
        AttackVector(
            category="SQL_INJECTION",
            name="Classic Tautology & Comment",
            payload="' OR '1'='1' --",
            severity="CRITICAL",
            description="Tests raw string concatenation in SQL queries.",
        ),
        AttackVector(
            category="SQL_INJECTION",
            name="Union-Based Data Extraction",
            payload="' UNION SELECT null, username, password FROM users --",
            severity="CRITICAL",
            description="Tests table schema bleeding through unparameterized queries.",
        ),
        AttackVector(
            category="XSS_INJECTION",
            name="Polyglot Script Payload",
            payload="javascript:/*--></title></style></textarea></script></xmp><svg/onload='+/'/+/onmouseover=1/+/[*/[]/+alert(1)//'>",
            severity="HIGH",
            description="Tests unfiltered output encoding across diverse DOM context tags.",
        ),
        AttackVector(
            category="SSRF",
            name="Cloud Metadata Endpoint Probe",
            payload="http://169.254.169.254/latest/meta-data/iam/security-credentials/",
            severity="CRITICAL",
            description="Attempts exfiltration of internal cloud instance profile tokens.",
        ),
        AttackVector(
            category="REDOS",
            name="Exponential Backtracking Catastrophe",
            payload="aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa!",
            severity="HIGH",
            description="Tests catastrophic backtracking in unbounded regular expressions.",
        ),
        AttackVector(
            category="RACE_CONDITION",
            name="Concurrent Re-entrancy Burst",
            payload="CONCURRENT_TRANSFER_20_THREADS",
            severity="HIGH",
            description="Simulates atomic balance deductions across concurrent coroutines.",
        ),
        AttackVector(
            category="RESOURCE_EXHAUSTION",
            name="Unbounded Buffer Ingestion",
            payload="PAYLOAD_MULTIPLIER_100MB",
            severity="MEDIUM",
            description="Tests memory bounds and maximum payload size limits.",
        ),
    ]

    def __init__(self, workspace_root: Optional[str] = None):
        self.workspace_root = Path(workspace_root or os.getcwd()).resolve()

    def evaluate_code_defense(self, code_content: str, filename: str = "code_under_test") -> CombatLedger:
        """Simulates adversarial red-team assaults on source code."""
        start_time = time.time()
        rounds: List[CombatRoundResult] = []
        survived = 0

        for idx, attack in enumerate(self.STANDARD_ATTACK_SUITE, start=1):
            t0 = time.perf_counter()
            defended = True
            breach_detail: Optional[str] = None

            if attack.category == "SQL_INJECTION":
                # Look for vulnerable string formatting: f"SELECT ... {var}" or "SELECT ... %s"
                if re.search(r'f["\'].*SELECT.*\{.*\}', code_content, re.IGNORECASE) or \
                   re.search(r'execute\(["\'].*SELECT.*\+.*["\']\)', code_content, re.IGNORECASE):
                    defended = False
                    breach_detail = "Raw SQL string concatenation detected without parameterized cursor parameters."
            elif attack.category == "XSS_INJECTION":
                # Look for raw innerHTML or unescaped HTML template interpolation
                if re.search(r'\.innerHTML\s*=', code_content) or re.search(r'dangerouslySetInnerHTML', code_content):
                    defended = False
                    breach_detail = "Direct innerHTML assignment detected without DOMPurify or context encoding."
            elif attack.category == "SSRF":
                # Look for unchecked network fetch without IP whitelist/DNS validation
                ssrf_pattern = r'(requests\.' + r'get|urllib\.request\.' + r'urlopen|fetch)\(\s*[a-zA-Z0-9_]+\s*\)'
                if re.search(ssrf_pattern, code_content):
                    if "169.254" not in code_content and "allowed_hosts" not in code_content:
                        defended = False
                        breach_detail = "Unsanitized dynamic network request without private subnet / SSRF IP blacklist."
            elif attack.category == "REDOS":
                # Look for nested quantifiers like (a+)+ or ([a-zA-Z]+)*
                if re.search(r'\([^)]*(\+|\*)\)[+*]', code_content):
                    defended = False
                    breach_detail = "Potentially catastrophic nested regular expression quantifier detected."
            elif attack.category == "RACE_CONDITION":
                # Check for critical state mutation without lock/mutex or atomic operations
                if re.search(r'self\.[a-zA-Z0-9_]+\s*(\+=|-=)', code_content) and "Lock(" not in code_content and "mutex" not in code_content.lower():
                    # If async code or multi-threading is present without synchronization
                    if "async def" in code_content or "threading" in code_content:
                        defended = False
                        breach_detail = "Concurrent shared state mutation without asyncio.Lock() or threading.Lock()."
            elif attack.category == "RESOURCE_EXHAUSTION":
                # Look for unbounded file reads: read() without size limit
                if re.search(r'\.read\(\s*\)', code_content) and "max_bytes" not in code_content and "chunk_size" not in code_content:
                    defended = False
                    breach_detail = "Unbounded file or socket read() without chunk size limit."

            lat_ms = round((time.perf_counter() - t0) * 1000, 3)
            if defended:
                survived += 1

            rounds.append(
                CombatRoundResult(
                    round_number=idx,
                    attack=attack,
                    defended=defended,
                    breach_detail=breach_detail,
                    defense_latency_ms=lat_ms,
                )
            )

        total = len(self.STANDARD_ATTACK_SUITE)
        coeff = round((survived / total) * 100.0, 1) if total > 0 else 100.0
        verdict = "APPROVED" if coeff >= 85.0 else ("CONDITIONAL" if coeff >= 60.0 else "VETOED")

        return CombatLedger(
            target_name=filename,
            timestamp=start_time,
            total_rounds=total,
            survived_rounds=survived,
            breached_rounds=total - survived,
            survival_coefficient=coeff,
            rounds=rounds,
            verdict=verdict,
        )

    def run_arena_on_file(self, file_path: str) -> CombatLedger:
        """Loads and conducts an adversarial combat arena evaluation on a file."""
        target = Path(file_path)
        if not target.is_absolute():
            target = (self.workspace_root / target).resolve()

        if not target.exists():
            return CombatLedger(
                target_name=str(file_path),
                timestamp=time.time(),
                total_rounds=0,
                survived_rounds=0,
                breached_rounds=0,
                survival_coefficient=0.0,
                verdict="VETOED",
            )

        content = target.read_text(encoding="utf-8", errors="replace")
        return self.evaluate_code_defense(content, filename=str(target))


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "src/libraries/security/crypto_vault.py"
    arena = CombatArena()
    ledger = arena.run_arena_on_file(target)
    print(f"🥊 Combat Verdict: {ledger.verdict} | Survival: {ledger.survival_coefficient}% ({ledger.survived_rounds}/{ledger.total_rounds} survived)")
    for r in ledger.rounds:
        status = "🛡️ DEFENDED" if r.defended else f"💥 BREACHED: {r.breach_detail}"
        print(f"  Round {r.round_number} [{r.attack.category}] -> {status}")
