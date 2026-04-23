# GreenDIGIT-CIM Project
This project implements the Common Information Model for GreenDIGIT with Unified Metric Namespace Mapping System. It enables ingestion, classification, and standard-aligned mapping of datacenter metrics from various formats and sources. The system supports metrics data from structured files (JSON, XML, CSV, YAML), unstructured text, and infrastructure's API sources.

Related repositories:
- [GreenDIGIT-project](https://github.com/GreenDIGIT-project)
- [GreenDIGIT-AuthServer](https://github.com/g-uva/GreenDIGIT-AuthServer)
- [GreenDIGIT-SQLAdapter](https://github.com/g-uva/GreenDIGIT-SQLAdapter)
- [GreenDIGIT-KPIService](https://github.com/g-uva/GreenDIGIT-WP6-KPI-Service)

*This work is funded from the European Union’s Horizon Europe research and innovation programme through the [GreenDIGIT project](https://greendigit-project.eu/), under the grant agreement No. [101131207](https://cordis.europa.eu/project/id/101131207)*.

<!-- ![GreenDIGIT Logo](auth_metrics_server/static/cropped-GD_logo.png)
![EU Logo](auth_metrics_server/static/EN-Funded-by-the-EU-POS-2.png) -->

<div style="display:flex;align-items:center;width:100%;">
  <img src="static/EN-Funded-by-the-EU-POS-2.png" alt="EU Logo" width="250px">
  <img src="static/cropped-GD_logo.png" alt="GreenDIGIT Logo" width="110px" style="margin-right:100px">
</div>

# Project Structure
cloud_metrics_api/ –> _Main application logic including ingestion, parsing, mapping, and API interface._

cloud_metrics_api/ingestion_controller/ –> _Orchestrates ingestion from files or real-time sources and manages classification and mapping._

cloud_metrics_api/parsers/ –> _Parsers for structured (JSON, XML, YAML, CSV) and unstructured (text) files._

cloud_metrics_api/project_models/ –> _SQLAlchemy ORM models for namespace elements and learned metric keywords._

cloud_metrics_api/sql_models/ –> _ORM models for metric definitions, upload logs, and datacenters._

cloud_metrics_api/sql_services/ –> _DB insert and mapping services for PostgreSQL._

cloud_metrics_api/project_config/ –> _Configuration for PostgreSQL and InfluxDB connectivity._

cloud_metrics_api/utils/ –> _Helper functions for syncing mapping with metric_mapping.json._

cloud_metrics_api/streamlit_uploader.py –> _Streamlit-based UI to upload files and visualize ingestion flow._

cloud_metrics_api/unified_ingestion.py –> _Command-line tool to ingest and process metrics from uploaded files._

cloud_metrics_api/namespace_mapper_core.py –> _The core router module that bridges parsing, classification, and storage services._

# Execution Flow
1. Input: A metric file (JSON, XML, etc.) is uploaded via Streamlit or CLI.
2. Parsing: The format is detected, and routed to the appropriate parser.
3. Extraction: Raw metrics are extracted into key-value pairs.
4. Classification: Each key is classified by the semantic classifier or fallback logic.
5. Namespace Generation: Unified key is generated using the ISO/JRC-compliant format.
6. Storage: Metadata is saved to PostgreSQL; values go to InfluxDB.
7. Mapping: All raw-unified mappings are synced in metric_mapping.json.
8. Access: Metrics are queryable via InfluxDB or APIs; ready for dashboards.

# How to Run
To run via Streamlit UI:
_streamlit run cloud_metrics_api/streamlit_uploader.py_

To run manually via CLI:
_python cloud_metrics_api/unified_ingestion.py --file path/to/file.json --datacenter SampleDC_

# Setup Instructions
- Install dependencies: `pip install -r requirements.txt`.
- Ensure PostgreSQL and InfluxDB are running.
- Configure `project_config/postgres_config.py` and `influx_service.py` with appropriate credentials.
- Run `create_schema.py` to initialize the database tables.

# Note
- Namespace generation auto-creates new standards, categories, and subcategories.
- New metric keys are logged in the `metric_keywords` table if not previously mapped.

---

# Note
- Namespace generation auto-creates new standards, categories, and subcategories.
- New metric keys are logged in the `metric_keywords` table if not previously mapped.

---

## Contact & Questions
**Contact:**  
For questions or to request access, please contact the GreenDIGIT UvA CIM team:
- Adnan Tahir: a.tahir2@uva.nl.
- Gonçalo Ferreira: goncalo.ferreira@student.uva.nl.
