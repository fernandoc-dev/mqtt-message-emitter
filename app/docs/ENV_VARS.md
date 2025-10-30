## Variables de entorno

### Selección de escenario
- `SCENARIO`: nombre del escenario (p.ej. `scenario1`).

### MQTT
- `MQTT_BROKER` (default: `localhost`)
- `MQTT_PORT` (default: `1883`)
- `MQTT_TOPIC` (default: `frame_detections`)
- `MQTT_QOS` (default: `1`)

### Impresión en consola
- `PRINT_MODE`: `none` | `first` | `nth` | `all` (default: `none`)
- `PRINT_N`: entero para `nth` (default: `1`)

### Logging a archivo
- `LOG_ENABLED`: `true` | `false` (default: `false`)
- `LOG_FILE`: ruta personalizada; si se omite, se usa `app/logs/<escenario>/<timestamp>.jsonl`


