## Plantilla de escenario

Ejemplo rápido para crear `app/scenarios/mi_escenario/__init__.py`:

```python
import json, random, time
from pathlib import Path
from typing import Any, Dict, List

ASSETS_DIR = Path(__file__).parent / "assets"

def _load_list(path: Path) -> List[Any]:
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    return data if isinstance(data, list) else data.get("list", [])

class Scenario:
    name = "mi_escenario"
    description = "Breve explicación del objetivo de la prueba (qué y por qué)."
    rate_hz = 10.0
    recurrence = {"mode": "fixed", "count": 50}  # o {"mode": "infinite"}
    assets = {
        "track_ids": _load_list(ASSETS_DIR / "track_id.json"),
        "names": _load_list(ASSETS_DIR / "names.json"),
    }
    _seq_index = 0

    @staticmethod
    def base_body() -> Dict[str, Any]:
        return {"name": "unknown", "user_name": "user-0", "sent_messages": 0}

    @classmethod
    def mapper(cls, msg: Dict[str, Any]) -> Dict[str, Any]:
        if cls.assets["names"]:
            msg["name"] = random.choice(cls.assets["names"]) or "unknown"
        if cls.assets["user_names"]:
            msg["user_name"] = str(
                cls.assets["user_names"][cls._seq_index % len(cls.assets["user_names"])]
            )
        msg["sent_messages"] = msg.get("sent_messages", 0) + 1
        cls._seq_index += 1
        return msg
```

Checklist al crear un escenario:
- [ ] Carpeta `app/scenarios/mi_escenario/` creada
- [ ] `assets/` con listas necesarias (si aplica)
- [ ] `base_body()` respeta la estructura esperada
- [ ] `mapper()` implementa la lógica (secuencial/aleatorio) y actualiza campos variables
- [ ] Registrar `mi_escenario` en `select_scenario()` de `app/main.py`
- [ ] Probar: `SCENARIO=mi_escenario PRINT_MODE=first LOG_ENABLED=true py run.py`


