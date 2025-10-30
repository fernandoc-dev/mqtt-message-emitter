#!/usr/bin/env python
import json
import random
import time
from pathlib import Path
from typing import Dict, Any, List


ASSETS_DIR = Path(__file__).parent / "assets"


def _load_json(path: Path):
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


class Scenario2:
    name = "scenario2"
    description = "Prueba real: 10× track_id=1/class=Fuego, 1× id=2/Humo, 1× id=3/Chispas; confidence y bbox aleatorios; 48 msg/s."
    # 48 mensajes por segundo
    rate_hz = 48.0
    # 10 (track_id=1) + 1 (id=2) + 1 (id=3) = 12 mensajes
    recurrence = {"mode": "fixed", "count": 12}
    detected_object = _load_json(ASSETS_DIR / "detected_object.json")  # opcional
    _seq_index = 0

    @staticmethod
    def base_body() -> Dict[str, Any]:
        # Estructura tipo FrameDetections (placeholders estáticos)
        return {
            "type": "FrameDetections",
            "properties": {
                "process_id": "process_001",
                "flight_id": "1",
                "frame_index": 0,
                "timestamp": 0,
                "category": "test"
            },
            "items": [
                {
                    "bbox": [[0, 0], [0, 0], [0, 0], [0, 0]],
                    "track_id": 0,
                    "class_name": "test_object",
                    "confidence": 0.0,
                    "camera": "opt"
                }
            ]
        }

    @classmethod
    def mapper(cls, msg: Dict[str, Any]) -> Dict[str, Any]:
        # Actualiza timestamp y frame_index
        msg["properties"]["timestamp"] = int(time.time() * 1000)
        msg["properties"]["frame_index"] = msg["properties"].get("frame_index", 0) + 1
        # Construir secuencia: 10× id=1/Fuego, 1× id=2/Humo, 1× id=3/Chispas
        idx = cls._seq_index
        if idx < 10:
            track_id = 1
            class_name = "Fuego"
        elif idx == 10:
            track_id = 2
            class_name = "Humo"
        else:
            track_id = 3
            class_name = "Chispas"

        # Random confidence 0..100 (1 decimal)
        confidence = round(random.uniform(0.0, 100.0), 1)
        # Random bbox: 4 puntos con coords 0..100
        def r():
            return random.randint(0, 100)
        bbox = [[r(), r()], [r(), r()], [r(), r()], [r(), r()]]

        item = msg["items"][0]
        item["track_id"] = track_id
        item["class_name"] = class_name
        item["confidence"] = confidence
        item["bbox"] = bbox

        cls._seq_index += 1
        return msg


