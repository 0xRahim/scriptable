import json
import uuid
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime

def new_id():
    return str(uuid.uuid4())[:8]

@dataclass
class AttackIdea:
    id: str = field(default_factory=new_id)
    title: str = ""
    description: str = ""
    template_hint: str = ""      # e.g. "can_non_admin_delete"
    workflow_hint: str = ""      # e.g. "member_access_revocation"

@dataclass
class Endpoint:
    id: str = field(default_factory=new_id)
    method: str = "GET"
    path: str = ""
    summary: str = ""
    description: str = ""
    headers: Dict[str, str] = field(default_factory=dict)
    query_params: Dict[str, Any] = field(default_factory=dict)
    body_schema: Optional[Dict] = None
    auth_required: bool = False
    tags: List[str] = field(default_factory=list)
    collection_id: Optional[str] = None
    attack_ideas: List[AttackIdea] = field(default_factory=list)
    notes: str = ""

@dataclass
class Collection:
    id: str = field(default_factory=new_id)
    name: str = ""
    description: str = ""
    endpoint_ids: List[str] = field(default_factory=list)

@dataclass
class ScriptableDocs:
    version: str = "1.0"
    project: str = ""
    base_url: str = ""
    imported_from: str = ""       # "openapi" | "caido" | "manual"
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    collections: List[Collection] = field(default_factory=list)
    endpoints: List[Endpoint] = field(default_factory=list)
    global_attack_ideas: List[AttackIdea] = field(default_factory=list)
    global_workflow_ideas: List[str] = field(default_factory=list)
    notes: str = ""

    # ── serialization ──────────────────────────────────────────

    def to_dict(self):
        import dataclasses
        def convert(obj):
            if dataclasses.is_dataclass(obj):
                return {k: convert(v) for k, v in dataclasses.asdict(obj).items()}
            if isinstance(obj, list):
                return [convert(i) for i in obj]
            return obj
        return convert(self)

    def save(self, path: str):
        self.updated_at = datetime.utcnow().isoformat()
        with open(path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)
        print(f"  📑 Docs saved → {path}")

    @classmethod
    def load(cls, path: str) -> "ScriptableDocs":
        with open(path) as f:
            data = json.load(f)

        docs = cls()
        docs.version     = data.get("version", "1.0")
        docs.project     = data.get("project", "")
        docs.base_url    = data.get("base_url", "")
        docs.imported_from = data.get("imported_from", "")
        docs.created_at  = data.get("created_at", "")
        docs.updated_at  = data.get("updated_at", "")
        docs.notes       = data.get("notes", "")
        docs.global_workflow_ideas = data.get("global_workflow_ideas", [])

        docs.collections = [
            Collection(**c) for c in data.get("collections", [])
        ]
        docs.endpoints = [
            Endpoint(
                **{k: v for k, v in e.items() if k != "attack_ideas"},
                attack_ideas=[AttackIdea(**a) for a in e.get("attack_ideas", [])]
            )
            for e in data.get("endpoints", [])
        ]
        docs.global_attack_ideas = [
            AttackIdea(**a) for a in data.get("global_attack_ideas", [])
        ]
        return docs

    # ── summary ────────────────────────────────────────────────

    def print_summary(self):
        bold  = "\033[1m"
        reset = "\033[0m"
        print(f"\n{bold}📑 Docs: {self.project}{reset}")
        print(f"   Base URL    : {self.base_url}")
        print(f"   Source      : {self.imported_from}")
        print(f"   Endpoints   : {len(self.endpoints)}")
        print(f"   Collections : {len(self.collections)}")
        print(f"   Attack Ideas: {len(self.global_attack_ideas)}")
        methods = {}
        for ep in self.endpoints:
            methods[ep.method] = methods.get(ep.method, 0) + 1
        for m, count in sorted(methods.items()):
            print(f"   {m:8}: {count}")