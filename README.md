# MQTT Message Emitter

Scenario-driven MQTT publisher with precise rate control, strict env-only configuration, and a reusable execution framework.

## Highlights
- Scenario-based message generation (per-scenario description, assets, and custom mapper)
- Precise rate control (Hz) and recurrence (fixed or infinite)
- Per-scenario structured logging with timestamped files
- Strict configuration only via environment files (no implicit defaults)
- Clean split between reusable framework and pluggable app (separate requirements)

## Repository Layout
```
.
├─ framework/                  # Reusable runner/venv management
│  ├─ environment.py           # venv lifecycle (create/install/destroy)
│  ├─ runner.py                # script runner + timings
│  └─ requirements.txt         # framework-only deps (empty for now)
├─ app/                        # Current MQTT emitting app
│  ├─ core/
│  │  ├─ engine.py             # central engine (rate, recurrence, print/log)
│  │  └─ mqtt_client.py        # thin wrapper over paho-mqtt
│  ├─ scenarios/
│  │  ├─ scenario1/            # simple body
│  │  └─ scenario2/            # FrameDetections-like body
│  ├─ docs/                    # app docs (how to write scenarios)
│  ├─ main.py                  # app entrypoint (strict .env.app)
│  └─ requirements.txt         # app-only deps (paho-mqtt, python-dotenv)
├─ .env.framework              # runner-only env (RUN_RECREATE, RUN_CLEANUP)
├─ .env.app                    # app-only env (SCENARIO, MQTT_*, PRINT_*, LOG_*)
└─ run.py                      # repository entrypoint using the framework
```

## Configuration (strict env-only)
This project intentionally rejects implicit defaults. All required values must live in env files.

- Framework runner: `.env.framework`
```
RUN_RECREATE=false   # recreate venv on each run
RUN_CLEANUP=false    # delete venv after run
```

- App runtime: `.env.app`
```
# Scenario selection
SCENARIO=scenario2

# MQTT
MQTT_BROKER=localhost
MQTT_PORT=1883
MQTT_TOPIC=frame_detections
MQTT_QOS=1

# Printing (console)
PRINT_MODE=none      # none | first | nth | all
PRINT_N=1            # used when PRINT_MODE=nth

# Logging (files)
LOG_ENABLED=true
LOG_FILE=app/logs/scenario2/auto.jsonl
```

If a required variable is missing, the run will fail early with a clear error.

## How it works
- `run.py` loads `.env.framework`, configures and invokes the framework `ScriptRunner`.
- The framework creates/reuses/destroys the venv (per flags) and executes `app/main.py`.
- `app/main.py` loads `.env.app`, resolves the selected scenario, and builds a `CentralEngine`:
  - Fixed-rate schedule (Hz), recurrence (fixed N or infinite)
  - Printing mode (none/first/nth/all)
  - Logging (JSON Lines) per scenario with timestamped filenames if you wish
- The scenario provides:
  - `name` and `description`
  - `base_body()` with a stable shape
  - `mapper(msg)` applying dynamic fields (e.g., timestamps, counters, random payload parts)

## Scenarios
Each scenario lives in `app/scenarios/<scenario_name>/` and may include `assets/` with lists or JSON sources.

- `scenario1` (simple testing)
  - description: simple body `{name, user_name, sent_messages}`
  - mapper: random `name`, sequential `user_name`, increment `sent_messages`
  - rate: 10 Hz, recurrence: 20 messages

- `scenario2` (FrameDetections-like)
  - description: 10× id=1/Fuego, 1× id=2/Humo, 1× id=3/Chispas; random confidence/bbox; 48 msg/s
  - mapper: enforces the sequence and randomizes confidence/bbox

See detailed authoring docs in `app/docs/` (README, ENV_VARS, SCENARIO_TEMPLATE).

## Run
1) Ensure env files exist and are complete:
   - `.env.framework`
   - `.env.app`
2) From repo root:
```
py run.py
```
The first run will create the venv if needed. Subsequent runs can reuse it or recreate it depending on `.env.framework`.

## Logging and Printing
- Console printing is controlled via `PRINT_MODE` and `PRINT_N`.
- File logging is controlled via `LOG_ENABLED` and `LOG_FILE`.
- A common practice during development: `PRINT_MODE=first`, `LOG_ENABLED=true`.

## Rate and Recurrence
- Rate is enforced at the engine with per-interval scheduling.
- Recurrence can be a fixed count (for deterministic tests) or infinite (for soak/load).

## Extending / Reusing
- The `framework/` folder is reusable for any Python app requiring an isolated venv lifecycle with timings and cleanup.
- To plug a different app later, keep `run.py` and `framework/`, and point `ScriptRunner(script_path=...)` to your new app entrypoint.

## Requirements
- `framework/requirements.txt`: framework-specific (empty by default)
- `app/requirements.txt`: app-specific (currently `paho-mqtt`, `python-dotenv`)
