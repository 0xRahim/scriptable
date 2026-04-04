import os
from scriptable.result import ResultCollector
from scriptable.loader import discover_builtins, discover_project
from scriptable.executor import run_sequential, run_threaded

class GenericRequest:
    def __init__(self, url, headers=None, params=None, extra=None,
                 data=None, json_data=None):
        self.url       = url
        self.headers   = headers or {}
        self.params    = params
        self.extra     = extra or {}
        self.data      = data
        self.json_data = json_data

def _resolve_env(headers):
    return {k: os.path.expandvars(v) for k, v in (headers or {}).items()}

def run_project(config: dict, project_root: str):
    project_root = os.path.abspath(project_root)

    builtin_templates = discover_builtins("scriptable.templates", "Plugin")
    builtin_workflows = discover_builtins("scriptable.workflows", "Workflow")
    project_templates = discover_project(f"{project_root}/templates", "Plugin")
    project_workflows = discover_project(f"{project_root}/workflows", "Workflow")

    skip_templates = set(config.get("skip", {}).get("templates", []))
    run_workflows  = config.get("run", {}).get("workflows", "all")

    # execution config
    exec_cfg    = config.get("execution", {})
    mode        = exec_cfg.get("mode", "sequential")
    max_workers = exec_cfg.get("max_workers", 5)
    delay       = exec_cfg.get("delay", 0.0)

    for target in config["targets"]:
        ctx = GenericRequest(
            url     = target["url"],
            headers = _resolve_env(target.get("headers", {})),
            params  = target.get("params"),
            extra   = target.get("extra", {}),
        )

        results = ResultCollector(
            project_name = config["project"],
            target_name  = target["name"],
            target_url   = target["url"],
        )

        print(f"\n🚀  {target['name']} — {target['url']}")
        print(f"    mode: {mode}" + (f" · workers: {max_workers} · delay: {delay}s"
              if mode == "threaded" else ""))
        print("=" * 55)

        # --- templates ---
        active_templates = [
            t for t in builtin_templates + project_templates
            if t.name not in skip_templates
        ]

        def make_template_task(tmpl):
            def task():
                print(f"\n▶ Template: {tmpl.name}")
                tmpl.run(ctx, results)
            return task

        template_tasks = [make_template_task(t) for t in active_templates]

        if mode == "threaded":
            run_threaded(template_tasks, max_workers=max_workers, delay=delay)
        else:
            run_sequential(template_tasks)

        # --- workflows always run sequentially (steps depend on prior results) ---
        active_workflows = [
            w for w in builtin_workflows + project_workflows
            if run_workflows == "all" or w.name in run_workflows
        ]

        for wf in active_workflows:
            print(f"\n▶ Workflow: {wf.name}")
            wf.run(ctx, results)

        results.summary()
        results.save(output_dir=f"{project_root}/reports")