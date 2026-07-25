# IntelGraph

IntelGraph is a semantic search engine designed for cybersecurity intelligence. Powered by **Actian VectorAI Database** and **FastAPI**, it allows analysts to search the MITRE ATT&CK knowledge base using natural language rather than relying on exact keyword matches or technique IDs.

For example, a query for *"browser credential theft"* semantically matches techniques like *"Credentials from Web Browsers"* and *"OS Credential Dumping"*.

## Features
- **Semantic Search**: Powered by Actian VectorAI and the `all-MiniLM-L6-v2` embedding model.
- **MITRE ATT&CK Ingestion**: Automated pipeline to download, parse, and embed the Enterprise ATT&CK STIX dataset.
- **Metadata Filtering**: Dynamically filter techniques by **Platform** (e.g., Windows, Linux, macOS) or **Tactic** (e.g., Credential Access, Defense Evasion).
- **Related Techniques**: Instantly discover structurally and semantically related techniques for any given threat.
- **Modern UI**: Clean, responsive, glassmorphic UI built with Vanilla JavaScript, HTML, and CSS. No bloated frontend frameworks.

## Architecture

```mermaid
graph TD;
    Client[Web Browser] -->|HTTP POST /api/search| API[FastAPI Backend];
    API -->|Generate Embeddings| Model[SentenceTransformer];
    Model --> API;
    API -->|Semantic Search| VectorDB[(Actian VectorAI)];
    VectorDB --> API;
    API --> Client;
```

## Tech Stack
- **Backend**: Python 3.11, FastAPI, Uvicorn, Pydantic
- **Vector Database**: Actian VectorAI Client
- **Embeddings**: SentenceTransformers (`all-MiniLM-L6-v2`)
- **Frontend**: HTML5, CSS3, Vanilla JavaScript

## Project Structure

```text
IntelGraph/
├── backend/
│   ├── api.py                  # FastAPI application and routing
│   ├── constants.py            # Global configuration
│   ├── create_collection.py    # Admin utility to init VectorAI collection
│   ├── embed.py                # Singleton for embedding generation
│   ├── ingest/                 # MITRE ATT&CK dataset ingestion pipeline
│   ├── models/                 # Pydantic schemas (Request/Response)
│   ├── routes/                 # API endpoint definitions
│   └── services/               # Core business logic and VectorAI queries
├── frontend/                   # Static assets (HTML, CSS, JS)
├── data/                       # Cached metadata and downloaded STIX files
├── .env.example
├── requirements.txt
└── docker-compose.yml          # Actian VectorAI database configuration
```

## Installation & Setup

### 1. Requirements
- Docker & Docker Compose (for the VectorAI Database)
- Python 3.10+

### 2. Start Actian VectorAI
IntelGraph requires a running instance of Actian VectorAI.
```bash
docker-compose up -d
```

### 3. Run the Application

Docker Compose starts both VectorAI and the Uvicorn API. The first startup creates the collection and ingests MITRE ATT&CK; later starts reuse persistent named volumes and skip ingestion.
```bash
docker compose up --build -d
```

Open `http://localhost:8000`. Follow initial ingestion with `docker compose logs -f api`.

The VectorAI database, Hugging Face model cache, and downloaded MITRE dataset each use one persistent Docker volume, so containers do not re-download or duplicate them on every start.
The application and frontend UI will now be available at `http://localhost:8000/`.

## Screenshots
*(Insert Screenshots Here)*

## Future Roadmap
- Ingest Sigma Rules, CVEs, and CAPEC.
- Add advanced conversational / RAG capabilities on top of search results.
- Implement user authentication and custom watchlist features.

## Acknowledgements
Built for the Actian VectorAI Track. 

## License
MIT License
