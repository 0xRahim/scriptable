import pkgutil
import importlib
import importlib.util
import sys
from pathlib import Path

def discover_builtins(package_name, class_name):
    """Load built-in templates/workflows from the installed package."""
    import importlib
    package = importlib.import_module(package_name)
    instances = []
    for loader, module_name, _ in pkgutil.iter_modules(package.__path__):
        try:
            module = importlib.import_module(f"{package_name}.{module_name}")
            if hasattr(module, class_name):
                instances.append(getattr(module, class_name)())
        except Exception as e:
            print(f"  [!] Failed to load {package_name}.{module_name}: {e}")
    return instances

def discover_project(folder_path, class_name):
    """Load project-specific templates/workflows from an arbitrary folder."""
    instances = []
    folder = Path(folder_path)
    if not folder.exists():
        return instances

    for filepath in sorted(folder.glob("*.py")):
        if filepath.name.startswith("_"):
            continue
        module_name = f"_project_{filepath.stem}"
        spec   = importlib.util.spec_from_file_location(module_name, filepath)
        module = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(module)
            if hasattr(module, class_name):
                instances.append(getattr(module, class_name)())
        except Exception as e:
            print(f"  [!] Failed to load {filepath.name}: {e}")
    return instances