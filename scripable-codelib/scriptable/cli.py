import sys
import os
import yaml
import argparse

def main():
    parser = argparse.ArgumentParser(prog="scriptable",
                                     description="API security testing framework")
    sub = parser.add_subparsers(dest="command")

    # ── scriptable new <name> ──────────────────────────────────
    new_cmd = sub.add_parser("new", help="Scaffold a new test project")
    new_cmd.add_argument("project_name", help="Name of the project folder to create")
    new_cmd.add_argument("--dir", default=".",
                         help="Parent directory (default: current dir)")

    # ── scriptable run [dir] ───────────────────────────────────
    run_cmd = sub.add_parser("run", help="Run tests against a project")
    run_cmd.add_argument("project_dir", nargs="?", default=".")
    run_cmd.add_argument("--mode", choices=["sequential", "threaded"])
    run_cmd.add_argument("--workers", type=int)
    run_cmd.add_argument("--delay",   type=float)

    # ── scriptable import openapi/caido ───────────────────────
    imp_cmd = sub.add_parser("import", help="Import API docs into project")
    imp_cmd.add_argument("source", choices=["openapi", "caido"],
                         help="Import format")
    imp_cmd.add_argument("file",   help="Path to the import file")
    imp_cmd.add_argument("--project-dir", default=".",
                         help="Target project folder (default: current dir)")
    imp_cmd.add_argument("--host",
                         help="[caido only] Filter requests by hostname")
    imp_cmd.add_argument("--out",
                         help="Output filename (default: docs/scriptable.docs.json)")

    # ── scriptable docs ───────────────────────────────────────
    docs_cmd = sub.add_parser("docs", help="View imported docs summary")
    docs_cmd.add_argument("project_dir", nargs="?", default=".")

    args = parser.parse_args()

    # ── dispatch ──────────────────────────────────────────────

    if args.command == "new":
        from scriptable.scaffold import create_project
        create_project(args.project_name, base_dir=args.dir)

    elif args.command == "run":
        _cmd_run(args)

    elif args.command == "import":
        _cmd_import(args)

    elif args.command == "docs":
        _cmd_docs(args)

    else:
        parser.print_help()


def _cmd_run(args):
    config_path = os.path.join(args.project_dir, "config.yaml")
    if not os.path.exists(config_path):
        print(f"No config.yaml in {args.project_dir}")
        sys.exit(1)
    with open(config_path) as f:
        config = yaml.safe_load(f)
    exec_cfg = config.setdefault("execution", {})
    if args.mode:    exec_cfg["mode"]        = args.mode
    if args.workers: exec_cfg["max_workers"] = args.workers
    if args.delay:   exec_cfg["delay"]       = args.delay
    from scriptable.runner import run_project
    run_project(config, args.project_dir)


def _cmd_import(args):
    project_dir = os.path.abspath(args.project_dir)
    config_path = os.path.join(project_dir, "config.yaml")

    project_name = "unknown"
    if os.path.exists(config_path):
        with open(config_path) as f:
            project_name = yaml.safe_load(f).get("project", "unknown")

    out_path = args.out or os.path.join(project_dir, "docs", "scriptable.docs.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    if args.source == "openapi":
        from scriptable.docs.openapi_importer import import_openapi
        print(f"\n📥  Importing OpenAPI spec: {args.file}")
        docs = import_openapi(args.file, project_name)

    elif args.source == "caido":
        from scriptable.docs.caido_importer import import_caido
        host = args.host
        if not host:
            host = input("  Filter by hostname (leave blank for all): ").strip() or None
        print(f"\n📥  Importing Caido export: {args.file}"
              + (f" (host: {host})" if host else ""))
        docs = import_caido(args.file, project_name, filter_host=host)
        if not docs:
            sys.exit(1)

    docs.save(out_path)
    docs.print_summary()


def _cmd_docs(args):
    project_dir = os.path.abspath(args.project_dir)
    docs_path   = os.path.join(project_dir, "docs", "scriptable.docs.json")
    if not os.path.exists(docs_path):
        print(f"  No docs found. Run: scriptable import openapi <file>")
        sys.exit(1)
    from scriptable.docs.models import ScriptableDocs
    docs = ScriptableDocs.load(docs_path)
    docs.print_summary()

    print("\n  Collections:")
    for col in docs.collections:
        print(f"    [{len(col.endpoint_ids):3} endpoints]  {col.name}")

    print("\n  Global attack ideas:")
    for idea in docs.global_attack_ideas:
        hint = f" → template:{idea.template_hint}" if idea.template_hint else ""
        hint += f" → workflow:{idea.workflow_hint}" if idea.workflow_hint else ""
        print(f"    • {idea.title}{hint}")