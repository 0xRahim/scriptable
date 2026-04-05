import requests
from scriptable.base import BasePlugin

class Plugin(BasePlugin):
    name        = "Example Check"
    description = ""

    def run(self, ctx, results):
        # ctx.url, ctx.headers, ctx.params, ctx.extra are available
        r = requests.get(ctx.url, headers=ctx.headers, timeout=5)

        if r.status_code == 200:
            self.ok(results, "check passed", evidence={"status": r.status_code})
        else:
            self.fail(results, "check failed", evidence={"status": r.status_code})
