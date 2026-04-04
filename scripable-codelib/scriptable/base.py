from scriptable.result import Status

class BasePlugin:
    name        = "Plugin Name"
    description = "What this plugin does"

    def run(self, context, results):
        raise NotImplementedError("Templates must implement run()")

    def ok(self, results, check, detail=None, evidence=None):
        results.add(source=self.name, source_type="template",
                    check=check, status=Status.PASS, detail=detail, evidence=evidence)

    def fail(self, results, check, detail=None, evidence=None):
        results.add(source=self.name, source_type="template",
                    check=check, status=Status.FAIL, detail=detail, evidence=evidence)

    def info(self, results, check, detail=None, evidence=None):
        results.add(source=self.name, source_type="template",
                    check=check, status=Status.INFO, detail=detail, evidence=evidence)

    def skip(self, results, check, detail=None):
        results.add(source=self.name, source_type="template",
                    check=check, status=Status.SKIP, detail=detail)

    def error(self, results, check, detail=None, evidence=None):
        results.add(source=self.name, source_type="template",
                    check=check, status=Status.ERROR, detail=detail, evidence=evidence)