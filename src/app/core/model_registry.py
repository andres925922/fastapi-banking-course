import importlib
import os
import pathlib

# from core.logger import get_logger
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def discover_models() -> list[str]:
    models_modules = []
    root_path = pathlib.Path(__file__).parent.parent

    for root, _, files in os.walk(root_path):
        if any(part in root for part in [
            "tests", 
            "migrations", 
            "__pycache__",
            "venv",
            ".venv",
            "env",
            "__pycache__",
        ]):
            continue

        if "models.py" in files:
            rel_path = os.path.relpath(root, root_path)
            module_path = rel_path.replace(os.path.sep, ".")

            if module_path == ".":
                full_module_path = "app.models"
            else:
                full_module_path = f"app.{module_path}.models"

            logger.debug(f"Discovered models file in: {full_module_path}")

            models_modules.append(full_module_path)
    return models_modules

def load_models() -> None:
    models_modules = discover_models()
    for module_path in models_modules:
        try:
            importlib.import_module(module_path.split("app.")[1])
            logger.info(f"Successfully imported models from: {module_path}")
        except ImportError as e:
            logger.error(f"Failed to import models from: {module_path}. Error: {e}")
        except Exception as e:
            logger.error(f"An unexpected error occurred while importing {module_path}: {e}")