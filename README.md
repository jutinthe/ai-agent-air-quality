# AI Literature Agent for Air Quality and Health

An AI-powered research assistant that converts environmental health research papers into structured evidence packages.

Instead of manually reading dozens of epidemiology papers, researchers can upload a publication and automatically extract:

- Pollutants studied
- Population characteristics
- Exposure information
- Health outcomes
- Effect estimates
- Study limitations
- Structured metadata
- Knowledge graph
- Machine-readable JSON

The goal is to accelerate literature review, evidence synthesis, and downstream AI applications.

---

# Features

✅ PDF ingestion

✅ AI-powered paper understanding

✅ Structured information extraction

✅ Knowledge graph generation

✅ Evidence package generation

✅ Interactive visualization

✅ Export to JSON

✅ Export structured tables

---

# Example Output

After uploading a paper, the system extracts information such as:

| Field | Example |
|--------|---------|
| Pollutant | PM2.5 |
| Population | Older Adults |
| Exposure | Long-term annual average |
| Outcome | Cardiovascular Mortality |
| Effect Direction | Increased Risk |
| Study Design | Cohort |
| Limitations | Exposure misclassification |

The application also produces

- Knowledge Graph
- Structured JSON
- Evidence Summary
- Entity Relationships

---

# System Architecture

```
                PDF
                 │
                 ▼
        Document Parser
                 │
                 ▼
      AI Information Extraction
                 │
      ┌──────────┴──────────┐
      ▼                     ▼
 Structured JSON      Knowledge Graph
      │                     │
      └──────────┬──────────┘
                 ▼
         Interactive UI
```

---

# Technology Stack

### Backend

- Python
- FastAPI
- Pydantic
- LangGraph
- LangChain
- OpenAI API

### Frontend

- Next.js
- React
- TypeScript
- TailwindCSS
- Cytoscape.js

### AI

- GPT-5
- Structured Output Extraction
- Knowledge Graph Construction

---

# Project Structure

```
backend/
    app/
    tests/
    storage/

frontend/
    app/
    components/
    lib/
```

---

# Installation

## Clone Repository

```bash
git clone https://github.com/USERNAME/REPOSITORY.git

cd REPOSITORY
```

---

## Backend

```bash
cd backend

python -m venv .venv

source .venv/bin/activate
```

Windows

```powershell
.venv\Scripts\activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

Create

```
.env
```

Example

```env
OPENAI_API_KEY=your_api_key_here
```

Run

```bash
uvicorn app.main:app --reload
```

Backend will start on

```
http://localhost:8000
```

---

## Frontend

```bash
cd frontend

npm install

npm run dev
```

Open

```
http://localhost:3000
```

---

# Workflow

1. Upload a research paper.

2. AI extracts structured information.

3. Generate evidence package.

4. Build knowledge graph.

5. Visualize extracted entities.

6. Export JSON and structured results.

---

