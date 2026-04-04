from scriptable.result import Status

class BaseWorkflow:
    name        = "Workflow Name"
    description = "What this workflow does"

    def __init__(self):
        self.steps   = []
        self.results = []

    def add_step(self, label, fn):
        self.steps.append((label, fn))

    def setup(self, context):
        """Override to register steps. Called automatically before run()."""
        raise NotImplementedError("Workflows must implement setup()")

    def run(self, context, results):
        self.setup(context)
        for label, fn in self.steps:
            print(f"  [STEP] {label}")
            try:
                result = fn(context, self.results, results)
                self.results.append({"step": label, "result": result, "error": None})
            except Exception as e:
                self.results.append({"step": label, "result": None, "error": str(e)})
                results.add(source=self.name, source_type="workflow",
                            check=label, status=Status.ERROR, detail=str(e))

    # convenience helpers (mirror BasePlugin)
    def ok(self, results, check, detail=None, evidence=None):
        results.add(source=self.name, source_type="workflow",
                    check=check, status=Status.PASS, detail=detail, evidence=evidence)

    def fail(self, results, check, detail=None, evidence=None):
        results.add(source=self.name, source_type="workflow",
                    check=check, status=Status.FAIL, detail=detail, evidence=evidence)

    def info(self, results, check, detail=None, evidence=None):
        results.add(source=self.name, source_type="workflow",
                    check=check, status=Status.INFO, detail=detail, evidence=evidence)