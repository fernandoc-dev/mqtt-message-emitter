# framework/environment.py
"""
Environment Management Module
Handles virtual environment creation, dependency installation, and cleanup.
"""

import subprocess
import sys
import os
import logging
from typing import List, Optional

logger = logging.getLogger(__name__)

class EnvironmentManager:
    """
    Manages virtual environment lifecycle for script execution.
    """
    
    def __init__(self, env_name: str = "env", requirements_file: str = "requirements.txt", app_path: str = "."):
        self.env_name = env_name
        self.requirements_file = requirements_file
        self.external_requirements_file = "external_requirements.txt"
        self.app_path = app_path
    
    def create_environment(self, force_recreate: bool = False) -> bool:
        """
        Create virtual environment and install dependencies.
        """
        try:
            logger.info(f"Setting up virtual environment '{self.env_name}'...")
            
            # Check if virtual environment already exists
            if os.path.exists(self.env_name):
                if force_recreate:
                    logger.info(f"Virtual environment '{self.env_name}' exists → recreating (force_recreate=True)")
                    self.destroy_environment()
                else:
                    logger.info(f"Virtual environment '{self.env_name}' already exists (reuse)")
                    return True
                
            # Create virtual environment
            subprocess.run([sys.executable, '-m', 'venv', self.env_name], check=True)
            logger.info("Virtual environment created successfully")
            
            # Install requirements
            self._install_dependencies()
            logger.info("Dependencies installed successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Error setting up environment: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return False
    
    def _install_dependencies(self):
        """
        Install Python dependencies.
        """
        # Get pip path
        if os.name == 'nt':  # Windows
            pip_path = os.path.join(self.env_name, 'Scripts', 'pip')
        else:  # Unix/Linux
            pip_path = os.path.join(self.env_name, 'bin', 'pip')
        
        # Install requirements.txt
        requirements_path = os.path.join(self.app_path, self.requirements_file)
        if os.path.exists(requirements_path):
            subprocess.run([pip_path, 'install', '-r', requirements_path], check=True)
        
        # Install external packages
        self._install_external_packages(pip_path)
    
    def _install_external_packages(self, pip_path: str):
        """
        Install external packages from external_requirements.txt.
        """
        external_requirements_path = os.path.join(self.app_path, self.external_requirements_file)
        if os.path.exists(external_requirements_path):
            with open(external_requirements_path, 'r') as f:
                external_packages = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            
            for package in external_packages:
                package_path = os.path.join(self.app_path, package)
                if os.path.exists(package_path):
                    subprocess.run([pip_path, 'install', package_path], check=True)
                    logger.info(f"External package {package} installed successfully")
                else:
                    logger.warning(f"External package {package} not found in {self.app_path}")
    
    def destroy_environment(self) -> bool:
        """
        Destroy virtual environment.
        """
        try:
            logger.info(f"Destroying virtual environment '{self.env_name}'...")
            
            if os.name == 'nt':  # Windows
                try:
                    subprocess.run(['rmdir', '/s', '/q', self.env_name], shell=True, check=True)
                except subprocess.CalledProcessError:
                    # Fallback: use PowerShell
                    subprocess.run(['powershell', '-Command', f'Remove-Item -Recurse -Force {self.env_name}'], check=True)
            else:  # Unix/Linux
                subprocess.run(['rm', '-rf', self.env_name], check=True)
                
            logger.info("Virtual environment destroyed successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Error destroying environment: {e}")
            logger.warning(f"You may need to manually delete the '{self.env_name}' folder")
            return False
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            logger.warning(f"You may need to manually delete the '{self.env_name}' folder")
            return False
    
    def get_python_path(self) -> str:
        """
        Get the Python executable path in the virtual environment.
        """
        if os.name == 'nt':  # Windows
            return os.path.join(self.env_name, 'Scripts', 'python')
        else:  # Unix/Linux
            return os.path.join(self.env_name, 'bin', 'python') 