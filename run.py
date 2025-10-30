#!/usr/bin/env python3
"""
Simple Runner Script
Executes the application using the framework.
"""

import sys
import os
from pathlib import Path

# Add framework to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'framework'))

from framework import ScriptRunner
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def load_env_file(path: Path) -> None:
    try:
        for line in path.read_text(encoding='utf-8').splitlines():
            line=line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' in line:
                k,v = line.split('=',1)
                k=k.strip(); v=v.strip()
                if k and (k not in os.environ):
                    os.environ[k]=v
    except Exception:
        pass


def str2bool(val: str) -> bool:
    return str(val).lower() in ("1", "true", "yes", "y", "on")


def main():
    # Cargar .env para parámetros de ejecución del runner
    env_framework = Path(__file__).resolve().parent / ".env.framework"
    if env_framework.exists():
        load_env_file(env_framework)
    """
    Execute the app/script using the framework.
    It requires:
        - The start point of the app to be in app/main.py
        - The virtual environment to be in env/
        - The requirements.txt to be in app/requirements.txt
    """
    try:
        # Create script runner
        # Lectura estricta de flags de ejecución desde entorno
        try:
            recreate_env = str2bool(os.environ["RUN_RECREATE"])  # true|false
            cleanup_after = str2bool(os.environ["RUN_CLEANUP"])  # true|false
        except KeyError as e:
            logger.error(f"Missing required environment variable: {e}")
            sys.exit(1)

        runner = ScriptRunner(
            script_path="app/main.py",
            env_name="env",
            requirements_file="requirements.txt",
            app_path="app",
            recreate_env=recreate_env,
            cleanup_after=cleanup_after
        )
        
        # Run the script
        # If RUN_CLEANUP is provided, ScriptRunner will honor it by default
        success = runner.run()
        
        # Log statistics
        stats = runner.get_execution_stats()
        logger.info(f"Execution completed. Stats: {stats}")
        
        # Exit with appropriate code
        sys.exit(0 if success else 1)
        
    except Exception as e:
        logger.error(f"Runner failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 