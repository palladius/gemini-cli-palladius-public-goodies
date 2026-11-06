#!/usr/bin/env python3
"""
Gemini Notebook API v1 CLI (notebook.googleapis.com/v1)
Public parameterized edition — reads configuration from .env / environment.
Supports: config, auth, list, create, get, sources, add-url, add-md, add-pdf, ask
"""

import argparse
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

API_BASE = "https://notebook.googleapis.com/v1"
SKILL_DIR = Path(__file__).resolve().parent.parent
CACHE_DIR = Path.home() / ".cache" / "gemini-notebook-api"


def load_dotenv_files() -> dict[str, str]:
    """Load key=value pairs from .env files without overwriting process env."""
    loaded: dict[str, str] = {}
    candidates = [
        Path.home() / "git" / "gic" / ".env.gprism",
        Path.cwd() / ".env",
        SKILL_DIR / ".env",
    ]
    for env_path in candidates:
        if env_path.is_file():
            try:
                for raw_line in env_path.read_text(encoding="utf-8").splitlines():
                    line = raw_line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    if line.startswith("export "):
                        line = line[len("export ") :].strip()
                    k, v = line.split("=", 1)
                    k = k.strip()
                    v = v.strip().strip('"').strip("'")
                    loaded[k] = v
            except Exception:
                pass
    return loaded


DOTENV = load_dotenv_files()


def get_cfg(key: str, default: str = "") -> str:
    val = os.environ.get(key) or DOTENV.get(key) or default
    if val.startswith("~"):
        val = os.path.expanduser(val)
    return val


DEFAULT_GMAIL_ACCOUNT = get_cfg("GMAIL_ACCOUNT", "")
DEFAULT_QUOTA_PROJECT = get_cfg(
    "QUOTA_PROJECT_ID",
    get_cfg("NOTEBOOK_QUOTA_PROJECT", ""),
)
DEFAULT_CLIENT_ID_FILE = get_cfg(
    "NOTEBOOK_CLIENT_ID_FILE",
    os.path.expanduser("~/.config/notebook-api/client_secret.json"),
)
DEFAULT_CLOUDSDK_CONFIG = get_cfg(
    "NOTEBOOK_CLOUDSDK_CONFIG",
    os.path.expanduser("~/.config/gcloud-notebook"),
)


def normalize_notebook_id(notebook_id: str) -> str:
    """Return bare UUID from 'notebooks/<uuid>' or full URL."""
    s = notebook_id.strip().rstrip("/")
    if "/" in s:
        s = s.split("/")[-1]
    return s


def require_quota_project(quota_project: str) -> str:
    if not quota_project or quota_project == "your-personal-gcp-project-id":
        print(
            "❌ QUOTA_PROJECT_ID is not configured!\n"
            f"   Copy {SKILL_DIR / '.env.dist'} to {SKILL_DIR / '.env'} and set QUOTA_PROJECT_ID and GMAIL_ACCOUNT.",
            file=sys.stderr,
        )
        sys.exit(1)
    return quota_project


