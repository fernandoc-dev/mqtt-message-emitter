# framework/__init__.py
"""
Simple Framework for Script Execution in Clean Environments
Provides isolated execution environments for Python scripts.
"""

from .runner import ScriptRunner
from .environment import EnvironmentManager

__version__ = "1.0.0"
__all__ = ['ScriptRunner', 'EnvironmentManager'] 