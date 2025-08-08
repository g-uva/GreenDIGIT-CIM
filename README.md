# GreenDIGIT-CIM Project
This project implements the Common Information Model for GreenDIGIT with Unified Metric Namespace Mapping System. It enables ingestion, classification, and standard-aligned mapping of datacenter metrics from various formats and sources. The system supports metrics data from structured files (JSON, XML, CSV, YAML), unstructured text, and infrastructure's API sources.

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

## CIM Metrics Aggregation API Service

### Overview

This service provides a secure API for collecting and aggregating CIM metrics from authorised partners. Authentication is managed via a list of allowed emails and token-based access. The service is built with FastAPI and runs on a Uvicorn server, designed for easy integration and future extensibility.

### User Registration & Authentication

- **Allowed Emails:**  
  Only users whose emails are listed in `allowed_emails.txt` (managed by UvA) can access the service. This file is maintained locally on the server and can only be modified by UvA administrators.

- **First Login & Password Setup:**  
  On their first login at the `/login` endpoint, users provide their email and set a password. If the email is in `allowed_emails.txt` and not yet registered, the password is securely stored in a local SQLite database.

- **Token Retrieval:**  
  After successful login, users receive a JWT token. This token must be included as a Bearer token in the Authorisation header for all subsequent API requests.

### API Endpoints
We use [FastAPI](https://fastapi.tiangolo.com/)—a simple Python RESTful API server, that follows the OpenAPI standards. Therefore, it also serves all teh specifications as you would expect from any OpenAPI server (e.g., if you access `/docs` or `/redocs` you should see all HTTP Request methods).

- **`POST /login`**  
  Accepts email and password (form data). On first login, sets the password; on subsequent logins, authenticates the user and returns a JWT token.

- **`GET /token-ui`**  
  A simple HTML form for manual login and token retrieval.

- **`GET /submit`**  
  Accepts a JSON payload containing metrics. Requires a valid Bearer token in the Authorisation header. The submitted metrics are validated and processed.


### Data Storage

- **User Credentials:**  
  Emails and hashed passwords are stored in a local SQLite database.

- **Metrics Storage:**  
  Submitted metrics will be transformed and stored in a SQL-compatible format (PostgreSQL) and organied into appropriate namespaces for future querying and analysis.

### Deployment

- The service runs on a Uvicorn server (default port: `8080`).
- Endpoints will be reverse-proxied via Nginx in production.
- Docker support is available for easy deployment.

### Integration & Next Steps
- [ ] Step by step tutorial for: (1) run uvicorn locally, (2) running Dockerfile (server context), showing the endpoints (UI, OpenAPI, and others)
- [ ] Integrate in the server :point_right: mc-a4.lab.uvalight.net
- [ ] Integrate `POST` service for CNR database—do this programmatically.
- [ ] Deploy and connect CIM service (transformation).
- [ ] Further discussions will determine the best approach for transforming and storing metrics, as well as any additional integration requirements.

**Contact:**  
For questions or to request access, please contact the UvA CIM team:
- Adnan Tahir: a.tahir2@uva.nl.
- Gonçalo Ferreira: goncalo.ferreira@student.uva.nl.