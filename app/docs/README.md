## Cola MQTT - Guía rápida para escenarios

Esta guía explica cómo crear y ejecutar escenarios de publicación de mensajes MQTT con el motor central.

### Estructura del proyecto (app/)
- `core/engine.py`: motor central (frecuencia, recurrencia, impresión, logging)
- `core/mqtt_client.py`: wrapper simple de publicación MQTT
- `scenarios/<nombre>/`: cada escenario vive en su carpeta
  - `__init__.py`: define `base_body()`, `mapper(msg)`, `rate_hz`, `recurrence`, y carga de assets
  - `assets/`: datos locales (listas/valores) del escenario
- `main.py`: punto de entrada. Selecciona escenario por variable de entorno
- `logs/<escenario>/YYYYMMDD_HHMMSS.jsonl`: salida de logs por escenario/ejecución

### Conceptos clave
- **Body del mensaje**: estructura base definida por el escenario. En ejemplos simples: `{ "name", "user_name", "sent_messages" }`.
- **description**: texto breve que documenta el propósito del escenario/prueba (memoria histórica).
- **Assets**: archivos JSON locales para alimentar valores (p.ej. `track_id.json`, `names.json`).
- **Mapper del escenario**: función personalizada por escenario que transforma el body con reglas (secuencial/aleatorio, etc.).
- **Frecuencia**: `rate_hz` en el escenario (mensajes por segundo).
- **Recurrencia**: `fixed` con `count=N` o `infinite`.

### Crear un nuevo escenario
1) Crear carpeta: `app/scenarios/mi_escenario/`
2) Opcional: `assets/` con JSONs (listas u objetos con clave `list`)
3) Implementar `__init__.py` siguiendo el ejemplo (body simple):

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
    description = "Explica en pocas líneas qué valida este escenario."
    rate_hz = 20.0
    recurrence = {"mode": "fixed", "count": 100}
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
        # Ejemplos:
        # name aleatorio desde assets
        if cls.assets["names"]:
            msg["name"] = random.choice(cls.assets["names"]) or "unknown"
        # user_name secuencial desde assets
        if cls.assets["user_names"]:
            msg["user_name"] = str(
                cls.assets["user_names"][cls._seq_index % len(cls.assets["user_names"])]
            )
        # contador de mensajes
        msg["sent_messages"] = msg.get("sent_messages", 0) + 1
        cls._seq_index += 1
        return msg
```

4) Registrar el escenario en `app/main.py` (función `select_scenario`).

### Ejecutar
Comando base:
```bash
py run.py
```

Variables de entorno útiles:
- Selección de escenario: `SCENARIO=scenario1`
- Impresión: `PRINT_MODE=none|first|nth|all`, `PRINT_N=5`
- Logging: `LOG_ENABLED=true`, `LOG_FILE=app/logs/custom.jsonl` (opcional; si no se define, se usa `app/logs/<escenario>/<timestamp>.jsonl`)
- MQTT: `MQTT_BROKER=localhost`, `MQTT_PORT=1883`, `MQTT_TOPIC=frame_detections`, `MQTT_QOS=1`

Ejemplos:
```bash
# Imprimir todos y log por escenario/fecha
PRINT_MODE=all LOG_ENABLED=true SCENARIO=scenario1 py run.py

# Solo imprimir el primer mensaje, sin log
PRINT_MODE=nth PRINT_N=1 LOG_ENABLED=false SCENARIO=scenario1 py run.py
```

### Buenas prácticas
- Mantén `base_body()` mínimo y compatible con el consumidor.
- Encapsula toda la lógica de variación de datos en `mapper()`.
- Coloca datos dependientes del escenario bajo `assets/` para portabilidad.
- Usa `recurrence` con `fixed` durante pruebas y `infinite` para estrés.

### Solución de problemas
- Sin conexión MQTT: verifica broker/puerto/topic y firewall.
- Sin logs: confirma `LOG_ENABLED=true` o la ruta por defecto creada bajo `logs/<escenario>/`.
- Rendimiento/frecuencia: baja `rate_hz` o reduce trabajo en `mapper()`.


