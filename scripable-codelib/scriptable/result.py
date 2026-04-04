import json
import os
from datetime import datetime
from enum import Enum

class Status(str, Enum):
    PASS  = "PASS"
    FAIL  = "FAIL"
    INFO  = "INFO"
    ERROR = "ERROR"
    SKIP  = "SKIP"

COLORS = {
    Status.PASS:  "\033[92m",
    Status.FAIL:  "\033[91m",
    Status.INFO:  "\033[94m",
    Status.ERROR: "\033[93m",
    Status.SKIP:  "\033[90m",
    "RESET":      "\033[0m",
    "BOLD":       "\033[1m",
}

class ResultCollector:
    def __init__(self, project_name, target_name, target_url):
        self.project_name = project_name
        self.target_name  = target_name
        self.target_url   = target_url
        self.started_at   = datetime.utcnow().isoformat()
        self.entries      = []

    def add(self, *, source, source_type, check, status: Status,
            detail=None, evidence=None):
        entry = {
            "timestamp":   datetime.utcnow().isoformat(),
            "source_type": source_type,
            "source":      source,
            "check":       check,
            "status":      status,
            "detail":      detail,
            "evidence":    evidence or {},
        }
        self.entries.append(entry)
        self._print(entry)
        return entry

    def _print(self, entry):
        color = COLORS.get(entry["status"], "")
        reset = COLORS["RESET"]
        bold  = COLORS["BOLD"]
        tag    = f"{color}[{entry['status']:5}]{reset}"
        detail = f" — {entry['detail']}" if entry["detail"] else ""
        print(f"    {tag} {bold}{entry['source']}{reset} › {entry['check']}{detail}")
        if entry["evidence"]:
            for k, v in entry["evidence"].items():
                print(f"           {k}: {v}")

    def summary(self):
        counts = {s: 0 for s in Status}
        for e in self.entries:
            counts[Status(e["status"])] += 1
        bold  = COLORS["BOLD"]
        reset = COLORS["RESET"]
        print(f"\n{bold}{'─'*55}")
        print(f"  Summary · {self.project_name} → {self.target_name}")
        print(f"{'─'*55}{reset}")
        for status, count in counts.items():
            if count:
                print(f"  {COLORS[status]}{status.value:6}{reset}  {count}")
        print(f"{bold}{'─'*55}{reset}")

    def save(self, output_dir="reports"):
        os.makedirs(output_dir, exist_ok=True)
        ts       = datetime.now().strftime("%Y-%m-%d_%H-%M")
        filename = f"{output_dir}/{ts}_{self.target_name}.json"
        report   = {
            "project":    self.project_name,
            "target":     self.target_name,
            "url":        self.target_url,
            "started_at": self.started_at,
            "ended_at":   datetime.utcnow().isoformat(),
            "summary":    {s.value: sum(1 for e in self.entries
                           if e["status"] == s) for s in Status},
            "results":    self.entries,
        }
        with open(filename, "w") as f:
            json.dump(report, f, indent=2, default=str)
        print(f"\n  📄 Report → {filename}\n")
        return filename