# Admin Console

Unified admin CMS for managing Portfolios, Documents, and other site content.

## Overview

This is a unified admin console that manages:
- **Portfolios**: Portfolio projects, clients, types, tech tags, features
- **Documents**: Knowledge base, articles, guides, resumes
- **Future additions**: Blog, pages, etc.

All systems are accessed through a single dashboard at one port.

## Setup

### Prerequisites

- Python 3.8+
- pip

### Installation

1. Create a virtual environment (required):

```bash
cd admin
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

**Note**: If you get an "externally-managed-environment" error, you must use a virtual environment.

### Running the Admin

#### Using the Management Script (Recommended)

Use the provided bash script for easy management:

```bash
cd admin
./admin-panel.sh start    # Start the server
./admin-panel.sh status   # Check if it's running
./admin-panel.sh kill     # Stop the server
./admin-panel.sh restart  # Restart the server
./admin-panel.sh logs     # View recent logs
```

#### Manual Start

Alternatively, start the FastAPI admin server manually:

```bash
cd admin
source venv/bin/activate  # Activate virtual environment if not already active
uvicorn app:app --reload --port 8000 --host 127.0.0.1
```

**Note**: Make sure to activate the virtual environment before running uvicorn. You'll know it's activated when you see `(venv)` in your terminal prompt.

Visit `http://localhost:8000/admin` to access the admin dashboard.

### First Run

On first startup, the admin will automatically:
- Create `portfolios/portfolios.sqlite` if it doesn't exist
- Create `documents/documents.sqlite` if it doesn't exist
- Initialize both database schemas

## Features

### Portfolios
- Dashboard with project/client stats
- Client management
- Project management with features, tech tags, images
- Project types and tech tags
- Feature library/component library

### Documents
- Document management (markdown/HTML)
- Categories and document types
- Tab assignments (Resumes, Articles, KBase, Guides, Others)
- Image uploads
- External links

## Database Structure

Each system uses its own SQLite database:
- `portfolios/portfolios.sqlite` - Portfolio data
- `documents/documents.sqlite` - Document data

These databases are committed to the repo and served as static files for the frontend.

## Workflow

1. Run the admin locally (`uvicorn app:app --reload --port 8000`)
2. Manage portfolios, documents, etc. via the unified admin
3. Commit database files and any new assets
4. Push to GitHub
5. GitHub Pages serves the static files

## Notes

- The admin runs **only locally** (never on GitHub Pages)
- All SQLite databases are committed to the repo
- Images are stored in `assets/images/{system}/`
- Can easily add more systems (blog, pages, etc.) in the future

