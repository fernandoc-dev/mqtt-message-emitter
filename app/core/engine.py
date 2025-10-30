#!/usr/bin/env python
import json
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, Optional


@dataclass
class RecurrenceConfig:
    mode: str  # "fixed" | "infinite"
    count: Optional[int] = None  # requerido si mode==fixed


class CentralEngine:
    """Motor central: ejecuta un escenario a una frecuencia fija,
    con control de impresión y logging.
    """

    def __init__(
        self,
        publish_fn: Callable[[str], None],
        print_mode: str = "none",  # none|first|nth|all
        print_n: int = 1,
        log_enabled: bool = False,
        log_file: Optional[str] = None,
    ) -> None:
        self.publish_fn = publish_fn
        self.print_mode = print_mode
        self.print_n = max(1, int(print_n))
        self.log_enabled = log_enabled
        self.log_file = log_file
        self._log_handle = None

    def _maybe_print(self, index: int, payload: str) -> None:
        if self.print_mode == "none":
            return
        if self.print_mode == "all":
            print(payload)
            return
        if self.print_mode == "first" and index == 1:
            print(payload)
            return
        if self.print_mode == "nth" and index == self.print_n:
            print(payload)
            return

    def _maybe_log(self, payload: str) -> None:
        if not self.log_enabled:
            return
        if self._log_handle is None:
            path = Path(self.log_file or "app_logs.jsonl")
            path.parent.mkdir(parents=True, exist_ok=True)
            self._log_handle = path.open("a", encoding="utf-8")
        self._log_handle.write(payload + "\n")
        self._log_handle.flush()

    def run(
        self,
        rate_hz: float,
        recurrence: RecurrenceConfig,
        next_payload: Callable[[], str],
    ) -> None:
        period = 1.0 / max(rate_hz, 0.001)
        next_t = time.time()
        i = 0

        try:
            if recurrence.mode == "fixed":
                target = int(recurrence.count or 0)
                while i < target:
                    i += 1
                    payload = next_payload()
                    self.publish_fn(payload)
                    self._maybe_print(i, payload)
                    self._maybe_log(payload)
                    now = time.time()
                    if now < next_t:
                        time.sleep(max(0.0, next_t - now))
                    next_t = max(now, next_t) + period
            else:  # infinite
                while True:
                    i += 1
                    payload = next_payload()
                    self.publish_fn(payload)
                    self._maybe_print(i, payload)
                    self._maybe_log(payload)
                    now = time.time()
                    if now < next_t:
                        time.sleep(max(0.0, next_t - now))
                    next_t = max(now, next_t) + period
        finally:
            if self._log_handle is not None:
                self._log_handle.close()


