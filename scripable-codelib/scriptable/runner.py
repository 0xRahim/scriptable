import os
from .result import ResultCollector
from .loader import discover_builtins, discover_project

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
        print("=" * 55)

        for tmpl in builtin_templates + project_templates:
            if tmpl.name not in skip_templates:
                print(f"\n▶ Template: {tmpl.name}")
                tmpl.run(ctx, results)

        for wf in builtin_workflows + project_workflows:
            if run_workflows == "all" or wf.name in run_workflows:
                print(f"\n▶ Workflow: {wf.name}")
                wf.run(ctx, results)

        results.summary()
        results.save(output_dir=f"{project_root}/reports")