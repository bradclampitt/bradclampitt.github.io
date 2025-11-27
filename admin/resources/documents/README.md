# Documents System

A custom document/knowledge-base system for GitHub Pages using SQLite, AlpineJS, and sql.js.

## Overview

This system provides:
- **Frontend**: Static HTML pages (`documents.html`, `document.html`) that read from SQLite via sql.js
- **Backend**: Local FastAPI admin CMS for managing documents
- **Database**: Single SQLite file (`documents/documents.sqlite`) committed to the repo

## Setup

### Prerequisites

- Python 3.8+
- pip

### Installation

1. Create a virtual environment (required):

```bash
cd documents
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

**Note**: If you get an "externally-managed-environment" error, you must use a virtual environment. The virtual environment creates an isolated Python environment for this project.

### Running the Admin

Start the FastAPI admin server:

```bash
cd documents
source venv/bin/activate  # Activate virtual environment if not already active
uvicorn admin.app:app --reload --port 8001 --host 127.0.0.1
```

**Note**: 
- Make sure to activate the virtual environment before running uvicorn. You'll know it's activated when you see `(venv)` in your terminal prompt.
- Port 8001 is used to avoid conflicts with other admin servers (e.g., portfolios admin on port 8000). If 8001 is also in use, change it to another port like 8002.

Visit `http://localhost:8001/admin` to access the admin dashboard.

### First Run

On first startup, the admin will automatically:
- Create `documents/documents.sqlite` if it doesn't exist
- Initialize the database schema from `schema.sql`

## Admin Features

- **Dashboard**: Overview of documents, categories, and types
- **Categories**: Manage document categories (e.g., "resume", "guide", "kb")
- **Document Types**: Manage document types (e.g., "technical", "process", "policy")
- **Documents**: Create and edit documents with:
  - Basic info (title, slug, summary)
  - Content (markdown or HTML, inline or file reference)
  - Date fields (created, posted, updated, effective dates)
  - Tab assignments (Resumes, Articles, KBase, Guides, Others)
  - Images (with cover image support)
  - External links

## Frontend

The frontend consists of two pages:

- **`documents.html`**: List view with tab filtering
- **`document.html`**: Detail view for a single document

Both pages:
- Load `documents/documents.sqlite` via sql.js
- Use AlpineJS for interactivity
- Support markdown rendering via marked.js
- Work entirely client-side (perfect for GitHub Pages)

## Database Schema

See `schema.sql` for the complete schema. Key tables:

- `doc_categories`: Document categories
- `doc_types`: Document types
- `doc_tabs`: Fixed tabs (All, Resumes, Articles, KBase, Guides, Others)
- `documents`: Main document table
- `document_tabs`: Many-to-many relationship between documents and tabs
- `document_images`: Images associated with documents
- `document_links`: External links for documents

## Workflow

1. Run the admin locally (`uvicorn admin.app:app --reload --port 8000`)
2. Create categories, types, and documents via the admin
3. Upload images (stored in `assets/images/documents/{document_id}/`)
4. Commit `documents/documents.sqlite` and any new images
5. Push to GitHub
6. GitHub Pages serves the static files, and browsers load the SQLite DB via sql.js

## Notes

- The admin runs **only locally** (never on GitHub Pages)
- The SQLite database is committed to the repo and served as a static file
- Images are stored in `assets/images/documents/{document_id}/`
- Document content can be stored inline (in DB) or referenced as files

## Troubleshooting

- **Database not found**: Ensure `documents/documents.sqlite` exists and is committed to the repo
- **Images not loading**: Check that image paths in the DB start with `/assets/images/documents/`
- **Markdown not rendering**: Ensure marked.js is loaded before the Alpine component initializes

