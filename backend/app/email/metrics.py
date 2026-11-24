"""Contadores em memória das tentativas de envio de e-mails de recuperação."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from threading import Lock


@dataclass(frozen=True)
class EmailDeliveryStats:
    attempts: int
    failures: int
    consecutive_failures: int
    last_failure_at: datetime | None
    last_failure_type: str | None


class EmailDeliveryMetrics:
    """Contadores por processo; reiniciam a cada restart da aplicação."""

    def __init__(self) -> None:
        self._lock = Lock()
        self._attempts = 0
        self._failures = 0
        self._consecutive_failures = 0
        self._last_failure_at: datetime | None = None
        self._last_failure_type: str | None = None

    def record_attempt(self) -> None:
        with self._lock:
            self._attempts += 1

    def record_success(self) -> None:
        with self._lock:
            self._consecutive_failures = 0

    def record_failure(self, error_type: str) -> EmailDeliveryStats:
        with self._lock:
            self._failures += 1
            self._consecutive_failures += 1
            self._last_failure_at = datetime.now(timezone.utc)
            self._last_failure_type = error_type
            return self._snapshot_locked()

    def snapshot(self) -> EmailDeliveryStats:
        with self._lock:
            return self._snapshot_locked()

    def reset(self) -> None:
        with self._lock:
            self._attempts = 0
            self._failures = 0
            self._consecutive_failures = 0
            self._last_failure_at = None
            self._last_failure_type = None

    def _snapshot_locked(self) -> EmailDeliveryStats:
        return EmailDeliveryStats(
            attempts=self._attempts,
            failures=self._failures,
            consecutive_failures=self._consecutive_failures,
            last_failure_at=self._last_failure_at,
            last_failure_type=self._last_failure_type,
        )


password_reset_email_metrics = EmailDeliveryMetrics()
