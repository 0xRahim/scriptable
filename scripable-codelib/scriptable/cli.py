import sys
import os
import yaml

def main():
    import argparse
    parser = argparse.ArgumentParser(prog="scriptable")
    sub    = parser.add_subparsers(dest="command")

    run_cmd = sub.add_parser("run", help="Run tests against a project")
    run_cmd.add_argument("project_dir", nargs="?", default=".",
                         help="Path to project folder (default: current dir)")
    run_cmd.add_argument("--mode", choices=["sequential", "threaded"],
                         help="Override execution mode from config")
    run_cmd.add_argument("--workers", type=int,
                         help="Override max_workers from config")
    run_cmd.add_argument("--delay", type=float,
                         help="Override delay (seconds) between requests")

    args = parser.parse_args()

    if args.command != "run":
        parser.print_help()
        sys.exit(1)

    config_path = os.path.join(args.project_dir, "config.yaml")
    if not os.path.exists(config_path):
        print(f"No config.yaml found in {args.project_dir}")
        sys.exit(1)

    with open(config_path) as f:
        config = yaml.safe_load(f)

    # CLI flags override config.yaml
    exec_cfg = config.setdefault("execution", {})
    if args.mode:    exec_cfg["mode"]        = args.mode
    if args.workers: exec_cfg["max_workers"] = args.workers
    if args.delay:   exec_cfg["delay"]       = args.delay

    from scriptable.runner import run_project
    run_project(config, args.project_dir)