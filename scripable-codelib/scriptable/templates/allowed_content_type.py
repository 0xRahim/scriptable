import requests
from scriptable.base import BasePlugin

class Plugin(BasePlugin):
    name        = "Allowed Content-Type"
    description = "Tests which Content-Type headers the endpoint accepts"

    CONTENT_TYPES = [
        "application/json",
        "application/x-www-form-urlencoded",
        "text/plain",
        "text/html",
        "application/xml",
        "multipart/form-data",
    ]

    def run(self, ctx, results):
        for ct in self.CONTENT_TYPES:
            headers = {**ctx.headers, "Content-Type": ct}
            try:
                r = requests.post(ctx.url, data=ctx.data, headers=headers,
                                  params=ctx.params, timeout=5)
                if 200 <= r.status_code < 300:
                    self.ok(results, f"accepts {ct}",
                            evidence={"status": r.status_code})
                elif r.status_code == 415:
                    self.info(results, f"rejects {ct}",
                              detail="415 Unsupported Media Type",
                              evidence={"status": r.status_code})
                else:
                    self.info(results, f"{ct}",
                              evidence={"status": r.status_code})
            except Exception as e:
                self.error(results, f"{ct}", detail=str(e))