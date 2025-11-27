# GitHub Profile Portfolio

**A modern, full-stack portfolio website showcasing professional work, blog posts, technical documentation, and more.**

Last Updated: January 2025

---

## 🎯 Overview

This repository contains a **hybrid portfolio system** designed for GitHub Pages:

- **Frontend**: Static HTML/CSS/JS files served via GitHub Pages (using sql.js to load SQLite databases)
- **Backend**: FastAPI admin panel running on a Proxmox server for content management
- **Database**: Unified SQLite database with namespaced tables for all sections

The frontend is completely static and can be hosted anywhere, while the backend admin panel provides a powerful CMS for managing all content.

---

## ✨ Features

### Content Sections

1. **📝 Blog** - Technical blog posts with markdown support, categories, and featured posts
2. **💼 Portfolio** - Project showcase with clients, tech tags, features, and images
3. **📄 Documents** - Knowledge base, articles, guides, and resumes
4. **👥 References** - Professional references and testimonials
5. **🛠️ Tech Skills** - Technical skills organized by categories
6. **🚀 Side Projects** - Personal and open-source projects
7. **🛒 Magento Modules** - Custom Magento 2 extensions and modules
8. **📸 Photography** - Photography portfolio and galleries
9. **💼 Experience** - Work experience, education, and professional background
10. **⚙️ CMS** - Site-wide settings and content blocks

### Technical Highlights

- **Unified Database**: Single SQLite database with namespaced tables for all sections
- **Static Frontend**: Zero server-side requirements, works on GitHub Pages
- **Modern Admin Panel**: FastAPI-based CMS with rich text editing
- **Responsive Design**: Mobile-first design with Tailwind CSS
- **Markdown Support**: Full markdown processing with syntax highlighting
- **Image Management**: Organized media storage with upload capabilities
- **SEO Friendly**: Semantic HTML and proper meta tags

---

## 🏗️ Architecture

### Repository Structure

```
github_v2/
├── admin/                          # Backend admin panel (FastAPI)
│   ├── app.py                     # Main FastAPI application
│   ├── config.py                  # Centralized configuration
│   ├── database/
│   │   ├── unified.sqlite         # Unified database (production)
│   │   ├── demo.sqlite            # Demo database (for GitHub)
│   │   ├── schema.sql             # Combined schema
│   │   └── migrations/            # Migration scripts
│   ├── resources/                 # Section-specific resources
│   │   ├── blog/
│   │   ├── documents/
│   │   └── ... (all sections)
│   ├── templates/                 # Jinja2 templates
│   ├── static/                    # Admin CSS/JS
│   └── requirements.txt           # Python dependencies
│
├── assets/                         # Static assets
│   ├── css/                       # Compiled Tailwind CSS
│   ├── js/                        # JavaScript libraries (sql.js, Alpine.js)
│   └── images/                    # Media files organized by section
│
├── docs/                          # Documentation
│   ├── CONSOLIDATION_OPTIONS.md   # Architecture consolidation docs
│   └── ...
│
├── *.html                         # Frontend pages (blog.html, portfolio.html, etc.)
├── shared/                        # Shared Python modules
├── package.json                   # Node.js dependencies (Tailwind)
└── README.md                      # This file
```

### Database Architecture

The system uses a **unified SQLite database** with namespaced tables:

- `blog_categories`, `blog_posts` - Blog content
- `doc_categories`, `documents`, `document_images` - Documents
- `portfolio_tabs`, `projects`, `project_images` - Portfolio
- `ref_*` - References
- `tech_skill_*` - Tech skills
- `side_project_*` - Side projects
- `magento_*` - Magento modules
- `photography_*` - Photography
- `experience_*` - Experience
- `cms_*` - CMS settings

This approach provides:
- Single database to manage and backup
- Clear separation between sections
- Easy cross-section queries when needed
- Simplified admin codebase

---

## 🚀 Quick Start

### Prerequisites

- **Node.js** 16+ (for Tailwind CSS)
- **Python** 3.8+ (for admin panel)
- **Git** (for version control)

### Frontend Setup (GitHub Pages)

1. **Install Node.js dependencies**:
```bash
npm install
```

2. **Build Tailwind CSS**:
```bash
npm run build
```

3. **Commit and push** to GitHub - GitHub Pages will automatically serve the static files.

### Backend Setup (Local/Proxmox Server)

1. **Navigate to admin directory**:
```bash
cd admin
```

2. **Create virtual environment**:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install Python dependencies**:
```bash
pip install -r requirements.txt
```

4. **Start the admin server**:
```bash
# Using the management script (recommended)
./admin-panel.sh start

# Or manually
uvicorn app:app --reload --port 8000 --host 127.0.0.1
```

5. **Access admin panel**: `http://localhost:8000/admin`

---

## 📖 Usage Guide

### Admin Panel

The admin panel provides a unified interface for managing all content:

- **Dashboard**: Overview of all sections and statistics
- **Blog Management**: Create/edit blog posts with markdown support
- **Portfolio Management**: Manage projects, clients, and tech tags
- **Document Management**: Create knowledge base articles and guides
- **And more**: Each section has its own management interface

### Frontend Pages

The frontend pages load data from the SQLite database using `sql.js`:

