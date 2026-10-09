# Changelog — `gcp-hardening`

## [1.0.0] - 2026-10-09

- 🛡️ Initial release of `gcp-hardening` skill (`(💛)`).
- 🪣 Added **Google Cloud Storage (GCS) Hardening** section covering the `roles/storage.objectViewer` (`storage.objects.list` XML bucket listing leak) vs `roles/storage.legacyObjectReader` (`storage.objects.get` only) trap, zero-downtime remediation commands, and V4 Signed URL ("Snapchat Mode") best practices.
- 🕵️‍♂️ Added **Pre-Open-Sourcing GCP & Repository Audit** 4-surface checklist (tracked files, git history, live GCS bucket probing, and GitLab/GitHub issues/MRs).
- 🔑 Added extensible **IAM & Service Account Hardening** section.
