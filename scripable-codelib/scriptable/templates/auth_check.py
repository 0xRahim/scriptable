# my-api-project/templates/auth_check.py
from scriptable.base import BasePlugin
import requests

class Plugin(BasePlugin):
    name = "Auth Header Required"

    def run(self, ctx, results):
        r = requests.get(ctx.url, timeout=5)   # no auth headers
        if r.status_code in (401, 403):
            self.ok(results, "unauthenticated request blocked",
                    evidence={"status": r.status_code})
        else:
            self.fail(results, "endpoint accessible without auth",
                      evidence={"status": r.status_code})