import requests
from scriptable.base_workflow import BaseWorkflow

class Workflow(BaseWorkflow):
    name        = "CORS Bypass"
    description = "Tries known origin spoofing techniques"

    ORIGINS = [
        "https://evil.com",
        "null",
        "https://attacker.com",
    ]

    def setup(self, context):
        for origin in self.ORIGINS:
            def step(ctx, prior, results, o=origin):
                headers = {**ctx.headers, "Origin": o}
                r       = requests.get(ctx.url, headers=headers,
                                       params=ctx.params, timeout=5)
                acao = r.headers.get("Access-Control-Allow-Origin", "")
                acac = r.headers.get("Access-Control-Allow-Credentials", "")
                reflected = o in acao or acao == "*"

                evidence = {"ACAO": acao or "(none)", "ACAC": acac or "(none)",
                            "origin_sent": o}
                if reflected:
                    self.fail(results, f"origin reflected: {o}",
                              detail="Server mirrors attacker origin",
                              evidence=evidence)
                else:
                    self.ok(results, f"origin not reflected: {o}",
                            evidence=evidence)
            self.add_step(f"origin: {origin}", step)