- `index.html` - Homepage
- `blog.html` - Blog listing and posts
- `portfolio.html` - Portfolio projects
- `documents.html` - Documents and knowledge base
- `experience.html` - Work experience
- `references.html` - Professional references
- `tech-skills.html` - Technical skills
- `side-projects.html` - Side projects
- `magento.html` - Magento modules
- `photography.html` - Photography portfolio

### Database Management

**Production Database** (on Proxmox server):
- Located at: `admin/database/unified.sqlite`
- Contains real production data
- **NOT committed to GitHub** (excluded via `.gitignore`)

**Demo Database** (for GitHub):
- Located at: `admin/database/demo.sqlite`
- Contains sample data for portfolio demonstration
- **Committed to GitHub** for showcasing functionality

### Media Management

All media files are stored in `assets/images/` organized by section:
- `assets/images/blog/` - Blog post images
- `assets/images/portfolio/` - Portfolio project images
- `assets/images/documents/` - Document images
- `assets/images/photography/` - Photography images
- And so on...

---

## 🔧 Development

### Adding a New Section

1. **Create section folder** in `admin/resources/{section-name}/`
2. **Add schema** to `admin/database/schema.sql` with namespaced tables
3. **Create admin routes** in `admin/app.py` or modularize into `admin/routes/`
4. **Create frontend page** (e.g., `{section-name}.html`)
5. **Update navigation** in all HTML files

### Database Migrations

Database migrations are handled via scripts in `admin/database/migrations/`:

```bash
cd admin
python database/migrations/migrate_unified.py
```

### Tailwind CSS Development

Watch for changes and rebuild CSS:

```bash
npm run build:watch
```

Or build once:

```bash
npm run build
```

---

## 📁 File Distribution

### Files on Proxmox Server (NOT in GitHub)

These files contain production data or are environment-specific:

- `admin/database/unified.sqlite` - Production database
- `admin/venv/` - Python virtual environment
- `admin/__pycache__/` - Python cache files
- `admin/*.log` - Log files
- `*.sqlite` - Any production database files

### Files in GitHub Repository

All code, templates, schemas, and static files are committed:

- All Python code (`admin/app.py`, `admin/config.py`, etc.)
- All templates (`admin/templates/`)
- Database schemas (`admin/database/schema.sql`)
- Frontend HTML files (`*.html`)
- Static assets (`assets/`)
- Documentation (`docs/`)
- Demo database (`admin/database/demo.sqlite`)

---

## 🛠️ Technology Stack

### Frontend
- **HTML5** - Semantic markup
- **Tailwind CSS** - Utility-first CSS framework
- **Alpine.js** - Lightweight JavaScript framework
- **sql.js** - SQLite compiled to WebAssembly for client-side database queries
- **Marked.js** - Markdown parser
- **Prism.js** - Syntax highlighting

### Backend
- **FastAPI** - Modern Python web framework
- **SQLite** - Lightweight database
- **Jinja2** - Template engine
- **Python 3.8+** - Programming language

### Tools
- **Node.js** - For Tailwind CSS compilation
- **Git** - Version control
- **GitHub Pages** - Static hosting

---

## 📝 Content Management Workflow

1. **Start admin panel** on Proxmox server
2. **Create/edit content** via admin interface
3. **Content is saved** to `admin/database/unified.sqlite`
4. **Export demo database** (optional, for GitHub demo)
5. **Commit changes** to Git (excluding production database)
6. **Push to GitHub** - Frontend automatically updates

---

## 🔒 Security & Best Practices

- **Production databases are NOT committed** to GitHub
- **Virtual environment is excluded** from Git
- **Environment variables** stored securely on server
- **Admin panel** runs only on localhost/private network
- **Input validation** on all admin forms
- **SQL injection protection** via parameterized queries

---

## 📚 Documentation

- **[Consolidation Options](./docs/CONSOLIDATION_OPTIONS.md)** - Architecture consolidation analysis
- **[Admin README](./admin/README.md)** - Admin panel documentation
- Section-specific READMEs in `admin/resources/{section}/`

---

## 🤝 Contributing

This is a personal portfolio repository. However, if you find it useful as a reference or want to fork it for your own use, feel free!

---

## 📄 License

This project is for personal/portfolio use. Feel free to use it as inspiration for your own projects.

---

## 👤 Author

**Bradley R. Clampitt**

- Portfolio: [GitHub Profile](https://github.com/yourusername)
- Built with modern web technologies and best practices

---

## 🙏 Acknowledgments

- Built with assistance from AI tools (ChatGPT) for learning and development
- Uses open-source libraries and frameworks (see dependencies)
- Inspired by modern portfolio and CMS design patterns

---

## 📅 Changelog

### January 2025
- ✅ Consolidated all sections into unified `admin/` structure
- ✅ Migrated to single unified SQLite database with namespaced tables
- ✅ Improved code organization and maintainability
- ✅ Added comprehensive documentation

### November 2025
- Initial setup with separate section databases
- Blog management system implementation
- Portfolio and documents management

---

## 🎯 Future Enhancements

- [ ] Modularize admin routes into separate files
- [ ] Add API endpoints for programmatic access
- [ ] Implement search across all sections
- [ ] Add analytics and tracking
- [ ] Improve mobile admin experience
- [ ] Add dark mode support
- [ ] Implement caching strategies

---

**Note**: This repository serves as both a functional portfolio website and a demonstration of full-stack development capabilities, including database design, API development, and modern frontend practices.
