#!/usr/bin/env python
import json
import os
import time
from typing import Callable
from pathlib import Path
from dotenv import load_dotenv

from core.engine import CentralEngine, RecurrenceConfig
from core.mqtt_client import MqttPublisher
from scenarios.scenario1 import Scenario1
from scenarios.scenario2 import Scenario2


def select_scenario(name: str):
    # Por ahora solo escenario1 básico
    if name == "scenario1":
        return Scenario1
    if name == "scenario2":
        return Scenario2
    raise ValueError(f"Escenario desconocido: {name}")


def main():
    # Cargar .env desde la raíz del proyecto si existe
    project_root_env_app = Path(__file__).resolve().parents[1] / ".env.app"
    if project_root_env_app.exists():
        load_dotenv(project_root_env_app)

    # Lectura estricta de .env (sin valores por defecto)
    try:
        scenario_name = os.environ["SCENARIO"]
        broker = os.environ["MQTT_BROKER"]
        port = int(os.environ["MQTT_PORT"])
        topic = os.environ["MQTT_TOPIC"]
        qos = int(os.environ["MQTT_QOS"])

        print_mode = os.environ["PRINT_MODE"]  # none|first|nth|all
        print_n = int(os.environ["PRINT_N"])
        log_enabled = os.environ["LOG_ENABLED"].lower() == "true"
        log_file = os.environ["LOG_FILE"]
    except KeyError as e:
        missing = str(e).strip("'")
        raise RuntimeError(f"Missing required environment variable: {missing}")

    # Validación básica
    if print_mode not in ("none", "first", "nth", "all"):
        raise RuntimeError("PRINT_MODE must be one of: none|first|nth|all")

    scenario = select_scenario(scenario_name)

    publisher = MqttPublisher(broker=broker, port=port, topic=topic, qos=qos)

    def publish_fn(payload: str) -> None:
        publisher.publish(payload)

    engine = CentralEngine(
        publish_fn=publish_fn,
        print_mode=print_mode,
        print_n=print_n,
        log_enabled=log_enabled,
        log_file=log_file,
    )

    # construir función next_payload a partir del body + mapper del escenario
    def next_payload() -> str:
        body = scenario.base_body()
        mapped = scenario.mapper(body)
        return json.dumps([mapped], ensure_ascii=False)

    rec = scenario.recurrence
    engine.run(
        rate_hz=float(scenario.rate_hz),
        recurrence=RecurrenceConfig(mode=rec["mode"], count=rec.get("count")),
        next_payload=next_payload,
    )

    publisher.close()


if __name__ == "__main__":
    main()