def get_access_token(cloudsdk_config: str) -> str:
    """Mint a fresh OAuth2 access token from the isolated ADC refresh token."""
    adc_path = Path(cloudsdk_config) / "application_default_credentials.json"
    if adc_path.exists():
        data = json.loads(adc_path.read_text(encoding="utf-8"))
        if all(k in data for k in ("client_id", "client_secret", "refresh_token")):
            payload = urllib.parse.urlencode(
                {
                    "client_id": data["client_id"],
                    "client_secret": data["client_secret"],
                    "refresh_token": data["refresh_token"],
                    "grant_type": "refresh_token",
                }
            ).encode("utf-8")
            req = urllib.request.Request(
                "https://oauth2.googleapis.com/token",
                data=payload,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                token_data = json.loads(resp.read().decode("utf-8"))
                return token_data["access_token"]

    # Fallback to gcloud CLI if direct refresh fails
    env = os.environ.copy()
    env["CLOUDSDK_CONFIG"] = cloudsdk_config
    out = subprocess.check_output(
        ["gcloud", "auth", "application-default", "print-access-token"],
        env=env,
        text=True,
    ).strip()
    return out


def api_request(
    method: str,
    path: str,
    token: str,
    quota_project: str,
    body: dict | None = None,
) -> dict:
    quota_project = require_quota_project(quota_project)
    url = f"{API_BASE}/{path.lstrip('/')}"
    headers = {
        "Authorization": f"Bearer {token}",
        "x-goog-user-project": quota_project,
    }
    data = None
    if body is not None:
        headers["Content-Type"] = "application/json; charset=utf-8"
        data = json.dumps(body, ensure_ascii=False).encode("utf-8")

    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            raw = resp.read().decode("utf-8")
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8", errors="replace")
        print(f"❌ HTTP {e.code} on {method} {url}:\n{err_body}", file=sys.stderr)
        if "WORKSPACE_ACCOUNT_NOT_SUPPORTED" in err_body:
            print(
                "💡 Hint: You authenticated with a Google Workspace account. Re-run `auth` using a personal @gmail.com account (GMAIL_ACCOUNT).",
                file=sys.stderr,
            )
        elif "SERVICE_DISABLED" in err_body:
            print(
                f"💡 Hint: Enable the API on your quota project:\n   gcloud services enable notebook.googleapis.com --project={quota_project}",
                file=sys.stderr,
            )
        sys.exit(1)


def cache_source_text(notebook_id: str, title: str, content: str) -> None:
    nb_id = normalize_notebook_id(notebook_id)
    nb_cache = CACHE_DIR / nb_id
    nb_cache.mkdir(parents=True, exist_ok=True)
    safe_name = "".join(c if c.isalnum() or c in "._- " else "_" for c in title).strip()
    (nb_cache / f"{safe_name}.md").write_text(content, encoding="utf-8")


def extract_pdf_to_markdown(pdf_path: Path) -> str:
    """Convert a PDF file to structured Markdown using pdftotext."""
    try:
        out = subprocess.check_output(
            ["pdftotext", str(pdf_path), "-"], text=True, stderr=subprocess.DEVNULL
        )
    except FileNotFoundError:
        print("❌ 'pdftotext' not found. Install poppler-utils (apt/brew).", file=sys.stderr)
        sys.exit(1)

    pages = out.split("\x0c")
    md_lines = [
        f"# PDF Source: {pdf_path.name}",
        f"- **Local Path**: `{pdf_path.resolve()}`",
        "",
    ]
    for idx, page in enumerate(pages, start=1):
        cleaned = page.strip()
        if cleaned:
            md_lines.append(f"## Page {idx}")
            md_lines.append(cleaned)
            md_lines.append("")
    return "\n".join(md_lines)


def wait_for_sources_active(
    notebook_id: str, source_names: list[str], token: str, quota_project: str
) -> None:
    pending = set(source_names)
    for _ in range(30):
        if not pending:
            break
        time.sleep(2)
        for sname in list(pending):
            res = api_request("GET", sname, token, quota_project)
            state = res.get("state", "UNKNOWN")
            if state == "ACTIVE":
                pending.remove(sname)
            elif state == "FAILED":
                pending.remove(sname)
                print(f"⚠️ Source failed: {res}", file=sys.stderr)


def cmd_config(args: argparse.Namespace) -> None:
    adc_path = Path(args.cloudsdk_config) / "application_default_credentials.json"
    print("🔧 Gemini Notebook API Configuration:")
    print(f"  • Skill .env file          : {SKILL_DIR / '.env'} (exists: {(SKILL_DIR / '.env').exists()})")
    print(f"  • GMAIL_ACCOUNT            : {DEFAULT_GMAIL_ACCOUNT or '(not set)'}")
    print(f"  • QUOTA_PROJECT_ID         : {args.quota_project or '(not set)'}")
    print(f"  • NOTEBOOK_CLIENT_ID_FILE  : {args.client_id_file} (exists: {Path(args.client_id_file).exists()})")
    print(f"  • NOTEBOOK_CLOUDSDK_CONFIG : {args.cloudsdk_config} (ADC exists: {adc_path.exists()})")


def cmd_auth(args: argparse.Namespace) -> None:
    if not Path(args.client_id_file).exists():
        print(
            f"❌ OAuth Client ID file not found at: {args.client_id_file}\n"
            "   Why: gcloud's default client ID is blocked ('This app is blocked') for the notebook scope.\n"
            "   Fix: Create a Desktop App OAuth Client ID in your QUOTA_PROJECT_ID and set NOTEBOOK_CLIENT_ID_FILE in .env.",
            file=sys.stderr,
        )
        sys.exit(1)
    os.makedirs(args.cloudsdk_config, exist_ok=True)
    cmd = [
        "gcloud",
        "auth",
        "application-default",
        "login",
        f"--client-id-file={args.client_id_file}",
        "--scopes=https://www.googleapis.com/auth/cloud-platform,https://www.googleapis.com/auth/notebook",
    ]
    if DEFAULT_GMAIL_ACCOUNT:
        print(f"👤 Please sign in with consumer account: {DEFAULT_GMAIL_ACCOUNT}")
    print(f"🔐 Running ADC login in CLOUDSDK_CONFIG={args.cloudsdk_config} ...")
    env = os.environ.copy()
    env["CLOUDSDK_CONFIG"] = args.cloudsdk_config
    subprocess.run(cmd, env=env, check=True)


def cmd_list(args: argparse.Namespace) -> None:
    token = get_access_token(args.cloudsdk_config)
    res = api_request("GET", f"notebooks?pageSize={args.page_size}", token, args.quota_project)
    notebooks = res.get("notebooks", [])
    if args.json:
        print(json.dumps(res, indent=2, ensure_ascii=False))
        return
    print(f"📓 Found {len(notebooks)} Gemini Notebook(s):")
    for nb in notebooks:
        nb_id = normalize_notebook_id(nb["name"])
        title = nb.get("displayName", "(Untitled)")
        updated = nb.get("updateTime", "")
        print(f"  • {title}")
        print(f"    ID : {nb_id}")
        print(f"    URL: https://notebooklm.google.com/notebook/{nb_id} (updated: {updated})")


def cmd_create(args: argparse.Namespace) -> None:
    token = get_access_token(args.cloudsdk_config)
    res = api_request("POST", "notebooks", token, args.quota_project, {"display_name": args.title})
    nb_id = normalize_notebook_id(res["name"])
    print(f"✅ Created Notebook: {res.get('displayName')}")
    print(f"   Name: {res['name']}")
    print(f"   URL : https://notebooklm.google.com/notebook/{nb_id}")


def cmd_get(args: argparse.Namespace) -> None:
    token = get_access_token(args.cloudsdk_config)
    nb_id = normalize_notebook_id(args.notebook_id)
    res = api_request("GET", f"notebooks/{nb_id}", token, args.quota_project)
    print(json.dumps(res, indent=2, ensure_ascii=False))


def cmd_sources(args: argparse.Namespace) -> None:
    token = get_access_token(args.cloudsdk_config)
    nb_id = normalize_notebook_id(args.notebook_id)
    res = api_request("GET", f"notebooks/{nb_id}/sources?pageSize=100", token, args.quota_project)
    sources = res.get("sources", [])
    if args.json:
        print(json.dumps(res, indent=2, ensure_ascii=False))
        return
    print(f"📚 {len(sources)} source(s) in notebooks/{nb_id}:")
    for idx, src in enumerate(sources, start=1):
        print(
            f"  {idx:2d}. [{src.get('state', '?')}] {src.get('displayName', '(Untitled)')} ({src['name']})"
        )


def cmd_add_url(args: argparse.Namespace) -> None:
    token = get_access_token(args.cloudsdk_config)
    nb_id = normalize_notebook_id(args.notebook_id)
    title = args.title or args.url
    body = {"display_name": title, "web_content": {"url": args.url}}
    res = api_request("POST", f"notebooks/{nb_id}/sources", token, args.quota_project, body)
    print(f"⏳ Created URL source: {res['name']} (waiting for ACTIVE...)")
    wait_for_sources_active(nb_id, [res["name"]], token, args.quota_project)
    print(f"✅ Source ACTIVE: {title}")


def cmd_add_md(args: argparse.Namespace) -> None:
    token = get_access_token(args.cloudsdk_config)
    nb_id = normalize_notebook_id(args.notebook_id)
    md_path = Path(args.file)
    content = md_path.read_text(encoding="utf-8")
    title = args.title or md_path.name
    body = {
        "display_name": title,
        "text_content": {"content": content, "mime_type": "text/markdown"},
    }
    res = api_request("POST", f"notebooks/{nb_id}/sources", token, args.quota_project, body)
    cache_source_text(nb_id, title, content)
    print(f"⏳ Created Markdown source: {res['name']} (waiting for ACTIVE...)")
    wait_for_sources_active(nb_id, [res["name"]], token, args.quota_project)
    print(f"✅ Source ACTIVE: {title}")


def cmd_add_pdf(args: argparse.Namespace) -> None:
    token = get_access_token(args.cloudsdk_config)
    nb_id = normalize_notebook_id(args.notebook_id)
    created_names = []
    for idx, pdf_str in enumerate(args.files):
        if idx > 0:
            time.sleep(3.1)  # Respect 20 RPM CreateSource quota
        pdf_path = Path(pdf_str)
        content = extract_pdf_to_markdown(pdf_path)
        title = f"PDF: {pdf_path.name}"
        body = {
            "display_name": title,
            "text_content": {"content": content, "mime_type": "text/markdown"},
        }
        res = api_request("POST", f"notebooks/{nb_id}/sources", token, args.quota_project, body)
        cache_source_text(nb_id, title, content)
        created_names.append(res["name"])
        print(f"📤 Uploaded ({idx + 1}/{len(args.files)}): {title} -> {res['name']}")

    print("⏳ Polling sources until ACTIVE...")
    wait_for_sources_active(nb_id, created_names, token, args.quota_project)
    print(
        f"✅ All {len(created_names)} PDF source(s) are ACTIVE in https://notebooklm.google.com/notebook/{nb_id}"
    )


def resolve_gemini_api_key() -> str:
    for var in ("GEMINI_API_KEY", "GOOGLE_API_KEY"):
        val = get_cfg(var, "")
        if val:
            return val
    print(
        "❌ GEMINI_API_KEY not found in environment or .env files.",
        file=sys.stderr,
    )
    sys.exit(1)


def cmd_ask(args: argparse.Namespace) -> None:
    token = get_access_token(args.cloudsdk_config)
    nb_id = normalize_notebook_id(args.notebook_id)
    nb = api_request("GET", f"notebooks/{nb_id}", token, args.quota_project)
    srcs = api_request(
        "GET", f"notebooks/{nb_id}/sources?pageSize=100", token, args.quota_project
    ).get("sources", [])

    context_blocks = [
        f"# Notebook: {nb.get('displayName')} (notebooks/{nb_id})",
        f"Web URL: https://notebooklm.google.com/notebook/{nb_id}",
        "## Live Sources Inventory from API:",
    ]
    for s in srcs:
        context_blocks.append(f"- {s.get('displayName')} (`{s['name']}`, state={s.get('state')})")

    nb_cache = CACHE_DIR / nb_id
    if nb_cache.exists():
        for md_file in sorted(nb_cache.glob("*.md")):
            context_blocks.append(
                f"\n---\n## Cached Content: {md_file.name}\n" + md_file.read_text(encoding="utf-8")
            )

    api_key = resolve_gemini_api_key()
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{args.model}:generateContent?key={api_key}"
    prompt = "\n".join(context_blocks) + f"\n\n---\nUSER QUESTION:\n{args.question}"
    payload = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.2},
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        text = data["candidates"][0]["content"]["parts"][0]["text"]
        print(text)


