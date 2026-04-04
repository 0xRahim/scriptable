import requests
from scriptable.base import BasePlugin

class Plugin(BasePlugin):
    name        = "API Version Exposure"
    description = "Probes common version path prefixes for accessible endpoints"

    VERSIONS = ["v1", "v2", "v3", "v4", "api/v1", "api/v2", "api"]

    def run(self, ctx, results):
        from urllib.parse import urlparse, urlunparse
        parsed = urlparse(ctx.url)
        base   = urlunparse((parsed.scheme, parsed.netloc, "", "", "", ""))

        for version in self.VERSIONS:
            url = f"{base}/{version}/"
            try:
                r = requests.get(url, headers=ctx.headers,
                                 params=ctx.params, timeout=5)
                if r.status_code < 400:
                    self.fail(results, f"{version} accessible",
                              detail=f"Endpoint responds at /{version}/",
                              evidence={"status": r.status_code, "url": url})
                else:
                    self.ok(results, f"{version} not exposed",
                            evidence={"status": r.status_code})
            except Exception as e:
                self.error(results, f"{version}", detail=str(e))