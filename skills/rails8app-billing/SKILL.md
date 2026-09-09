---
name: rails8app-billing
description: (💛) Real-time GCP cost and resource usage estimator for attendees of the Rails 8 on GCP workshop with $5 GDP promotional credits.
---

# 💸 rails8app-billing

Calculates real-time incurred costs on Google Cloud Platform for the Rails 8 on GCP workshop.

Because standard Cloud Billing export reports have a 6–24 hour latency, this skill inspects active project resources (Cloud SQL, Cloud Run, GCS, Cloud Build) and queries Cloud Monitoring telemetry to compute live costs against the attendee's $5.00 GDP promotional credit budget.

## Usage

Run the Ruby cost estimator script:

```bash
ruby $SKILL_DIR/scripts/rails8app_billing.rb --project <PROJECT_ID> --hours 6
```

Or from within the `rails8-app-on-gcp` repository:

```bash
bin/rails8app-billing --hours 6
```

Or via justfile:

```bash
just billing
```
