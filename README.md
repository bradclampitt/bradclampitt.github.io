# GitHub Profile Portfolio

**A modern, full-stack portfolio site for GitHub Pages: static frontend with sql.js, FastAPI admin for content, and a single SQLite database.**

Last Updated: July 2026

---

## Overview

This repo is a **hybrid portfolio** built for **GitHub Pages**:

- **Frontend**: Static HTML/CSS/JS served by GitHub Pages. Pages load `admin/database/unified.sqlite` in the browser via **sql.js** (SQLite in WebAssembly) and query it for portfolio, documents, blog, etc. No server or backend required for the live site.
- **Backend**: Optional **FastAPI** admin panel (run locally or on your own server) for creating and editing content. All content is stored in the same unified SQLite database.
- **Database**: One **unified SQLite** file (`admin/database/unified.sqlite`) with namespaced tables for every section. The file is committed so GitHub Pages can serve it; it contains no secrets or private data.

The live site is 100% static; the admin panel is for myself (the admin or anyone who clones the repo) to manage content.

---

## Features

### Content sections

1. **Blog** - Posts with markdown, categories, featured posts  
2. **Portfolio** - Projects with clients, tech tags, features, images  
3. **Documents** - Knowledge base, guides, articles (e.g. `documents/posts/*.html`)  
4. **References** - Testimonials and references  
5. **Tech skills** - Skills by category  
6. **Side projects** - Personal and open-source projects  
7. **Magento modules** - Custom Magento 2 extensions  
8. **Photography** - Galleries and images  
9. **Experience** - Work history, education, background  
10. **CMS** - Site-wide settings and blocks  

### Technical highlights

- **Unified SQLite**: One database, namespaced tables; committed for GitHub Pages + sql.js  
- **Static frontend**: No server required on GitHub Pages  
- **FastAPI admin**: Rich editing, markdown, image uploads  
- **Tailwind CSS**: Responsive, utility-first styling  
- **Alpine.js**: Lightweight interactivity  
- **Markdown**: Processed with syntax highlighting (e.g. Prism, Marked.js)  

---

## Repository structure

```
bradclampitt.github.io/
├── admin/                          # Backend admin panel (FastAPI)
│   ├── app.py                      # Main FastAPI app
│   ├── config.py                   # Paths and config
│   ├── admin-panel.sh              # Start/stop script
│   ├── database/
│   │   ├── unified.sqlite          # Unified DB (in repo for GitHub Pages)
│   │   ├── schema.sql              # Full schema
│   │   └── connection.py           # DB connection helper
│   │
│   ├── resources/
│   │   ├── blog/                   # Blog templates, posts.json, etc.
│   │   └── documents/              # Document templates
│   │
│   ├── templates/                  # Jinja2 admin templates
│   ├── static/                     # Admin CSS/JS
│   └── requirements.txt
│
├── assets/
│   ├── css/                        # Tailwind output (tailwind-built.css built locally)
│   ├── js/                         # sql-wasm.js, static-site.js, sidebar-loader.js
│   ├── includes/                   # Reusable HTML (e.g. sidebar.html)
│   └── images/                     # Media by section (blog, portfolio, documents, …)
│
├── blog/
│   └── posts/                      # Generated blog post HTML
│
├── documents/
│   ├── document.html               # Document viewer (slug-based)
│   └── posts/                      # Document article HTML
│
├── docs/
│   ├── SETUP_GUIDE.md              # Full server/setup guide
│   ├── ROLLBACK_PLAN.md            # Deploy rollback steps
│   └── references/                 # Reference docs
│
├── shared/                         # Shared Python (e.g. markdown_processor.py)
│
├── index.html                      # Home
├── blog.html                       # Blog listing
├── portfolio.html                  # Portfolio (loads unified.sqlite via sql.js)
├── project.html                    # Single project (slug)
├── documents.html                  # Documents listing
├── experience.html, resume.html, references.html
├── magento.html, photography.html, side-projects.html, personal.html, contact.html
├── 404.html
├── _config.yml, _redirects         # GitHub Pages / Jekyll (if used)
├── package.json, tailwind.config.js # Tailwind build
└── README.md
```

### Database layout (unified SQLite)

Namespaced tables in `admin/database/unified.sqlite`:

