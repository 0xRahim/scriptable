import os
import yaml

TEMPLATE_CONFIG = """\
project: "{project}"

targets:
  - name: "dev"
    url: "{base_url}"
    headers:
      Authorization: "Bearer ${{TOKEN}}"
    params: {{}}
    extra:
      member_token: "${{MEMBER_TOKEN}}"
      member_id: "${{MEMBER_ID}}"

run:
  templates: all
  workflows: all

skip:
  templates: []

execution:
  mode: sequential        # or: threaded
  max_workers: 5
  delay: 0.0
"""

TEMPLATE_PLUGIN = '''\
import requests
from scriptable.base import BasePlugin

class Plugin(BasePlugin):
    name        = "{name}"
    description = ""

    def run(self, ctx, results):
        # ctx.url, ctx.headers, ctx.params, ctx.extra are available
        r = requests.get(ctx.url, headers=ctx.headers, timeout=5)

        if r.status_code == 200:
            self.ok(results, "check passed", evidence={{"status": r.status_code}})
        else:
            self.fail(results, "check failed", evidence={{"status": r.status_code}})
'''

TEMPLATE_WORKFLOW = '''\
import requests
from scriptable.base_workflow import BaseWorkflow

class Workflow(BaseWorkflow):
    name        = "{name}"
    description = ""

    def setup(self, context):
        self.add_step("Step 1", self._step_one)
        self.add_step("Step 2", self._step_two)

    def _step_one(self, ctx, prior, results):
        self.info(results, "step one", detail="Add your logic here")
        return {{"data": "from step one"}}

    def _step_two(self, ctx, prior, results):
        # prior[-1]["result"] contains step one\'s return value
        self.info(results, "step two", detail="Add your logic here")
'''


def prompt(label, default=None):
    suffix = f" [{default}]" if default else ""
    val = input(f"  {label}{suffix}: ").strip()
    return val if val else default


def create_project(project_name: str, base_dir: str = "."):
    root = os.path.join(base_dir, project_name)

    if os.path.exists(root):
        print(f"  [!] Folder already exists: {root}")
        return

    print(f"\n🛠  Creating project: {project_name}")
    print("  Answer a few questions (press Enter to use defaults)\n")

    base_url    = prompt("Target base URL", "https://api.example.com")
    description = prompt("Project description", "API security tests")

    # create folders
    for folder in ["templates", "workflows", "reports", "docs"]:
        os.makedirs(os.path.join(root, folder), exist_ok=True)

    # config.yaml
    config_content = TEMPLATE_CONFIG.format(
        project=project_name, base_url=base_url
    )
    _write(root, "config.yaml", config_content)

    # boilerplate template
    snake = project_name.lower().replace("-", "_")
    _write(root, f"templates/example_check.py",
           TEMPLATE_PLUGIN.format(name="Example Check"))

    # boilerplate workflow
    _write(root, f"workflows/example_workflow.py",
           TEMPLATE_WORKFLOW.format(name="Example Workflow"))

    # .env.example
    _write(root, ".env.example", "TOKEN=your_token_here\nMEMBER_TOKEN=\nMEMBER_ID=\n")

    # .gitignore
    _write(root, ".gitignore", "reports/\n.env\n__pycache__/\n*.pyc\n")

    # README
    _write(root, "README.md", f"# {project_name}\n\n{description}\n\n"
           "## Run\n```bash\nscriptable run .\n```\n\n"
           "## Import API docs\n```bash\n"
           "scriptable import openapi ./openapi.json\n"
           "scriptable import caido ./caido_export.json --host api.example.com\n```\n")

    print(f"\n✅  Project ready: {root}/")
    print(f"    cd {root}")
    print(f"    cp .env.example .env && vim .env")
    print(f"    scriptable run .\n")


def _write(root, rel_path, content):
    full = os.path.join(root, rel_path)
    with open(full, "w") as f:
        f.write(content)
    print(f"    created  {rel_path}")