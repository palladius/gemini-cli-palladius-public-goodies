---
name: gcp-hardening
description: "(💛) Use when configuring, auditing, hardening, or open-sourcing projects that use Google Cloud Platform (GCP) resources — especially Google Cloud Storage (GCS) buckets, IAM roles, V4 Signed URLs, or pre-release repository security checks."
compatibility: gemini-cli
metadata:
  version: "1.0.0"
  author: "Riccardo Carlesso"
  tags: "gcp, security, hardening, gcs, iam, oss-hygiene"
---

# 🛡️ GCP Hardening & Pre-Release Security Guide (`gcp-hardening`)

## Overview

Actionable security hardening rules and audit workflows for Google Cloud Platform (GCP) resources and open-source repositories that interact with GCP. Designed to be modular and extensible by GCP product area (starting with **Google Cloud Storage (GCS)** and **Pre-Open-Source GCP Leak Audits**).

---

## 1. 🪣 Google Cloud Storage (GCS) Hardening

### 1.1 The `objectViewer` vs `legacyObjectReader` Trap (Bucket Listing Exfiltration)

When hosting static reports, media galleries, or capability-URL pages (e.g., `storagify` with `--salt`, or unguessable folder prefixes) on a GCS bucket where direct browser links must work without login:

> [!CAUTION]
> **NEVER grant `roles/storage.objectViewer` (or `roles/storage.legacyBucketReader`) to `allUsers` or `allAuthenticatedUsers`!**

| IAM Role on `allUsers` | Permissions Granted | Direct Object GET (`/.../file.html`) | Root Bucket XML Listing (`https://storage.googleapis.com/<BUCKET>/`) | Security Posture |
| :--- | :--- | :--- | :--- | :--- |
| `roles/storage.objectViewer` | `storage.objects.get`<br>**`storage.objects.list`** | `200 OK` | **`200 OK` (`<ListBucketResult>`)** 🚨 | **INSECURE**: Leaks every object key, manifest, and salted filename in the bucket! |
| `roles/storage.legacyObjectReader` | `storage.objects.get` **ONLY** | `200 OK` | **`403 Forbidden`** ✅ | **SECURE**: Direct links work; directory enumeration is blocked. |

#### Why this matters
If a bucket name is ever mentioned in a public repository, issue tracker, or shared URL, and `allUsers` has `roles/storage.objectViewer`, anyone can run:
```bash
curl -s "https://storage.googleapis.com/<BUCKET>/"
```
and receive a full XML `<ListBucketResult>` dump of every object in the bucket — completely bypassing 16-character URL salts (`[salt]-index.html`), hidden metadata directories (`.storagify/entries/*.json`), and unlisted subfolders.

#### Mandatory GCS Remediation & Verification
Always apply `legacyObjectReader` **before** removing `objectViewer` to ensure zero downtime for existing shared links:

```bash
# 1. Grant direct object read access ONLY (no directory listing)
gcloud storage buckets add-iam-policy-binding gs://<BUCKET> \
  --member=allUsers \
  --role=roles/storage.legacyObjectReader \
  --project=<PROJECT_ID> --quiet

# 2. Remove objectViewer (blocks public XML bucket listing)
gcloud storage buckets remove-iam-policy-binding gs://<BUCKET> \
  --member=allUsers \
  --role=roles/storage.objectViewer \
  --project=<PROJECT_ID> --quiet

# 3. Verify: Root listing MUST return 403, direct object MUST return 200
curl -s -o /dev/null -w "Root Listing HTTP (expect 403): %{http_code}\n" "https://storage.googleapis.com/<BUCKET>/"
curl -s -o /dev/null -w "Direct Object HTTP (expect 200): %{http_code}\n" "https://storage.googleapis.com/<BUCKET>/<KNOWN_OBJECT_PATH>"
```

### 1.2 Private Buckets & Ephemeral V4 Signed URLs ("Snapchat Mode")

When data is sensitive and should expire automatically rather than relying on public object reads:
1. **Enforce Public Access Prevention**:
   ```bash
   gcloud storage buckets update gs://<BUCKET> --public-access-prevention --project=<PROJECT_ID> --quiet
   ```
2. **Use GCS V4 Signed URLs (`version="v4"`)**:
   - Maximum TTL is **7 days** (`604800` seconds).
   - **Self-Contained HTML**: When serving HTML via V4 Signed URLs on a private bucket, inline local CSS/JS (`<style>`, `<script>`) and pre-sign all embedded relative subresources (`<img src>`, `<video src>`, links) with the same expiration timestamp; otherwise the browser will get `403 AccessDenied` on subresources.
   - **User ADC + IAM `signBlob` Pitfall**: Credentials from `gcloud auth application-default login` do not contain a local private key. When calling `blob.generate_signed_url(version="v4", ...)` in Python with user ADC, you must refresh the credentials and pass both `service_account_email` and `access_token=creds.token` (requiring `roles/iam.serviceAccountTokenCreator`), or use a Service Account key.

---

## 2. 🕵️‍♂️ Pre-Open-Sourcing GCP & Repository Audit

Before flipping a private GitHub or GitLab repository to **Public**, always audit **4 surfaces** (not just `.env`!):

1. **Tracked Files (`git ls-files`)**:
   - Scan code, tests, docstrings, `.agents/`, and `docs/` for real `gs://` bucket names, real GCP Project IDs, corporate FQDNs (`*.corp.google.com`), internal home paths (`/usr/local/google/...`), internal shortlinks (`go/...`), Buganizer IDs (`b/...`), and corporate emails.
   - Replace all real bucket and project names in tests/docs with generic placeholders (`my-bucket`, `test-bucket`, `my-gcp-project`).
2. **Full Git Commit History (`git log --all -p`)**:
   - Verify `.env`, service account JSON keys (`PRIVATE KEY`), OAuth tokens (`ya29.`), and API keys (`AIza...`) were never committed and later deleted in an earlier commit.
3. **Live Cloud Resource Probing**:
   - For every `gs://<BUCKET>` or `https://storage.googleapis.com/<BUCKET>` ever mentioned in git history or `.env`, test anonymous access (`curl -s https://storage.googleapis.com/<BUCKET>/`) to confirm it does not return `200 OK` `<ListBucketResult>`.
4. **Issue Tracker & Merge/Pull Requests (`glab issue list --all` / `gh issue list --state all`)**:
   - Issue descriptions and MR comments frequently contain copy-pasted terminal stack traces, real bucket URLs, secondary email identities, and internal ticket numbers. Sanitize open and closed issues via CLI/API before making the project public.

---

## 3. 🔑 IAM & Service Account Hardening (Extensible)

- **Principle of Least Privilege**: Never grant primitive roles (`roles/owner`, `roles/editor`) or overly broad predefined roles (`roles/storage.admin`) to workload service accounts.
- **No Exported JSON Keys When Avoidable**: Prefer Workload Identity Federation, Cloud Run / GKE attached service accounts, or Service Account impersonation (`--impersonate-service-account`) over downloading long-lived `.json` private keys.
- **Quota Project Hygiene**: When using user ADC (`google.auth.default()`), bind `creds.with_quota_project(project_id)` explicitly to avoid quota/billing leaks across projects.