- **Blog**: `blog_categories`, `blog_posts`  
- **Documents**: `doc_tabs`, `documents`, `document_images`, etc.  
- **Portfolio**: `portfolio_tabs`, `portfolio_projects`, `portfolio_project_*`, `clients`  
- **References**: `ref_*`  
- **Tech skills**: `tech_skill_*`  
- **Side projects**: `side_project_*`  
- **Magento**: `magento_*`  
- **Photography**: `photography_*`  
- **Experience**: `experience_*`  
- **CMS**: `cms_*`  

One file to backup and deploy; clear separation by section.

---

## Quick start

### Prerequisites

- **Node.js** 16+ (Tailwind)
- **Python** 3.8+ (admin only)
- **Git**

### Frontend (GitHub Pages)

1. **Install and build**:
   ```bash
   npm install
   npm run build
   ```
2. **Commit and push** - GitHub Pages serves the repo; the site loads `unified.sqlite` in the browser via sql.js.

### Admin panel (local or your server)

1. **Go to admin**:
   ```bash
   cd admin
   ```
2. **Create venv and install**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate   # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. **Start server**:
   ```bash
   ./admin-panel.sh start
   ```
4. **Open**: `http://localhost:8000/admin`  
   Or run manually: `uvicorn app:app --reload --port 8000 --host 127.0.0.1`

---

## Install from GitHub (full setup)

1. **Clone**:
   ```bash
   git clone https://github.com/bradclampitt/bradclampitt.github.io.git
   cd bradclampitt.github.io
   ```
2. **Frontend**:
   ```bash
   npm install
   npm run build
   ```
3. **Database**: The repo includes `admin/database/unified.sqlite`. To start from an empty DB instead:
   ```bash
   sqlite3 admin/database/unified.sqlite < admin/database/schema.sql
   ```
4. **Admin**:
   ```bash
   cd admin
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ./admin-panel.sh start
   ```
5. **Admin UI**: `http://localhost:8000/admin`  
   When you change the schema, update `admin/database/schema.sql` for future installs.

---

## Usage

### Admin panel

- **Dashboard**: Overview of sections  
- **Blog / Portfolio / Documents / References / Tech skills / Side projects / Magento / Photography / Experience / CMS**: Each has its own list and edit screens  

Content is written to `admin/database/unified.sqlite`. The same file is used by the static site on GitHub Pages (via sql.js).

### Frontend pages (static)

- `index.html` - Home  
- `blog.html` - Blog list; `blog/posts/*.html` - posts  
- `portfolio.html` - Projects; `project.html?slug=...` - single project  
- `documents.html` - Document list; `documents/document.html?slug=...` - single document  
- `experience.html`, `resume.html`, `references.html`, `magento.html`, `photography.html`, `side-projects.html`, `personal.html`, `contact.html`  

On the **live site** (e.g. `bradclampitt.github.io`), pages use **static-site.js** to detect the host; they then load `admin/database/unified.sqlite` via **sql.js** (sql-wasm.js) and query it in the browser. When the admin server is running locally, the same pages can call `/api/*` instead. Blog, portfolio, documents, experience, magento, side-projects, photography, references, CMS settings, and contact all support this hybrid behavior.

### Media

Media lives under `assets/images/` by section (e.g. `blog/`, `portfolio/`, `documents/`, `photography/`).

---

## File distribution

### In the GitHub repo

- All HTML, CSS, JS, and assets  
- `admin/` code and templates (no venv, no `__pycache__`)  
- `admin/database/unified.sqlite` - committed so GitHub Pages can serve it (sql.js loads it client-side)  
- `admin/database/schema.sql`  
- `docs/` (e.g. SETUP_GUIDE.md, ROLLBACK_PLAN.md)  
- `.gitignore` excludes: `venv/`, `node_modules/`, `*.log`, `_archived/`, `blog/archive/`, `assets/css/tailwind-built.css`, etc. Other `.sqlite` files are ignored; only `admin/database/unified.sqlite` is allowed.

### Not in the repo (local / server only)

- `admin/venv/`, `__pycache__/`, `*.log`  
- `_archived/`, `blog/archive/`  
- Built file: `assets/css/tailwind-built.css` (generated by `npm run build`)  

The database in the repo is the same one the live site uses; it contains no secrets. For a private copy, keep a separate DB and do not commit it (or use a different branch).

---

## Technology stack

