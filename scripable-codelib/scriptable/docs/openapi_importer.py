import json
from scriptable.docs.models import ScriptableDocs, Collection, Endpoint, AttackIdea

def import_openapi(file_path: str, project_name: str) -> ScriptableDocs:
    with open(file_path) as f:
        spec = json.load(f)

    docs = ScriptableDocs()
    docs.project       = project_name
    docs.imported_from = "openapi"
    docs.base_url      = spec.get("servers", [{}])[0].get("url", "")

    # resolve $ref components
    components = spec.get("components", {})

    def resolve_ref(obj):
        """Follow a single $ref in components/parameters."""
        if not isinstance(obj, dict) or "$ref" not in obj:
            return obj
        ref = obj["$ref"]            # e.g. "#/components/parameters/OrgName"
        parts = ref.lstrip("#/").split("/")
        node = spec
        for part in parts:
            node = node.get(part, {})
        return node

    # build collections from tags
    tag_map: dict[str, Collection] = {}
    for tag in spec.get("tags", []):
        name = tag.get("x-displayName") or tag.get("name", "")
        col  = Collection(name=name, description=tag.get("description", ""))
        tag_map[tag["name"]] = col
        docs.collections.append(col)

    default_col = Collection(name="Uncategorized", description="")
    has_default = False

    # walk paths
    for path, path_item in spec.get("paths", {}).items():
        # path-level params
        path_params = [resolve_ref(p) for p in path_item.get("parameters", [])]

        for method in ["get", "post", "put", "patch", "delete", "options", "head"]:
            op = path_item.get(method)
            if not op:
                continue

            # merge path + operation params
            op_params  = [resolve_ref(p) for p in op.get("parameters", [])]
            all_params = {p.get("name"): p for p in path_params + op_params
                          if p.get("name")}

            headers     = {}
            query_params = {}
            for pname, pobj in all_params.items():
                loc = pobj.get("in", "")
                if loc == "header":
                    headers[pname] = pobj.get("example", "")
                elif loc == "query":
                    query_params[pname] = pobj.get("example", "")

            # body schema
            body_schema = None
            req_body = op.get("requestBody", {})
            if req_body:
                content = req_body.get("content", {})
                for ct, ct_obj in content.items():
                    body_schema = {"content_type": ct,
                                   "schema": ct_obj.get("schema", {})}
                    break

            # auth
            auth_required = bool(op.get("security") or path_item.get("security"))

            # attack ideas seeded from operation metadata
            attack_ideas = _seed_attack_ideas(method, path, op, auth_required)

            ep = Endpoint(
                method       = method.upper(),
                path         = path,
                summary      = op.get("summary", ""),
                description  = op.get("description", ""),
                headers      = headers,
                query_params = query_params,
                body_schema  = body_schema,
                auth_required= auth_required,
                tags         = op.get("tags", []),
                attack_ideas = attack_ideas,
            )

            # assign to collection
            for tag in ep.tags:
                if tag in tag_map:
                    col = tag_map[tag]
                    ep.collection_id = col.id
                    col.endpoint_ids.append(ep.id)
                    break
            else:
                if not has_default:
                    docs.collections.append(default_col)
                    has_default = True
                ep.collection_id = default_col.id
                default_col.endpoint_ids.append(ep.id)

            docs.endpoints.append(ep)

    # global attack ideas
    docs.global_attack_ideas = _global_attack_ideas()
    docs.global_workflow_ideas = [
        "cors_bypass",
        "parameter_fuzzer",
        "auth_token_expiry",
        "privilege_escalation",
        "rate_limit_check",
    ]

    return docs


def _seed_attack_ideas(method, path, op, auth_required):
    ideas = []
    m = method.upper()

    if auth_required:
        ideas.append(AttackIdea(
            title="Auth bypass",
            description="Try accessing without Authorization header",
            template_hint="auth_check"
        ))
    if m in ("DELETE", "PUT", "PATCH"):
        ideas.append(AttackIdea(
            title="Unauthorized mutation",
            description=f"Try {m} as lower-privileged user",
            template_hint="privilege_check"
        ))
    if "{" in path:
        ideas.append(AttackIdea(
            title="IDOR",
            description="Enumerate path parameters — try other users' IDs",
            template_hint="idor_check"
        ))
    if m == "GET":
        ideas.append(AttackIdea(
            title="Parameter pollution",
            description="Duplicate query params with different values",
            workflow_hint="param_fuzzer"
        ))
    return ideas


def _global_attack_ideas():
    return [
        AttackIdea(title="CORS misconfiguration",
                   description="Test origin reflection across all endpoints",
                   workflow_hint="cors_bypass"),
        AttackIdea(title="Rate limiting absent",
                   description="Hammer sensitive endpoints — login, token creation",
                   template_hint="rate_limit_check"),
        AttackIdea(title="Mass assignment",
                   description="Send unexpected fields in POST/PUT bodies"),
        AttackIdea(title="JWT algorithm confusion",
                   description="Try alg:none or RS256→HS256 swap on JWT tokens"),
        AttackIdea(title="Stale token acceptance",
                   description="Use expired/revoked tokens — check if still accepted"),
    ]