# Changelog

All notable changes to the `gemini-finops` skill will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.0.1] - 2026-05-11

### Added
- Initial release of `gemini-finops` skill.
- `list_project_costs`: List usage per API key.
- `show_cost_graph`: ASCII graph of usage.
- `export_cost_csv`: Export usage to CSV.
- `apikey_usage_by_project`: High-signal "dream" CLI with estimated costs and sparklines.
  - Defaults to aggregation by credential.
  - Added `--breakdown-by-product` flag for service-level details.
  - Added `--for-id` flag to "double-click" on a specific ID with method-level breakdown.
  - Added grouped type headers and color-coded human-readable identities.
- `compare_costs`: Compare two CSV reports.
- Python scripts for data fetching, visualization, and comparison using `uv run` for automatic dependency management.
