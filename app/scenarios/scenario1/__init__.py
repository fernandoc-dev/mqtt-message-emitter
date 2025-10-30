#!/usr/bin/env python
import json
import random
from pathlib import Path
from typing import Dict, Any, List


ASSETS_DIR = Path(__file__).parent / "assets"


def _load_list(path: Path) -> List[Any]:
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        return data
    if isinstance(data, dict) and isinstance(data.get("list"), list):
        return data["list"]
    return []


class Scenario1:
    name = "scenario1"
    description = "Body simple para pruebas rápidas: {name,user_name,sent_messages}. name aleatorio, user_name secuencial, contador incrementa por mensaje."
    rate_hz = 10.0
    recurrence = {"mode": "fixed", "count": 20}
    assets = {
        "names": _load_list(ASSETS_DIR / "names.json"),
        "user_names": _load_list(ASSETS_DIR / "user_names.json"),
    }
    _seq_index = 0

    @staticmethod
    def base_body() -> Dict[str, Any]:
        # Body amigable y simple
        return {
            "name": "unknown",
            "user_name": "user-0",
            "sent_messages": 0
        }

    @classmethod
    def mapper(cls, msg: Dict[str, Any]) -> Dict[str, Any]:
        # name aleatorio desde assets/names.json
        if cls.assets["names"]:
            msg["name"] = random.choice(cls.assets["names"]) or "unknown"

        # user_name secuencial desde assets/user_names.json
        if cls.assets["user_names"]:
            msg["user_name"] = str(
                cls.assets["user_names"][cls._seq_index % len(cls.assets["user_names"])]
            )
        else:
            msg["user_name"] = f"user-{cls._seq_index}"

        # contador de mensajes enviados
        msg["sent_messages"] = msg.get("sent_messages", 0) + 1
        cls._seq_index += 1
        return msg


