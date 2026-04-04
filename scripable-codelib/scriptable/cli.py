import sys
import os
import yaml

def main():
    # Usage: scriptable run [path/to/project]
    # Defaults to current directory
    command     = sys.argv[1] if len(sys.argv) > 1 else "run"
    project_dir = sys.argv[2] if len(sys.argv) > 2 else "."

    if command != "run":
        print(f"Unknown command: {command}")
        sys.exit(1)

    config_path = os.path.join(project_dir, "config.yaml")
    if not os.path.exists(config_path):
        print(f"No config.yaml found in {project_dir}")
        sys.exit(1)

    from scriptable.runner import run_project
    with open(config_path) as f:
        config = yaml.safe_load(f)

    run_project(config, project_dir)