| Layer    | Tech |
|----------|------|
| Frontend | HTML5, Tailwind CSS, Alpine.js, sql.js (SQLite in browser), Marked.js, Prism.js |
| Backend  | FastAPI, Jinja2, Python 3.8+ |
| Data     | SQLite (unified, namespaced tables) |
| Hosting  | GitHub Pages (static) |
| Build    | Node.js (Tailwind), npm |

---

## Content workflow

1. Run the admin panel locally (or on your server).  
2. Create and edit content in the admin; it’s saved to `admin/database/unified.sqlite`.  
3. Commit changes (including `unified.sqlite` if you want the live site to reflect them).  
4. Push to GitHub - Pages serves the updated static site and DB.

---

## Security and practices

- **unified.sqlite** in the repo is intended for public, non-sensitive content.  
- Admin panel should run only on localhost or a trusted network.  
- Venv, logs, and env files are gitignored.  
- Use parameterized queries (no raw SQL from user input).

---

## Documentation

- **[SETUP_GUIDE.md](./docs/SETUP_GUIDE.md)** - Full server/setup (e.g. Proxmox, Nginx, Tailwind, admin)  
- **[ROLLBACK_PLAN.md](./docs/ROLLBACK_PLAN.md)** - How to roll back a deploy (tags, force-push)  
- **[admin/README.md](./admin/README.md)** - Admin panel usage and scripts  
- **docs/references/** - Reference-style docs  

---

## Contributing and reuse

This is a personal portfolio repo. You’re welcome to fork or use it as a template for your own GitHub Pages profile; adjust content and branding as needed.

---

## Author

**Bradley R. Clampitt**

- GitHub: [bradclampitt](https://github.com/bradclampitt)  
- Live site: [bradclampitt.github.io](https://bradclampitt.github.io) (when deployed from this repo)

---

## Changelog

### March 2026
- v2 deploy to GitHub Pages: unified SQLite in repo for sql.js client-side loading  
- Cleanup: removed obsolete docs and duplicate blog/admin paths; consolidated documents under `documents/posts/`  
- Added `docs/ROLLBACK_PLAN.md`, `assets/includes/` (sidebar), `sidebar-loader.js`  
- `.gitignore` updated: only `admin/database/unified.sqlite` allowed for SQLite  
- **Static-site fallbacks**: Added `assets/js/static-site.js` (host detection, `getIndexDb()`). Pages that need data (experience, blog, magento, side-projects, photography, portfolio, documents, references, contact, CMS settings) now load from the DB on GitHub Pages and use the API when the admin server is available.  

### December 2025
- Unified SQLite database with namespaced tables  
- Consolidated admin under single FastAPI app and `admin/` structure  

### November 2025
- Initial multi-section setup; blog, portfolio, documents management  

---

## Possible future improvements

Ways to do these within a GitHub Pages (static) profile and optional local/admin setup:

- [ ] **Split admin routes into modules** - Admin-only. Refactor `admin/app.py` into FastAPI routers or Blueprints (e.g. `routers/blog.py`, `routers/portfolio.py`). No impact on the static site.
- [ ] **Optional API for programmatic access** - (1) **Static**: Export key data to JSON at build/deploy time (e.g. `data/experience.json`, `data/blog-posts.json`) and commit them; the live site or external tools can fetch via raw GitHub or the deployed URL. (2) **When admin runs**: Document existing FastAPI `/api/*` endpoints for local or server use.
- [ ] **Search across sections** - Client-side only (no server on GitHub Pages). Options: (1) Use sql.js + the existing `unified.sqlite` and run full-text or simple `LIKE` queries in the browser. (2) At build time, generate a static search index (e.g. Lunr.js or FlexSearch JSON), commit it, and run search in JS on the live site.
- [ ] **Dark mode, improved mobile admin** - Dark mode: CSS (`prefers-color-scheme`) and/or a toggle with `localStorage`; works on static pages and admin. Mobile admin: improve responsive layout and touch targets in `admin/templates/`; admin is only used when the FastAPI app is running (local or your server).
- [ ] **Caching strategy for heavy pages** - (1) Rely on browser caching for `unified.sqlite` and assets (GitHub Pages sends ETag/Last-Modified). (2) Optional: for the heaviest sections, export pre-built JSON (e.g. `data/experience.json`) at deploy time and have those pages fetch JSON instead of loading the full DB. (3) Optional: service worker to cache the DB and assets for repeat visits.

---

This repo works as both a live portfolio on GitHub Pages and a template for static sites backed by a single SQLite file and an optional FastAPI admin.
