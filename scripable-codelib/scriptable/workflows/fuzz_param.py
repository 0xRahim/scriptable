import requests
from scriptable.base_workflow import BaseWorkflow

PAYLOADS = ["'", '"', "<script>alert(1)</script>", "{{7*7}}", "../etc/passwd", ";ls"]

class Workflow(BaseWorkflow):
    name        = "Parameter Fuzzer"
    description = "Injects common payloads into each query parameter"

    def setup(self, context):
        if not context.params:
            return

        for param in context.params:
            def step(ctx, prior, results, p=param):
                hits = []
                for payload in PAYLOADS:
                    fuzzed = {**ctx.params, p: payload}
                    try:
                        r = requests.get(ctx.url, params=fuzzed,
                                         headers=ctx.headers, timeout=5)
                        interesting = r.status_code >= 500 or payload in r.text
                        if interesting:
                            hits.append(payload)
                            self.fail(results, f"param '{p}' reflects payload",
                                      evidence={"payload": payload,
                                                "status":  r.status_code})
                    except Exception as e:
                        self.error(results, f"param '{p}'", detail=str(e))

                if not hits:
                    self.ok(results, f"param '{p}' no hits")
                return {"param": p, "hits": hits}

            self.add_step(f"fuzz: {param}", step)