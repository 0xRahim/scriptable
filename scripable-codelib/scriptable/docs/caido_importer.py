import json
import base64
from scriptable.docs.models import ScriptableDocs, Collection, Endpoint

def import_caido(file_path: str, project_name: str, filter_host: str = None) -> ScriptableDocs:
    with open(file_path) as f:
        raw = json.load(f)

    # caido export can be a list of requests or {"items": [...]}
    items = raw if isinstance(raw, list) else raw.get("items", [])

    # filter by host if provided
    if filter_host:
        items = [i for i in items if filter_host in i.get("host", "")]

    if not items:
        print(f"  [!] No requests found for host: {filter_host}")
        return None

    docs = ScriptableDocs()
    docs.project       = project_name
    docs.imported_from = "caido"

    # infer base_url from first item
    first = items[0]
    scheme = "https" if first.get("is_tls") else "http"
    docs.base_url = f"{scheme}://{first.get('host', '')}"

    # one collection per host
    host_cols: dict[str, Collection] = {}

    seen_paths: set = set()     # deduplicate method+path combos

    for item in items:
        host   = item.get("host", "unknown")
        method = item.get("method", "GET").upper()
        path   = item.get("path", "/") or "/"
        key    = f"{method} {path}"

        if key in seen_paths:
            continue
        seen_paths.add(key)

        # decode raw request to extract headers
        headers = _decode_headers(item.get("raw", ""))

        # collection per host
        if host not in host_cols:
            col = Collection(name=host, description=f"Requests to {host}")
            host_cols[host] = col
            docs.collections.append(col)

        col = host_cols[host]

        # response info
        resp        = item.get("response") or {}
        status_code = resp.get("status_code")

        ep = Endpoint(
            method      = method,
            path        = path,
            summary     = f"{method} {path}",
            description = f"Imported from Caido. Response: {status_code}",
            headers     = headers,
            query_params= _parse_query(item.get("query", "")),
            auth_required = "Authorization" in headers or "Cookie" in headers,
            tags        = [host],
            notes       = f"Original status: {status_code} | Source: {item.get('source','')}"
        )
        ep.collection_id = col.id
        col.endpoint_ids.append(ep.id)
        docs.endpoints.append(ep)

    return docs


def _decode_headers(raw_b64: str) -> dict:
    """Decode base64 raw HTTP request, extract headers."""
    if not raw_b64:
        return {}
    try:
        raw = base64.b64decode(raw_b64).decode("utf-8", errors="ignore")
        lines = raw.split("\r\n")
        headers = {}
        for line in lines[1:]:    # skip request line
            if not line or ":" not in line:
                break
            k, _, v = line.partition(":")
            headers[k.strip()] = v.strip()
        return headers
    except Exception:
        return {}

def _parse_query(query_str: str) -> dict:
    if not query_str:
        return {}
    from urllib.parse import parse_qs
    return {k: v[0] for k, v in parse_qs(query_str.lstrip("?")).items()}