def main() -> None:
    parser = argparse.ArgumentParser(description="Gemini Notebook API v1 CLI")
    parser.add_argument("--cloudsdk-config", default=DEFAULT_CLOUDSDK_CONFIG)
    parser.add_argument("--quota-project", default=DEFAULT_QUOTA_PROJECT)
    parser.add_argument("--client-id-file", default=DEFAULT_CLIENT_ID_FILE)
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_cfg = sub.add_parser("config", help="Show resolved configuration from .env / environment")
    p_cfg.set_defaults(func=cmd_config)

    p_auth = sub.add_parser("auth", help="Authenticate GMAIL_ACCOUNT with notebook scope")
    p_auth.set_defaults(func=cmd_auth)

    p_list = sub.add_parser("list", help="List Gemini Notebooks")
    p_list.add_argument("--page-size", type=int, default=50)
    p_list.add_argument("--json", action="store_true")
    p_list.set_defaults(func=cmd_list)

    p_create = sub.add_parser("create", help="Create a new Gemini Notebook")
    p_create.add_argument("title")
    p_create.set_defaults(func=cmd_create)

    p_get = sub.add_parser("get", help="Get Notebook metadata")
    p_get.add_argument("notebook_id")
    p_get.set_defaults(func=cmd_get)

    p_sources = sub.add_parser("sources", help="List sources in a Notebook")
    p_sources.add_argument("notebook_id")
    p_sources.add_argument("--json", action="store_true")
    p_sources.set_defaults(func=cmd_sources)

    p_url = sub.add_parser("add-url", help="Add a Web or YouTube URL source")
    p_url.add_argument("notebook_id")
    p_url.add_argument("url")
    p_url.add_argument("--title")
    p_url.set_defaults(func=cmd_add_url)

    p_md = sub.add_parser("add-md", help="Add a Markdown/text file source")
    p_md.add_argument("notebook_id")
    p_md.add_argument("file")
    p_md.add_argument("--title")
    p_md.set_defaults(func=cmd_add_md)

    p_pdf = sub.add_parser("add-pdf", help="Add one or more PDF files (converted via pdftotext)")
    p_pdf.add_argument("notebook_id")
    p_pdf.add_argument("files", nargs="+")
    p_pdf.set_defaults(func=cmd_add_pdf)

    p_ask = sub.add_parser("ask", help="Ask a question grounded on the notebook sources")
    p_ask.add_argument("notebook_id")
    p_ask.add_argument("question")
    p_ask.add_argument("--model", default="gemini-3-flash-preview")
    p_ask.set_defaults(func=cmd_ask)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
