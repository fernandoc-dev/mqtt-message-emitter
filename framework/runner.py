# framework/runner.py
"""
Script Runner Module
Executes scripts in isolated environments with lifecycle management.
"""

import subprocess
import sys
import logging
import time
from typing import Optional, Dict, Any
from .environment import EnvironmentManager

logger = logging.getLogger(__name__)

class ScriptRunner:
    """
    Executes scripts in isolated environments with automatic cleanup.
    """
    
    def __init__(self, script_path: str, env_name: str = "env", requirements_file: str = "requirements.txt", app_path: str = ".", recreate_env: bool = False, cleanup_after: bool = True):
        self.script_path = script_path
        self.env_manager = EnvironmentManager(env_name, requirements_file, app_path)
        self.setup_start_time = None
        self.setup_end_time = None
        self.script_start_time = None
        self.script_end_time = None
        self.recreate_env = recreate_env
        self.cleanup_after = cleanup_after
    
    def run(self, cleanup: bool | None = None, **kwargs) -> bool:
        """
        Run the script in an isolated environment.
        
        Args:
            cleanup: Whether to destroy the environment after execution
            **kwargs: Additional arguments to pass to the script
        
        Returns:
            bool: True if execution was successful, False otherwise
        """
        logger.info(f"Starting script execution: {self.script_path}")
        
        try:
            # Setup environment
            self.setup_start_time = time.time()
            if not self.env_manager.create_environment(force_recreate=self.recreate_env):
                logger.error("Failed to create environment")
                return False
            self.setup_end_time = time.time()
            
            # Execute script
            self.script_start_time = time.time()
            success = self._execute_script(**kwargs)
            self.script_end_time = time.time()
            
            if success:
                logger.info("Script executed successfully")
            else:
                logger.error("Script execution failed")
            
            return success
            
        except KeyboardInterrupt:
            logger.info("Process interrupted by user")
            return False
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return False
        finally:
            # Cleanup
            do_cleanup = self.cleanup_after if cleanup is None else cleanup
            if do_cleanup:
                self._cleanup()
            
            # Log execution times
            self._log_execution_times()
    
    def _execute_script(self, **kwargs) -> bool:
        """
        Execute the script in the virtual environment.
        """
        try:
            # Get Python path from virtual environment
            python_path = self.env_manager.get_python_path()
            
            # Build command
            cmd = [python_path, self.script_path]
            
            # Add additional arguments
            for key, value in kwargs.items():
                cmd.extend([f"--{key}", str(value)])
            
            logger.info(f"Executing: {' '.join(cmd)}")
            
            # Execute script
            result = subprocess.run(cmd, check=True)
            return result.returncode == 0
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Error executing script: {e}")
            return False
    
    def _cleanup(self):
        """
        Clean up the virtual environment.
        """
        logger.info("Cleaning up virtual environment...")
        try:
            self.env_manager.destroy_environment()
            logger.info("Virtual environment cleanup completed")
        except Exception as e:
            logger.warning(f"Could not clean up virtual environment: {e}")
    
    def _log_execution_times(self):
        """
        Log the setup and script execution times separately.
        """
        if self.setup_start_time and self.setup_end_time:
            setup_time = self.setup_end_time - self.setup_start_time
            logger.info(f"Environment setup time: {setup_time:.2f} seconds")
        
        if self.script_start_time and self.script_end_time:
            script_time = self.script_end_time - self.script_start_time
            logger.info(f"Script execution time: {script_time:.2f} seconds")
        
        if self.setup_start_time and self.script_end_time:
            total_time = self.script_end_time - self.setup_start_time
            logger.info(f"Total time: {total_time:.2f} seconds")
    
    def get_execution_stats(self) -> Dict[str, Any]:
        """
        Get execution statistics.
        """
        stats = {
            'script_path': self.script_path,
            'setup_time': None,
            'script_time': None,
            'total_time': None,
        }
        
        if self.setup_start_time and self.setup_end_time:
            stats['setup_time'] = self.setup_end_time - self.setup_start_time
        
        if self.script_start_time and self.script_end_time:
            stats['script_time'] = self.script_end_time - self.script_start_time
        
        if self.setup_start_time and self.script_end_time:
            stats['total_time'] = self.script_end_time - self.setup_start_time
        
        return stats 