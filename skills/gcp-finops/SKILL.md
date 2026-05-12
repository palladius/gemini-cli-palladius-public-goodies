---
name: gemini-finops
description: Monitor and analyze GenAI expenditure on Google Cloud (Vertex AI/Gemini).
compatibility: gemini-cli
metadata:
  version: 0.0.1
---

# Gemini FinOps Skill

Monitor and analyze GenAI expenditure on Google Cloud (Vertex AI/Gemini).

## Tools

### `list_project_costs`
Lists GenAI costs per project and per API key for "today" and "yesterday".
**Arguments:**
- `project_id` (string): The GCP project ID.
- `days` (integer, optional): Number of days to look back (default: 2).

### `show_cost_graph`
Displays an ASCII graph of GenAI costs from a CSV file.
**Arguments:**
- `csv_file` (string): Path to the CSV file containing cost data.

### `export_cost_csv`
Downloads/exports the cost data to a CSV file.
**Arguments:**
- `project_id` (string): The GCP project ID.
- `output_file` (string): Path to the output CSV file.
- `days` (integer, optional): Number of days to look back (default: 7).

### `apikey_usage_by_project`
Provides a high-signal summary of GenAI usage per API key, including estimated costs and visual sparklines.
**Arguments:**
- `project_id` (string): The GCP project ID.
- `breakdown_by_product` (boolean, optional): If true, breaks down usage by specific GCP service (default: false).
- `credential_types` (string, optional): Comma-separated list of types to include: `apikey`, `serviceaccount`, `oauth2`, `unknown`, or `all` (default: `apikey`).

### `compare_costs`
Compares two CSV cost reports and highlights differences.
**Arguments:**
- `file1` (string): Path to the first CSV file.
- `file2` (string): Path to the second CSV file.
