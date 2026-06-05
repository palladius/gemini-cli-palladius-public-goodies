# Specification: Gemini FinOps Skill

## Goal
A Gemini CLI skill to monitor and analyze GenAI expenditure on Google Cloud (Vertex AI/Gemini) and per-API key token usage.

## Requirements
- **Cost Tracking**: Monitor pay-as-you-go spend for Vertex AI and Gemini.
- **Granularity**: Track costs per project and per API key.
- **Comparison**: Compare costs between "today" and "yesterday".
- **Visualization**: Provide a simple ASCII graph of cost trends.
- **Data Export**: Support downloading/generating CSV files of the cost data.
- **Analysis**: Ability to compare different CSV exports to identify changes.
- **Implementation**: Use Python scripts for data retrieval and processing.

## Technical Details
- **APIs**: Likely requires Google Cloud Billing API, Cloud Quotas, or specific Vertex AI usage metrics.
- **Language**: Python 3.
- **Output**: Terminal-friendly (ASCII) and CSV.

## User Interface
- Commands to list costs per project/API key.
- Commands to show a graph.
- Commands to export/compare CSVs.
