from __future__ import annotations

import json
import re
import secrets
import sqlite3
import sys
from datetime import date
from itertools import zip_longest
from pathlib import Path
from typing import Any, Iterable, List, Tuple

from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import RedirectResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

# Import shared markdown processor
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
try:
    from shared.markdown_processor import SharedMarkdownProcessor
    MARKDOWN_PROCESSOR = SharedMarkdownProcessor()
    HAS_MARKDOWN_PROCESSOR = True
except ImportError:
    # Fallback if shared module not available
    MARKDOWN_PROCESSOR = None
    HAS_MARKDOWN_PROCESSOR = False

# Import configuration
from admin.config import (
    BLOG_RESOURCES, BLOG_MEDIA,
    DOCUMENTS_RESOURCES, DOCUMENTS_MEDIA,
    PORTFOLIOS_RESOURCES, PORTFOLIO_MEDIA,
    REFERENCES_RESOURCES,
    TECH_SKILLS_RESOURCES,
    SIDE_PROJECTS_RESOURCES, PROJECTS_MEDIA,
    MAGENTO_RESOURCES, MAGENTO_MEDIA,
    PHOTOGRAPHY_RESOURCES, PHOTOGRAPHY_MEDIA,
    EXPERIENCE_RESOURCES,
    CMS_RESOURCES,
    RESOURCES_DIR,
    DATABASE_PATH, SCHEMA_PATH
)

# Import unified database connection
from admin.database.connection import get_conn, row_to_dict

# Import BlogManager for blog processing
try:
    import importlib.util
    blog_manager_path = BLOG_RESOURCES / "blog-manager.py"
    if blog_manager_path.exists():
        spec = importlib.util.spec_from_file_location("blog_manager", blog_manager_path)
        blog_manager_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(blog_manager_module)
        # BlogManager expects the blog root directory (where HTML files are generated), not the resources directory
        BLOG_MANAGER = blog_manager_module.BlogManager(str(ROOT / "blog"))
        HAS_BLOG_MANAGER = True
    else:
        BLOG_MANAGER = None
        HAS_BLOG_MANAGER = False
except Exception as e:
    BLOG_MANAGER = None
    HAS_BLOG_MANAGER = False
    print(f"Warning: BlogManager not available: {e}")

# Legacy paths (will be updated section by section)
# Portfolio paths - NOW USING CONFIG AND UNIFIED DATABASE
# PORTFOLIO_DIR, DB_PATH, SCHEMA_PATH now come from config
# IMG_ROOT now comes from config as PORTFOLIO_MEDIA

# Blog system paths - NOW USING CONFIG AND UNIFIED DATABASE
# BLOG_DIR, BLOG_DB_PATH, BLOG_SCHEMA_PATH now come from config
# BLOG_IMG_ROOT now comes from config as BLOG_MEDIA
BLOG_SRC = BLOG_RESOURCES  # Updated to use resources directory

# Documents system paths - NOW USING CONFIG AND UNIFIED DATABASE
# DOC_DIR, DOC_DB_PATH, DOC_SCHEMA_PATH now come from config
# DOC_IMG_ROOT now comes from config as DOCUMENTS_MEDIA

# References system paths - NOW USING CONFIG AND UNIFIED DATABASE
# REF_DIR, REF_DB_PATH, REF_SCHEMA_PATH now come from config

# Tech Skills system paths - NOW USING CONFIG AND UNIFIED DATABASE
# TECH_SKILLS_DIR, TECH_SKILLS_DB_PATH, TECH_SKILLS_SCHEMA_PATH now come from config

# Side Projects system paths - NOW USING CONFIG AND UNIFIED DATABASE
# SIDE_PROJECTS_DIR, SIDE_PROJECTS_DB_PATH, SIDE_PROJECTS_SCHEMA_PATH now come from config
# PROJECTS_MEDIA now comes from config as PROJECTS_MEDIA

# Magento system paths - NOW USING CONFIG AND UNIFIED DATABASE
# MAGENTO_DIR, MAGENTO_DB_PATH, MAGENTO_SCHEMA_PATH now come from config
# MAGENTO_MEDIA now comes from config as MAGENTO_MEDIA

# Photography system paths - NOW USING CONFIG AND UNIFIED DATABASE
# PHOTOGRAPHY_DIR, PHOTOGRAPHY_DB_PATH, PHOTOGRAPHY_SCHEMA_PATH now come from config
# PHOTOGRAPHY_MEDIA now comes from config as PHOTOGRAPHY_MEDIA

# Experience system paths - NOW USING CONFIG AND UNIFIED DATABASE
# EXPERIENCE_DIR, EXPERIENCE_DB_PATH, EXPERIENCE_SCHEMA_PATH now come from config
LOGO_IMG_ROOT = ROOT / "assets" / "images" / "logos"

# CMS system paths - NOW USING CONFIG AND UNIFIED DATABASE
# CMS_DIR, CMS_DB_PATH, CMS_SCHEMA_PATH now come from config

TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"
STATIC_DIR = Path(__file__).resolve().parent / "static"

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"}
STATUS_DEFAULTS = [
    "",
    "Active",
    "Updated",
    "Archived",
    "Future",
    "Shutdown",
    "Revised by Ultrasun NL",
]


# Portfolio now uses unified database - get_conn() replaced with unified get_conn()
# def get_conn() -> sqlite3.Connection:
#     conn = sqlite3.connect(DB_PATH)
#     conn.row_factory = sqlite3.Row
#     return conn


# Documents now uses unified database - get_conn() replaced with get_conn()
# def get_conn() -> sqlite3.Connection:
#     ensure_documents_database()
#     conn = sqlite3.connect(DOC_DB_PATH)
#     conn.row_factory = sqlite3.Row
#     return conn


# Documents database now handled by unified database - ensure_documents_database() no longer needed
# def ensure_documents_database() -> None:
#     DOC_DIR.mkdir(parents=True, exist_ok=True)
#     if not DOC_DB_PATH.exists():
#         if not DOC_SCHEMA_PATH.exists():
#             return
#         with sqlite3.connect(DOC_DB_PATH) as conn, DOC_SCHEMA_PATH.open("r", encoding="utf-8") as fh:
#             conn.executescript(fh.read())
#     else:
#         # Migrate existing database if needed
#         migrate_documents_database()


# Documents migration now handled by unified database - migrate_documents_database() no longer needed
def migrate_documents_database() -> None:
    """Migrate documents database schema if needed - DEPRECATED: Now using unified database"""
    # This function is no longer used - documents uses unified database
    pass


# References now uses unified database - get_conn() replaced with get_conn()
# def get_conn() -> sqlite3.Connection:
#     ensure_references_database()
#     conn = sqlite3.connect(REF_DB_PATH)
#     conn.row_factory = sqlite3.Row
#     return conn


# References database now handled by unified database - ensure_references_database() no longer needed
# def ensure_references_database() -> None:
#     REF_DIR.mkdir(parents=True, exist_ok=True)
#     if not REF_DB_PATH.exists():
#         if not REF_SCHEMA_PATH.exists():
#             return
#         with sqlite3.connect(REF_DB_PATH) as conn, REF_SCHEMA_PATH.open("r", encoding="utf-8") as fh:
#             conn.executescript(fh.read())


# Tech Skills now uses unified database - get_conn() replaced with get_conn()
# def get_conn() -> sqlite3.Connection:
#     ensure_tech_skills_database()
#     conn = sqlite3.connect(TECH_SKILLS_DB_PATH)
#     conn.row_factory = sqlite3.Row
#     return conn


# Tech Skills database now handled by unified database - ensure_tech_skills_database() no longer needed
# def ensure_tech_skills_database() -> None:
#     TECH_SKILLS_DIR.mkdir(parents=True, exist_ok=True)
#     if not TECH_SKILLS_DB_PATH.exists():
#         if not TECH_SKILLS_SCHEMA_PATH.exists():
#             return
#         with sqlite3.connect(TECH_SKILLS_DB_PATH) as conn, TECH_SKILLS_SCHEMA_PATH.open("r", encoding="utf-8") as fh:
#             conn.executescript(fh.read())
#     else:
#         # Migrate existing database if needed
#         migrate_tech_skills_database()


# Side Projects now uses unified database - get_conn() replaced with get_conn()
# def get_conn() -> sqlite3.Connection:
#     ensure_side_projects_database()
#     conn = sqlite3.connect(SIDE_PROJECTS_DB_PATH)
#     conn.row_factory = sqlite3.Row
#     return conn


# Side Projects database now handled by unified database - ensure_side_projects_database() no longer needed
# def ensure_side_projects_database() -> None:
#     SIDE_PROJECTS_DIR.mkdir(parents=True, exist_ok=True)
#     if not SIDE_PROJECTS_DB_PATH.exists():
#         if not SIDE_PROJECTS_SCHEMA_PATH.exists():
#             return
#         with sqlite3.connect(SIDE_PROJECTS_DB_PATH) as conn, SIDE_PROJECTS_SCHEMA_PATH.open("r", encoding="utf-8") as fh:
#             conn.executescript(fh.read())


# Magento now uses unified database - get_conn() replaced with get_conn()
# def get_conn() -> sqlite3.Connection:
#     ensure_magento_database()
#     conn = sqlite3.connect(MAGENTO_DB_PATH)
#     conn.row_factory = sqlite3.Row
#     return conn


# Magento database now handled by unified database - ensure_magento_database() no longer needed
# def ensure_magento_database() -> None:
#     MAGENTO_DIR.mkdir(parents=True, exist_ok=True)
#     if not MAGENTO_DB_PATH.exists():
#         if not MAGENTO_SCHEMA_PATH.exists():
#             return
#         with sqlite3.connect(MAGENTO_DB_PATH) as conn, MAGENTO_SCHEMA_PATH.open("r", encoding="utf-8") as fh:
#             conn.executescript(fh.read())


# Photography now uses unified database - get_conn() replaced with get_conn()
# def get_conn() -> sqlite3.Connection:
#     ensure_photography_database()
#     conn = sqlite3.connect(PHOTOGRAPHY_DB_PATH)
#     conn.row_factory = sqlite3.Row
#     return conn


# Photography database now handled by unified database - ensure_photography_database() no longer needed
# def ensure_photography_database() -> None:
#     PHOTOGRAPHY_DIR.mkdir(parents=True, exist_ok=True)
#     if not PHOTOGRAPHY_DB_PATH.exists():
#         if not PHOTOGRAPHY_SCHEMA_PATH.exists():
#             return
#         with sqlite3.connect(PHOTOGRAPHY_DB_PATH) as conn, PHOTOGRAPHY_SCHEMA_PATH.open("r", encoding="utf-8") as fh:
#             conn.executescript(fh.read())


# Experience now uses unified database - get_conn() replaced with get_conn()
# def get_conn() -> sqlite3.Connection:
#     ensure_experience_database()
#     conn = sqlite3.connect(EXPERIENCE_DB_PATH)
#     conn.row_factory = sqlite3.Row
#     return conn


# Blog now uses unified database - get_conn() replaced with get_conn()
# def get_conn() -> sqlite3.Connection:
#     ensure_blog_database()
#     conn = sqlite3.connect(BLOG_DB_PATH)
#     conn.row_factory = sqlite3.Row
#     return conn


# CMS now uses unified database - get_conn() replaced with get_conn()
# def get_conn() -> sqlite3.Connection:
#     ensure_cms_database()
#     conn = sqlite3.connect(CMS_DB_PATH)
#     conn.row_factory = sqlite3.Row
#     return conn


# CMS database now handled by unified database - ensure_cms_database() no longer needed
# def ensure_cms_database() -> None:
#     CMS_DIR.mkdir(parents=True, exist_ok=True)
#     if not CMS_DB_PATH.exists():
#         if not CMS_SCHEMA_PATH.exists():
#             return
#         with sqlite3.connect(CMS_DB_PATH) as conn, CMS_SCHEMA_PATH.open("r", encoding="utf-8") as fh:
#             conn.executescript(fh.read())
#     else:
#         # Migrate existing database if needed
#         migrate_cms_database()


# CMS migration now handled by unified database migration script
def migrate_cms_database() -> None:
    """Migrate CMS database schema if needed"""
    # Migration now handled by unified database migration script
    pass


# Blog database now handled by unified database - ensure_blog_database() no longer needed
# def ensure_blog_database() -> None:
#     BLOG_DIR.mkdir(parents=True, exist_ok=True)
#     if not BLOG_DB_PATH.exists():
#         if not BLOG_SCHEMA_PATH.exists():
#             return
#         with sqlite3.connect(BLOG_DB_PATH) as conn, BLOG_SCHEMA_PATH.open("r", encoding="utf-8") as fh:
#             conn.executescript(fh.read())
#     else:
#         # Migrate existing database if needed
#         migrate_blog_database()


# Blog migration now handled by unified database - migrate_blog_database() no longer needed
def migrate_blog_database() -> None:
    """Migrate blog database schema if needed - DEPRECATED: Now using unified database"""
    # This function is no longer used - blog uses unified database
    pass


# Experience database now handled by unified database - ensure_experience_database() no longer needed
# def ensure_experience_database() -> None:
#     EXPERIENCE_DIR.mkdir(parents=True, exist_ok=True)
#     if not EXPERIENCE_DB_PATH.exists():
#         if not EXPERIENCE_SCHEMA_PATH.exists():
#             return
#         with sqlite3.connect(EXPERIENCE_DB_PATH) as conn, EXPERIENCE_SCHEMA_PATH.open("r", encoding="utf-8") as fh:
#             conn.executescript(fh.read())


def magento_slugify(text: str) -> str:
    """Generate a URL-friendly slug from text"""
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text


# Tech Skills migration now handled by unified database migration script
def migrate_tech_skills_database() -> None:
    """Migrate old schema (category TEXT) to new schema (category_id INTEGER)"""
    # Migration now handled by unified database migration script
    pass


def doc_slugify(value: str) -> str:
    cleaned = "".join(char if char.isalnum() else "-" for char in value.strip().lower())
    while "--" in cleaned:
        cleaned = cleaned.replace("--", "-")
    return cleaned.strip("-")


def ensure_database() -> None:
    """Ensure the unified database exists and is up to date"""
    # Use the unified database connection module
    from admin.database.connection import ensure_database as ensure_unified_database
    ensure_unified_database()
    # Run schema updates
    with get_conn() as conn:
        _ensure_schema_updates(conn)


def slugify(value: str) -> str:
    cleaned = "".join(char if char.isalnum() else "-" for char in value.strip().lower())
    while "--" in cleaned:
        cleaned = cleaned.replace("--", "-")
    return cleaned.strip("-")


def _optional_int(value: str | None) -> int | None:
    if value is None:
        return None
    value = value.strip()
    if not value:
        return None
    try:
        return int(value)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=f"Invalid integer: {value}") from exc


def _form_error_redirect(path: str, message: str) -> RedirectResponse:
    from urllib.parse import quote

    return RedirectResponse(url=f"{path}?error={quote(message)}", status_code=303)


def _experience_unique_name_redirect(
    *,
    base_path: str,
    record_id: int | None,
    name: str,
) -> RedirectResponse:
    message = f"A record named '{name.strip()}' already exists. Please use a different name."
    if record_id is None:
        return _form_error_redirect(f"{base_path}/new", message)
    return _form_error_redirect(f"{base_path}/{record_id}", message)


def _coerce_int(value: str | None, default: int = 0) -> int:
    if value is None:
        return default
    try:
        cleaned = value.strip()
    except AttributeError as exc:
        raise HTTPException(status_code=400, detail=f"Invalid integer: {value}") from exc
    if not cleaned:
        return default
    try:
        return int(cleaned)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=f"Invalid integer: {value}") from exc


def _as_bool(value: str | None) -> bool:
    if value is None:
        return False
    return value.lower() not in {"", "0", "false", "off"}


def _load_blog_manager() -> Any | None:
    try:
        import importlib.util
        blog_manager_path = BLOG_RESOURCES / "blog-manager.py"
        if not blog_manager_path.exists():
            return None
        spec = importlib.util.spec_from_file_location("blog_manager", blog_manager_path)
        blog_manager_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(blog_manager_module)
        return blog_manager_module.BlogManager(str(ROOT / "blog"))
    except Exception as e:
        print(f"Warning: Unable to load BlogManager: {e}")
        return None


def _generate_document_html_fallback(metadata: dict, html_body: str, slug_value: str) -> bool:
    """Generate document HTML without BlogManager (no markdown dependency)."""
    template_path = ROOT / "admin" / "resources" / "documents" / "document-template.html"
    posts_dir = ROOT / "documents" / "posts"
    try:
        if not template_path.exists():
            print(f"Warning: Document template not found: {template_path}")
            return False
        posts_dir.mkdir(exist_ok=True)
        template = template_path.read_text(encoding="utf-8")

        title_text = metadata.get("title", "Untitled")
        summary_text = metadata.get("summary") or ""
        category_text = metadata.get("category") or ""
        type_text = metadata.get("type") or ""
        date_text = metadata.get("date") or ""
        updated_text = metadata.get("updated_date") or ""
        author_text = metadata.get("author") or "Bradley R. Clampitt"
        tags_list = metadata.get("tags") or []

        html_file = template.replace("[DOCUMENT_TITLE]", title_text)

        if summary_text:
            html_file = html_file.replace(
                "[DOCUMENT_SUMMARY]",
                f'<div class="bg-blue-50 border-l-4 border-blue-500 rounded-r-lg p-4 lg:p-5"><h3 class="text-sm font-semibold text-gray-600 uppercase tracking-wide mb-2">Summary</h3><p class="text-base lg:text-lg text-gray-700 leading-relaxed">{summary_text}</p></div>',
            )
        else:
            html_file = html_file.replace("[DOCUMENT_SUMMARY]", "")

        if category_text:
            html_file = html_file.replace(
                "[DOCUMENT_CATEGORY]",
                f'<span class="inline-flex items-center px-3 py-1.5 bg-purple-100 text-purple-800 rounded-full text-xs lg:text-sm font-medium"><i class="fas fa-folder mr-2 text-xs"></i>{category_text}</span>',
            )
        else:
            html_file = html_file.replace("[DOCUMENT_CATEGORY]", "")

        if type_text:
            html_file = html_file.replace(
                "[DOCUMENT_TYPE]",
                f'<span class="inline-flex items-center px-3 py-1.5 bg-indigo-100 text-indigo-800 rounded-full text-xs lg:text-sm font-medium"><i class="fas fa-file-alt mr-2 text-xs"></i>{type_text}</span>',
            )
        else:
            html_file = html_file.replace("[DOCUMENT_TYPE]", "")

        if date_text:
            html_file = html_file.replace(
                "[DOCUMENT_DATE]",
                f'<span class="inline-flex items-center px-3 py-1.5 bg-gray-100 text-gray-700 rounded-full text-xs lg:text-sm font-medium"><i class="fas fa-calendar mr-2 text-xs"></i>Posted: {date_text}</span>',
            )
        else:
            html_file = html_file.replace("[DOCUMENT_DATE]", "")

        if updated_text and updated_text != date_text:
            html_file = html_file.replace(
                "[DOCUMENT_UPDATED_DATE]",
                f'<span class="inline-flex items-center px-3 py-1.5 bg-orange-100 text-orange-800 rounded-full text-xs lg:text-sm font-medium"><i class="fas fa-edit mr-2 text-xs"></i>Updated: {updated_text}</span>',
            )
        else:
            html_file = html_file.replace("[DOCUMENT_UPDATED_DATE]", "")

        if author_text:
            html_file = html_file.replace(
                "[DOCUMENT_AUTHOR]",
                f'<span class="inline-flex items-center px-3 py-1.5 bg-green-100 text-green-800 rounded-full text-xs lg:text-sm font-medium"><i class="fas fa-user mr-2 text-xs"></i>{author_text}</span>',
            )
        else:
            html_file = html_file.replace("[DOCUMENT_AUTHOR]", "")

        if tags_list:
            tags_html = '<div class="flex flex-wrap items-center gap-2 w-full mt-4">'
            tags_html += '<span class="text-xs lg:text-sm font-semibold text-gray-600 mr-2"><i class="fas fa-tags mr-1"></i>Tags:</span>'
            tags_html += " ".join(
                f'<span class="px-2.5 py-1 bg-blue-100 text-blue-800 rounded-full text-xs lg:text-sm font-medium hover:bg-blue-200 transition-colors">{tag.strip()}</span>'
                for tag in tags_list if str(tag).strip()
            )
            tags_html += "</div>"
            html_file = html_file.replace("[DOCUMENT_TAGS]", tags_html)
        else:
            html_file = html_file.replace("[DOCUMENT_TAGS]", "")

        formatted_content = f'<div id="document-content" class="space-y-4 lg:space-y-6 leading-relaxed w-full max-w-none">{html_body or ""}</div>'
        content_pattern = r'<div id="document-content" class="[^"]*markdown-content[^"]*">.*?<!-- Content will be dynamically loaded here -->.*?</div>'
        html_file = re.sub(content_pattern, lambda _m: formatted_content, html_file, flags=re.DOTALL)

        output_path = posts_dir / f"{slug_value}.html"
        output_path.write_text(html_file, encoding="utf-8")
        return True
    except Exception as e:
        print(f"Warning: Fallback document generation failed: {e}")
        return False


def _ensure_schema_updates(conn: sqlite3.Connection) -> None:
    # Schema updates for unified database - using namespaced tables
    try:
        cursor = conn.execute("PRAGMA table_info(portfolio_project_features)")
        columns = {row[1] for row in cursor.fetchall()}
        if "icon" not in columns:
            conn.execute("ALTER TABLE portfolio_project_features ADD COLUMN icon TEXT")
            conn.commit()
    except:
        pass  # Table might not exist yet

    try:
        cursor = conn.execute("PRAGMA table_info(portfolio_tech_tags)")
        columns = {row[1] for row in cursor.fetchall()}
        if "icon" not in columns:
            conn.execute("ALTER TABLE portfolio_tech_tags ADD COLUMN icon TEXT")
            conn.commit()
    except:
        pass  # Table might not exist yet

    # Note: sort_order column and project_statuses table removed from unified schema

    # Add status column to blog_posts if it doesn't exist
    try:
        cursor = conn.execute("PRAGMA table_info(blog_posts)")
        columns = {row[1] for row in cursor.fetchall()}
        if "status" not in columns:
            conn.execute("ALTER TABLE blog_posts ADD COLUMN status TEXT DEFAULT 'Published'")
            conn.commit()
    except:
        pass  # Table might not exist yet

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS feature_library (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            label TEXT NOT NULL,
            icon TEXT,
            description TEXT,
            category TEXT
        )
        """
    )
    conn.commit()


def list_portfolio_images() -> List[str]:
    if not PORTFOLIO_MEDIA.exists():
        return []
    paths: List[str] = []
    for path in PORTFOLIO_MEDIA.rglob("*"):
        if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS:
            rel = "/" + str(path.relative_to(ROOT)).replace("\\", "/")
            paths.append(rel)
    return sorted(paths)


def _validate_existing_image(path_value: str) -> str:
    if not path_value:
        raise HTTPException(status_code=400, detail="Image path is required.")
    normalized = path_value.lstrip("/")
    candidate = ROOT / normalized
    if not candidate.exists() or not candidate.is_file():
        raise HTTPException(status_code=400, detail="Image path does not exist.")
    if candidate.suffix.lower() not in IMAGE_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Unsupported image format.")
    rel_url = "/" + str(candidate.relative_to(ROOT)).replace("\\", "/")
    if not rel_url.startswith("/assets/images/portfolio"):
        raise HTTPException(status_code=400, detail="Image must reside inside assets/images/portfolio.")
    return rel_url


async def _validate_image_upload(file: UploadFile, max_size: int = 10 * 1024 * 1024) -> tuple[bytes, str, str | None]:
    """
    Validate an uploaded image file for security.
    
    Returns:
        tuple: (file_content, file_extension, error_message)
        If error_message is not None, the upload is invalid.
    """
    # Maximum file size: 10MB by default
    MAX_FILE_SIZE = max_size
    
    # Validate file was provided
    if not file or not file.filename:
        return (b'', '', "No file provided")
    
    # Validate file extension
    ext = Path(file.filename).suffix.lower()
    if ext not in IMAGE_EXTENSIONS:
        return (b'', '', "Unsupported image format")
    
    # Read file content
    try:
        content = await file.read()
    except Exception:
        return (b'', '', "Error reading file")
    
    # Validate file size
    if len(content) == 0:
        return (b'', '', "File is empty")
    
    if len(content) > MAX_FILE_SIZE:
        return (b'', '', f"File too large (max {MAX_FILE_SIZE // (1024 * 1024)}MB)")
    
    # Validate MIME type
    file_mime_type = file.content_type
    allowed_mime_types = {
        "image/png", "image/jpeg", "image/jpg", "image/gif", 
        "image/webp", "image/svg+xml"
    }
    
    # Check MIME type from content-type header
    if file_mime_type and file_mime_type not in allowed_mime_types:
        return (b'', '', "Invalid file type")
    
    # Additional validation: Check file signature (magic bytes)
    file_signature = content[:12]  # Check first 12 bytes
    signature_match = False
    
    # Check JPEG
    if file_signature[:3] == b'\xff\xd8\xff':
        signature_match = ext in ['.jpg', '.jpeg']
    # Check PNG
    elif file_signature[:8] == b'\x89PNG\r\n\x1a\n':
        signature_match = ext == '.png'
    # Check GIF
    elif file_signature[:6] in [b'GIF87a', b'GIF89a']:
        signature_match = ext == '.gif'
    # Check WEBP (RIFF...WEBP)
    elif file_signature[:4] == b'RIFF' and b'WEBP' in content[:20]:
        signature_match = ext == '.webp'
    # Check SVG (text-based, check for SVG tag or XML declaration)
    elif ext == '.svg':
        content_str = content[:200].decode('utf-8', errors='ignore').lower()
        signature_match = '<svg' in content_str or '<?xml' in content_str
    
    if not signature_match:
        return (b'', '', "File content does not match file type")
    
    # Additional security: Validate filename doesn't contain path traversal
    filename = Path(file.filename).name  # Get just the filename, no path
    if '..' in filename or '/' in filename or '\\' in filename:
        return (b'', '', "Invalid filename")
    
    return (content, ext, None)


def _ensure_list(value: Iterable[str] | str | None) -> List[str]:
    if value is None:
        return []
    if isinstance(value, (list, tuple)):
        return ["" if v is None else str(v) for v in value]
    return ["" if value is None else str(value)]


app = FastAPI(title="Site Admin Console")

# Add CORS middleware to allow frontend to access API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add request logging middleware - log ALL POST requests
@app.middleware("http")
async def log_requests(request: Request, call_next):
    try:
        if request.method == "POST" and request.url.path == "/admin/documents/save":
            import sys
            print(f"POST REQUEST TO /admin/documents/save", file=sys.stderr)
            sys.stderr.flush()
    except Exception:
        pass  # Don't break the request if logging fails
    response = await call_next(request)
    return response
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# Static file mounts
# Static HTML output files are at root level (blog/, documents/) for GitHub Pages
# These mounts serve the static HTML files directly
app.mount("/admin/static", StaticFiles(directory=str(STATIC_DIR)), name="admin-static")
app.mount("/admin/database", StaticFiles(directory=str(DATABASE_PATH.parent)), name="admin-database")
app.mount("/assets", StaticFiles(directory=str(ROOT / "assets")), name="public-assets")
app.mount("/portfolios", StaticFiles(directory=str(PORTFOLIOS_RESOURCES)), name="public-portfolios")
app.mount("/documents", StaticFiles(directory=str(ROOT / "documents")), name="public-documents")
app.mount("/docs", StaticFiles(directory=str(ROOT / "docs")), name="public-docs")
app.mount("/blog", StaticFiles(directory=str(ROOT / "blog")), name="public-blog")


@app.get("/favicon.ico")
def favicon() -> FileResponse:
    """Serve favicon.ico to prevent 404 errors"""
    # Try to find favicon in static directory, or return a 204 No Content
    favicon_path = STATIC_DIR / "favicon.ico"
    if favicon_path.exists():
        return FileResponse(favicon_path, media_type="image/x-icon")
    # Return empty response to prevent 404
    from fastapi.responses import Response
    return Response(status_code=204)


@app.get("/admin/documents/media/images/{filename:path}")
def admin_documents_media_images(filename: str) -> FileResponse:
    """Serve images from admin/documents/media/images directory"""
    image_path = ROOT / "admin" / "documents" / "media" / "images" / filename
    if image_path.exists() and image_path.is_file():
        return FileResponse(image_path, media_type="image/png")
    raise HTTPException(status_code=404, detail="Image not found")


@app.on_event("startup")
def startup_event() -> None:
    """Initialize unified database on startup"""
    ensure_database()
    # All section databases now handled by unified database
    # No need to call individual ensure_*_database() functions


@app.get("/resume.html")
def resume_page() -> FileResponse:
    """Serve the resume page"""
    resume_path = ROOT / "resume.html"
    if not resume_path.exists():
        raise HTTPException(status_code=404, detail="Resume page not found")
    return FileResponse(resume_path, media_type="text/html")


@app.get("/experience.html")
def experience_page() -> FileResponse:
    """Serve the experience page"""
    experience_path = ROOT / "experience.html"
    if not experience_path.exists():
        raise HTTPException(status_code=404, detail="Experience page not found")
    return FileResponse(experience_path, media_type="text/html")


@app.get("/open-to-opportunities.html")
def open_to_opportunities_page() -> FileResponse:
    """Serve the Open to Opportunities page"""
    page_path = ROOT / "open-to-opportunities.html"
    if not page_path.exists():
        raise HTTPException(status_code=404, detail="Open to Opportunities page not found")
    return FileResponse(page_path, media_type="text/html")


@app.get("/admin")
def dashboard(request: Request) -> Any:
    with get_conn() as conn:
        clients_count = conn.execute("SELECT COUNT(*) FROM portfolio_clients").fetchone()[0]
        projects_count = conn.execute("SELECT COUNT(*) FROM portfolio_projects").fetchone()[0]
        tab_breakdown = conn.execute(
            """
            SELECT t.label, t.code, COUNT(pt.project_id) as total
            FROM portfolio_tabs t
            LEFT JOIN portfolio_project_tabs pt ON pt.tab_id = t.id
            GROUP BY t.id
            ORDER BY t.sort, t.label
            """
        ).fetchall()
        client_activity = conn.execute(
            """
            SELECT c.name, COUNT(p.id) AS projects_total
            FROM portfolio_clients c
            LEFT JOIN portfolio_projects p ON p.client_id = c.id
            GROUP BY c.id
            ORDER BY projects_total DESC, c.name COLLATE NOCASE
            LIMIT 6
            """
        ).fetchall()
        latest_projects = conn.execute(
            """
            SELECT p.id, p.title, p.slug, p.client_id, p.launched_date, p.updated_at, p.extra,
                   c.name AS client_name
            FROM portfolio_projects p
            LEFT JOIN portfolio_clients c ON c.id = p.client_id
            ORDER BY COALESCE(p.updated_at, p.launched_date, p.posted_at) DESC, p.id DESC
            LIMIT 6
            """
        ).fetchall()

    status_counts: dict[str, int] = {}
    parsed_projects: list[dict[str, Any]] = []
    for row in latest_projects:
        extra_data: dict[str, Any] = {}
        if row["extra"]:
            try:
                extra_data = json.loads(row["extra"])
            except json.JSONDecodeError:
                extra_data = {}
        status_label = extra_data.get("status", "").strip()
        if status_label:
            status_counts[status_label] = status_counts.get(status_label, 0) + 1
        parsed_projects.append(
            {
                "id": row["id"],
                "title": row["title"],
                "client": row["client_name"],
                "launched_date": row["launched_date"],
                "updated_at": row["updated_at"],
                "status": status_label,
                "slug": row["slug"],
            }
        )

    # Documents stats
    documents_count = 0
    doc_categories_count = 0
    doc_types_count = 0
    latest_documents = []
    try:
        with get_conn() as doc_conn:
            documents_count = doc_conn.execute("SELECT COUNT(*) FROM documents").fetchone()[0]
            doc_categories_count = doc_conn.execute("SELECT COUNT(*) FROM doc_categories").fetchone()[0]
            doc_types_count = doc_conn.execute("SELECT COUNT(*) FROM doc_types").fetchone()[0]
            latest_docs_rows = doc_conn.execute("""
                SELECT d.id, d.title, d.slug, d.updated_at, c.label AS category_label
                FROM documents d
                LEFT JOIN doc_categories c ON c.id = d.category_id
                ORDER BY COALESCE(d.updated_at, d.posted_at) DESC, d.id DESC
                LIMIT 6
            """).fetchall()
            latest_documents = [
                {
                    "id": row["id"],
                    "title": row["title"],
                    "slug": row["slug"],
                    "updated_at": row["updated_at"],
                    "category": row["category_label"],
                }
                for row in latest_docs_rows
            ]
    except Exception:
        pass

    # Tech Skills stats
    tech_skills_count = 0
    tech_skill_categories_count = 0
    try:
        with get_conn() as tech_conn:
            tech_skills_count = tech_conn.execute("SELECT COUNT(*) FROM tech_skills").fetchone()[0]
            tech_skill_categories_count = tech_conn.execute("SELECT COUNT(*) FROM tech_skill_categories").fetchone()[0]
    except Exception:
        pass

    # Experience stats
    job_experiences_count = 0
    companies_count = 0
    skills_sets_count = 0
    tools_count = 0
    soft_skills_count = 0
    education_count = 0
    try:
        with get_conn() as exp_conn:
            job_experiences_count = exp_conn.execute("SELECT COUNT(*) FROM experience_job_experiences").fetchone()[0]
            companies_count = exp_conn.execute("SELECT COUNT(*) FROM experience_companies").fetchone()[0]
            skills_sets_count = exp_conn.execute("SELECT COUNT(*) FROM experience_skills_sets").fetchone()[0]
            tools_count = exp_conn.execute("SELECT COUNT(*) FROM experience_tools").fetchone()[0]
            soft_skills_count = exp_conn.execute("SELECT COUNT(*) FROM experience_soft_skills").fetchone()[0]
            education_count = exp_conn.execute("SELECT COUNT(*) FROM experience_education").fetchone()[0]
    except Exception:
        pass

    # Blog stats
    blog_posts_count = 0
    blog_categories_count = 0
    blog_featured_count = 0
    latest_blog_posts = []
    try:
        with get_conn() as blog_conn:
            blog_posts_count = blog_conn.execute("SELECT COUNT(*) FROM blog_posts").fetchone()[0]
            blog_categories_count = blog_conn.execute("SELECT COUNT(*) FROM blog_categories").fetchone()[0]
            blog_featured_count = blog_conn.execute("SELECT COUNT(*) FROM blog_posts WHERE featured = 1").fetchone()[0]
            latest_blog_rows = blog_conn.execute("""
                SELECT p.id, p.title, p.slug, p.date, p.updated_at, p.status, c.label AS category_label
                FROM blog_posts p
                LEFT JOIN blog_categories c ON c.id = p.category_id
                ORDER BY COALESCE(p.updated_at, p.date) DESC, p.id DESC
                LIMIT 6
            """).fetchall()
            latest_blog_posts = [
                {
                    "id": row["id"],
                    "title": row["title"],
                    "slug": row["slug"],
                    "date": row["date"],
                    "updated_at": row["updated_at"],
                    "status": row["status"],
                    "category": row["category_label"],
                }
                for row in latest_blog_rows
            ]
    except Exception:
        pass

    # Side Projects stats
    side_projects_count = 0
    side_project_categories_count = 0
    latest_side_projects = []
    try:
        with get_conn() as sp_conn:
            side_projects_count = sp_conn.execute("SELECT COUNT(*) FROM side_projects").fetchone()[0]
            side_project_categories_count = sp_conn.execute("SELECT COUNT(*) FROM side_project_categories").fetchone()[0]
            latest_sp_rows = sp_conn.execute("""
                SELECT p.id, p.title, p.slug, p.status, p.posted_date, p.revised_date, c.label AS category_label
                FROM side_projects p
                LEFT JOIN side_project_categories c ON c.id = p.category_id
                ORDER BY COALESCE(p.revised_date, p.posted_date, p.updated_at) DESC, p.id DESC
                LIMIT 6
            """).fetchall()
            latest_side_projects = [
                {
                    "id": row["id"],
                    "title": row["title"],
                    "slug": row["slug"],
                    "status": row["status"],
                    "posted_date": row["posted_date"],
                    "revised_date": row["revised_date"],
                    "category": row["category_label"],
                }
                for row in latest_sp_rows
            ]
    except Exception:
        pass

    # Magento stats
    magento_modules_count = 0
    magento_categories_count = 0
    latest_magento_modules = []
    try:
        with get_conn() as mag_conn:
            magento_modules_count = mag_conn.execute("SELECT COUNT(*) FROM magento_modules").fetchone()[0]
            magento_categories_count = mag_conn.execute("SELECT COUNT(*) FROM magento_module_categories").fetchone()[0]
            latest_mag_rows = mag_conn.execute("""
                SELECT m.id, m.title, m.slug, m.status, m.posted_date, m.revised_date, c.label AS category_label
                FROM magento_modules m
                LEFT JOIN magento_module_categories c ON c.id = m.category_id
                ORDER BY COALESCE(m.revised_date, m.posted_date, m.updated_at) DESC, m.id DESC
                LIMIT 6
            """).fetchall()
            latest_magento_modules = [
                {
                    "id": row["id"],
                    "title": row["title"],
                    "slug": row["slug"],
                    "status": row["status"],
                    "posted_date": row["posted_date"],
                    "revised_date": row["revised_date"],
                    "category": row["category_label"],
                }
                for row in latest_mag_rows
            ]
    except Exception:
        pass

    # Photography stats
    photography_count = 0
    photography_categories_count = 0
    latest_photography = []
    try:
        with get_conn() as photo_conn:
            photography_count = photo_conn.execute("SELECT COUNT(*) FROM photography").fetchone()[0]
            photography_categories_count = photo_conn.execute("SELECT COUNT(*) FROM photography_categories").fetchone()[0]
            latest_photo_rows = photo_conn.execute("""
                SELECT p.id, p.photo_name, p.location, p.year, c.label AS category_label, p.created_at, p.updated_at
                FROM photography p
                LEFT JOIN photography_categories c ON c.id = p.category_id
                ORDER BY COALESCE(p.updated_at, p.created_at) DESC, p.id DESC
                LIMIT 6
            """).fetchall()
            latest_photography = [
                {
                    "id": row["id"],
                    "photo_name": row["photo_name"],
                    "location": row["location"],
                    "year": row["year"],
                    "category": row["category_label"],
                    "updated_at": row["updated_at"],
                }
                for row in latest_photo_rows
            ]
    except Exception:
        pass

    # References stats
    references_count = 0
    latest_references = []
    try:
        with get_conn() as ref_conn:
            references_count = ref_conn.execute("SELECT COUNT(*) FROM ref_entries").fetchone()[0]
            latest_ref_rows = ref_conn.execute("""
                SELECT id, person_name, company, title, created_at, updated_at
                FROM ref_entries
                ORDER BY COALESCE(updated_at, created_at) DESC, id DESC
                LIMIT 6
            """).fetchall()
            latest_references = [
                {
                    "id": row["id"],
                    "person_name": row["person_name"],
                    "company": row["company"],
                    "title": row["title"],
                    "updated_at": row["updated_at"],
                }
                for row in latest_ref_rows
            ]
    except Exception:
        pass

    # CMS stats
    cms_blocks_count = 0
    cms_blocks_active_count = 0
    cms_settings_count = 0
    cms_contact_count = 0
    cms_block_edit_ids: dict[str, int] = {}
    try:
        with get_conn() as cms_conn:
            cms_blocks_count = cms_conn.execute("SELECT COUNT(*) FROM cms_blocks").fetchone()[0]
            cms_blocks_active_count = cms_conn.execute("SELECT COUNT(*) FROM cms_blocks WHERE is_active = 1").fetchone()[0]
            cms_settings_count = cms_conn.execute("SELECT COUNT(*) FROM cms_site_settings").fetchone()[0]
            cms_contact_count = cms_conn.execute("SELECT COUNT(*) FROM cms_contact_info").fetchone()[0]
            for slug in ("about-me", "availability"):
                row = cms_conn.execute(
                    "SELECT id FROM cms_blocks WHERE block_id = ?", (slug,)
                ).fetchone()
                if row:
                    cms_block_edit_ids[slug] = row["id"]
    except Exception:
        pass

    context = {
        "request": request,
        "clients_count": clients_count,
        "projects_count": projects_count,
        "tab_breakdown": tab_breakdown,
        "client_activity": client_activity,
        "latest_projects": parsed_projects,
        "status_counts": status_counts,
        "documents_count": documents_count,
        "doc_categories_count": doc_categories_count,
        "doc_types_count": doc_types_count,
        "latest_documents": latest_documents,
        "tech_skills_count": tech_skills_count,
        "tech_skill_categories_count": tech_skill_categories_count,
        "job_experiences_count": job_experiences_count,
        "companies_count": companies_count,
        "skills_sets_count": skills_sets_count,
        "tools_count": tools_count,
        "soft_skills_count": soft_skills_count,
        "education_count": education_count,
        "blog_posts_count": blog_posts_count,
        "blog_categories_count": blog_categories_count,
        "blog_featured_count": blog_featured_count,
        "latest_blog_posts": latest_blog_posts,
        "side_projects_count": side_projects_count,
        "side_project_categories_count": side_project_categories_count,
        "latest_side_projects": latest_side_projects,
        "magento_modules_count": magento_modules_count,
        "magento_categories_count": magento_categories_count,
        "latest_magento_modules": latest_magento_modules,
        "photography_count": photography_count,
        "photography_categories_count": photography_categories_count,
        "latest_photography": latest_photography,
        "references_count": references_count,
        "latest_references": latest_references,
        "cms_blocks_count": cms_blocks_count,
        "cms_blocks_active_count": cms_blocks_active_count,
        "cms_settings_count": cms_settings_count,
        "cms_contact_count": cms_contact_count,
        "cms_block_edit_ids": cms_block_edit_ids,
    }
    return templates.TemplateResponse(request, "dashboard.html", context)


@app.get("/admin/clients")
def clients_list(request: Request) -> Any:
    with get_conn() as conn:
        clients = conn.execute(
            """
            SELECT c.id, c.name, c.website, c.logo_url, c.blurb,
                   COUNT(p.id) AS project_total
            FROM portfolio_clients c
            LEFT JOIN portfolio_projects p ON p.client_id = c.id
            GROUP BY c.id
            ORDER BY c.name COLLATE NOCASE
            """
        ).fetchall()
    clients_payload = [
        {
            "id": row["id"],
            "name": row["name"],
            "website": row["website"] or "",
            "logo_url": row["logo_url"] or "",
            "blurb": row["blurb"] or "",
            "project_total": row["project_total"],
        }
        for row in clients
    ]
    return templates.TemplateResponse(request, "clients_list.html",
        {
            "request": request,
            "clients": clients,
            "clients_payload": clients_payload,
        },
    )


@app.get("/admin/clients/images/browse")
def clients_images_browse() -> JSONResponse:
    """API endpoint to browse existing client logo images."""
    images = list_logo_images()
    return JSONResponse(content={"images": images})


@app.post("/admin/clients/new")
async def create_client(
    request: Request,
    name: str = Form(...),
    website: str | None = Form(None),
    logo_url: str | None = Form(None),
    blurb: str | None = Form(None),
) -> RedirectResponse:
    if not name.strip():
        raise HTTPException(status_code=400, detail="Client name is required.")
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO portfolio_clients (name, website, logo_url, blurb) VALUES (?, ?, ?, ?)",
            (name.strip(), website or None, logo_url or None, blurb or None),
        )
        conn.commit()
    return RedirectResponse(url=request.url_for("clients_list"), status_code=303)


@app.get("/admin/features")
def feature_library_list(request: Request) -> Any:
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT id, label, icon, description, category
            FROM feature_library
            ORDER BY COALESCE(category, ''), label COLLATE NOCASE
            """
        ).fetchall()
    features = [
        {
            "id": row["id"],
            "label": row["label"],
            "icon": row["icon"] or "",
            "description": row["description"] or "",
            "category": row["category"] or "",
        }
        for row in rows
    ]
    return templates.TemplateResponse(request, "feature_library.html",
        {
            "request": request,
            "features": rows,
            "features_payload": features,
        },
    )


@app.post("/admin/features/new")
async def feature_library_create(
    request: Request,
    label: str = Form(...),
    icon: str | None = Form(None),
    description: str | None = Form(None),
    category: str | None = Form(None),
) -> RedirectResponse:
    if not label.strip():
        raise HTTPException(status_code=400, detail="Feature label is required.")
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO feature_library (label, icon, description, category) VALUES (?, ?, ?, ?)",
            (
                label.strip(),
                icon.strip() if icon else None,
                description.strip() if description else None,
                category.strip() if category else None,
            ),
        )
        conn.commit()
    return RedirectResponse(url=request.url_for("feature_library_list"), status_code=303)


@app.post("/admin/features/update")
async def feature_library_update(
    request: Request,
    feature_id: str = Form(...),
    label: str = Form(...),
    icon: str | None = Form(None),
    description: str | None = Form(None),
    category: str | None = Form(None),
) -> RedirectResponse:
    pk = _optional_int(feature_id)
    if pk is None:
        raise HTTPException(status_code=400, detail="Invalid feature id.")
    if not label.strip():
        raise HTTPException(status_code=400, detail="Feature label is required.")
    with get_conn() as conn:
        conn.execute(
            """
            UPDATE feature_library
            SET label = ?, icon = ?, description = ?, category = ?
            WHERE id = ?
            """,
            (
                label.strip(),
                icon.strip() if icon else None,
                description.strip() if description else None,
                category.strip() if category else None,
                pk,
            ),
        )
        conn.commit()
    return RedirectResponse(url=request.url_for("feature_library_list"), status_code=303)


@app.post("/admin/features/delete")
async def feature_library_delete(
    request: Request,
    feature_id: str = Form(...),
) -> RedirectResponse:
    pk = _optional_int(feature_id)
    if pk is None:
        raise HTTPException(status_code=400, detail="Invalid feature id.")
    with get_conn() as conn:
        conn.execute("DELETE FROM feature_library WHERE id = ?", (pk,))
        conn.commit()
    return RedirectResponse(url=request.url_for("feature_library_list"), status_code=303)


@app.get("/admin/clients/{client_id}")
def client_edit_view(request: Request, client_id: int) -> Any:
    with get_conn() as conn:
        client = conn.execute(
            "SELECT id, name, website, logo_url, blurb FROM portfolio_clients WHERE id = ?", (client_id,)
        ).fetchone()
        if not client:
            raise HTTPException(status_code=404, detail="Client not found.")
    return templates.TemplateResponse(request, "client_edit.html",
        {"request": request, "client": client},
    )


@app.post("/admin/clients/update")
async def client_update(
    request: Request,
    client_id: str = Form(...),
    name: str = Form(...),
    website: str | None = Form(None),
    logo_url: str | None = Form(None),
    blurb: str | None = Form(None),
) -> RedirectResponse:
    pk = _optional_int(client_id)
    if pk is None:
        raise HTTPException(status_code=400, detail="Invalid client id.")
    if not name.strip():
        raise HTTPException(status_code=400, detail="Client name is required.")
    with get_conn() as conn:
        conn.execute(
            "UPDATE portfolio_clients SET name = ?, website = ?, logo_url = ?, blurb = ? WHERE id = ?",
            (name.strip(), website or None, logo_url or None, blurb or None, pk),
        )
        conn.commit()
    return RedirectResponse(url=request.url_for("clients_list"), status_code=303)


@app.post("/admin/clients/delete")
async def client_delete(
    request: Request,
    client_id: str = Form(...),
) -> RedirectResponse:
    pk = _optional_int(client_id)
    if pk is None:
        raise HTTPException(status_code=400, detail="Invalid client id.")
    with get_conn() as conn:
        has_projects = conn.execute(
            "SELECT COUNT(*) FROM portfolio_projects WHERE client_id = ?", (pk,)
        ).fetchone()[0]
        if has_projects:
            raise HTTPException(
                status_code=400, detail="Cannot delete client while projects are assigned."
            )
        conn.execute("DELETE FROM portfolio_clients WHERE id = ?", (pk,))
        conn.commit()
    return RedirectResponse(url=request.url_for("clients_list"), status_code=303)


@app.get("/admin/project-types")
def project_types_list(request: Request) -> Any:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT id, code, label FROM portfolio_project_types ORDER BY label COLLATE NOCASE"
        ).fetchall()
    types = [
        {"id": row["id"], "code": row["code"], "label": row["label"]}
        for row in rows
    ]
    return templates.TemplateResponse(request, "project_types.html",
        {
            "request": request,
            "types": rows,
            "types_payload": types,
        },
    )


@app.post("/admin/project-types/new")
async def create_project_type(
    request: Request,
    code: str = Form(...),
    label: str = Form(...),
) -> RedirectResponse:
    if not code.strip() or not label.strip():
        raise HTTPException(status_code=400, detail="Both code and label are required.")
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO portfolio_project_types (code, label) VALUES (?, ?)",
            (code.strip().lower(), label.strip()),
        )
        conn.commit()
    return RedirectResponse(url=request.url_for("project_types_list"), status_code=303)


@app.post("/admin/project-types/update")
async def update_project_type(
    request: Request,
    type_id: str = Form(...),
    code: str = Form(...),
    label: str = Form(...),
) -> RedirectResponse:
    pk = _optional_int(type_id)
    if pk is None:
        raise HTTPException(status_code=400, detail="Invalid project type id.")
    if not code.strip() or not label.strip():
        raise HTTPException(status_code=400, detail="Both code and label are required.")
    with get_conn() as conn:
        conn.execute(
            "UPDATE portfolio_project_types SET code = ?, label = ? WHERE id = ?",
            (code.strip().lower(), label.strip(), pk),
        )
        conn.commit()
    return RedirectResponse(url=request.url_for("project_types_list"), status_code=303)


@app.post("/admin/project-types/delete")
async def delete_project_type(
    request: Request,
    type_id: str = Form(...),
) -> RedirectResponse:
    pk = _optional_int(type_id)
    if pk is None:
        raise HTTPException(status_code=400, detail="Invalid project type id.")
    with get_conn() as conn:
        assigned = conn.execute(
            "SELECT COUNT(*) FROM portfolio_projects WHERE type_id = ?",
            (pk,),
        ).fetchone()[0]
        if assigned:
            raise HTTPException(
                status_code=400,
                detail="Cannot delete a project type that is assigned to existing projects.",
            )
        conn.execute("DELETE FROM portfolio_project_types WHERE id = ?", (pk,))
        conn.commit()
    return RedirectResponse(url=request.url_for("project_types_list"), status_code=303)


@app.get("/admin/tech-tags")
def tech_tags_list(request: Request) -> Any:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT id, code, label, icon, category FROM portfolio_tech_tags ORDER BY category COLLATE NOCASE, label COLLATE NOCASE"
        ).fetchall()
    tags = [
        {
            "id": row["id"],
            "code": row["code"],
            "label": row["label"],
            "icon": row["icon"] or "",
            "category": row["category"] or "",
        }
        for row in rows
    ]
    return templates.TemplateResponse(request, "tech_tags.html",
        {"request": request, "tags": tags},
    )


@app.post("/admin/tech-tags/new")
async def create_tech_tag(
    request: Request,
    code: str = Form(...),
    label: str = Form(...),
    icon: str | None = Form(None),
    category: str | None = Form(None),
) -> RedirectResponse:
    if not code.strip() or not label.strip():
        raise HTTPException(status_code=400, detail="Both code and label are required.")
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO portfolio_tech_tags (code, label, icon, category) VALUES (?, ?, ?, ?)",
            (
                code.strip().lower(),
                label.strip(),
                icon.strip() if icon else None,
                category.strip() if category else None,
            ),
        )
        conn.commit()
    return RedirectResponse(url=request.url_for("tech_tags_list"), status_code=303)


@app.post("/admin/tech-tags/update")
async def update_tech_tag(
    request: Request,
    tag_id: str = Form(...),
    code: str = Form(...),
    label: str = Form(...),
    icon: str | None = Form(None),
    category: str | None = Form(None),
) -> RedirectResponse:
    pk = _optional_int(tag_id)
    if pk is None:
        raise HTTPException(status_code=400, detail="Invalid tech tag id.")
    if not code.strip() or not label.strip():
        raise HTTPException(status_code=400, detail="Both code and label are required.")
    with get_conn() as conn:
        conn.execute(
            "UPDATE portfolio_tech_tags SET code = ?, label = ?, icon = ?, category = ? WHERE id = ?",
            (
                code.strip().lower(),
                label.strip(),
                icon.strip() if icon else None,
                category.strip() if category else None,
                pk,
            ),
        )
        conn.commit()
    return RedirectResponse(url=request.url_for("tech_tags_list"), status_code=303)


@app.post("/admin/tech-tags/delete")
async def delete_tech_tag(
    request: Request,
    tag_id: str = Form(...),
) -> RedirectResponse:
    pk = _optional_int(tag_id)
    if pk is None:
        raise HTTPException(status_code=400, detail="Invalid tech tag id.")
    with get_conn() as conn:
        conn.execute("DELETE FROM portfolio_tech_tags WHERE id = ?", (pk,))
        conn.commit()
    return RedirectResponse(url=request.url_for("tech_tags_list"), status_code=303)


def fetch_projects_with_meta(conn: sqlite3.Connection) -> List[sqlite3.Row]:
    query = """
        SELECT
            p.id,
            p.title,
            p.slug,
            p.summary,
            p.tags,
            p.extra,
            p.launched_date,
            p.in_use_start,
            p.in_use_end,
            p.updated_at,
            COALESCE(c.name, '') AS client_name,
            GROUP_CONCAT(DISTINCT t.label) AS tab_labels,
            GROUP_CONCAT(DISTINCT t.code) AS tab_codes
        FROM portfolio_projects p
        LEFT JOIN portfolio_clients c ON c.id = p.client_id
        LEFT JOIN portfolio_project_tabs pt ON pt.project_id = p.id
        LEFT JOIN portfolio_tabs t ON t.id = pt.tab_id
        GROUP BY p.id
        ORDER BY CASE WHEN p.launched_date IS NULL THEN 1 ELSE 0 END,
                 p.launched_date DESC,
                 p.id DESC
    """
    return conn.execute(query).fetchall()


@app.get("/admin/projects")
def projects_list(request: Request) -> Any:
    with get_conn() as conn:
        projects = fetch_projects_with_meta(conn)
        tab_rows = conn.execute(
            "SELECT id, code, label FROM portfolio_tabs ORDER BY sort, label"
        ).fetchall()
    project_payload = []
    status_set: set[str] = set()
    for row in projects:
        extra_data: dict[str, Any] = {}
        if row["extra"]:
            try:
                extra_data = json.loads(row["extra"])
            except json.JSONDecodeError:
                extra_data = {}
        status_value = extra_data.get("status", "")
        if status_value:
            status_set.add(status_value)
        project_payload.append(
            {
                "id": row["id"],
                "title": row["title"],
                "slug": row["slug"],
                "summary": row["summary"] or "",
                "tags": row["tags"] or "",
                "launched_date": row["launched_date"],
                "updated_at": row["updated_at"],
                "in_use_start": row["in_use_start"],
                "in_use_end": row["in_use_end"],
                "client_name": row["client_name"],
                "tab_labels": (row["tab_labels"] or "").split(",") if row["tab_labels"] else [],
                "tab_codes": (row["tab_codes"] or "").split(",") if row["tab_codes"] else [],
                "status": status_value,
            }
        )
    tabs_payload = [
        {"id": row["id"], "code": row["code"], "label": row["label"]}
        for row in tab_rows
    ]
    return templates.TemplateResponse(request, "projects_list.html",
        {
            "request": request,
            "projects": projects,
            "project_payload": project_payload,
            "tabs_payload": tabs_payload,
            "status_options": sorted(status_set),
        },
    )


def fetch_project_form_data(
    conn: sqlite3.Connection, project_id: int | None
) -> Tuple[
    Any,
    List[sqlite3.Row],
    List[sqlite3.Row],
    List[int],
    List[sqlite3.Row],
    List[int],
    List[sqlite3.Row],
    List[sqlite3.Row],
]:
    project = None
    selected_tabs: List[int] = []
    features: List[sqlite3.Row] = []
    selected_tech: List[int] = []
    images: List[sqlite3.Row] = []

    if project_id is not None:
        project = conn.execute("SELECT * FROM portfolio_projects WHERE id = ?", (project_id,)).fetchone()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found.")
        selected_tabs = [
            row[0]
            for row in conn.execute("SELECT tab_id FROM portfolio_project_tabs WHERE project_id = ?", (project_id,))
        ]
        selected_tech = [
            row[0]
            for row in conn.execute(
                "SELECT tag_id FROM portfolio_project_tech_tags WHERE project_id = ?", (project_id,)
            )
        ]
        images = conn.execute(
            "SELECT id, url, alt, is_cover, sort FROM portfolio_project_images WHERE project_id = ? ORDER BY sort, id",
            (project_id,),
        ).fetchall()
        features = conn.execute(
            "SELECT id, label, icon, description, sort FROM portfolio_project_features WHERE project_id = ? ORDER BY sort, id",
            (project_id,),
        ).fetchall()
    else:
        features = []

    clients = conn.execute("SELECT id, name FROM portfolio_clients ORDER BY name COLLATE NOCASE").fetchall()
    project_types = conn.execute(
        "SELECT id, code, label FROM portfolio_project_types ORDER BY label COLLATE NOCASE"
    ).fetchall()
    tabs = conn.execute(
        "SELECT id, code, label FROM portfolio_tabs ORDER BY sort, label COLLATE NOCASE"
    ).fetchall()
    tech_tags = conn.execute(
        "SELECT id, code, label, category FROM portfolio_tech_tags ORDER BY category COLLATE NOCASE, label COLLATE NOCASE"
    ).fetchall()
    return (
        project,
        clients,
        project_types,
        selected_tabs,
        tabs,
        selected_tech,
        tech_tags,
        images,
        features,
)


@app.get("/admin/projects/new")
def project_new(request: Request) -> Any:
    with get_conn() as conn:
        (
            project,
            clients,
            project_types,
            selected_tabs,
            tabs,
            selected_tech,
            tech_tags,
            images,
            features,
        ) = fetch_project_form_data(conn, None)
        status_choices = fetch_status_options(conn)
        feature_library = conn.execute(
            "SELECT id, label, icon, description, category FROM feature_library ORDER BY label COLLATE NOCASE"
        ).fetchall()
        tab_payload = [
            {"id": tab["id"], "label": tab["label"], "code": tab["code"]}
            for tab in tabs
        ]
        tech_payload = [
            {
                "id": tag["id"],
                "label": tag["label"],
                "category": tag["category"],
            }
            for tag in tech_tags
        ]
    extra_data: dict[str, Any] = {}
    context = {
        "request": request,
        "project": project,
        "clients": clients,
        "project_types": project_types,
        "selected_tabs": selected_tabs,
        "tabs": tabs,
        "selected_tech": selected_tech,
        "tech_tags": tech_tags,
        "tabs_payload": tab_payload,
        "tech_payload": tech_payload,
        "features": features,
        "images": images,
        "extra_data": extra_data,
        "badges_str": "",
        "status_options": status_choices,
        "selected_status": "",
        "primary_link": "",
        "primary_link_label": "",
        "available_images": list_portfolio_images(),
        "feature_library": feature_library,
        "mode": "new",
    }
    return templates.TemplateResponse(request, "project_edit.html", context)


@app.get("/admin/projects/{project_id}")
def project_edit(request: Request, project_id: int) -> Any:
    with get_conn() as conn:
        (
            project,
            clients,
            project_types,
            selected_tabs,
            tabs,
            selected_tech,
            tech_tags,
            images,
            features,
        ) = fetch_project_form_data(conn, project_id)
        extra_data: dict[str, Any] = {}
        if project and project["extra"]:
            try:
                extra_data = json.loads(project["extra"])
            except json.JSONDecodeError:
                extra_data = {}
        status_choices = fetch_status_options(conn)
        feature_library = conn.execute(
            "SELECT id, label, icon, description, category FROM feature_library ORDER BY label COLLATE NOCASE"
        ).fetchall()
        tab_payload = [
            {"id": tab["id"], "label": tab["label"], "code": tab["code"]}
            for tab in tabs
        ]
        tech_payload = [
            {
                "id": tag["id"],
                "label": tag["label"],
                "category": tag["category"],
            }
            for tag in tech_tags
        ]
    badges_str = ", ".join(extra_data.get("badges", [])) if extra_data.get("badges") else ""
    context_status = extra_data.get("status", "")
    context_primary_link = extra_data.get("primary_link", "")
    context_primary_link_label = extra_data.get("primary_link_label", "")
    context = {
        "request": request,
        "project": project,
        "clients": clients,
        "project_types": project_types,
        "selected_tabs": selected_tabs,
        "tabs": tabs,
        "selected_tech": selected_tech,
        "tech_tags": tech_tags,
        "tabs_payload": tab_payload,
        "tech_payload": tech_payload,
        "features": features,
        "images": images,
        "extra_data": extra_data,
        "badges_str": badges_str,
        "status_options": status_choices,
        "selected_status": context_status,
        "primary_link": context_primary_link,
        "primary_link_label": context_primary_link_label,
        "available_images": list_portfolio_images(),
        "feature_library": feature_library,
        "mode": "edit",
    }
    return templates.TemplateResponse(request, "project_edit.html", context)


def _parse_feature_forms(
    labels: Iterable[str],
    descriptions: Iterable[str],
    sorts: Iterable[str],
    icons: Iterable[str],
) -> List[Tuple[str, str | None, int, str | None]]:
    label_list = _ensure_list(labels)
    desc_list = _ensure_list(descriptions)
    sort_list = _ensure_list(sorts)
    icon_list = _ensure_list(icons)

    max_len = max(len(label_list), len(desc_list), len(sort_list), len(icon_list))
    features: List[Tuple[str, str | None, int, str | None]] = []

    for idx in range(max_len):
        label = label_list[idx].strip() if idx < len(label_list) else ""
        if not label:
            continue
        desc = desc_list[idx] if idx < len(desc_list) else ""
        sort_raw = sort_list[idx] if idx < len(sort_list) else ""
        icon = icon_list[idx] if idx < len(icon_list) else ""
        try:
            sort_value = int(sort_raw)
        except (TypeError, ValueError):
            sort_value = 0
        desc_value = desc.strip() or None
        icon_value = icon.strip() or None
        features.append((label, desc_value, sort_value, icon_value))

    return features


def _coerce_json(value: str | None) -> str:
    if not value:
        return "{}"
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=400, detail=f"Invalid JSON payload: {exc}") from exc
    return json.dumps(parsed, ensure_ascii=False)


@app.post("/admin/projects/save")
async def project_save(
    request: Request,
    project_id: str | None = Form(None),
    title: str = Form(...),
    slug: str | None = Form(None),
    client_id: str | None = Form(None),
    type_id: str | None = Form(None),
    summary: str | None = Form(None),
    description_html: str | None = Form(None),
    launched_date: str | None = Form(None),
    posted_at: str | None = Form(None),
    updated_at: str | None = Form(None),
    in_use_start: str | None = Form(None),
    in_use_end: str | None = Form(None),
    tags: str | None = Form(None),
    extra: str | None = Form(None),
    status: str | None = Form(None),
    badges: str | None = Form(None),
    primary_link: str | None = Form(None),
    primary_link_label: str | None = Form(None),
    sort_order: str | None = Form(None),
    tab_ids: List[str] = Form([]),
    feature_labels: List[str] = Form([]),
    feature_descriptions: List[str] = Form([]),
    feature_sorts: List[str] = Form([]),
    feature_icons: List[str] = Form([]),
    tech_tag_ids: List[str] = Form([]),
) -> RedirectResponse:
    if not title.strip():
        raise HTTPException(status_code=400, detail="Title is required.")

    auto_slug = slugify(title) if not slug or not slug.strip() else slugify(slug)
    today_str = date.today().isoformat()

    extra_json = _coerce_json(extra)
    extra_data = json.loads(extra_json)

    status_value = (status or "").strip()
    if status_value:
        extra_data["status"] = status_value
    else:
        extra_data.pop("status", None)

    badge_values = []
    if badges:
        badge_values = [b.strip() for b in re.split(r"[\n,]", badges) if b.strip()]
    if badge_values:
        extra_data["badges"] = badge_values
    else:
        extra_data.pop("badges", None)

    primary_link_value = (primary_link or "").strip()
    primary_label_value = (primary_link_label or "").strip()
    if primary_link_value:
        extra_data["primary_link"] = primary_link_value
        extra_data["primary_link_label"] = primary_label_value or extra_data.get("primary_link_label") or "Visit Website"
    else:
        extra_data.pop("primary_link", None)
        if primary_label_value:
            extra_data["primary_link_label"] = primary_label_value
        else:
            extra_data.pop("primary_link_label", None)

    extra_json = json.dumps(extra_data, ensure_ascii=False)

    tags_clean = None
    if tags:
        tag_tokens = [t.strip() for t in re.split(r"[\n,]", tags) if t.strip()]
        if tag_tokens:
            tags_clean = ", ".join(tag_tokens)
    features = _parse_feature_forms(
        feature_labels, feature_descriptions, feature_sorts, feature_icons
    )

    project_pk = _optional_int(project_id)
    client_fk = _optional_int(client_id)
    type_fk = _optional_int(type_id)
    sort_value = _coerce_int(sort_order or "0")
    selected_tabs = [
        tab_id for tab_id in (_optional_int(value) for value in tab_ids) if tab_id is not None
    ]
    selected_tech = [
        tag_id for tag_id in (_optional_int(value) for value in tech_tag_ids) if tag_id is not None
    ]

    with get_conn() as conn:
        cur = conn.cursor()
        # project_statuses table removed - status stored directly in projects
        # if status_value:
        #     cur.execute(
        #         "INSERT OR IGNORE INTO project_statuses (label) VALUES (?)",
        #         (status_value,),
        #     )
        if project_pk:
            cur.execute(
                """
                UPDATE portfolio_projects
                SET title = ?, slug = ?, client_id = ?, type_id = ?, summary = ?,
                    description_html = ?, launched_date = ?, posted_at = ?,
                    updated_at = ?, in_use_start = ?, in_use_end = ?, tags = ?, extra = ?
                WHERE id = ?
                """,
                (
                    title.strip(),
                    auto_slug,
                    client_fk,
                    type_fk,
                    summary or None,
                    description_html or None,
                    launched_date or None,
                    posted_at or today_str if not posted_at else posted_at,
                    updated_at or today_str,
                    in_use_start or None,
                    in_use_end or None,
                    tags_clean,
                    extra_json,
                    project_pk,
                ),
            )
        else:
            cur.execute(
                """
                INSERT INTO portfolio_projects (
                    title, slug, client_id, type_id, summary, description_html,
                    launched_date, posted_at, updated_at, in_use_start, in_use_end,
                    tags, extra
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    title.strip(),
                    auto_slug,
                    client_fk,
                    type_fk,
                    summary or None,
                    description_html or None,
                    launched_date or None,
                    posted_at or today_str,
                    updated_at or today_str,
                    in_use_start or None,
                    in_use_end or None,
                    tags_clean,
                    extra_json,
                ),
            )
            project_pk = cur.lastrowid

        if project_pk is None:
            raise HTTPException(status_code=500, detail="Failed to persist project.")

        cur.execute("DELETE FROM portfolio_project_tabs WHERE project_id = ?", (project_pk,))
        cur.executemany(
            "INSERT INTO portfolio_project_tabs (project_id, tab_id) VALUES (?, ?)",
            [(project_pk, tab_id) for tab_id in selected_tabs],
        )

        cur.execute("DELETE FROM portfolio_project_features WHERE project_id = ?", (project_pk,))
        cur.executemany(
            "INSERT INTO portfolio_project_features (project_id, label, icon, description, sort) VALUES (?, ?, ?, ?, ?)",
            [(project_pk, label, icon, desc, sort) for label, desc, sort, icon in features],
        )

        cur.execute("DELETE FROM portfolio_project_tech_tags WHERE project_id = ?", (project_pk,))
        cur.executemany(
            "INSERT INTO portfolio_project_tech_tags (project_id, tag_id) VALUES (?, ?)",
            [(project_pk, tag_id) for tag_id in selected_tech],
        )

        conn.commit()

    return RedirectResponse(
        url=request.url_for("projects_list"),
        status_code=303,
    )


@app.post("/admin/images/upload")
async def upload_image(
    request: Request,
    project_id: str = Form(...),
    file: UploadFile = File(...),
    alt: str | None = Form(None),
    sort: str | None = Form(None),
    is_cover: str | None = Form(None),
) -> RedirectResponse:
    project_pk = _optional_int(project_id)
    if project_pk is None:
        return RedirectResponse(
            url=request.url_for("project_edit", project_id=project_id) + "?error=Invalid+project+id",
            status_code=303
        )
    
    # Validate image upload
    content, ext, error_msg = await _validate_image_upload(file)
    if error_msg:
        return RedirectResponse(
            url=request.url_for("project_edit", project_id=project_pk) + f"?error={error_msg.replace(' ', '+')}",
            status_code=303
        )

    project_dir = PORTFOLIO_MEDIA / str(project_pk)
    project_dir.mkdir(parents=True, exist_ok=True)

    # Generate safe filename
    safe_filename = secrets.token_urlsafe(16) + ext
    destination = project_dir / safe_filename
    
    # Ensure we're writing within the intended directory
    try:
        destination.resolve().relative_to(project_dir.resolve())
    except ValueError:
        return RedirectResponse(
            url=request.url_for("project_edit", project_id=project_pk) + "?error=Invalid+file+path",
            status_code=303
        )

    # Write file
    try:
        destination.write_bytes(content)
    except Exception as e:
        import sys
        print(f"Error writing file: {e}", file=sys.stderr)
        return RedirectResponse(
            url=request.url_for("project_edit", project_id=project_pk) + "?error=Error+saving+file",
            status_code=303
        )

    rel_url = "/" + str(destination.relative_to(ROOT)).replace("\\", "/")

    with get_conn() as conn:
        cur = conn.cursor()
        if _as_bool(is_cover):
            cur.execute("UPDATE portfolio_project_images SET is_cover = 0 WHERE project_id = ?", (project_pk,))
        cur.execute(
            """
            INSERT INTO portfolio_project_images (project_id, url, alt, sort, is_cover)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                project_pk,
                rel_url,
                alt or None,
                _coerce_int(sort),
                1 if _as_bool(is_cover) else 0,
            ),
        )
        conn.commit()

    return RedirectResponse(
        url=request.url_for("project_edit", project_id=project_pk) + "?success=Image+uploaded+successfully",
        status_code=303,
    )


@app.post("/admin/images/set-cover")
async def set_cover_image(
    request: Request,
    project_id: str = Form(...),
    image_id: str = Form(...),
) -> RedirectResponse:
    project_pk = _optional_int(project_id)
    image_pk = _optional_int(image_id)
    if project_pk is None or image_pk is None:
        raise HTTPException(status_code=400, detail="Invalid identifiers.")

    with get_conn() as conn:
        cur = conn.cursor()
        row = cur.execute(
            "SELECT id FROM portfolio_project_images WHERE id = ? AND project_id = ?",
            (image_pk, project_pk),
        ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Image not found.")
        cur.execute("UPDATE portfolio_project_images SET is_cover = 0 WHERE project_id = ?", (project_pk,))
        cur.execute(
            "UPDATE portfolio_project_images SET is_cover = 1 WHERE id = ? AND project_id = ?",
            (image_pk, project_pk),
        )
        conn.commit()

    return RedirectResponse(
        url=request.url_for("project_edit", project_id=project_pk),
        status_code=303,
    )


@app.post("/admin/images/delete")
async def delete_image(
    request: Request,
    project_id: str = Form(...),
    image_id: str = Form(...),
) -> RedirectResponse:
    project_pk = _optional_int(project_id)
    image_pk = _optional_int(image_id)
    if project_pk is None or image_pk is None:
        raise HTTPException(status_code=400, detail="Invalid identifiers.")

    with get_conn() as conn:
        cur = conn.cursor()
        row = cur.execute(
            "SELECT url FROM portfolio_project_images WHERE id = ? AND project_id = ?",
            (image_pk, project_pk),
        ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Image not found.")
        cur.execute("DELETE FROM portfolio_project_images WHERE id = ?", (image_pk,))
        conn.commit()

    if row:
        try:
            rel_part = row[0].lstrip("/")
            abs_path = (ROOT / rel_part).resolve()
            project_dir = (PORTFOLIO_MEDIA / str(project_pk)).resolve()
            if abs_path.is_file() and abs_path.is_relative_to(project_dir):
                # Only remove file if no other project references it
                with get_conn() as conn:
                    remaining = conn.execute(
                        "SELECT COUNT(*) FROM portfolio_project_images WHERE url = ?",
                        (row[0],),
                    ).fetchone()[0]
                if remaining == 0:
                    abs_path.unlink(missing_ok=True)
        except Exception:
            pass

    return RedirectResponse(
        url=request.url_for("project_edit", project_id=project_pk),
        status_code=303,
    )


@app.post("/admin/images/add-existing")
async def add_existing_image(
    request: Request,
    project_id: str = Form(...),
    image_path: str = Form(...),
    alt: str | None = Form(None),
    sort: str | None = Form(None),
    is_cover: str | None = Form(None),
) -> RedirectResponse:
    project_pk = _optional_int(project_id)
    if project_pk is None:
        raise HTTPException(status_code=400, detail="Invalid project id.")
    normalized = _validate_existing_image(image_path)

    with get_conn() as conn:
        cur = conn.cursor()
        if _as_bool(is_cover):
            cur.execute("UPDATE portfolio_project_images SET is_cover = 0 WHERE project_id = ?", (project_pk,))
        cur.execute(
            """
            INSERT INTO portfolio_project_images (project_id, url, alt, sort, is_cover)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                project_pk,
                normalized,
                alt or None,
                _coerce_int(sort),
                1 if _as_bool(is_cover) else 0,
            ),
        )
        conn.commit()

    return RedirectResponse(
        url=request.url_for("project_edit", project_id=project_pk),
        status_code=303,
    )
def fetch_status_options(conn: sqlite3.Connection) -> List[str]:
    # project_statuses table removed - using STATUS_DEFAULTS constant instead
    return [label for label in STATUS_DEFAULTS if label.strip()]

# ============================================================================
# Documents System Routes
# ============================================================================

@app.get("/admin/documents")
def documents_list(request: Request) -> Any:
    try:
        with get_conn() as conn:
            documents_rows = conn.execute("""
                SELECT 
                    d.*,
                    c.label AS category_label,
                    t.label AS type_label,
                    GROUP_CONCAT(DISTINCT tab.code) AS tab_codes
                FROM documents d
                    LEFT JOIN doc_categories c ON c.id = d.category_id
                    LEFT JOIN doc_types t ON t.id = d.type_id
                    LEFT JOIN document_tabs dt ON dt.document_id = d.id
                    LEFT JOIN doc_tabs tab ON tab.id = dt.tab_id
                GROUP BY d.id
                ORDER BY d.created_at DESC, d.id DESC
            """).fetchall()
            # Convert Row objects to dictionaries for JSON serialization
            documents = [dict(row) for row in documents_rows]
    except Exception:
        documents = []
    return templates.TemplateResponse(request, "documents_list.html",
        {"request": request, "documents": documents},
    )


@app.post("/admin/documents/regenerate")
def documents_regenerate(request: Request) -> RedirectResponse:
    blog_mgr = BLOG_MANAGER if HAS_BLOG_MANAGER and BLOG_MANAGER else None
    if not blog_mgr:
        blog_mgr = _load_blog_manager()

    regenerated = 0
    with get_conn() as conn:
        rows = conn.execute("""
            SELECT d.id, d.title, d.slug, d.summary, d.posted_at, d.created_at, d.updated_at,
                   d.tags, d.content_html, d.content_markdown, d.content_format,
                   c.label AS category_label,
                   t.label AS type_label
            FROM documents d
                LEFT JOIN doc_categories c ON c.id = d.category_id
                LEFT JOIN doc_types t ON t.id = d.type_id
            WHERE d.status = 'Published'
            ORDER BY d.id
        """).fetchall()

    for row in rows:
        metadata = {
            "title": row["title"],
            "slug": row["slug"],
            "summary": row["summary"],
            "author": "Bradley R. Clampitt",
            "date": row["posted_at"] or row["created_at"] or row["updated_at"] or "",
            "updated_date": row["updated_at"] or "",
            "category": row["category_label"] or "",
            "type": row["type_label"] or "",
            "tags": row["tags"].split(",") if row["tags"] else [],
        }
        html_body = row["content_html"] or ""
        if blog_mgr and row["content_format"] == "markdown" and row["content_markdown"]:
            try:
                html_body = blog_mgr.markdown_to_html(row["content_markdown"])
            except Exception as e:
                print(f"Warning: Failed to reprocess markdown for {row['slug']}: {e}")

        if blog_mgr:
            try:
                success, _output = blog_mgr.generate_document_html_from_db(
                    metadata,
                    html_body,
                    row["slug"],
                    str(ROOT / "documents"),
                )
                if success:
                    regenerated += 1
                else:
                    _generate_document_html_fallback(metadata, html_body, row["slug"])
            except Exception as e:
                print(f"Warning: Failed to regenerate document {row['slug']}: {e}")
                _generate_document_html_fallback(metadata, html_body, row["slug"])
        else:
            if _generate_document_html_fallback(metadata, html_body, row["slug"]):
                regenerated += 1

    return RedirectResponse(url=request.url_for("documents_list"), status_code=303)


@app.get("/admin/documents/categories")
def doc_categories_list(request: Request) -> Any:
    try:
        with get_conn() as conn:
            rows = conn.execute(
                "SELECT * FROM doc_categories ORDER BY sort, label"
            ).fetchall()
            categories = [
                {
                    "id": row["id"],
                    "code": row["code"],
                    "label": row["label"],
                    "description": row["description"] or "",
                    "icon": row["icon"] or "",
                    "sort": row["sort"],
                }
                for row in rows
            ]
    except Exception:
        categories = []
    return templates.TemplateResponse(request, "doc_categories_list.html",
        {"request": request, "categories": categories},
    )


@app.post("/admin/documents/types/new")
def doc_types_new(
    code: str = Form(...),
    label: str = Form(...),
    description: str = Form(""),
    icon: str = Form(""),
    sort: int = Form(0),
) -> RedirectResponse:
    with get_conn() as conn:
        try:
            conn.execute(
                "INSERT INTO doc_types (code, label, description, icon, sort) VALUES (?, ?, ?, ?, ?)",
                (code.strip(), label.strip(), description.strip(), icon.strip(), sort),
            )
            conn.commit()
        except sqlite3.IntegrityError as exc:
            raise HTTPException(status_code=400, detail=f"Type code '{code}' already exists") from exc
    return RedirectResponse(url="/admin/documents/types", status_code=303)


@app.post("/admin/documents/types/update")
def doc_types_update(
    type_id: str = Form(...),
    code: str = Form(...),
    label: str = Form(...),
    description: str = Form(""),
    icon: str = Form(""),
    sort: int = Form(0),
) -> RedirectResponse:
    pk = _optional_int(type_id)
    if pk is None:
        raise HTTPException(status_code=400, detail="Invalid document type id.")
    with get_conn() as conn:
        try:
            conn.execute(
                "UPDATE doc_types SET code = ?, label = ?, description = ?, icon = ?, sort = ? WHERE id = ?",
                (code.strip(), label.strip(), description.strip(), icon.strip(), sort, pk),
            )
            conn.commit()
        except sqlite3.IntegrityError as exc:
            raise HTTPException(status_code=400, detail=f"Type code '{code}' already exists") from exc
    return RedirectResponse(url="/admin/documents/types", status_code=303)


@app.post("/admin/documents/types/reorder")
def doc_types_reorder(
    request: Request,
    type_orders: str = Form(...),  # JSON string: {"1": 1, "2": 2, ...}
) -> JSONResponse:
    import json
    
    try:
        orders = json.loads(type_orders)
        with get_conn() as conn:
            for type_id, order in orders.items():
                conn.execute("""
                    UPDATE doc_types
                    SET sort = ?
                    WHERE id = ?
                """, (order, int(type_id)))
            conn.commit()
        return JSONResponse(content={"success": True})
    except Exception as e:
        return JSONResponse(content={"success": False, "error": str(e)}, status_code=500)


@app.post("/admin/documents/categories/new")
def doc_categories_new(
    code: str = Form(...),
    label: str = Form(...),
    description: str = Form(""),
    icon: str = Form(""),
    sort: int = Form(0),
) -> RedirectResponse:
    with get_conn() as conn:
        try:
            conn.execute(
                "INSERT INTO doc_categories (code, label, description, icon, sort) VALUES (?, ?, ?, ?, ?)",
                (code.strip(), label.strip(), description.strip(), icon.strip(), sort),
            )
            conn.commit()
        except sqlite3.IntegrityError as exc:
            raise HTTPException(status_code=400, detail=f"Category code '{code}' already exists") from exc
    return RedirectResponse(url="/admin/documents/categories", status_code=303)


@app.post("/admin/documents/types/delete")
def doc_types_delete(
    type_id: str = Form(...),
) -> RedirectResponse:
    pk = _optional_int(type_id)
    if pk is None:
        raise HTTPException(status_code=400, detail="Invalid document type id.")
    with get_conn() as conn:
        # Check if any documents are using this type
        assigned = conn.execute(
            "SELECT COUNT(*) FROM documents WHERE type_id = ?",
            (pk,)
        ).fetchone()[0]
        if assigned > 0:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot delete type: {assigned} document(s) are using it. Please reassign them first."
            )
        conn.execute("DELETE FROM doc_types WHERE id = ?", (pk,))
        conn.commit()
    return RedirectResponse(url="/admin/documents/types", status_code=303)


@app.post("/admin/documents/categories/update")
def doc_categories_update(
    category_id: str = Form(...),
    code: str = Form(...),
    label: str = Form(...),
    description: str = Form(""),
    icon: str = Form(""),
    sort: int = Form(0),
) -> RedirectResponse:
    pk = _optional_int(category_id)
    if pk is None:
        raise HTTPException(status_code=400, detail="Invalid document category id.")
    with get_conn() as conn:
        try:
            conn.execute(
                "UPDATE doc_categories SET code = ?, label = ?, description = ?, icon = ?, sort = ? WHERE id = ?",
                (code.strip(), label.strip(), description.strip(), icon.strip(), sort, pk),
            )
            conn.commit()
        except sqlite3.IntegrityError as exc:
            raise HTTPException(status_code=400, detail=f"Category code '{code}' already exists") from exc
    return RedirectResponse(url="/admin/documents/categories", status_code=303)


@app.post("/admin/documents/categories/reorder")
def doc_categories_reorder(
    request: Request,
    category_orders: str = Form(...),  # JSON string: {"1": 1, "2": 2, ...}
) -> JSONResponse:
    import json
    
    try:
        orders = json.loads(category_orders)
        with get_conn() as conn:
            for cat_id, order in orders.items():
                conn.execute("""
                    UPDATE doc_categories
                    SET sort = ?
                    WHERE id = ?
                """, (order, int(cat_id)))
            conn.commit()
        return JSONResponse(content={"success": True})
    except Exception as e:
        return JSONResponse(content={"success": False, "error": str(e)}, status_code=500)


@app.post("/admin/documents/categories/delete")
def doc_categories_delete(
    category_id: str = Form(...),
) -> RedirectResponse:
    pk = _optional_int(category_id)
    if pk is None:
        raise HTTPException(status_code=400, detail="Invalid document category id.")
    with get_conn() as conn:
        # Check if any documents are using this category
        assigned = conn.execute(
            "SELECT COUNT(*) FROM documents WHERE category_id = ?",
            (pk,)
        ).fetchone()[0]
        if assigned > 0:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot delete category: {assigned} document(s) are using it. Please reassign them first."
            )
        conn.execute("DELETE FROM doc_categories WHERE id = ?", (pk,))
        conn.commit()
    return RedirectResponse(url="/admin/documents/categories", status_code=303)


@app.get("/admin/documents/types")
def doc_types_list(request: Request) -> Any:
    try:
        with get_conn() as conn:
            rows = conn.execute(
                "SELECT * FROM doc_types ORDER BY sort, label"
            ).fetchall()
            types = [
                {
                    "id": row["id"],
                    "code": row["code"],
                    "label": row["label"],
                    "description": row["description"] or "",
                    "icon": row["icon"] or "",
                    "sort": row["sort"],
                }
                for row in rows
            ]
    except Exception:
        types = []
    return templates.TemplateResponse(request, "doc_types_list.html",
        {"request": request, "types": types},
    )


@app.get("/admin/documents/new")
def document_new(request: Request) -> Any:
    try:
        with get_conn() as conn:
            categories = conn.execute("SELECT id, label, icon FROM doc_categories ORDER BY sort, label").fetchall()
            types = conn.execute("SELECT id, label, icon FROM doc_types ORDER BY sort, label").fetchall()
            tabs = conn.execute("SELECT id, code, label FROM doc_tabs WHERE code != 'all' ORDER BY sort").fetchall()
    except Exception:
        categories = []
        types = []
        tabs = []
    return templates.TemplateResponse(request, "document_edit.html",
        {
            "request": request,
            "document": None,
            "categories": categories,
            "types": types,
            "tabs": tabs,
            "selected_tabs": [],
            "images": [],
            "links": [],
        },
    )


@app.get("/admin/documents/{doc_id}")
def document_edit(request: Request, doc_id: int) -> Any:
    with get_conn() as conn:
        document_row = conn.execute("SELECT * FROM documents WHERE id = ?", (doc_id,)).fetchone()
        if not document_row:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Convert Row to dict and replace None with empty strings for text fields
        document = dict(document_row)
        # Replace None with empty string for text fields
        text_fields = ['content_markdown', 'content_html', 'summary', 'tags', 'extra', 'slug']
        for field in text_fields:
            if document.get(field) is None:
                document[field] = ''
        # Ensure featured is an integer (not None)
        if document.get('featured') is None:
            document['featured'] = 0
        else:
            document['featured'] = int(document['featured']) if document['featured'] else 0
        
        categories = conn.execute("SELECT id, label, icon FROM doc_categories ORDER BY sort, label").fetchall()
        types = conn.execute("SELECT id, label, icon FROM doc_types ORDER BY sort, label").fetchall()
        tabs = conn.execute("SELECT id, code, label FROM doc_tabs WHERE code != 'all' ORDER BY sort").fetchall()
        
        selected_tabs = [
            row[0] for row in conn.execute(
                "SELECT tab_id FROM document_tabs WHERE document_id = ?", (doc_id,)
            )
        ]
        
        images = conn.execute(
            "SELECT * FROM document_images WHERE document_id = ? ORDER BY sort", (doc_id,)
        ).fetchall()
        
        links = conn.execute(
            "SELECT * FROM document_links WHERE document_id = ? ORDER BY sort", (doc_id,)
        ).fetchall()
    
    return templates.TemplateResponse(request, "document_edit.html",
        {
            "request": request,
            "document": document,
            "categories": categories,
            "types": types,
            "tabs": tabs,
            "selected_tabs": selected_tabs,
            "images": images,
            "links": links,
        },
    )


@app.get("/admin/test-logging")
def test_logging():
    """Test endpoint to verify logging works"""
    debug_log_path = Path(__file__).parent / "admin.log"
    try:
        with open(debug_log_path, "a", encoding="utf-8") as f:
            f.write(f"\n[{date.today().isoformat()}] TEST ENDPOINT CALLED - LOGGING WORKS!\n")
            f.flush()
            import os
            os.fsync(f.fileno())
        return {"status": "success", "message": "Logging test successful - check admin.log"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.post("/admin/documents/save")
def document_save(
    request: Request,
    doc_id: str | None = Form(None),
    title: str = Form(...),
    slug: str | None = Form(None),
    category_id: str | None = Form(None),
    type_id: str | None = Form(None),
    summary: str | None = Form(None),
    content_format: str = Form("markdown"),
    content_source: str = Form("inline"),
    content_path: str | None = Form(None),
    content_markdown: str | None = Form(None),
    content_html: str | None = Form(None),
    created_at: str | None = Form(None),
    posted_at: str | None = Form(None),
    updated_at: str | None = Form(None),
    effective_from: str | None = Form(None),
    effective_to: str | None = Form(None),
    tags: str | None = Form(None),
    extra: str | None = Form(None),
    tab_ids: list[int] | None = Form(None),
    status: str = Form("Published"),
    featured: str | None = Form(None),  # Match blog handler exactly
) -> RedirectResponse:
    import sys
    import traceback
    
    # IMMEDIATE logging at function start - multiple methods
    debug_log_path = Path(__file__).parent / "admin.log"
    
    # Method 1: stderr (always works)
    print("="*80, file=sys.stderr)
    print("DOCUMENT SAVE FUNCTION CALLED", file=sys.stderr)
    print(f"featured = {featured!r}", file=sys.stderr)
    print("="*80, file=sys.stderr)
    sys.stderr.flush()
    
    # Method 2: log file
    try:
        with open(debug_log_path, "a", encoding="utf-8") as f:
            f.write(f"\n{'='*80}\n")
            f.write(f"[{date.today().isoformat()}] DOCUMENT SAVE FUNCTION CALLED\n")
            f.write(f"  featured parameter: {featured!r}\n")
            f.write(f"  featured type: {type(featured).__name__}\n")
            f.write(f"  doc_id: {doc_id!r}\n")
            f.write(f"  title: {title[:50]!r}...\n")
            f.flush()
            import os
            os.fsync(f.fileno())  # Force write to disk
    except Exception as e:
        print(f"ERROR writing to log file: {e}", file=sys.stderr)
        print(traceback.format_exc(), file=sys.stderr)
        sys.stderr.flush()
    
    today = date.today().isoformat()
    
    # Debug: Log ALL form parameters received
    print("=" * 80, file=sys.stderr)
    print("DOCUMENT SAVE DEBUG - ALL PARAMETERS:", file=sys.stderr)
    print(f"  doc_id: {doc_id!r}", file=sys.stderr)
    print(f"  title: {title[:50]!r}...", file=sys.stderr)
    print(f"  status: {status!r}", file=sys.stderr)
    print(f"  featured: {featured!r} (type: {type(featured).__name__})", file=sys.stderr)
    print("=" * 80, file=sys.stderr)
    
    # Also print to stdout for console
    print(f"DEBUG: Featured from Form() parameter: {featured!r}, type: {type(featured)}")
    
    if not slug:
        slug = doc_slugify(title)
    
    if not doc_id or doc_id == "":
        if not created_at:
            created_at = today
        if not posted_at:
            posted_at = today
        if not updated_at:
            updated_at = today
    else:
        if not updated_at:
            updated_at = today
    
    category_id_val = _optional_int(category_id)
    type_id_val = _optional_int(type_id)
    
    extra_json = None
    if extra:
        try:
            extra_json = json.dumps(json.loads(extra))
        except json.JSONDecodeError:
            extra_json = None
    
    # Process featured checkbox - EXACT same logic as blog posts
    # Write debug info to a file for easy checking
    try:
        debug_file = Path("/tmp/document_save_debug.txt")
        with open(debug_file, "w") as f:
            f.write(f"featured parameter: {featured!r}\n")
            f.write(f"featured type: {type(featured)}\n")
            f.write(f"featured == '1': {featured == '1'}\n")
            f.write(f"featured == 'on': {featured == 'on'}\n")
    except Exception as e:
        print(f"Could not write debug file: {e}", file=sys.stderr)
    
    # Write debug info to admin.log and debug file
    debug_log_path = Path(__file__).parent / "admin.log"
    debug_file_path = Path(__file__).parent / "document_save_debug.txt"
    
    try:
        debug_msg = f"[{date.today().isoformat()}] DOCUMENT SAVE - featured={featured!r}, type={type(featured).__name__}, featured=='1'={featured == '1'}, featured=='on'={featured == 'on'}\n"
        with open(debug_log_path, "a") as f:
            f.write(debug_msg)
        with open(debug_file_path, "w") as f:
            f.write(debug_msg)
            f.write(f"All parameters:\n")
            f.write(f"  doc_id: {doc_id!r}\n")
            f.write(f"  title: {title[:50]!r}...\n")
            f.write(f"  status: {status!r}\n")
            f.write(f"  featured: {featured!r}\n")
    except Exception as e:
        print(f"Could not write debug file: {e}", file=sys.stderr)
    
    print(f"DEBUG DOCUMENTS SAVE: featured parameter = {featured!r}, type = {type(featured)}", file=sys.stderr)
    print(f"DEBUG DOCUMENTS SAVE: featured == '1' = {featured == '1'}, featured == 'on' = {featured == 'on'}", file=sys.stderr)
    
    # Process featured - EXACT same as blog: 1 if "1" or "on", else 0
    featured_val = 1 if featured == "on" or featured == "1" else 0
    
    print(f"DEBUG DOCUMENTS SAVE: featured_val = {featured_val}", file=sys.stderr)
    
    # Log featured_val to files
    try:
        with open(debug_log_path, "a") as f:
            f.write(f"[{date.today().isoformat()}] DOCUMENT SAVE - featured_val={featured_val}\n")
        with open(debug_file_path, "a") as f:
            f.write(f"featured_val calculated: {featured_val}\n")
    except Exception as e:
        pass
    
    # Process markdown to HTML using BlogManager (same as blog posts)
    # Reload BlogManager module to ensure we have the latest code changes
    processed_html = content_html
    blog_manager_instance = None
    
    if content_format == 'markdown' and content_markdown:
        try:
            blog_manager_path = BLOG_RESOURCES / "blog-manager.py"
            if blog_manager_path.exists():
                # Force reload by using a unique module name with timestamp to avoid caching
                import time
                unique_name = f"blog_manager_doc_{int(time.time() * 1000000)}"
                spec = importlib.util.spec_from_file_location(unique_name, str(blog_manager_path))
                blog_manager_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(blog_manager_module)
                # BlogManager expects the blog root directory (where HTML files are generated), not the resources directory
                blog_manager_instance = blog_manager_module.BlogManager(str(ROOT / "blog"))
                processed_html = blog_manager_instance.markdown_to_html(content_markdown.strip())
            else:
                raise ImportError("BlogManager file not found")
        except Exception as e:
            print(f"Error processing markdown with reloaded BlogManager: {e}")
            # Fallback to cached BLOG_MANAGER if available
            if HAS_BLOG_MANAGER and BLOG_MANAGER:
                try:
                    processed_html = BLOG_MANAGER.markdown_to_html(content_markdown.strip())
                except Exception as e2:
                    print(f"Error with cached BlogManager: {e2}")
                    # Fallback to SharedMarkdownProcessor if available
                    if HAS_MARKDOWN_PROCESSOR:
                        try:
                            processed_html = MARKDOWN_PROCESSOR.markdown_to_html(content_markdown.strip())
                        except Exception as e3:
                            print(f"Warning: All markdown processing failed: {e3}")
                            processed_html = content_html
                    else:
                        processed_html = content_html
            else:
                # Fallback to SharedMarkdownProcessor if available
                if HAS_MARKDOWN_PROCESSOR:
                    try:
                        processed_html = MARKDOWN_PROCESSOR.markdown_to_html(content_markdown.strip())
                    except Exception as e3:
                        print(f"Warning: Markdown processing failed: {e3}")
                        processed_html = content_html
                else:
                    processed_html = content_html
    
    # Initialize old_slug for potential cleanup
    old_slug = None
    
    with get_conn() as conn:
        if doc_id and doc_id != "":
            doc_id_int = int(doc_id)
            
            # Get old slug before updating (to delete old HTML file if slug changed)
            old_doc_row = conn.execute("SELECT slug FROM documents WHERE id = ?", (doc_id_int,)).fetchone()
            old_slug = old_doc_row[0] if old_doc_row else None
            
            debug_log_path = Path(__file__).parent / "admin.log"
            debug_file_path = Path(__file__).parent / "document_save_debug.txt"
            
            print(f"DEBUG DOCUMENTS SAVE: About to UPDATE document {doc_id_int} with featured_val = {featured_val}", file=sys.stderr)
            try:
                with open(debug_log_path, "a") as f:
                    f.write(f"[{date.today().isoformat()}] About to UPDATE document {doc_id_int} with featured_val = {featured_val}\n")
                with open(debug_file_path, "a") as f:
                    f.write(f"About to UPDATE document {doc_id_int} with featured_val = {featured_val}\n")
            except:
                pass
            
            conn.execute("""
                UPDATE documents SET
                    category_id = ?, type_id = ?, title = ?, slug = ?, summary = ?,
                    content_format = ?, content_source = ?, content_path = ?,
                    content_markdown = ?, content_html = ?,
                    created_at = ?, posted_at = ?, updated_at = ?,
                    effective_from = ?, effective_to = ?, tags = ?, extra = ?, status = ?, featured = ?
                WHERE id = ?
            """, (
                category_id_val, type_id_val, title.strip(), slug.strip(), summary.strip() if summary else None,
                content_format, content_source, content_path.strip() if content_path else None,
                content_markdown.strip() if content_markdown else None,
                processed_html.strip() if processed_html else None,
                created_at, posted_at, updated_at,
                effective_from if effective_from else None,
                effective_to if effective_to else None,
                tags.strip() if tags else None, extra_json, status, featured_val,
                doc_id_int,
            ))
            conn.commit()
            
            # Verify what was actually saved
            verify = conn.execute("SELECT featured FROM documents WHERE id = ?", (doc_id_int,)).fetchone()
            db_value = verify[0] if verify else 'NOT FOUND'
            print(f"DEBUG DOCUMENTS SAVE: After UPDATE, featured value in DB = {db_value}", file=sys.stderr)
            try:
                with open(debug_log_path, "a") as f:
                    f.write(f"[{date.today().isoformat()}] After UPDATE, featured value in DB = {db_value}\n")
                with open(debug_file_path, "a") as f:
                    f.write(f"After UPDATE, featured value in DB = {db_value}\n")
            except:
                pass
            document_id = doc_id_int
        else:
            cursor = conn.execute("""
                INSERT INTO documents (
                    category_id, type_id, title, slug, summary,
                    content_format, content_source, content_path,
                    content_markdown, content_html,
                    created_at, posted_at, updated_at,
                    effective_from, effective_to, tags, extra, status, featured
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                category_id_val, type_id_val, title.strip(), slug.strip(), summary.strip() if summary else None,
                content_format, content_source, content_path.strip() if content_path else None,
                content_markdown.strip() if content_markdown else None,
                processed_html.strip() if processed_html else None,
                created_at, posted_at, updated_at,
                effective_from if effective_from else None,
                effective_to if effective_to else None,
                tags.strip() if tags else None, extra_json, status, featured_val,
            ))
            conn.commit()
            document_id = cursor.lastrowid
        
        conn.execute("DELETE FROM document_tabs WHERE document_id = ?", (document_id,))
        if tab_ids:
            for tab_id in tab_ids:
                conn.execute(
                    "INSERT INTO document_tabs (document_id, tab_id) VALUES (?, ?)",
                    (document_id, tab_id),
                )
        conn.commit()
        
        # Get category and type labels for metadata
        category_label = None
        type_label = None
        if category_id_val:
            cat_row = conn.execute("SELECT label FROM doc_categories WHERE id = ?", (category_id_val,)).fetchone()
            if cat_row:
                category_label = cat_row[0]
        if type_id_val:
            type_row = conn.execute("SELECT label FROM doc_types WHERE id = ?", (type_id_val,)).fetchone()
            if type_row:
                type_label = type_row[0]
    
    # Generate static HTML file only if status is "Published" (same as blog posts)
    # Use reloaded blog_manager_instance if available, otherwise fall back to cached BLOG_MANAGER
    blog_mgr = blog_manager_instance if blog_manager_instance else (BLOG_MANAGER if HAS_BLOG_MANAGER and BLOG_MANAGER else None)
    if not blog_mgr and status == 'Published':
        blog_mgr = _load_blog_manager()

    if blog_mgr and status == 'Published':
        try:
            # Prepare metadata dict for HTML generation
            metadata = {
                'title': title.strip(),
                'slug': slug.strip(),
                'summary': summary.strip() if summary else None,
                'author': 'Bradley R. Clampitt',  # Default author for documents
                'date': posted_at or created_at or updated_at or '',
                'updated_date': updated_at or '',
                'category': category_label or '',
                'type': type_label or '',
                'tags': tags.strip().split(',') if tags else [],
            }
            
            # Generate HTML file
            success, output_path = blog_mgr.generate_document_html_from_db(
                metadata,
                processed_html,
                slug.strip(),
                str(ROOT / "documents")
            )
            
            if not success:
                print(f"Warning: Failed to generate HTML file for document {document_id}")
                _generate_document_html_fallback(metadata, processed_html or "", slug.strip())
            else:
                print(f"Successfully generated document HTML file: {output_path}")
                
                # Delete old HTML file if slug changed (only for updates, not new documents)
                if old_slug and old_slug != slug.strip():
                    old_html_file = ROOT / "documents" / "posts" / f"{old_slug}.html"
                    if old_html_file.exists():
                        try:
                            old_html_file.unlink()
                            print(f"Deleted old document HTML file: {old_html_file}")
                        except Exception as e:
                            print(f"Warning: Failed to delete old document HTML file {old_html_file}: {e}")
        except Exception as e:
            print(f"Error generating document HTML file: {e}")
            import traceback
            traceback.print_exc()
            _generate_document_html_fallback(metadata, processed_html or "", slug.strip())
    elif status == 'Published':
        print("Warning: Document HTML generation skipped because BlogManager is unavailable.")
        _generate_document_html_fallback(metadata, processed_html or "", slug.strip())
    else:
        # Ensure drafts (or any non-published status) have no static HTML
        current_html_file = ROOT / "documents" / "posts" / f"{slug.strip()}.html"
        if current_html_file.exists():
            try:
                current_html_file.unlink()
                print(f"Deleted draft document HTML file: {current_html_file}")
            except Exception as e:
                print(f"Warning: Failed to delete draft document HTML file {current_html_file}: {e}")

        if old_slug and old_slug != slug.strip():
            old_html_file = ROOT / "documents" / "posts" / f"{old_slug}.html"
            if old_html_file.exists():
                try:
                    old_html_file.unlink()
                    print(f"Deleted old draft document HTML file: {old_html_file}")
                except Exception as e:
                    print(f"Warning: Failed to delete old draft document HTML file {old_html_file}: {e}")
    
    # Redirect to documents list with success message
    from urllib.parse import quote
    title_encoded = quote(title.strip())
    return RedirectResponse(url=f"/admin/documents?success=saved&title={title_encoded}", status_code=303)


@app.post("/admin/documents/delete")
def documents_delete(
    request: Request,
    doc_id: str = Form(...),
) -> RedirectResponse:
    doc_pk = _optional_int(doc_id)
    if doc_pk is None:
        raise HTTPException(status_code=400, detail="Document ID is required.")

    slug = None
    with get_conn() as conn:
        row = conn.execute("SELECT slug FROM documents WHERE id = ?", (doc_pk,)).fetchone()
        if row:
            slug = row[0]
        # Clean up related records (in case ON DELETE CASCADE isn't enforced)
        conn.execute("DELETE FROM document_tabs WHERE document_id = ?", (doc_pk,))
        conn.execute("DELETE FROM document_images WHERE document_id = ?", (doc_pk,))
        conn.execute("DELETE FROM document_links WHERE document_id = ?", (doc_pk,))
        conn.execute("DELETE FROM documents WHERE id = ?", (doc_pk,))
        conn.commit()

    # Remove generated HTML file
    if slug:
        html_path = ROOT / "documents" / "posts" / f"{slug}.html"
        if html_path.exists():
            try:
                html_path.unlink()
            except Exception as e:
                print(f"Warning: Failed to delete document HTML file {html_path}: {e}")

    # Remove uploaded images folder
    images_dir = ROOT / "assets" / "images" / "documents" / str(doc_pk)
    if images_dir.exists():
        try:
            import shutil
            shutil.rmtree(images_dir)
        except Exception as e:
            print(f"Warning: Failed to delete document images folder {images_dir}: {e}")

    return RedirectResponse(url=request.url_for("documents_list"), status_code=303)


@app.get("/admin/documents/images/browse")
def documents_images_browse() -> JSONResponse:
    """List all available images from assets/images/documents directory"""
    images = []
    documents_dir = ROOT / "assets" / "images" / "documents"

    if documents_dir.exists() and documents_dir.is_dir():
        # Scan all subdirectories recursively
        for item in documents_dir.rglob("*"):
            if item.is_file() and item.suffix.lower() in IMAGE_EXTENSIONS:
                # Get relative path from assets/images directory
                relative_path = item.relative_to(ROOT / "assets" / "images")
                url = f"/assets/images/{relative_path.as_posix()}"
                images.append({
                    "url": url,
                    "filename": item.name,
                    "path": str(relative_path),
                    "size": item.stat().st_size
                })

    # Sort by filename
    images.sort(key=lambda x: x["filename"].lower())

    return JSONResponse(content={"images": images})


@app.post("/admin/documents/images/upload")
async def doc_image_upload(
    document_id: int = Form(...),
    file: UploadFile = File(...),
    is_cover: bool = Form(False),
) -> RedirectResponse:
    # Validate image upload
    content, ext, error_msg = await _validate_image_upload(file)
    if error_msg:
        return RedirectResponse(
            url=f"/admin/documents/{document_id}?error={error_msg.replace(' ', '+')}",
            status_code=303
        )
    
    doc_img_dir = DOCUMENTS_MEDIA / str(document_id)
    doc_img_dir.mkdir(parents=True, exist_ok=True)
    
    safe_filename = secrets.token_urlsafe(16) + ext
    file_path = doc_img_dir / safe_filename
    
    # Ensure we're writing within the intended directory
    try:
        file_path.resolve().relative_to(doc_img_dir.resolve())
    except ValueError:
        return RedirectResponse(
            url=f"/admin/documents/{document_id}?error=Invalid+file+path",
            status_code=303
        )
    
    url = f"/assets/images/documents/{document_id}/{safe_filename}"
    
    # Write file
    try:
        with file_path.open("wb") as f:
            f.write(content)
    except Exception as e:
        import sys
        print(f"Error writing file: {e}", file=sys.stderr)
        return RedirectResponse(
            url=f"/admin/documents/{document_id}?error=Error+saving+file",
            status_code=303
        )
    
    with get_conn() as conn:
        if is_cover:
            conn.execute(
                "UPDATE document_images SET is_cover = 0 WHERE document_id = ?",
                (document_id,),
            )
        conn.execute("""
            INSERT INTO document_images (document_id, url, alt, is_cover, sort)
            VALUES (?, ?, ?, ?, (SELECT COALESCE(MAX(sort), 0) + 1 FROM document_images WHERE document_id = ?))
        """, (document_id, url, file.filename, 1 if is_cover else 0, document_id))
        conn.commit()
    
    return RedirectResponse(url=f"/admin/documents/{document_id}", status_code=303)


@app.post("/admin/documents/images/add-existing")
async def doc_image_add_existing(
    document_id: int = Form(...),
    image_path: str = Form(...),
    is_cover: bool = Form(False),
) -> RedirectResponse:
    """Add an existing image from the server as a document image"""
    with get_conn() as conn:
        if is_cover:
            conn.execute(
                "UPDATE document_images SET is_cover = 0 WHERE document_id = ?",
                (document_id,),
            )
        conn.execute("""
            INSERT INTO document_images (document_id, url, alt, is_cover, sort)
            VALUES (?, ?, ?, ?, (SELECT COALESCE(MAX(sort), 0) + 1 FROM document_images WHERE document_id = ?))
        """, (document_id, image_path, '', 1 if is_cover else 0, document_id))
        conn.commit()
    
    return RedirectResponse(url=f"/admin/documents/{document_id}", status_code=303)


@app.post("/admin/documents/links/save")
def doc_link_save(
    document_id: int = Form(...),
    label: str = Form(...),
    url: str = Form(...),
    sort: int = Form(0),
) -> RedirectResponse:
    with get_conn() as conn:
        conn.execute("""
            INSERT INTO document_links (document_id, label, url, sort)
            VALUES (?, ?, ?, ?)
        """, (document_id, label.strip(), url.strip(), sort))
        conn.commit()
    return RedirectResponse(url=f"/admin/documents/{document_id}", status_code=303)


@app.post("/admin/documents/images/delete")
def doc_image_delete(
    request: Request,
    image_id: int = Form(...),
) -> RedirectResponse:
    with get_conn() as conn:
        # Get image info to delete file and get document_id for redirect
        image = conn.execute(
            "SELECT document_id, url FROM document_images WHERE id = ?", (image_id,)
        ).fetchone()
        
        if not image:
            raise HTTPException(status_code=404, detail="Image not found")
        
        document_id = image["document_id"]
        url = image["url"]
        
        # Delete the file
        if url.startswith("/assets/images/documents/"):
            file_path = ROOT / url.lstrip("/")
            if file_path.exists():
                try:
                    file_path.unlink()
                except Exception as e:
                    print(f"Warning: Could not delete image file {file_path}: {e}")
        
        # Delete from database
        conn.execute("DELETE FROM document_images WHERE id = ?", (image_id,))
        conn.commit()
    
    return RedirectResponse(url=f"/admin/documents/{document_id}", status_code=303)


@app.post("/admin/documents/links/delete")
def doc_link_delete(
    request: Request,
    link_id: int = Form(...),
) -> RedirectResponse:
    with get_conn() as conn:
        # Get document_id for redirect
        link = conn.execute(
            "SELECT document_id FROM document_links WHERE id = ?", (link_id,)
        ).fetchone()
        
        if not link:
            raise HTTPException(status_code=404, detail="Link not found")
        
        document_id = link["document_id"]
        
        # Delete from database
        conn.execute("DELETE FROM document_links WHERE id = ?", (link_id,))
        conn.commit()
    
    return RedirectResponse(url=f"/admin/documents/{document_id}", status_code=303)


@app.post("/admin/documents/preview")
async def document_preview(
    request: Request,
    content_markdown: str = Form(...),
) -> dict:
    """
    Preview endpoint that processes markdown using the shared markdown processor.
    Returns the processed HTML that matches the frontend rendering exactly.
    """
    if not content_markdown or not content_markdown.strip():
        return {"html": "<p class='text-slate-500 italic'>No content to preview.</p>"}
    
    if not HAS_MARKDOWN_PROCESSOR:
        return {
            "html": "<p class='text-red-600'>Markdown processor not available. Preview unavailable.</p>",
            "error": "Markdown processor not available"
        }
    
    try:
        # Process markdown using the shared processor (same as frontend)
        processed_html = MARKDOWN_PROCESSOR.markdown_to_html(content_markdown.strip())
        return {"html": processed_html}
    except Exception as e:
        return {
            "html": f"<p class='text-red-600'>Error processing markdown: {str(e)}</p>",
            "error": str(e)
        }

# ============================================================================
# References System Routes
# ============================================================================

@app.get("/admin/references")
def references_list(request: Request) -> Any:
    try:
        with get_conn() as conn:
            references_rows = conn.execute("""
                SELECT 
                    id,
                    person_name,
                    company,
                    connection_type,
                    title,
                    reference_text,
                    created_at,
                    updated_at
                FROM ref_entries
                ORDER BY created_at DESC, id DESC
            """).fetchall()
        
        # Parse connection_type JSON for each reference
        references = []
        for row in references_rows:
            ref_dict = dict(row)
            connection_types = []
            if ref_dict.get("connection_type"):
                try:
                    connection_types = json.loads(ref_dict["connection_type"])
                except json.JSONDecodeError:
                    pass
            ref_dict["connection_types"] = connection_types
            references.append(ref_dict)
    except Exception:
        references = []
    return templates.TemplateResponse(request, "references_list.html",
        {"request": request, "references": references},
    )


@app.get("/admin/references/new")
def reference_new(request: Request) -> Any:
    return templates.TemplateResponse(request, "reference_edit.html",
        {
            "request": request,
            "reference": None,
        },
    )


@app.get("/admin/references/{ref_id}")
def reference_edit(request: Request, ref_id: int) -> Any:
    with get_conn() as conn:
        reference_row = conn.execute("SELECT * FROM ref_entries WHERE id = ?", (ref_id,)).fetchone()
        if not reference_row:
            raise HTTPException(status_code=404, detail="Reference not found")
        
        reference = dict(reference_row)
        # Parse connection_type JSON if it exists
        if reference.get("connection_type"):
            try:
                reference["connection_types"] = json.loads(reference["connection_type"])
            except json.JSONDecodeError:
                reference["connection_types"] = []
        else:
            reference["connection_types"] = []
    
    return templates.TemplateResponse(request, "reference_edit.html",
        {
            "request": request,
            "reference": reference,
        },
    )


@app.post("/admin/references/save")
def reference_save(
    request: Request,
    ref_id: str | None = Form(None),
    person_name: str = Form(...),
    company: str | None = Form(None),
    title: str | None = Form(None),
    connection_types: list[str] | None = Form(None),
    reference_text: str = Form(...),
) -> RedirectResponse:
    from datetime import datetime
    
    # Convert connection_types list to JSON
    connection_type_json = json.dumps(connection_types) if connection_types else None
    
    with get_conn() as conn:
        now = datetime.now().isoformat()
        
        if ref_id:
            ref_id_int = int(ref_id)
            conn.execute("""
                UPDATE ref_entries
                SET person_name = ?, company = ?, title = ?, connection_type = ?, reference_text = ?, updated_at = ?
                WHERE id = ?
            """, (
                person_name.strip(),
                company.strip() if company else None,
                title.strip() if title else None,
                connection_type_json,
                reference_text.strip(),
                now,
                ref_id_int,
            ))
            conn.commit()
        else:
            cursor = conn.execute("""
                INSERT INTO ref_entries (
                    person_name, company, title, connection_type, reference_text, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                person_name.strip(),
                company.strip() if company else None,
                title.strip() if title else None,
                connection_type_json,
                reference_text.strip(),
                now,
                now,
            ))
            conn.commit()
            ref_id_int = cursor.lastrowid
    
    return RedirectResponse(url="/admin/references", status_code=303)


# ============================================================================
# CMS Routes - CMS Blocks, Site Settings, Contact Info
# ============================================================================

@app.get("/admin/cms/blocks")
def cms_blocks_list(request: Request) -> Any:
    """List all CMS blocks"""
    try:
        with get_conn() as conn:
            blocks_rows = conn.execute("""
                SELECT * FROM cms_blocks 
                ORDER BY sort_order, title
            """).fetchall()
            blocks = [row_to_dict(row) for row in blocks_rows]
    except Exception:
        blocks = []
    
    # Scan frontend for CMS block references
    frontend_usage = scan_frontend_for_cms_blocks()
    
    return templates.TemplateResponse(request, "cms/blocks_list.html",
        {"request": request, "blocks": blocks, "frontend_usage": frontend_usage},
    )


def scan_frontend_for_cms_blocks() -> dict:
    """Scan frontend HTML files for CMS block references"""
    frontend_blocks = {}  # {block_id: [list of files]}
    
    # HTML files to scan (excluding admin templates and generated files)
    html_files = [
        ROOT / "index.html",
        ROOT / "personal.html",
        ROOT / "contact.html",
        ROOT / "blog.html",
        ROOT / "documents.html",
        ROOT / "portfolio.html",
        ROOT / "experience.html",
        ROOT / "photography.html",
        ROOT / "magento.html",
        ROOT / "side-projects.html",
        ROOT / "references.html",
        ROOT / "resume.html",
        ROOT / "open-to-opportunities.html",
    ]
    
    import re
    # Pattern to match cmsBlocks['block-id'] or cmsBlocks["block-id"]
    pattern = r"cmsBlocks\[['\"]([^'\"]+)['\"]"
    
    for html_file in html_files:
        if html_file.exists():
            try:
                with open(html_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    matches = re.findall(pattern, content)
                    # Use set to get unique block IDs per file
                    unique_block_ids = set(matches)
                    for block_id in unique_block_ids:
                        if block_id not in frontend_blocks:
                            frontend_blocks[block_id] = []
                        # Only add file once per block ID
                        if html_file.name not in frontend_blocks[block_id]:
                            frontend_blocks[block_id].append(html_file.name)
            except Exception as e:
                print(f"Error scanning {html_file}: {e}")
    
    return frontend_blocks


@app.get("/admin/cms/blocks/new")
def cms_blocks_new(request: Request) -> Any:
    """Create new CMS block form"""
    # Fetch all blocks for reference
    try:
        with get_conn() as conn:
            blocks_rows = conn.execute("""
                SELECT id, block_id, title, description, is_active, image
                FROM cms_blocks 
                ORDER BY block_id
            """).fetchall()
            all_blocks = [row_to_dict(row) for row in blocks_rows]
    except Exception:
        all_blocks = []
    
    # Scan frontend for CMS block usage
    frontend_usage = scan_frontend_for_cms_blocks()
    
    return templates.TemplateResponse(request, "cms/blocks_edit.html",
        {"request": request, "block": None, "all_blocks": all_blocks, "frontend_usage": frontend_usage},
    )


@app.get("/admin/cms/blocks/{block_id}")
def cms_blocks_edit(request: Request, block_id: int) -> Any:
    """Edit CMS block form"""
    with get_conn() as conn:
        block = conn.execute(
            "SELECT * FROM cms_blocks WHERE id = ?", (block_id,)
        ).fetchone()
        if not block:
            raise HTTPException(status_code=404, detail="CMS block not found")
        
        # Fetch all blocks for reference
        try:
            blocks_rows = conn.execute("""
                SELECT id, block_id, title, description, is_active, image
                FROM cms_blocks 
                ORDER BY block_id
            """).fetchall()
            all_blocks = [row_to_dict(row) for row in blocks_rows]
        except Exception:
            all_blocks = []
    
    # Scan frontend for CMS block usage
    frontend_usage = scan_frontend_for_cms_blocks()
    
    # Convert block to dict and parse gallery_images JSON if present
    block_dict = row_to_dict(block)
    if block_dict.get("gallery_images"):
        try:
            block_dict["gallery_images"] = json.loads(block_dict["gallery_images"])
        except (json.JSONDecodeError, ValueError):
            block_dict["gallery_images"] = []
    else:
        block_dict["gallery_images"] = []
    
    return templates.TemplateResponse(request, "cms/blocks_edit.html",
        {"request": request, "block": block_dict, "all_blocks": all_blocks, "frontend_usage": frontend_usage},
    )


@app.post("/admin/cms/blocks/save")
def cms_blocks_save(
    block_id: str = Form(None),
    block_id_code: str = Form(...),
    title: str = Form(...),
    content: str = Form(...),
    content_format: str = Form("html"),
    description: str = Form(""),
    image: str = Form(""),
    image_position: str = Form("right"),
    image_description: str = Form(""),
    gallery_images: str = Form(""),  # JSON string of gallery images
    is_active: bool = Form(True),
    sort_order: int = Form(0),
) -> RedirectResponse:
    """Save CMS block (create or update)"""
    pk = _optional_int(block_id) if block_id else None
    
    # Validate image_position
    if image_position not in ['left', 'right', 'none']:
        image_position = 'right'
    
    # Parse gallery_images JSON
    gallery_images_json = None
    if gallery_images:
        try:
            # Validate JSON format
            parsed = json.loads(gallery_images)
            if isinstance(parsed, list):
                gallery_images_json = gallery_images.strip()
        except (json.JSONDecodeError, ValueError):
            # Invalid JSON, ignore it
            gallery_images_json = None
    
    with get_conn() as conn:
        if pk:
            # Update existing
            conn.execute("""
                UPDATE cms_blocks 
                SET block_id = ?, title = ?, content = ?, content_format = ?, 
                    description = ?, image = ?, image_position = ?, image_description = ?, gallery_images = ?, is_active = ?, sort_order = ?, updated_at = datetime('now')
                WHERE id = ?
            """, (
                block_id_code.strip(),
                title.strip(),
                content.strip(),
                content_format,
                description.strip(),
                image.strip() if image else None,
                image_position,
                image_description.strip() if image_description else None,
                gallery_images_json,
                1 if is_active else 0,
                sort_order,
                pk,
            ))
        else:
            # Create new
            conn.execute("""
                INSERT INTO cms_blocks 
                (block_id, title, content, content_format, description, image, image_position, image_description, gallery_images, is_active, sort_order, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
            """, (
                block_id_code.strip(),
                title.strip(),
                content.strip(),
                content_format,
                description.strip(),
                image.strip() if image else None,
                image_position,
                image_description.strip() if image_description else None,
                gallery_images_json,
                1 if is_active else 0,
                sort_order,
            ))
        conn.commit()
    
    # Redirect back to edit page if updating, or list if creating
    if pk:
        return RedirectResponse(url=f"/admin/cms/blocks/{pk}?saved=1", status_code=303)
    return RedirectResponse(url="/admin/cms/blocks", status_code=303)


@app.post("/admin/cms/blocks/delete")
def cms_blocks_delete(
    block_id: str = Form(...),
) -> RedirectResponse:
    """Delete CMS block"""
    pk = _optional_int(block_id)
    if pk is None:
        raise HTTPException(status_code=400, detail="Invalid block ID.")
    with get_conn() as conn:
        conn.execute("DELETE FROM cms_blocks WHERE id = ?", (pk,))
        conn.commit()
    return RedirectResponse(url="/admin/cms/blocks", status_code=303)


@app.get("/admin/cms/settings")
def cms_settings_list(request: Request) -> Any:
    """List all site settings"""
    try:
        with get_conn() as conn:
            settings_rows = conn.execute("""
                SELECT * FROM cms_site_settings 
                ORDER BY setting_key
            """).fetchall()
            settings = [dict(row) for row in settings_rows]
    except Exception:
        settings = []
    
    # Scan frontend for CMS block references
    frontend_usage = scan_frontend_for_cms_blocks()
    
    return templates.TemplateResponse(request, "cms/settings_list.html",
        {"request": request, "settings": settings, "frontend_usage": frontend_usage},
    )


@app.post("/admin/cms/settings/save")
def cms_settings_save(
    setting_id: str = Form(None),
    setting_key: str = Form(...),
    setting_value: str = Form(...),
    setting_type: str = Form("text"),
    description: str = Form(""),
) -> RedirectResponse:
    """Save site setting (create or update)"""
    pk = _optional_int(setting_id) if setting_id else None
    
    with get_conn() as conn:
        if pk:
            # Update existing
            conn.execute("""
                UPDATE cms_site_settings 
                SET setting_key = ?, setting_value = ?, setting_type = ?, 
                    description = ?, updated_at = datetime('now')
                WHERE id = ?
            """, (
                setting_key.strip(),
                setting_value.strip(),
                setting_type,
                description.strip(),
                pk,
            ))
        else:
            # Create new
            conn.execute("""
                INSERT INTO cms_site_settings 
                (setting_key, setting_value, setting_type, description, updated_at)
                VALUES (?, ?, ?, ?, datetime('now'))
            """, (
                setting_key.strip(),
                setting_value.strip(),
                setting_type,
                description.strip(),
            ))
        conn.commit()
    
    return RedirectResponse(url="/admin/cms/settings", status_code=303)


@app.post("/admin/cms/settings/delete")
def cms_settings_delete(
    setting_id: str = Form(...),
) -> RedirectResponse:
    """Delete site setting"""
    pk = _optional_int(setting_id)
    if pk is None:
        raise HTTPException(status_code=400, detail="Invalid setting ID.")
    with get_conn() as conn:
        conn.execute("DELETE FROM cms_site_settings WHERE id = ?", (pk,))
        conn.commit()
    return RedirectResponse(url="/admin/cms/settings", status_code=303)


@app.get("/admin/cms/contact")
def cms_contact_list(request: Request) -> Any:
    """List all contact info fields"""
    try:
        with get_conn() as conn:
            # Ensure new columns exist (for migration)
            try:
                conn.execute("ALTER TABLE cms_contact_info ADD COLUMN description TEXT")
                conn.commit()
            except sqlite3.OperationalError:
                pass
            try:
                conn.execute("ALTER TABLE cms_contact_info ADD COLUMN show_in_get_in_touch INTEGER DEFAULT 0")
                conn.commit()
            except sqlite3.OperationalError:
                pass
            try:
                conn.execute("ALTER TABLE cms_contact_info ADD COLUMN get_in_touch_title TEXT")
                conn.commit()
            except sqlite3.OperationalError:
                pass
            try:
                conn.execute("ALTER TABLE cms_contact_info ADD COLUMN get_in_touch_description TEXT")
                conn.commit()
            except sqlite3.OperationalError:
                pass
            
            contact_rows = conn.execute("""
                SELECT * FROM cms_contact_info 
                ORDER BY sort_order, field_name
            """).fetchall()
            contact_fields = [dict(row) for row in contact_rows]
    except Exception:
        contact_fields = []
    return templates.TemplateResponse(request, "cms/contact_list.html",
        {"request": request, "contact_fields": contact_fields},
    )


@app.post("/admin/cms/contact/save")
def cms_contact_save(
    contact_id: str = Form(None),
    field_name: str = Form(...),
    label: str = Form(...),
    value: str = Form(...),
    field_type: str = Form("text"),
    icon: str = Form(""),
    description: str = Form(""),
    is_public: str = Form(None),  # Changed to Optional[str] to handle unchecked checkbox
    show_in_get_in_touch: str = Form(None),
    get_in_touch_title: str = Form(""),
    get_in_touch_description: str = Form(""),
    sort_order: int = Form(0),
) -> RedirectResponse:
    """Save contact info field (create or update)"""
    pk = _optional_int(contact_id) if contact_id else None
    
    # Checkbox sends "true" when checked, None when unchecked
    is_public_value = 1 if is_public == "true" else 0
    show_in_get_in_touch_value = 1 if show_in_get_in_touch == "true" else 0
    
    with get_conn() as conn:
        # Ensure new columns exist (for migration)
        try:
            conn.execute("ALTER TABLE cms_contact_info ADD COLUMN description TEXT")
        except sqlite3.OperationalError:
            pass  # Column already exists
        try:
            conn.execute("ALTER TABLE cms_contact_info ADD COLUMN show_in_get_in_touch INTEGER DEFAULT 0")
        except sqlite3.OperationalError:
            pass  # Column already exists
        try:
            conn.execute("ALTER TABLE cms_contact_info ADD COLUMN get_in_touch_title TEXT")
        except sqlite3.OperationalError:
            pass  # Column already exists
        try:
            conn.execute("ALTER TABLE cms_contact_info ADD COLUMN get_in_touch_description TEXT")
        except sqlite3.OperationalError:
            pass  # Column already exists
        
        if pk:
            # Update existing
            conn.execute("""
                UPDATE cms_contact_info 
                SET field_name = ?, label = ?, value = ?, field_type = ?, 
                    icon = ?, description = ?, is_public = ?, show_in_get_in_touch = ?,
                    get_in_touch_title = ?, get_in_touch_description = ?, sort_order = ?, updated_at = datetime('now')
                WHERE id = ?
            """, (
                field_name.strip(),
                label.strip(),
                value.strip(),
                field_type,
                icon.strip(),
                description.strip() if description else None,
                is_public_value,
                show_in_get_in_touch_value,
                get_in_touch_title.strip() if get_in_touch_title else None,
                get_in_touch_description.strip() if get_in_touch_description else None,
                sort_order,
                pk,
            ))
        else:
            # Create new
            conn.execute("""
                INSERT INTO cms_contact_info 
                (field_name, label, value, field_type, icon, description, is_public, show_in_get_in_touch, get_in_touch_title, get_in_touch_description, sort_order, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
            """, (
                field_name.strip(),
                label.strip(),
                value.strip(),
                field_type,
                icon.strip(),
                description.strip() if description else None,
                is_public_value,
                show_in_get_in_touch_value,
                get_in_touch_title.strip() if get_in_touch_title else None,
                get_in_touch_description.strip() if get_in_touch_description else None,
                sort_order,
            ))
        conn.commit()
    
    return RedirectResponse(url="/admin/cms/contact", status_code=303)


@app.post("/admin/cms/contact/reorder")
def cms_contact_reorder(
    request: Request,
    contact_orders: str = Form(...),  # JSON string: {"1": 1, "2": 2, ...}
) -> JSONResponse:
    import json
    from datetime import datetime
    
    try:
        orders = json.loads(contact_orders)
        with get_conn() as conn:
            now = datetime.now().isoformat()
            for contact_id, order in orders.items():
                conn.execute("""
                    UPDATE cms_contact_info
                    SET sort_order = ?, updated_at = ?
                    WHERE id = ?
                """, (order, now, int(contact_id)))
            conn.commit()
        return JSONResponse(content={"success": True})
    except Exception as e:
        return JSONResponse(content={"success": False, "error": str(e)}, status_code=500)


@app.post("/admin/cms/contact/delete")
def cms_contact_delete(
    contact_id: str = Form(...),
) -> RedirectResponse:
    """Delete contact info field"""
    pk = _optional_int(contact_id)
    if pk is None:
        raise HTTPException(status_code=400, detail="Invalid contact ID.")
    with get_conn() as conn:
        conn.execute("DELETE FROM cms_contact_info WHERE id = ?", (pk,))
        conn.commit()
    return RedirectResponse(url="/admin/cms/contact", status_code=303)


@app.get("/api/references")
def api_references() -> JSONResponse:
    """API endpoint to fetch all references for frontend"""
    try:
        with get_conn() as conn:
            references = conn.execute("""
                SELECT 
                    id,
                    person_name,
                    company,
                    connection_type,
                    reference_text,
                    title,
                    created_at
                FROM ref_entries
                ORDER BY created_at DESC, id DESC
            """).fetchall()
        
        result = []
        for ref in references:
            connection_types = []
            if ref["connection_type"]:
                try:
                    connection_types = json.loads(ref["connection_type"])
                except json.JSONDecodeError:
                    pass
            
            # Generate avatar initials
            initials = "".join([name[0].upper() for name in ref["person_name"].split()[:2]])
            
            result.append({
                "id": ref["id"],
                "name": ref["person_name"],
                "title": ref["title"] or "",
                "company": ref["company"] or "",
                "relationship": ", ".join(connection_types) if connection_types else "",
                "quote": ref["reference_text"],
                "avatar": f"https://placehold.co/60x60/6366f1/fff?text={initials}",
            })
        
        return JSONResponse(content={"references": result})
    except Exception as e:
        return JSONResponse(content={"references": [], "error": str(e)}, status_code=500)

# ============================================================================
# Tech Skills System Routes
# ============================================================================

SKILL_LEVELS = ["Beginner", "Learning", "Medium", "Advanced", "Expert"]


def ensure_tech_skills_categories() -> None:
    """Initialize default categories if they don't exist"""
    # Tech Skills database now handled by unified database
    conn = get_conn()
    try:
        existing = conn.execute("SELECT COUNT(*) as count FROM tech_skill_categories").fetchone()
        if existing["count"] == 0:
            default_categories = [
                ("Languages", 1),
                ("Frontend Frameworks", 2),
                ("Mobile Frameworks", 3),
                ("Frontend Technologies", 4),
                ("Backend Frameworks & Platforms", 5),
                ("Messaging & Queuing", 6),
                ("CMS & eCommerce", 7),
                ("APIs & Integrations", 8),
                ("Business Integrations", 9),
                ("Package Managers", 10),
                ("Databases", 11),
                ("Cloud & Infrastructure", 12),
                ("DevOps & Deployment", 13),
                ("Operating Systems", 14),
                ("Development Tools", 15),
                ("Project Management", 16),
                ("Design Tools", 17),
                ("Productivity Tools", 18),
                ("Video & Audio", 19),
                ("Communications", 20),
                ("Performance & Monitoring", 21),
                ("Marketing & Analytics", 22),
                ("Payments Processing", 23),
                ("Enterprise Systems", 24),
                ("Hardware & IoT", 25),
                ("Security & Infrastructure", 26),
                ("Homelab", 27),
                ("Creative & Personal", 28),
            ]
            from datetime import datetime
            now = datetime.now().isoformat()
            for name, order in default_categories:
                # Check if category already exists before inserting
                cursor = conn.execute("SELECT id FROM tech_skill_categories WHERE name = ?", (name,))
                if not cursor.fetchone():
                    conn.execute("""
                        INSERT INTO tech_skill_categories (name, display_order, created_at, updated_at)
                        VALUES (?, ?, ?, ?)
                    """, (name, order, now, now))
            conn.commit()
    finally:
        conn.close()


# ============================================================================
# Category Management Routes
# ============================================================================

@app.get("/admin/tech-skills/categories")
def tech_skill_categories_list(request: Request) -> Any:
    try:
        ensure_tech_skills_categories()
        with get_conn() as conn:
            categories_rows = conn.execute("""
                SELECT 
                    id,
                    name,
                    display_order,
                    created_at,
                    updated_at,
                    (SELECT COUNT(*) FROM tech_skills WHERE category_id = tech_skill_categories.id) as skill_count
                FROM tech_skill_categories
                ORDER BY display_order, name
            """).fetchall()
        
        # Convert rows to dicts for JSON serialization
        categories = [dict(row) for row in categories_rows]
        
        return templates.TemplateResponse(request, "tech_skill_categories_list.html",
            {
                "request": request,
                "categories": categories,
                "categories_payload": categories,  # For Alpine.js
            },
        )
    except Exception as e:
        import traceback
        import sys
        error_details = traceback.format_exc()
        print(f"Error in tech_skill_categories_list: {error_details}", file=sys.stderr)
        # Return a simple error response
        from fastapi.responses import HTMLResponse
        return HTMLResponse(
            content=f"""
            <html>
                <head><title>Error</title></head>
                <body>
                    <h1>Error Loading Categories</h1>
                    <p>{str(e)}</p>
                    <pre>{error_details}</pre>
                </body>
            </html>
            """,
            status_code=500
        )


@app.get("/admin/tech-skills/categories/new")
def tech_skill_category_new(request: Request) -> Any:
    ensure_tech_skills_categories()
    with get_conn() as conn:
        max_order = conn.execute("SELECT COALESCE(MAX(display_order), 0) as max_order FROM tech_skill_categories").fetchone()
        next_order = (max_order["max_order"] or 0) + 1
    
    return templates.TemplateResponse(request, "tech_skill_category_edit.html",
        {
            "request": request,
            "category": None,
            "next_order": next_order,
        },
    )


@app.get("/admin/tech-skills/categories/{category_id}")
def tech_skill_category_edit(request: Request, category_id: int) -> Any:
    ensure_tech_skills_categories()
    with get_conn() as conn:
        category_row = conn.execute("SELECT * FROM tech_skill_categories WHERE id = ?", (category_id,)).fetchone()
        if not category_row:
            raise HTTPException(status_code=404, detail="Category not found")
        
        category = dict(category_row)
    
    return templates.TemplateResponse(request, "tech_skill_category_edit.html",
        {
            "request": request,
            "category": category,
            "next_order": None,
        },
    )


@app.post("/admin/tech-skills/categories/save")
def tech_skill_category_save(
    request: Request,
    category_id: str | None = Form(None),
    name: str = Form(...),
    display_order: int = Form(...),
) -> RedirectResponse:
    from datetime import datetime
    
    ensure_tech_skills_categories()
    with get_conn() as conn:
        now = datetime.now().isoformat()
        
        if category_id:
            category_id_int = int(category_id)
            conn.execute("""
                UPDATE tech_skill_categories
                SET name = ?, display_order = ?, updated_at = ?
                WHERE id = ?
            """, (
                name.strip(),
                display_order,
                now,
                category_id_int,
            ))
            conn.commit()
        else:
            cursor = conn.execute("""
                INSERT INTO tech_skill_categories (name, display_order, created_at, updated_at)
                VALUES (?, ?, ?, ?)
            """, (
                name.strip(),
                display_order,
                now,
                now,
            ))
            conn.commit()
            category_id_int = cursor.lastrowid
    
    return RedirectResponse(url="/admin/tech-skills/categories", status_code=303)


@app.post("/admin/tech-skills/categories/reorder")
def tech_skill_categories_reorder(
    request: Request,
    category_orders: str = Form(...),  # JSON string: {"1": 1, "2": 2, ...}
) -> JSONResponse:
    import json
    from datetime import datetime
    
    ensure_tech_skills_categories()
    try:
        orders = json.loads(category_orders)
        with get_conn() as conn:
            now = datetime.now().isoformat()
            for cat_id, order in orders.items():
                conn.execute("""
                    UPDATE tech_skill_categories
                    SET display_order = ?, updated_at = ?
                    WHERE id = ?
                """, (order, now, int(cat_id)))
            conn.commit()
        return JSONResponse(content={"success": True})
    except Exception as e:
        return JSONResponse(content={"success": False, "error": str(e)}, status_code=500)


@app.post("/admin/tech-skills/categories/{category_id}/delete")
def tech_skill_category_delete(request: Request, category_id: int) -> RedirectResponse:
    ensure_tech_skills_categories()
    with get_conn() as conn:
        # Check if category has skills
        skill_count = conn.execute("SELECT COUNT(*) as count FROM tech_skills WHERE category_id = ?", (category_id,)).fetchone()
        if skill_count["count"] > 0:
            # Don't delete, redirect with error message
            return RedirectResponse(url="/admin/tech-skills/categories?error=Cannot delete category with existing skills", status_code=303)
        
        conn.execute("DELETE FROM tech_skill_categories WHERE id = ?", (category_id,))
        conn.commit()
    
    return RedirectResponse(url="/admin/tech-skills/categories", status_code=303)


@app.get("/admin/tech-skills")
def tech_skills_list(request: Request) -> Any:
    ensure_tech_skills_categories()
    try:
        with get_conn() as conn:
            skills_rows = conn.execute("""
                SELECT 
                    ts.id,
                    ts.skill_name,
                    ts.logo_url,
                    ts.description,
                    ts.skill_level,
                    ts.years_usage,
                    ts.num_projects,
                    ts.category_id,
                    c.name as category_name,
                    ts.created_at,
                    ts.updated_at
                FROM tech_skills ts
                LEFT JOIN tech_skill_categories c ON ts.category_id = c.id
                ORDER BY c.display_order, c.name, ts.skill_name
            """).fetchall()
        
        # Convert rows to dicts for JSON serialization
        skills = [dict(row) for row in skills_rows]
        
        # Get unique categories and skill levels for filters
        categories = conn.execute("""
            SELECT DISTINCT c.id, c.name, c.display_order
            FROM tech_skill_categories c
            INNER JOIN tech_skills ts ON ts.category_id = c.id
            ORDER BY c.display_order, c.name
        """).fetchall()
        
        unique_levels = conn.execute("""
            SELECT DISTINCT skill_level
            FROM tech_skills
            ORDER BY 
                CASE skill_level
                    WHEN 'Expert' THEN 1
                    WHEN 'Advanced' THEN 2
                    WHEN 'Medium' THEN 3
                    WHEN 'Learning' THEN 4
                    WHEN 'Beginner' THEN 5
                    ELSE 6
                END
        """).fetchall()
        
    except Exception:
        skills = []
        categories = []
        unique_levels = []
    
    return templates.TemplateResponse(request, "tech_skills_list.html",
        {
            "request": request,
            "skills": skills,
            "skills_payload": skills,  # For Alpine.js
            "categories": [dict(cat) for cat in categories],
            "skill_levels": [level["skill_level"] for level in unique_levels],
        },
    )


@app.get("/admin/tech-skills/new")
def tech_skill_new(request: Request) -> Any:
    ensure_tech_skills_categories()
    with get_conn() as conn:
        categories = conn.execute("""
            SELECT id, name, display_order
            FROM tech_skill_categories
            ORDER BY display_order, name
        """).fetchall()
    
    return templates.TemplateResponse(request, "tech_skill_edit.html",
        {
            "request": request,
            "skill": None,
            "categories": categories,
            "skill_levels": SKILL_LEVELS,
        },
    )


@app.get("/admin/tech-skills/{skill_id}")
def tech_skill_edit(request: Request, skill_id: int) -> Any:
    ensure_tech_skills_categories()
    with get_conn() as conn:
        skill_row = conn.execute("SELECT * FROM tech_skills WHERE id = ?", (skill_id,)).fetchone()
        if not skill_row:
            raise HTTPException(status_code=404, detail="Tech skill not found")
        
        skill = dict(skill_row)
        
        categories = conn.execute("""
            SELECT id, name, display_order
            FROM tech_skill_categories
            ORDER BY display_order, name
        """).fetchall()
    
    return templates.TemplateResponse(request, "tech_skill_edit.html",
        {
            "request": request,
            "skill": skill,
            "categories": categories,
            "skill_levels": SKILL_LEVELS,
        },
    )


@app.post("/admin/tech-skills/save")
def tech_skill_save(
    request: Request,
    skill_id: str | None = Form(None),
    skill_name: str = Form(...),
    logo_url: str | None = Form(None),
    description: str | None = Form(None),
    skill_level: str = Form(...),
    years_usage: str | None = Form(None),
    num_projects: str | None = Form(None),
    category_id: str = Form(...),
) -> RedirectResponse:
    from datetime import datetime

    ensure_tech_skills_categories()
    with get_conn() as conn:
        now = datetime.now().isoformat()
        category_id_int = int(category_id)

        if skill_id:
            skill_id_int = int(skill_id)
            conn.execute("""
                UPDATE tech_skills
                SET skill_name = ?, logo_url = ?, description = ?, skill_level = ?,
                    years_usage = ?, num_projects = ?, category_id = ?, updated_at = ?
                WHERE id = ?
            """, (
                skill_name.strip(),
                logo_url.strip() if logo_url else None,
                description.strip() if description else None,
                skill_level,
                years_usage.strip() if years_usage else None,
                num_projects.strip() if num_projects else None,
                category_id_int,
                now,
                skill_id_int,
            ))
            conn.commit()
        else:
            cursor = conn.execute("""
                INSERT INTO tech_skills (
                    skill_name, logo_url, description, skill_level,
                    years_usage, num_projects, category_id, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                skill_name.strip(),
                logo_url.strip() if logo_url else None,
                description.strip() if description else None,
                skill_level,
                years_usage.strip() if years_usage else None,
                num_projects.strip() if num_projects else None,
                category_id_int,
                now,
                now,
            ))
            conn.commit()
            skill_id_int = cursor.lastrowid

    return RedirectResponse(url="/admin/tech-skills", status_code=303)


@app.get("/admin/tech-skills/images/browse")
def tech_skills_images_browse() -> JSONResponse:
    """List all available images from assets/images/skills directory"""
    images = []
    skills_dir = ROOT / "assets" / "images" / "skills"

    if skills_dir.exists() and skills_dir.is_dir():
        # Scan all subdirectories recursively
        for item in skills_dir.rglob("*"):
            if item.is_file() and item.suffix.lower() in IMAGE_EXTENSIONS:
                # Get relative path from assets/images directory
                relative_path = item.relative_to(ROOT / "assets" / "images")
                url = f"/assets/images/{relative_path.as_posix()}"
                images.append({
                    "url": url,
                    "filename": item.name,
                    "path": str(relative_path),
                    "size": item.stat().st_size
                })

    # Sort by filename
    images.sort(key=lambda x: x["filename"].lower())

    return JSONResponse(content={"images": images})


@app.post("/admin/tech-skills/delete")
def tech_skill_delete(
    request: Request,
    skill_id: str = Form(...),
) -> RedirectResponse:
    ensure_tech_skills_categories()
    skill_id_int = int(skill_id)
    with get_conn() as conn:
        # Verify skill exists
        skill_row = conn.execute("SELECT id FROM tech_skills WHERE id = ?", (skill_id_int,)).fetchone()
        if not skill_row:
            raise HTTPException(status_code=404, detail="Tech skill not found")

        conn.execute("DELETE FROM tech_skills WHERE id = ?", (skill_id_int,))
        conn.commit()

    return RedirectResponse(url="/admin/tech-skills", status_code=303)


@app.get("/api/tech-skills")
def api_tech_skills() -> JSONResponse:
    """API endpoint to fetch all tech skills for frontend"""
    try:
        ensure_tech_skills_categories()
        with get_conn() as conn:
            # Get categories ordered by display_order
            categories = conn.execute("""
                SELECT id, name, display_order
                FROM tech_skill_categories
                ORDER BY display_order, name
            """).fetchall()

            # Get skills with category info
            skills = conn.execute("""
                SELECT
                    ts.id,
                    ts.skill_name,
                    ts.logo_url,
                    ts.description,
                    ts.skill_level,
                    ts.years_usage,
                    ts.num_projects,
                    ts.category_id,
                    c.name as category_name
                FROM tech_skills ts
                LEFT JOIN tech_skill_categories c ON ts.category_id = c.id
                ORDER BY c.display_order, c.name, ts.skill_name
            """).fetchall()

        # Build categories list with order
        categories_list = [{"id": cat["id"], "name": cat["name"], "order": cat["display_order"]} for cat in categories]

        # Group skills by category
        skills_by_category = {}
        for skill in skills:
            cat_name = skill["category_name"] or "Uncategorized"
            if cat_name not in skills_by_category:
                skills_by_category[cat_name] = []

            skills_by_category[cat_name].append({
                "name": skill["skill_name"],
                "logo": skill["logo_url"] or "",
                "level": skill["skill_level"],
                "years": skill["years_usage"] or "",
                "projects": skill["num_projects"] or "",
                "description": skill["description"] or "",
            })

        return JSONResponse(content={
            "categories": categories_list,
            "skills": skills_by_category
        })
    except Exception as e:
        return JSONResponse(content={"categories": [], "skills": {}, "error": str(e)}, status_code=500)


# ============================================================================
# Side Projects System Routes
# ============================================================================

def side_project_slugify(value: str) -> str:
    cleaned = "".join(char if char.isalnum() else "-" for char in value.strip().lower())
    while "--" in cleaned:
        cleaned = cleaned.replace("--", "-")
    return cleaned.strip("-")


@app.get("/admin/side-projects")
def side_projects_list(request: Request) -> Any:
    try:
        with get_conn() as conn:
            projects_rows = conn.execute("""
                SELECT
                    sp.*,
                    c.label AS category_label,
                    c.code AS category_code,
                    c.color AS category_color
                FROM side_projects sp
                LEFT JOIN side_project_categories c ON c.id = sp.category_id
                ORDER BY sp.revised_date DESC, sp.posted_date DESC, sp.id DESC
            """).fetchall()
            # Convert Row objects to dictionaries for JSON serialization
            projects = [dict(row) for row in projects_rows]
    except Exception:
        projects = []
    return templates.TemplateResponse(request, "side-projects/side_projects_list.html",
        {"request": request, "projects": projects},
    )


@app.get("/admin/side-projects/categories")
def side_project_categories_list(request: Request) -> Any:
    try:
        with get_conn() as conn:
            categories_rows = conn.execute("""
                SELECT
                    c.*,
                    COUNT(sp.id) AS project_count
                FROM side_project_categories c
                LEFT JOIN side_projects sp ON sp.category_id = c.id
                GROUP BY c.id
                ORDER BY c.display_order, c.label
            """).fetchall()
            # Convert Row objects to dictionaries for JSON serialization
            categories = [dict(row) for row in categories_rows]
    except Exception:
        categories = []
    return templates.TemplateResponse(request, "side-projects/side_project_categories_list.html",
        {"request": request, "categories": categories},
    )


@app.get("/admin/side-projects/new")
def side_project_new(request: Request) -> Any:
    with get_conn() as conn:
        categories = conn.execute("""
            SELECT * FROM side_project_categories
            ORDER BY display_order, label
        """).fetchall()
    return templates.TemplateResponse(request, "side-projects/side_project_edit.html",
        {
            "request": request,
            "project": None,
            "categories": categories,
            "technologies": [],
            "features": [],
            "technical_details": [],
            "images": [],
        },
    )


@app.get("/admin/side-projects/{project_id}")
def side_project_edit(request: Request, project_id: int) -> Any:
    with get_conn() as conn:
        project = conn.execute(
            "SELECT * FROM side_projects WHERE id = ?", (project_id,)
        ).fetchone()
        if not project:
            raise HTTPException(status_code=404, detail="Side project not found")

        categories = conn.execute("""
            SELECT * FROM side_project_categories
            ORDER BY display_order, label
        """).fetchall()

        technologies_rows = conn.execute("""
            SELECT * FROM side_project_technologies
            WHERE project_id = ?
            ORDER BY display_order, name
        """, (project_id,)).fetchall()

        features_rows = conn.execute("""
            SELECT * FROM side_project_features
            WHERE project_id = ?
            ORDER BY display_order, name
        """, (project_id,)).fetchall()

        technical_details_rows = conn.execute("""
            SELECT * FROM side_project_technical_details
            WHERE project_id = ?
            ORDER BY display_order, title
        """, (project_id,)).fetchall()

        images_rows = conn.execute("""
            SELECT * FROM side_project_images
            WHERE project_id = ?
            ORDER BY display_order, id
        """, (project_id,)).fetchall()

    # Convert Row objects to dictionaries for JSON serialization
    technologies = [dict(row) for row in technologies_rows]
    features = [dict(row) for row in features_rows]
    technical_details = [dict(row) for row in technical_details_rows]
    images = [dict(row) for row in images_rows]

    return templates.TemplateResponse(request, "side-projects/side_project_edit.html",
        {
            "request": request,
            "project": project,
            "categories": categories,
            "technologies": technologies,
            "features": features,
            "technical_details": technical_details,
            "images": images,
        },
    )


@app.post("/admin/side-projects/save")
def side_project_save(
    request: Request,
    project_id: str | None = Form(None),
    title: str = Form(...),
    slug: str | None = Form(None),
    category_id: str | None = Form(None),
    description: str | None = Form(None),
    status: str = Form("in development"),
    metrics: str | None = Form(None),
    posted_date: str | None = Form(None),
    revised_date: str | None = Form(None),
    stats: str | None = Form(None),
    technologies: list[str] | None = Form(None),
    technology_icons: list[str] | None = Form(None),
    features: list[str] | None = Form(None),
    feature_descriptions: list[str] | None = Form(None),
    feature_icons: list[str] | None = Form(None),
    technical_detail_titles: list[str] | None = Form(None),
    technical_detail_descriptions: list[str] | None = Form(None),
) -> RedirectResponse:
    today = date.today().isoformat()

    if not slug:
        slug = side_project_slugify(title)

    category_id_val = _optional_int(category_id)

    stats_json = None
    if stats:
        try:
            stats_json = json.dumps(json.loads(stats))
        except json.JSONDecodeError:
            stats_json = None

    with get_conn() as conn:
        if not project_id or project_id == "":
            if not posted_date:
                posted_date = today
            if not revised_date:
                revised_date = today

            cursor = conn.execute("""
                INSERT INTO side_projects
                (category_id, title, slug, description, status, metrics, posted_date, revised_date, stats)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                category_id_val,
                title.strip(),
                slug,
                description.strip() if description else None,
                status,
                metrics.strip() if metrics else None,
                posted_date,
                revised_date,
                stats_json,
            ))
            project_id_int = cursor.lastrowid
        else:
            project_id_int = int(project_id)
            if not revised_date:
                revised_date = today

            conn.execute("""
                UPDATE side_projects
                SET category_id = ?, title = ?, slug = ?, description = ?, status = ?,
                    metrics = ?, revised_date = ?, stats = ?
                WHERE id = ?
            """, (
                category_id_val,
                title.strip(),
                slug,
                description.strip() if description else None,
                status,
                metrics.strip() if metrics else None,
                revised_date,
                stats_json,
                project_id_int,
            ))

        # Delete existing related records
        conn.execute("DELETE FROM side_project_technologies WHERE project_id = ?", (project_id_int,))
        conn.execute("DELETE FROM side_project_features WHERE project_id = ?", (project_id_int,))
        conn.execute("DELETE FROM side_project_technical_details WHERE project_id = ?", (project_id_int,))

        # Insert technologies
        if technologies:
            for idx, tech_name in enumerate(technologies):
                if tech_name and tech_name.strip():
                    tech_icon = ""
                    if technology_icons and idx < len(technology_icons):
                        tech_icon = technology_icons[idx] or ""
                    conn.execute("""
                        INSERT INTO side_project_technologies (project_id, name, icon, display_order)
                        VALUES (?, ?, ?, ?)
                    """, (project_id_int, tech_name.strip(), tech_icon.strip(), idx))

        # Insert features
        if features:
            for idx, feature_name in enumerate(features):
                if feature_name and feature_name.strip():
                    feature_desc = ""
                    feature_icon = ""
                    if feature_descriptions and idx < len(feature_descriptions):
                        feature_desc = feature_descriptions[idx] or ""
                    if feature_icons and idx < len(feature_icons):
                        feature_icon = feature_icons[idx] or ""
                    conn.execute("""
                        INSERT INTO side_project_features (project_id, name, description, icon, display_order)
                        VALUES (?, ?, ?, ?, ?)
                    """, (project_id_int, feature_name.strip(), feature_desc.strip(), feature_icon.strip(), idx))

        # Insert technical details
        if technical_detail_titles:
            for idx, detail_title in enumerate(technical_detail_titles):
                if detail_title and detail_title.strip():
                    detail_desc = ""
                    if technical_detail_descriptions and idx < len(technical_detail_descriptions):
                        detail_desc = technical_detail_descriptions[idx] or ""
                    conn.execute("""
                        INSERT INTO side_project_technical_details (project_id, title, description, display_order)
                        VALUES (?, ?, ?, ?)
                    """, (project_id_int, detail_title.strip(), detail_desc.strip(), idx))

        conn.commit()

    return RedirectResponse(url="/admin/side-projects", status_code=303)


@app.post("/admin/side-projects/images/upload")
async def side_project_image_upload(
    project_id: int = Form(...),
    file: UploadFile = File(...),
    is_cover: bool = Form(False),
) -> RedirectResponse:
    # Validate image upload
    content, ext, error_msg = await _validate_image_upload(file)
    if error_msg:
        return RedirectResponse(
            url=f"/admin/side-projects/{project_id}?error={error_msg.replace(' ', '+')}",
            status_code=303
        )

    project_img_dir = PROJECTS_MEDIA / str(project_id)
    project_img_dir.mkdir(parents=True, exist_ok=True)

    safe_filename = secrets.token_urlsafe(16) + ext
    file_path = project_img_dir / safe_filename
    
    # Ensure we're writing within the intended directory
    try:
        file_path.resolve().relative_to(project_img_dir.resolve())
    except ValueError:
        return RedirectResponse(
            url=f"/admin/side-projects/{project_id}?error=Invalid+file+path",
            status_code=303
        )
    
    url = f"/assets/images/projects/{project_id}/{safe_filename}"

    # Write file
    try:
        with file_path.open("wb") as f:
            f.write(content)
    except Exception as e:
        import sys
        print(f"Error writing file: {e}", file=sys.stderr)
        return RedirectResponse(
            url=f"/admin/side-projects/{project_id}?error=Error+saving+file",
            status_code=303
        )

    with get_conn() as conn:
        # If setting as cover, unset all other cover images for this project
        if is_cover:
            conn.execute("""
                UPDATE side_project_images SET is_cover = 0 WHERE project_id = ?
            """, (project_id,))

        max_order = conn.execute("""
            SELECT COALESCE(MAX(display_order), 0) FROM side_project_images WHERE project_id = ?
        """, (project_id,)).fetchone()[0]

        conn.execute("""
            INSERT INTO side_project_images (project_id, url, alt, is_cover, display_order)
            VALUES (?, ?, ?, ?, ?)
        """, (project_id, url, file.filename, 1 if is_cover else 0, max_order + 1))
        conn.commit()

    return RedirectResponse(url=f"/admin/side-projects/{project_id}?success=Image+uploaded+successfully", status_code=303)


@app.post("/admin/side-projects/images/{image_id}/set-cover")
def side_project_image_set_cover(
    image_id: int,
    is_cover: str = Form("true"),
) -> JSONResponse:
    with get_conn() as conn:
        # Get project_id from image
        image = conn.execute(
            "SELECT project_id FROM side_project_images WHERE id = ?", (image_id,)
        ).fetchone()
        if not image:
            raise HTTPException(status_code=404, detail="Image not found")

        project_id = image["project_id"]

        # Unset all other cover images for this project
        conn.execute("""
            UPDATE side_project_images SET is_cover = 0 WHERE project_id = ?
        """, (project_id,))

        # Set this image as cover
        conn.execute("""
            UPDATE side_project_images SET is_cover = 1 WHERE id = ?
        """, (image_id,))
        conn.commit()

    return JSONResponse(content={"success": True})


@app.post("/admin/side-projects/images/{image_id}/delete")
def side_project_image_delete(image_id: int) -> JSONResponse:
    with get_conn() as conn:
        # Get image info before deleting
        image = conn.execute(
            "SELECT url, project_id FROM side_project_images WHERE id = ?", (image_id,)
        ).fetchone()
        if not image:
            raise HTTPException(status_code=404, detail="Image not found")

        # Delete from database
        conn.execute("DELETE FROM side_project_images WHERE id = ?", (image_id,))
        conn.commit()

        # Delete file if it exists
        if image["url"]:
            # Extract path from URL (e.g., "/assets/images/projects/1/abc123.jpg")
            url_path = image["url"].lstrip("/")
            file_path = ROOT / url_path
            if file_path.exists() and file_path.is_file():
                try:
                    file_path.unlink()
                except Exception:
                    pass  # Continue even if file deletion fails

    return JSONResponse(content={"success": True})


@app.post("/admin/side-projects/images/{image_id}/update")
def side_project_image_update(
    image_id: int,
    alt: str = Form(""),
) -> JSONResponse:
    with get_conn() as conn:
        conn.execute("""
            UPDATE side_project_images SET alt = ? WHERE id = ?
        """, (alt.strip(), image_id))
        conn.commit()

    return JSONResponse(content={"success": True})


@app.get("/admin/side-projects/images/browse")
def side_project_images_browse() -> JSONResponse:
    """List all available images from assets/images/projects directory"""
    images = []
    projects_dir = ROOT / "assets" / "images" / "projects"

    if projects_dir.exists() and projects_dir.is_dir():
        # Scan all subdirectories recursively
        for item in projects_dir.rglob("*"):
            if item.is_file() and item.suffix.lower() in IMAGE_EXTENSIONS:
                # Get relative path from projects directory
                relative_path = item.relative_to(ROOT / "assets" / "images")
                url = f"/assets/images/{relative_path.as_posix()}"
                images.append({
                    "url": url,
                    "filename": item.name,
                    "path": str(relative_path),
                    "size": item.stat().st_size
                })

    # Sort by filename
    images.sort(key=lambda x: x["filename"].lower())

    return JSONResponse(content={"images": images})


@app.post("/admin/side-projects/images/add-existing")
def side_project_image_add_existing(
    project_id: int = Form(...),
    url: str = Form(...),
    alt: str = Form(""),
    is_cover: bool = Form(False),
) -> RedirectResponse:
    """Add an existing image from the file system to a project"""
    with get_conn() as conn:
        # If setting as cover, unset all other cover images for this project
        if is_cover:
            conn.execute("""
                UPDATE side_project_images SET is_cover = 0 WHERE project_id = ?
            """, (project_id,))

        max_order = conn.execute("""
            SELECT COALESCE(MAX(display_order), 0) FROM side_project_images WHERE project_id = ?
        """, (project_id,)).fetchone()[0]

        conn.execute("""
            INSERT INTO side_project_images (project_id, url, alt, is_cover, display_order)
            VALUES (?, ?, ?, ?, ?)
        """, (project_id, url, alt.strip(), 1 if is_cover else 0, max_order + 1))
        conn.commit()

    return RedirectResponse(url=f"/admin/side-projects/{project_id}", status_code=303)


@app.post("/admin/side-projects/categories/new")
def side_project_category_new(
    code: str = Form(...),
    label: str = Form(...),
    description: str = Form(""),
    color: str = Form(""),
    icon: str = Form(""),
    display_order: int = Form(0),
) -> RedirectResponse:
    with get_conn() as conn:
        try:
            conn.execute("""
                INSERT INTO side_project_categories
                (code, label, description, color, icon, display_order)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                code.strip(),
                label.strip(),
                description.strip(),
                color.strip(),
                icon.strip(),
                display_order,
            ))
            conn.commit()
        except sqlite3.IntegrityError as exc:
            raise HTTPException(status_code=400, detail=f"Category code '{code}' already exists") from exc
    return RedirectResponse(url="/admin/side-projects/categories", status_code=303)


@app.post("/admin/side-projects/categories/update")
def side_project_category_update(
    category_id: str = Form(...),
    code: str = Form(...),
    label: str = Form(...),
    description: str = Form(""),
    color: str = Form(""),
    icon: str = Form(""),
    display_order: int = Form(0),
) -> RedirectResponse:
    pk = _optional_int(category_id)
    if pk is None:
        raise HTTPException(status_code=400, detail="Invalid category id.")
    with get_conn() as conn:
        try:
            conn.execute("""
                UPDATE side_project_categories
                SET code = ?, label = ?, description = ?, color = ?, icon = ?, display_order = ?
                WHERE id = ?
            """, (
                code.strip(),
                label.strip(),
                description.strip(),
                color.strip(),
                icon.strip(),
                display_order,
                pk,
            ))
            conn.commit()
        except sqlite3.IntegrityError as exc:
            raise HTTPException(status_code=400, detail=f"Category code '{code}' already exists") from exc
    return RedirectResponse(url="/admin/side-projects/categories", status_code=303)


@app.post("/admin/side-projects/categories/reorder")
def side_project_categories_reorder(
    request: Request,
    category_orders: str = Form(...),  # JSON string: {"1": 1, "2": 2, ...}
) -> JSONResponse:
    import json
    from datetime import datetime
    
    try:
        orders = json.loads(category_orders)
        with get_conn() as conn:
            now = datetime.now().isoformat()
            for cat_id, order in orders.items():
                conn.execute("""
                    UPDATE side_project_categories
                    SET display_order = ?, updated_at = ?
                    WHERE id = ?
                """, (order, now, int(cat_id)))
            conn.commit()
        return JSONResponse(content={"success": True})
    except Exception as e:
        return JSONResponse(content={"success": False, "error": str(e)}, status_code=500)


@app.get("/admin/side-projects/categories/{category_id}")
def side_project_category_edit(request: Request, category_id: int) -> Any:
    with get_conn() as conn:
        category = conn.execute(
            "SELECT * FROM side_project_categories WHERE id = ?", (category_id,)
        ).fetchone()
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
    return templates.TemplateResponse(request, "side-projects/side_project_category_edit.html",
        {"request": request, "category": category},
    )


@app.get("/api/side-projects")
def api_side_projects() -> JSONResponse:
    """API endpoint to fetch all side projects for frontend"""
    try:
        with get_conn() as conn:
            # Get categories - convert Row objects to dicts
            categories_rows = conn.execute("""
                SELECT id, code, label, color, icon, display_order
                FROM side_project_categories
                ORDER BY display_order, label
            """).fetchall()
            categories = [dict(row) for row in categories_rows]

            # Get projects with category info - convert Row objects to dicts
            projects_rows = conn.execute("""
                SELECT
                    sp.*,
                    c.code AS category_code,
                    c.label AS category_label,
                    c.color AS category_color,
                    c.icon AS category_icon
                FROM side_projects sp
                LEFT JOIN side_project_categories c ON sp.category_id = c.id
                ORDER BY sp.revised_date DESC, sp.posted_date DESC, sp.id DESC
            """).fetchall()
            projects = [dict(row) for row in projects_rows]

            # Build projects list with related data
            projects_list = []
            for project in projects:
                # Get technologies - convert Row objects to dicts
                technologies_rows = conn.execute("""
                    SELECT name, icon FROM side_project_technologies
                    WHERE project_id = ? ORDER BY display_order, name
                """, (project["id"],)).fetchall()
                technologies = [dict(row) for row in technologies_rows]

                # Get features - convert Row objects to dicts
                features_rows = conn.execute("""
                    SELECT name, description, icon FROM side_project_features
                    WHERE project_id = ? ORDER BY display_order, name
                """, (project["id"],)).fetchall()
                features = [dict(row) for row in features_rows]

                # Get technical details - convert Row objects to dicts
                technical_details_rows = conn.execute("""
                    SELECT title, description FROM side_project_technical_details
                    WHERE project_id = ? ORDER BY display_order, title
                """, (project["id"],)).fetchall()
                technical_details = [dict(row) for row in technical_details_rows]

                # Get images - convert Row objects to dicts
                images_rows = conn.execute("""
                    SELECT url, alt FROM side_project_images
                    WHERE project_id = ? ORDER BY display_order, id
                """, (project["id"],)).fetchall()
                images = [dict(row) for row in images_rows]

                # Parse stats JSON
                stats = {}
                if project.get("stats"):
                    try:
                        stats = json.loads(project["stats"])
                    except json.JSONDecodeError:
                        stats = {}

                projects_list.append({
                    "id": project["id"],
                    "name": project["title"],
                    "category": project.get("category_label") or "Uncategorized",
                    "category_code": project.get("category_code") or "",
                    "status": project.get("status") or "in development",
                    "lastUpdated": project.get("revised_date") or project.get("posted_date") or "",
                    "description": project.get("description") or "",
                    "metrics": project.get("metrics") or "",
                    "technologies": [{"name": t.get("name") or "", "icon": t.get("icon") or ""} for t in technologies],
                    "features": [{"name": f.get("name") or "", "icon": f.get("icon") or "", "description": f.get("description") or ""} for f in features],
                    "technicalDetails": [{"title": td.get("title") or "", "description": td.get("description") or ""} for td in technical_details],
                    "stats": stats,
                    "images": [{"url": img.get("url") or "", "alt": img.get("alt") or ""} for img in images],
                    "gallery": [{"url": img.get("url") or "", "alt": img.get("alt") or ""} for img in images]
                })

            # Group projects by category code
            projects_by_category = {}
            for project in projects_list:
                cat_code = project["category_code"] or "uncategorized"
                if cat_code not in projects_by_category:
                    projects_by_category[cat_code] = []
                projects_by_category[cat_code].append(project)

            # Build categories list
            categories_list = [{
                "code": cat.get("code") or "",
                "label": cat.get("label") or "",
                "color": cat.get("color") or "",
                "icon": cat.get("icon") or "",
                "count": len(projects_by_category.get(cat.get("code") or "", []))
            } for cat in categories]

        return JSONResponse(content={
            "categories": categories_list,
            "projects": projects_by_category
        })
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        return JSONResponse(content={"categories": [], "projects": {}, "error": str(e), "traceback": error_trace}, status_code=500)


# ============================================================================
# Magento Modules System Routes
# ============================================================================

@app.get("/admin/magento")
def magento_modules_list(request: Request) -> Any:
    try:
        with get_conn() as conn:
            modules_rows = conn.execute("""
                SELECT
                    mm.*,
                    c.label AS category_label,
                    c.code AS category_code,
                    c.color AS category_color
                FROM magento_modules mm
                LEFT JOIN magento_module_categories c ON c.id = mm.category_id
                ORDER BY mm.revised_date DESC, mm.posted_date DESC, mm.id DESC
            """).fetchall()
            # Convert Row objects to dictionaries for JSON serialization
            modules = [dict(row) for row in modules_rows]
    except Exception:
        modules = []
    return templates.TemplateResponse(request, "magento/magento_modules_list.html",
        {"request": request, "modules": modules},
    )


@app.get("/admin/magento/categories")
def magento_module_categories_list(request: Request) -> Any:
    try:
        with get_conn() as conn:
            categories_rows = conn.execute("""
                SELECT
                    c.*,
                    COUNT(mm.id) AS module_count
                FROM magento_module_categories c
                LEFT JOIN magento_modules mm ON mm.category_id = c.id
                GROUP BY c.id
                ORDER BY c.display_order, c.label
            """).fetchall()
            # Convert Row objects to dictionaries for JSON serialization
            categories = [dict(row) for row in categories_rows]
    except Exception:
        categories = []
    return templates.TemplateResponse(request, "magento/magento_module_categories_list.html",
        {"request": request, "categories": categories},
    )


@app.get("/admin/magento/new")
def magento_module_new(request: Request) -> Any:
    with get_conn() as conn:
        categories = conn.execute("""
            SELECT * FROM magento_module_categories
            ORDER BY display_order, label
        """).fetchall()
    return templates.TemplateResponse(request, "magento/magento_module_edit.html",
        {
            "request": request,
            "module": None,
            "categories": categories,
            "technologies": [],
            "features": [],
            "technical_details": [],
            "images": [],
        },
    )


@app.get("/admin/magento/{module_id}")
def magento_module_edit(request: Request, module_id: int) -> Any:
    with get_conn() as conn:
        module = conn.execute(
            "SELECT * FROM magento_modules WHERE id = ?", (module_id,)
        ).fetchone()
        if not module:
            raise HTTPException(status_code=404, detail="Magento module not found")

        categories = conn.execute("""
            SELECT * FROM magento_module_categories
            ORDER BY display_order, label
        """).fetchall()

        technologies_rows = conn.execute("""
            SELECT * FROM magento_module_technologies
            WHERE module_id = ?
            ORDER BY display_order, name
        """, (module_id,)).fetchall()

        features_rows = conn.execute("""
            SELECT * FROM magento_module_features
            WHERE module_id = ?
            ORDER BY display_order, name
        """, (module_id,)).fetchall()

        technical_details_rows = conn.execute("""
            SELECT * FROM magento_module_technical_details
            WHERE module_id = ?
            ORDER BY display_order, title
        """, (module_id,)).fetchall()

        images_rows = conn.execute("""
            SELECT * FROM magento_module_images
            WHERE module_id = ?
            ORDER BY display_order, id
        """, (module_id,)).fetchall()

    # Convert Row objects to dictionaries for JSON serialization
    technologies = [dict(row) for row in technologies_rows]
    features = [dict(row) for row in features_rows]
    technical_details = [dict(row) for row in technical_details_rows]
    images = [dict(row) for row in images_rows]

    return templates.TemplateResponse(request, "magento/magento_module_edit.html",
        {
            "request": request,
            "module": module,
            "categories": categories,
            "technologies": technologies,
            "features": features,
            "technical_details": technical_details,
            "images": images,
        },
    )


@app.post("/admin/magento/save")
def magento_module_save(
    request: Request,
    module_id: str | None = Form(None),
    title: str = Form(...),
    slug: str | None = Form(None),
    category_id: str | None = Form(None),
    description: str | None = Form(None),
    status: str = Form("in development"),
    metrics: str | None = Form(None),
    version: str | None = Form(None),
    posted_date: str | None = Form(None),
    revised_date: str | None = Form(None),
    stats: str | None = Form(None),
    technologies: list[str] | None = Form(None),
    technology_icons: list[str] | None = Form(None),
    features: list[str] | None = Form(None),
    feature_descriptions: list[str] | None = Form(None),
    feature_icons: list[str] | None = Form(None),
    technical_detail_titles: list[str] | None = Form(None),
    technical_detail_descriptions: list[str] | None = Form(None),
) -> RedirectResponse:
    today = date.today().isoformat()

    if not slug:
        slug = magento_slugify(title)

    category_id_val = _optional_int(category_id)

    stats_json = None
    if stats:
        try:
            stats_json = json.dumps(json.loads(stats))
        except json.JSONDecodeError:
            stats_json = None

    with get_conn() as conn:
        if not module_id or module_id == "":
            if not posted_date:
                posted_date = today
            if not revised_date:
                revised_date = today

            cursor = conn.execute("""
                INSERT INTO magento_modules
                (category_id, title, slug, version, description, status, metrics, posted_date, revised_date, stats)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                category_id_val,
                title.strip(),
                slug,
                version.strip() if version else None,
                description.strip() if description else None,
                status,
                metrics.strip() if metrics else None,
                posted_date,
                revised_date,
                stats_json,
            ))
            module_id_int = cursor.lastrowid
        else:
            module_id_int = int(module_id)
            if not revised_date:
                revised_date = today

            conn.execute("""
                UPDATE magento_modules
                SET category_id = ?, title = ?, slug = ?, version = ?, description = ?, status = ?,
                    metrics = ?, revised_date = ?, stats = ?
                WHERE id = ?
            """, (
                category_id_val,
                title.strip(),
                slug,
                version.strip() if version else None,
                description.strip() if description else None,
                status,
                metrics.strip() if metrics else None,
                revised_date,
                stats_json,
                module_id_int,
            ))

        # Delete existing related records
        conn.execute("DELETE FROM magento_module_technologies WHERE module_id = ?", (module_id_int,))
        conn.execute("DELETE FROM magento_module_features WHERE module_id = ?", (module_id_int,))
        conn.execute("DELETE FROM magento_module_technical_details WHERE module_id = ?", (module_id_int,))

        # Insert technologies
        if technologies:
            for idx, tech_name in enumerate(technologies):
                if tech_name and tech_name.strip():
                    tech_icon = ""
                    if technology_icons and idx < len(technology_icons):
                        tech_icon = technology_icons[idx] or ""
                    conn.execute("""
                        INSERT INTO magento_module_technologies (module_id, name, icon, display_order)
                        VALUES (?, ?, ?, ?)
                    """, (module_id_int, tech_name.strip(), tech_icon.strip(), idx))

        # Insert features
        if features:
            for idx, feature_name in enumerate(features):
                if feature_name and feature_name.strip():
                    feature_desc = ""
                    feature_icon = ""
                    if feature_descriptions and idx < len(feature_descriptions):
                        feature_desc = feature_descriptions[idx] or ""
                    if feature_icons and idx < len(feature_icons):
                        feature_icon = feature_icons[idx] or ""
                    conn.execute("""
                        INSERT INTO magento_module_features (module_id, name, description, icon, display_order)
                        VALUES (?, ?, ?, ?, ?)
                    """, (module_id_int, feature_name.strip(), feature_desc.strip(), feature_icon.strip(), idx))

        # Insert technical details
        if technical_detail_titles:
            for idx, detail_title in enumerate(technical_detail_titles):
                if detail_title and detail_title.strip():
                    detail_desc = ""
                    if technical_detail_descriptions and idx < len(technical_detail_descriptions):
                        detail_desc = technical_detail_descriptions[idx] or ""
                    conn.execute("""
                        INSERT INTO magento_module_technical_details (module_id, title, description, display_order)
                        VALUES (?, ?, ?, ?)
                    """, (module_id_int, detail_title.strip(), detail_desc.strip(), idx))

        conn.commit()

    return RedirectResponse(url="/admin/magento", status_code=303)


@app.post("/admin/magento/images/upload")
async def magento_module_image_upload(
    module_id: int = Form(...),
    file: UploadFile = File(...),
    is_cover: bool = Form(False),
) -> RedirectResponse:
    # Validate image upload
    content, ext, error_msg = await _validate_image_upload(file)
    if error_msg:
        return RedirectResponse(
            url=f"/admin/magento/{module_id}?error={error_msg.replace(' ', '+')}",
            status_code=303
        )

    module_img_dir = MAGENTO_MEDIA / str(module_id)
    module_img_dir.mkdir(parents=True, exist_ok=True)

    safe_filename = secrets.token_urlsafe(16) + ext
    file_path = module_img_dir / safe_filename
    
    # Ensure we're writing within the intended directory
    try:
        file_path.resolve().relative_to(module_img_dir.resolve())
    except ValueError:
        return RedirectResponse(
            url=f"/admin/magento/{module_id}?error=Invalid+file+path",
            status_code=303
        )
    
    url = f"/assets/images/magento/{module_id}/{safe_filename}"

    # Write file
    try:
        with file_path.open("wb") as f:
            f.write(content)
    except Exception as e:
        import sys
        print(f"Error writing file: {e}", file=sys.stderr)
        return RedirectResponse(
            url=f"/admin/magento/{module_id}?error=Error+saving+file",
            status_code=303
        )

    with get_conn() as conn:
        # If setting as cover, unset all other cover images for this module
        if is_cover:
            conn.execute("""
                UPDATE magento_module_images SET is_cover = 0 WHERE module_id = ?
            """, (module_id,))

        max_order = conn.execute("""
            SELECT COALESCE(MAX(display_order), 0) FROM magento_module_images WHERE module_id = ?
        """, (module_id,)).fetchone()[0]

        conn.execute("""
            INSERT INTO magento_module_images (module_id, url, alt, is_cover, display_order)
            VALUES (?, ?, ?, ?, ?)
        """, (module_id, url, file.filename, 1 if is_cover else 0, max_order + 1))
        conn.commit()

    return RedirectResponse(url=f"/admin/magento/{module_id}?success=Image+uploaded+successfully", status_code=303)


@app.post("/admin/magento/images/{image_id}/set-cover")
def magento_module_image_set_cover(
    image_id: int,
    is_cover: str = Form("true"),
) -> JSONResponse:
    with get_conn() as conn:
        # Get module_id and current is_cover status from image
        image = conn.execute(
            "SELECT module_id, is_cover FROM magento_module_images WHERE id = ?", (image_id,)
        ).fetchone()
        if not image:
            raise HTTPException(status_code=404, detail="Image not found")

        module_id = image["module_id"]
        current_cover_status = image["is_cover"]
        
        # Convert form value to boolean
        set_as_cover = is_cover.lower() in ("true", "1", "yes", "on")
        
        # If setting as cover, unset all other cover images for this module
        if set_as_cover:
            conn.execute("""
                UPDATE magento_module_images SET is_cover = 0 WHERE module_id = ?
            """, (module_id,))
            # Set this image as cover
            conn.execute("""
                UPDATE magento_module_images SET is_cover = 1 WHERE id = ?
            """, (image_id,))
        else:
            # Unset this image as cover
            conn.execute("""
                UPDATE magento_module_images SET is_cover = 0 WHERE id = ?
            """, (image_id,))
        conn.commit()

    return JSONResponse(content={"success": True, "is_cover": set_as_cover})


@app.post("/admin/magento/images/{image_id}/delete")
def magento_module_image_delete(image_id: int) -> JSONResponse:
    """Remove image from module but keep the file in the system"""
    with get_conn() as conn:
        # Get image info before deleting
        image = conn.execute(
            "SELECT url, module_id FROM magento_module_images WHERE id = ?", (image_id,)
        ).fetchone()
        if not image:
            raise HTTPException(status_code=404, detail="Image not found")

        # Delete from database only (do NOT delete the file)
        conn.execute("DELETE FROM magento_module_images WHERE id = ?", (image_id,))
        conn.commit()

        # Note: We intentionally do NOT delete the file from the filesystem
        # The image remains available in the system for potential reuse

    return JSONResponse(content={"success": True})


@app.post("/admin/magento/images/{image_id}/update")
def magento_module_image_update(
    image_id: int,
    alt: str = Form(""),
) -> JSONResponse:
    with get_conn() as conn:
        conn.execute("""
            UPDATE magento_module_images SET alt = ? WHERE id = ?
        """, (alt.strip(), image_id))
        conn.commit()

    return JSONResponse(content={"success": True})


@app.get("/admin/magento/images/browse")
def magento_module_images_browse() -> JSONResponse:
    """List all available images from assets/images/magento-modules and other common directories"""
    images = []
    
    # Scan assets/images/magento-modules directory
    magento_modules_dir = ROOT / "assets" / "images" / "magento-modules"
    if magento_modules_dir.exists() and magento_modules_dir.is_dir():
        for item in magento_modules_dir.rglob("*"):
            if item.is_file() and item.suffix.lower() in IMAGE_EXTENSIONS:
                relative_path = item.relative_to(ROOT / "assets" / "images")
                url = f"/assets/images/{relative_path.as_posix()}"
                images.append({
                    "url": url,
                    "filename": item.name,
                    "path": str(relative_path),
                    "size": item.stat().st_size,
                    "directory": "magento-modules"
                })
    
    # Also scan assets/images/projects directory (common alternative)
    projects_dir = ROOT / "assets" / "images" / "projects"
    if projects_dir.exists() and projects_dir.is_dir():
        for item in projects_dir.rglob("*"):
            if item.is_file() and item.suffix.lower() in IMAGE_EXTENSIONS:
                relative_path = item.relative_to(ROOT / "assets" / "images")
                url = f"/assets/images/{relative_path.as_posix()}"
                images.append({
                    "url": url,
                    "filename": item.name,
                    "path": str(relative_path),
                    "size": item.stat().st_size,
                    "directory": "projects"
                })

    # Sort by directory, then filename
    images.sort(key=lambda x: (x.get("directory", ""), x["filename"].lower()))

    return JSONResponse(content={"images": images})


@app.post("/admin/magento/images/add-existing")
def magento_module_image_add_existing(
    module_id: int = Form(...),
    url: str = Form(...),
    alt: str = Form(""),
    is_cover: bool = Form(False),
) -> RedirectResponse:
    """Add an existing image from the file system to a module"""
    with get_conn() as conn:
        # If setting as cover, unset all other cover images for this module
        if is_cover:
            conn.execute("""
                UPDATE magento_module_images SET is_cover = 0 WHERE module_id = ?
            """, (module_id,))

        max_order = conn.execute("""
            SELECT COALESCE(MAX(display_order), 0) FROM magento_module_images WHERE module_id = ?
        """, (module_id,)).fetchone()[0]

        conn.execute("""
            INSERT INTO magento_module_images (module_id, url, alt, is_cover, display_order)
            VALUES (?, ?, ?, ?, ?)
        """, (module_id, url, alt.strip(), 1 if is_cover else 0, max_order + 1))
        conn.commit()

    return RedirectResponse(url=f"/admin/magento/{module_id}", status_code=303)


@app.get("/admin/magento/categories/new")
def magento_module_category_new_form(request: Request) -> Any:
    return templates.TemplateResponse(request, "magento/magento_module_category_edit.html",
        {"request": request, "category": None},
    )


@app.post("/admin/magento/categories/new")
def magento_module_category_new(
    code: str = Form(...),
    label: str = Form(...),
    description: str = Form(""),
    color: str = Form(""),
    icon: str = Form(""),
    display_order: int = Form(0),
) -> RedirectResponse:
    with get_conn() as conn:
        try:
            conn.execute("""
                INSERT INTO magento_module_categories
                (code, label, description, color, icon, display_order)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                code.strip(),
                label.strip(),
                description.strip(),
                color.strip(),
                icon.strip(),
                display_order,
            ))
            conn.commit()
        except sqlite3.IntegrityError as exc:
            raise HTTPException(status_code=400, detail=f"Category code '{code}' already exists") from exc
    return RedirectResponse(url="/admin/magento/categories", status_code=303)


@app.post("/admin/magento/categories/update")
def magento_module_category_update(
    category_id: str = Form(...),
    code: str = Form(...),
    label: str = Form(...),
    description: str = Form(""),
    color: str = Form(""),
    icon: str = Form(""),
    display_order: int = Form(0),
) -> RedirectResponse:
    pk = _optional_int(category_id)
    if pk is None:
        raise HTTPException(status_code=400, detail="Invalid category id.")
    with get_conn() as conn:
        try:
            conn.execute("""
                UPDATE magento_module_categories
                SET code = ?, label = ?, description = ?, color = ?, icon = ?, display_order = ?
                WHERE id = ?
            """, (
                code.strip(),
                label.strip(),
                description.strip(),
                color.strip(),
                icon.strip(),
                display_order,
                pk,
            ))
            conn.commit()
        except sqlite3.IntegrityError as exc:
            raise HTTPException(status_code=400, detail=f"Category code '{code}' already exists") from exc
    return RedirectResponse(url="/admin/magento/categories", status_code=303)


@app.post("/admin/magento/categories/reorder")
def magento_module_categories_reorder(
    request: Request,
    category_orders: str = Form(...),  # JSON string: {"1": 1, "2": 2, ...}
) -> JSONResponse:
    import json
    from datetime import datetime
    
    try:
        orders = json.loads(category_orders)
        with get_conn() as conn:
            now = datetime.now().isoformat()
            for cat_id, order in orders.items():
                conn.execute("""
                    UPDATE magento_module_categories
                    SET display_order = ?, updated_at = ?
                    WHERE id = ?
                """, (order, now, int(cat_id)))
            conn.commit()
        return JSONResponse(content={"success": True})
    except Exception as e:
        return JSONResponse(content={"success": False, "error": str(e)}, status_code=500)


@app.get("/admin/magento/categories/{category_id}")
def magento_module_category_edit(request: Request, category_id: int) -> Any:
    with get_conn() as conn:
        category = conn.execute(
            "SELECT * FROM magento_module_categories WHERE id = ?", (category_id,)
        ).fetchone()
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
    return templates.TemplateResponse(request, "magento/magento_module_category_edit.html",
        {"request": request, "category": category},
    )


@app.get("/api/magento-modules")
def api_magento_modules() -> JSONResponse:
    """API endpoint to fetch all magento modules for frontend"""
    try:
        with get_conn() as conn:
            # Get categories - convert Row objects to dicts
            categories_rows = conn.execute("""
                SELECT id, code, label, color, icon, display_order
                FROM magento_module_categories
                ORDER BY display_order, label
            """).fetchall()
            categories = [dict(row) for row in categories_rows]

            # Get modules with category info - convert Row objects to dicts
            modules_rows = conn.execute("""
                SELECT
                    mm.*,
                    c.code AS category_code,
                    c.label AS category_label,
                    c.color AS category_color,
                    c.icon AS category_icon
                FROM magento_modules mm
                LEFT JOIN magento_module_categories c ON mm.category_id = c.id
                ORDER BY mm.revised_date DESC, mm.posted_date DESC, mm.id DESC
            """).fetchall()
            modules = [dict(row) for row in modules_rows]

            # Build modules list with related data
            modules_list = []
            for module in modules:
                # Get technologies - convert Row objects to dicts
                technologies_rows = conn.execute("""
                    SELECT name, icon FROM magento_module_technologies
                    WHERE module_id = ? ORDER BY display_order, name
                """, (module["id"],)).fetchall()
                technologies = [dict(row) for row in technologies_rows]

                # Get features - convert Row objects to dicts
                features_rows = conn.execute("""
                    SELECT name, description, icon FROM magento_module_features
                    WHERE module_id = ? ORDER BY display_order, name
                """, (module["id"],)).fetchall()
                features = [dict(row) for row in features_rows]

                # Get technical details - convert Row objects to dicts
                technical_details_rows = conn.execute("""
                    SELECT title, description FROM magento_module_technical_details
                    WHERE module_id = ? ORDER BY display_order, title
                """, (module["id"],)).fetchall()
                technical_details = [dict(row) for row in technical_details_rows]

                # Get images - convert Row objects to dicts
                images_rows = conn.execute("""
                    SELECT url, alt FROM magento_module_images
                    WHERE module_id = ? ORDER BY display_order, id
                """, (module["id"],)).fetchall()
                images = [dict(row) for row in images_rows]

                # Parse stats JSON
                stats = {}
                if module.get("stats"):
                    try:
                        stats = json.loads(module["stats"])
                    except json.JSONDecodeError:
                        stats = {}

                modules_list.append({
                    "id": module["id"],
                    "name": module["title"],
                    "version": module.get("version") or "",
                    "category": module.get("category_label") or "Uncategorized",
                    "category_code": module.get("category_code") or "",
                    "status": module.get("status") or "in development",
                    "lastUpdated": module.get("revised_date") or module.get("posted_date") or "",
                    "description": module.get("description") or "",
                    "metrics": module.get("metrics") or "",
                    "technologies": [{"name": t.get("name") or "", "icon": t.get("icon") or ""} for t in technologies],
                    "features": [{"name": f.get("name") or "", "icon": f.get("icon") or "", "description": f.get("description") or ""} for f in features],
                    "technicalDetails": [{"title": td.get("title") or "", "description": td.get("description") or ""} for td in technical_details],
                    "images": [{"url": img.get("url") or "", "alt": img.get("alt") or ""} for img in images],
                    "stats": stats,
                    "gallery": [{"url": img.get("url") or "", "alt": img.get("alt") or ""} for img in images]
                })

            # Group modules by category code
            modules_by_category = {}
            for module in modules_list:
                cat_code = module["category_code"] or "uncategorized"
                if cat_code not in modules_by_category:
                    modules_by_category[cat_code] = []
                modules_by_category[cat_code].append(module)

            # Build categories list
            categories_list = [{
                "code": cat.get("code") or "",
                "label": cat.get("label") or "",
                "color": cat.get("color") or "",
                "icon": cat.get("icon") or "",
                "count": len(modules_by_category.get(cat.get("code") or "", []))
            } for cat in categories]

        return JSONResponse(content={
            "categories": categories_list,
            "modules": modules_by_category
        })
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        return JSONResponse(content={"categories": [], "modules": {}, "error": str(e), "traceback": error_trace}, status_code=500)


# ============================================================================
# Photography System Routes
# ============================================================================

def list_photography_images() -> List[dict]:
    """List all images in the photography directory"""
    images = []
    if PHOTOGRAPHY_MEDIA.exists():
        for ext in IMAGE_EXTENSIONS:
            for img_file in PHOTOGRAPHY_MEDIA.rglob(f"*{ext}"):
                rel_path = img_file.relative_to(ROOT)
                url = "/" + str(rel_path).replace("\\", "/")
                images.append({
                    "url": url,
                    "filename": img_file.name,
                    "path": str(rel_path),
                })
    return sorted(images, key=lambda x: x["filename"])


@app.get("/admin/photography")
def photography_list(request: Request) -> Any:
    try:
        with get_conn() as conn:
            photos_rows = conn.execute("""
                SELECT
                    p.*,
                    c.label AS category_label,
                    c.code AS category_code,
                    c.color AS category_color
                FROM photography p
                LEFT JOIN photography_categories c ON c.id = p.category_id
                ORDER BY p.year DESC, p.created_at DESC, p.id DESC
            """).fetchall()
            photos = [dict(row) for row in photos_rows]
    except Exception:
        photos = []
    return templates.TemplateResponse(request, "photography/photography_list.html",
        {"request": request, "photos": photos},
    )


@app.get("/admin/photography/new")
def photography_new(request: Request) -> Any:
    with get_conn() as conn:
        categories = conn.execute("""
            SELECT * FROM photography_categories
            ORDER BY display_order, label
        """).fetchall()
    return templates.TemplateResponse(request, "photography/photography_edit.html",
        {
            "request": request,
            "photo": None,
            "categories": categories,
            "available_images": list_photography_images(),
        },
    )


@app.get("/admin/photography/categories")
def photography_categories_list(request: Request) -> Any:
    try:
        with get_conn() as conn:
            categories_rows = conn.execute("""
                SELECT
                    c.*,
                    COUNT(p.id) AS photo_count
                FROM photography_categories c
                LEFT JOIN photography p ON p.category_id = c.id
                GROUP BY c.id
                ORDER BY c.display_order, c.label
            """).fetchall()
            categories = [dict(row) for row in categories_rows]
    except Exception:
        categories = []
    return templates.TemplateResponse(request, "photography/photography_categories_list.html",
        {"request": request, "categories": categories},
    )


@app.get("/admin/photography/categories/new")
def photography_category_new(request: Request) -> Any:
    return templates.TemplateResponse(request, "photography/photography_category_edit.html",
        {"request": request, "category": None},
    )


@app.get("/admin/photography/categories/{category_id}")
def photography_category_edit(request: Request, category_id: int) -> Any:
    with get_conn() as conn:
        category = conn.execute(
            "SELECT * FROM photography_categories WHERE id = ?", (category_id,)
        ).fetchone()
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
    return templates.TemplateResponse(request, "photography/photography_category_edit.html",
        {"request": request, "category": category},
    )


@app.get("/admin/photography/{photo_id}")
def photography_edit(request: Request, photo_id: int) -> Any:
    with get_conn() as conn:
        photo_row = conn.execute(
            "SELECT * FROM photography WHERE id = ?", (photo_id,)
        ).fetchone()
        if not photo_row:
            raise HTTPException(status_code=404, detail="Photo not found")
        
        # Convert Row to dict and ensure JSON fields are properly formatted
        photo = dict(photo_row)
        
        from datetime import datetime
        import os
        debug_log_path = Path(__file__).parent / "admin.log"
        try:
            with open(debug_log_path, "a", encoding="utf-8") as f:
                f.write(f"\n{'='*80}\n")
                f.write(f"[{datetime.now().isoformat()}] PHOTOGRAPHY EDIT - Photo ID: {photo_id}\n")
                f.write(f"Loading photo_details from DB (raw): {repr(str(photo.get('photo_details'))[:200])}\n")
                f.flush()
                os.fsync(f.fileno())
        except:
            pass
        
        # Format JSON fields for display - if they're valid JSON, format them nicely
        photo_details_value = photo.get("photo_details")
        if photo_details_value is not None:
            photo_details_str = str(photo_details_value).strip()
            if photo_details_str and photo_details_str != "{}":
                try:
                    parsed = json.loads(photo_details_str)
                    photo["photo_details"] = json.dumps(parsed, indent=2, ensure_ascii=False)
                    try:
                        with open(debug_log_path, "a", encoding="utf-8") as f:
                            f.write(f"Successfully parsed and formatted photo_details for display\n")
                            f.flush()
                            os.fsync(f.fileno())
                    except:
                        pass
                except (json.JSONDecodeError, TypeError) as e:
                    # If it's not valid JSON, keep the original value
                    try:
                        with open(debug_log_path, "a", encoding="utf-8") as f:
                            f.write(f"WARNING: Could not parse photo_details as JSON: {e}\n")
                            f.write(f"WARNING: Keeping original value: {repr(photo_details_str[:200])}\n")
                            f.flush()
                            os.fsync(f.fileno())
                    except:
                        pass
                    photo["photo_details"] = photo_details_str
            else:
                photo["photo_details"] = "{}"
                try:
                    with open(debug_log_path, "a", encoding="utf-8") as f:
                        f.write(f"photo_details is empty or '{{}}', using default\n")
                        f.flush()
                        os.fsync(f.fileno())
                except:
                    pass
        else:
            photo["photo_details"] = "{}"
            try:
                with open(debug_log_path, "a", encoding="utf-8") as f:
                    f.write(f"photo_details is None, using default\n")
                    f.flush()
                    os.fsync(f.fileno())
            except:
                pass
            
        technical_details_value = photo.get("technical_details")
        if technical_details_value is not None:
            technical_details_str = str(technical_details_value).strip()
            if technical_details_str and technical_details_str != "{}":
                try:
                    parsed = json.loads(technical_details_str)
                    photo["technical_details"] = json.dumps(parsed, indent=2, ensure_ascii=False)
                except (json.JSONDecodeError, TypeError):
                    # If it's not valid JSON, keep the original value
                    photo["technical_details"] = technical_details_str
            else:
                photo["technical_details"] = "{}"
        else:
            photo["technical_details"] = "{}"
        
        categories = conn.execute("""
            SELECT * FROM photography_categories
            ORDER BY display_order, label
        """).fetchall()
    return templates.TemplateResponse(request, "photography/photography_edit.html",
        {
            "request": request,
            "photo": photo,
            "categories": categories,
            "available_images": list_photography_images(),
        },
    )


@app.post("/admin/photography/save")
async def photography_save(
    request: Request,
    photo_id: str | None = Form(None),
    photo_name: str = Form(...),
    photo_description: str | None = Form(None),
    location: str | None = Form(None),
    year: str | None = Form(None),
    tags: str | None = Form(None),
    category_id: str | None = Form(None),
    photo_details: str | None = Form(None),
    technical_details: str | None = Form(None),
    image_url: str | None = Form(None),
) -> RedirectResponse:
    from datetime import datetime
    import os
    
    photo_pk = _optional_int(photo_id)
    
    # Log raw form data first
    debug_log_path = Path(__file__).parent / "admin.log"
    try:
        form_data = await request.form()
        with open(debug_log_path, "a", encoding="utf-8") as f:
            f.write(f"\n{'='*80}\n")
            f.write(f"[{datetime.now().isoformat()}] PHOTOGRAPHY SAVE - Photo ID: {photo_pk}\n")
            f.write(f"Photo Name: {photo_name}\n")
            f.write(f"RAW FORM DATA - All keys: {list(form_data.keys())}\n")
            if 'photo_details' in form_data:
                raw_value = form_data.get('photo_details', '')
                f.write(f"RAW photo_details from form_data: type={type(raw_value).__name__}, value={repr(str(raw_value)[:500])}\n")
            else:
                f.write(f"RAW photo_details: NOT FOUND IN FORM DATA\n")
            f.write(f"photo_details parameter (type: {type(photo_details).__name__}, length: {len(photo_details) if photo_details else 0}):\n")
            f.write(f"  {repr(photo_details[:500]) if photo_details else 'None'}\n")
            f.flush()
            os.fsync(f.fileno())  # Force write to disk
    except Exception as e:
        import sys
        print(f"ERROR writing to log file: {e}", file=sys.stderr)

    # Validate and parse JSON fields
    # Form always sends these fields, so they're either empty strings or have content
    photo_details_json = "{}"
    if photo_details and photo_details.strip():
        photo_details_trimmed = photo_details.strip()
        if photo_details_trimmed != "{}":
            try:
                # Parse and re-stringify to ensure valid JSON
                parsed = json.loads(photo_details_trimmed)
                photo_details_json = json.dumps(parsed, ensure_ascii=False)
                try:
                    with open(debug_log_path, "a", encoding="utf-8") as f:
                        f.write(f"SUCCESS: Parsed photo_details, saving: {photo_details_json[:200]}\n")
                        f.flush()
                        os.fsync(f.fileno())
                except:
                    pass
            except json.JSONDecodeError as e:
                # If invalid JSON, log and save as empty object
                try:
                    with open(debug_log_path, "a", encoding="utf-8") as f:
                        f.write(f"ERROR: Invalid JSON in photo_details for photo {photo_pk}: {e}\n")
                        f.write(f"ERROR: Received value (first 500 chars): {repr(photo_details_trimmed[:500])}\n")
                        f.flush()
                        os.fsync(f.fileno())
                except:
                    pass
                photo_details_json = "{}"
        else:
            try:
                with open(debug_log_path, "a", encoding="utf-8") as f:
                    f.write(f"INFO: photo_details is empty or just '{{}}', saving as '{{}}'\n")
                    f.flush()
                    os.fsync(f.fileno())
            except:
                pass
    else:
        try:
            with open(debug_log_path, "a", encoding="utf-8") as f:
                f.write(f"INFO: photo_details is None or empty, saving as '{{}}'\n")
                f.flush()
                os.fsync(f.fileno())
        except:
            pass

    technical_details_json = "{}"
    if technical_details and technical_details.strip():
        technical_details_trimmed = technical_details.strip()
        if technical_details_trimmed != "{}":
            try:
                parsed = json.loads(technical_details_trimmed)
                technical_details_json = json.dumps(parsed, ensure_ascii=False)
            except json.JSONDecodeError as e:
                try:
                    with open(debug_log_path, "a", encoding="utf-8") as f:
                        f.write(f"ERROR: Invalid JSON in technical_details for photo {photo_pk}: {e}\n")
                        f.write(f"ERROR: Received value (first 500 chars): {repr(technical_details_trimmed[:500])}\n")
                        f.flush()
                        os.fsync(f.fileno())
                except:
                    pass
                technical_details_json = "{}"

    with get_conn() as conn:
        cur = conn.cursor()
        if photo_pk is None:
            cur.execute("""
                INSERT INTO photography
                (photo_name, photo_description, location, year, tags, category_id, photo_details, technical_details, image_url)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                photo_name.strip(),
                photo_description.strip() if photo_description else None,
                location.strip() if location else None,
                year.strip() if year else None,
                tags.strip() if tags else None,
                _optional_int(category_id),
                photo_details_json,
                technical_details_json,
                image_url.strip() if image_url else None,
            ))
            photo_pk = cur.lastrowid
        else:
            cur.execute("""
                UPDATE photography SET
                    photo_name = ?,
                    photo_description = ?,
                    location = ?,
                    year = ?,
                    tags = ?,
                    category_id = ?,
                    photo_details = ?,
                    technical_details = ?,
                    image_url = ?,
                    updated_at = datetime('now')
                WHERE id = ?
            """, (
                photo_name.strip(),
                photo_description.strip() if photo_description else None,
                location.strip() if location else None,
                year.strip() if year else None,
                tags.strip() if tags else None,
                _optional_int(category_id),
                photo_details_json,
                technical_details_json,
                image_url.strip() if image_url else None,
                photo_pk,
            ))
        conn.commit()
        
        # Log what was actually saved
        cur.execute("SELECT photo_details, technical_details FROM photography WHERE id = ?", (photo_pk,))
        saved_row = cur.fetchone()
        if saved_row:
            try:
                with open(debug_log_path, "a", encoding="utf-8") as f:
                    f.write(f"VERIFIED: Saved to DB - photo_details: {repr(saved_row[0][:200]) if saved_row[0] else 'None'}\n")
                    f.write(f"VERIFIED: Saved to DB - technical_details: {repr(saved_row[1][:200]) if saved_row[1] else 'None'}\n")
                    f.write(f"{'='*80}\n")
                    f.flush()
                    os.fsync(f.fileno())
            except:
                pass

    return RedirectResponse(url="/admin/photography", status_code=303)


@app.post("/admin/photography/images/upload")
async def photography_image_upload(
    request: Request,
    photo_id: int = Form(...),
    file: UploadFile = File(...),
) -> RedirectResponse:
    # Validate image upload
    content, ext, error_msg = await _validate_image_upload(file)
    if error_msg:
        return RedirectResponse(
            url=f"/admin/photography/{photo_id}?error={error_msg.replace(' ', '+')}",
            status_code=303
        )
    
    # Create safe filename
    photo_img_dir = PHOTOGRAPHY_MEDIA
    photo_img_dir.mkdir(parents=True, exist_ok=True)
    
    safe_filename = secrets.token_urlsafe(16) + ext
    file_path = photo_img_dir / safe_filename
    
    # Ensure we're writing within the intended directory (prevent path traversal)
    try:
        file_path.resolve().relative_to(photo_img_dir.resolve())
    except ValueError:
        return RedirectResponse(
            url=f"/admin/photography/{photo_id}?error=Invalid+file+path",
            status_code=303
        )
    
    # Write file
    try:
        with file_path.open("wb") as f:
            f.write(content)
    except Exception as e:
        import sys
        print(f"Error writing file: {e}", file=sys.stderr)
        return RedirectResponse(
            url=f"/admin/photography/{photo_id}?error=Error+saving+file",
            status_code=303
        )
    
    return RedirectResponse(url=f"/admin/photography/{photo_id}?success=Image+uploaded+successfully", status_code=303)


@app.get("/admin/photography/images/browse")
def photography_images_browse() -> JSONResponse:
    """API endpoint to browse existing photography images"""
    images = list_photography_images()
    return JSONResponse(content={"images": images})


@app.get("/admin/portfolio/images/browse")
def portfolio_images_browse() -> JSONResponse:
    """API endpoint to browse existing portfolio images"""
    images = []
    if PORTFOLIO_MEDIA.exists():
        for ext in IMAGE_EXTENSIONS:
            for img_file in PORTFOLIO_MEDIA.rglob(f"*{ext}"):
                rel_path = img_file.relative_to(ROOT)
                url = "/" + str(rel_path).replace("\\", "/")
                images.append({
                    "url": url,
                    "filename": img_file.name,
                    "path": str(rel_path),
                })
    return JSONResponse(content={"images": sorted(images, key=lambda x: x["filename"])})


@app.post("/admin/photography/categories/save")
def photography_category_save(
    request: Request,
    category_id: str | None = Form(None),
    code: str = Form(...),
    label: str = Form(...),
    description: str | None = Form(None),
    color: str | None = Form(None),
    icon: str | None = Form(None),
    display_order: str | None = Form(None),
) -> RedirectResponse:
    category_pk = _optional_int(category_id)
    order_value = _coerce_int(display_order) if display_order else 0

    with get_conn() as conn:
        cur = conn.cursor()
        if category_pk is None:
            cur.execute("""
                INSERT INTO photography_categories (code, label, description, color, icon, display_order)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                code.strip().lower(),
                label.strip(),
                description.strip() if description else None,
                color.strip() if color else None,
                icon.strip() if icon else None,
                order_value,
            ))
        else:
            cur.execute("""
                UPDATE photography_categories SET
                    code = ?,
                    label = ?,
                    description = ?,
                    color = ?,
                    icon = ?,
                    display_order = ?,
                    updated_at = datetime('now')
                WHERE id = ?
            """, (
                code.strip().lower(),
                label.strip(),
                description.strip() if description else None,
                color.strip() if color else None,
                icon.strip() if icon else None,
                order_value,
                category_pk,
            ))
        conn.commit()
    return RedirectResponse(url="/admin/photography/categories", status_code=303)


@app.post("/admin/photography/categories/reorder")
def photography_categories_reorder(
    request: Request,
    category_orders: str = Form(...),  # JSON string: {"1": 1, "2": 2, ...}
) -> JSONResponse:
    import json
    from datetime import datetime
    
    try:
        orders = json.loads(category_orders)
        with get_conn() as conn:
            now = datetime.now().isoformat()
            for cat_id, order in orders.items():
                conn.execute("""
                    UPDATE photography_categories
                    SET display_order = ?, updated_at = ?
                    WHERE id = ?
                """, (order, now, int(cat_id)))
            conn.commit()
        return JSONResponse(content={"success": True})
    except Exception as e:
        return JSONResponse(content={"success": False, "error": str(e)}, status_code=500)


@app.get("/api/photography")
def api_photography() -> JSONResponse:
    """API endpoint to fetch all photography entries for frontend"""
    try:
        with get_conn() as conn:
            # Get categories - convert Row objects to dicts
            categories_rows = conn.execute("""
                SELECT id, code, label, color, icon, display_order
                FROM photography_categories
                ORDER BY display_order, label
            """).fetchall()
            categories = [dict(row) for row in categories_rows]

            # Get photos with category info - convert Row objects to dicts
            photos_rows = conn.execute("""
                SELECT
                    p.*,
                    c.code AS category_code,
                    c.label AS category_label,
                    c.color AS category_color
                FROM photography p
                LEFT JOIN photography_categories c ON c.id = p.category_id
                ORDER BY p.year DESC, p.created_at DESC, p.id DESC
            """).fetchall()
            photos = [dict(row) for row in photos_rows]

            # Parse JSON fields
            photos_list = []
            for photo in photos:
                photo_details = {}
                if photo.get("photo_details"):
                    try:
                        photo_details = json.loads(photo["photo_details"])
                    except json.JSONDecodeError:
                        photo_details = {}

                technical_details = {}
                if photo.get("technical_details"):
                    try:
                        technical_details = json.loads(photo["technical_details"])
                    except json.JSONDecodeError:
                        technical_details = {}

                photos_list.append({
                    "id": photo["id"],
                    "title": photo["photo_name"],
                    "description": photo["photo_description"] or "",
                    "location": photo["location"] or photo_details.get("location", ""),
                    "year": photo["year"] or photo_details.get("year", ""),
                    "category": photo["category_label"] or photo_details.get("category", ""),
                    "category_code": photo["category_code"] or "",
                    "image": photo["image_url"] or "",
                    "camera": technical_details.get("camera", ""),
                    "lens": technical_details.get("lens", ""),
                    "settings": technical_details.get("settings", ""),
                    "tags": photo["tags"] or "",
                })

            # Group photos by category code
            photos_by_category = {}
            for photo in photos_list:
                cat_code = photo["category_code"] or "uncategorized"
                if cat_code not in photos_by_category:
                    photos_by_category[cat_code] = []
                photos_by_category[cat_code].append(photo)

            # Build categories list with counts
            categories_list = [{
                "code": cat.get("code") or "",
                "label": cat.get("label") or "",
                "color": cat.get("color") or "",
                "icon": cat.get("icon") or "",
                "count": len(photos_by_category.get(cat.get("code") or "", []))
            } for cat in categories]

        return JSONResponse(content={
            "categories": categories_list,
            "photos": photos_by_category
        })
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        return JSONResponse(content={"categories": [], "photos": {}, "error": str(e), "traceback": error_trace}, status_code=500)


# ============================================================================
# Experience System Routes
# ============================================================================

def calculate_duration(start_date: str, end_date: str | None) -> str:
    """Calculate duration between two dates in format: 'X yrs Y mos' or 'X mos'"""
    from datetime import datetime

    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        if end_date:
            end = datetime.strptime(end_date, "%Y-%m-%d")
        else:
            end = datetime.now()

        years = end.year - start.year
        months = end.month - start.month

        if months < 0:
            years -= 1
            months += 12

        if years > 0:
            if months > 0:
                return f"{years} yrs {months} mos"
            return f"{years} yrs"
        return f"{months} mos"
    except Exception:
        return ""


@app.get("/admin/experience")
def experience_list(request: Request) -> Any:
    """List all job experiences grouped by company"""
    try:
        with get_conn() as conn:
            # Get all companies with their job experiences
            companies_rows = conn.execute("""
                SELECT c.*,
                       COUNT(je.id) as position_count,
                       MAX(je.start_date) as latest_start_date
                FROM experience_companies c
                LEFT JOIN experience_job_experiences je ON je.company_id = c.id
                GROUP BY c.id
                ORDER BY latest_start_date DESC, c.name
            """).fetchall()

            companies = []
            for company_row in companies_rows:
                company = dict(company_row)
                # Get all positions for this company
                positions_rows = conn.execute("""
                    SELECT je.*,
                           GROUP_CONCAT(DISTINCT s.name) as skills,
                           GROUP_CONCAT(DISTINCT t.name) as tools,
                           GROUP_CONCAT(DISTINCT ss.name) as soft_skills
                    FROM experience_job_experiences je
                    LEFT JOIN experience_job_experience_skills jes ON jes.job_experience_id = je.id
                    LEFT JOIN experience_skills_sets s ON s.id = jes.skill_id
                    LEFT JOIN experience_job_experience_tools jet ON jet.job_experience_id = je.id
                    LEFT JOIN experience_tools t ON t.id = jet.tool_id
                    LEFT JOIN experience_job_experience_soft_skills jess ON jess.job_experience_id = je.id
                    LEFT JOIN experience_soft_skills ss ON ss.id = jess.soft_skill_id
                    WHERE je.company_id = ?
                    GROUP BY je.id
                    ORDER BY je.start_date DESC
                """, (company["id"],)).fetchall()

                company["positions"] = [dict(row) for row in positions_rows]
                companies.append(company)
    except Exception:
        companies = []

    return templates.TemplateResponse(request, "experience/experience_list.html",
        {"request": request, "companies": companies},
    )


@app.get("/admin/experience/new")
def experience_new(request: Request) -> Any:
    """New job experience form"""
    with get_conn() as conn:
        companies = conn.execute("SELECT * FROM experience_companies ORDER BY name").fetchall()
        skills = conn.execute("SELECT * FROM experience_skills_sets ORDER BY name").fetchall()
        tools = conn.execute("SELECT * FROM experience_tools ORDER BY name").fetchall()
        soft_skills = conn.execute("SELECT * FROM experience_soft_skills ORDER BY name").fetchall()

    return templates.TemplateResponse(request, "experience/experience_edit.html",
        {
            "request": request,
            "job": None,
            "companies": companies,
            "skills": skills,
            "tools": tools,
            "soft_skills": soft_skills,
        },
    )


@app.post("/admin/experience/save")
def experience_save(
    request: Request,
    job_id: str | None = Form(None),
    company_id: str = Form(...),
    job_title: str = Form(...),
    start_date: str = Form(...),
    end_date: str | None = Form(None),
    is_current: str | None = Form(None),
    employment_type: str | None = Form(None),
    is_remote: str | None = Form(None),
    is_concurrent: str | None = Form(None),
    role_overview: str | None = Form(None),
    key_achievements: str | None = Form(None),
    key_responsibilities: str | None = Form(None),
    skill_ids: str | None = Form(None),
    tool_ids: str | None = Form(None),
    soft_skill_ids: str | None = Form(None),
) -> RedirectResponse:
    """Save job experience"""
    job_pk = _optional_int(job_id)
    company_pk = _optional_int(company_id)

    if not company_pk:
        raise HTTPException(status_code=400, detail="Company is required")

    # Parse JSON arrays
    achievements_json = "[]"
    if key_achievements:
        try:
            parsed = json.loads(key_achievements)
            achievements_json = json.dumps(parsed, ensure_ascii=False)
        except json.JSONDecodeError:
            achievements_json = "[]"

    responsibilities_json = "[]"
    if key_responsibilities:
        try:
            parsed = json.loads(key_responsibilities)
            responsibilities_json = json.dumps(parsed, ensure_ascii=False)
        except json.JSONDecodeError:
            responsibilities_json = "[]"

    # Parse skill/tool IDs
    skill_id_list = []
    if skill_ids:
        for sid in skill_ids.split(","):
            sid = sid.strip()
            if sid:
                try:
                    skill_id_list.append(int(sid))
                except ValueError:
                    pass

    tool_id_list = []
    if tool_ids:
        for tid in tool_ids.split(","):
            tid = tid.strip()
            if tid:
                try:
                    tool_id_list.append(int(tid))
                except ValueError:
                    pass

    soft_skill_id_list = []
    if soft_skill_ids:
        for sid in soft_skill_ids.split(","):
            sid = sid.strip()
            if sid:
                try:
                    soft_skill_id_list.append(int(sid))
                except ValueError:
                    pass

    with get_conn() as conn:
        cur = conn.cursor()
        if job_pk is None:
            cur.execute("""
                INSERT INTO experience_job_experiences
                (company_id, job_title, start_date, end_date, is_current, employment_type,
                 is_remote, is_concurrent, role_overview, key_achievements, key_responsibilities)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                company_pk,
                job_title.strip(),
                start_date.strip(),
                end_date.strip() if end_date else None,
                1 if is_current else 0,
                employment_type.strip() if employment_type else None,
                1 if is_remote else 0,
                1 if is_concurrent else 0,
                role_overview.strip() if role_overview else None,
                achievements_json,
                responsibilities_json,
            ))
            job_pk = cur.lastrowid
        else:
            cur.execute("""
                UPDATE experience_job_experiences SET
                    company_id = ?,
                    job_title = ?,
                    start_date = ?,
                    end_date = ?,
                    is_current = ?,
                    employment_type = ?,
                    is_remote = ?,
                    is_concurrent = ?,
                    role_overview = ?,
                    key_achievements = ?,
                    key_responsibilities = ?,
                    updated_at = datetime('now')
                WHERE id = ?
            """, (
                company_pk,
                job_title.strip(),
                start_date.strip(),
                end_date.strip() if end_date else None,
                1 if is_current else 0,
                employment_type.strip() if employment_type else None,
                1 if is_remote else 0,
                1 if is_concurrent else 0,
                role_overview.strip() if role_overview else None,
                achievements_json,
                responsibilities_json,
                job_pk,
            ))

        # Update skills
        cur.execute("DELETE FROM experience_job_experience_skills WHERE job_experience_id = ?", (job_pk,))
        for skill_id in skill_id_list:
            cur.execute(
                "INSERT INTO experience_job_experience_skills (job_experience_id, skill_id) VALUES (?, ?)",
                (job_pk, skill_id)
            )

        # Update tools
        cur.execute("DELETE FROM experience_job_experience_tools WHERE job_experience_id = ?", (job_pk,))
        for tool_id in tool_id_list:
            cur.execute(
                "INSERT INTO experience_job_experience_tools (job_experience_id, tool_id) VALUES (?, ?)",
                (job_pk, tool_id)
            )

        # Update soft skills
        cur.execute("DELETE FROM experience_job_experience_soft_skills WHERE job_experience_id = ?", (job_pk,))
        for soft_skill_id in soft_skill_id_list:
            cur.execute(
                "INSERT INTO experience_job_experience_soft_skills (job_experience_id, soft_skill_id) VALUES (?, ?)",
                (job_pk, soft_skill_id)
            )

        conn.commit()

    return RedirectResponse(url="/admin/experience", status_code=303)


@app.post("/admin/experience/projects/save")
def experience_project_save(
    request: Request,
    project_id: str | None = Form(None),
    job_experience_id: str = Form(...),
    month_year: str | None = Form(None),
    title: str | None = Form(None),
    link: str | None = Form(None),
    sort_order: str | None = Form(None),
) -> RedirectResponse:
    """Save a project/accomplishment for a job experience"""
    project_pk = _optional_int(project_id)
    job_pk = _optional_int(job_experience_id)

    if not job_pk:
        raise HTTPException(status_code=400, detail="Job experience is required")

    # Validate required fields only if creating new project
    if project_pk is None:
        if not month_year or not month_year.strip():
            raise HTTPException(status_code=400, detail="Month/Year is required")
        if not title or not title.strip():
            raise HTTPException(status_code=400, detail="Title is required")

    sort_value = _coerce_int(sort_order)

    with get_conn() as conn:
        cur = conn.cursor()
        if project_pk is None:
            cur.execute("""
                INSERT INTO experience_job_projects (job_experience_id, month_year, title, link, sort_order)
                VALUES (?, ?, ?, ?, ?)
            """, (
                job_pk,
                month_year.strip(),
                title.strip(),
                link.strip() if link else None,
                sort_value,
            ))
        else:
            cur.execute("""
                UPDATE job_projects SET
                    month_year = ?,
                    title = ?,
                    link = ?,
                    sort_order = ?
                WHERE id = ?
            """, (
                month_year.strip(),
                title.strip(),
                link.strip() if link else None,
                sort_value,
                project_pk,
            ))
        conn.commit()

    return RedirectResponse(url=f"/admin/experience/{job_pk}", status_code=303)


@app.post("/admin/experience/projects/delete")
def experience_project_delete(
    request: Request,
    project_id: str = Form(...),
) -> RedirectResponse:
    """Delete a project/accomplishment"""
    project_pk = _optional_int(project_id)

    with get_conn() as conn:
        # Get job_experience_id before deleting
        job_row = conn.execute(
            "SELECT job_experience_id FROM experience_job_projects WHERE id = ?", (project_pk,)
        ).fetchone()
        job_id = job_row["job_experience_id"] if job_row else None

        conn.execute("DELETE FROM experience_job_projects WHERE id = ?", (project_pk,))
        conn.commit()

    if job_id:
        return RedirectResponse(url=f"/admin/experience/{job_id}", status_code=303)
    return RedirectResponse(url="/admin/experience", status_code=303)


@app.get("/admin/experience/companies")
def experience_companies_list(request: Request) -> Any:
    """List all companies"""
    try:
        with get_conn() as conn:
            companies_rows = conn.execute("""
                SELECT c.*, COUNT(je.id) as position_count
                FROM experience_companies c
                LEFT JOIN experience_job_experiences je ON je.company_id = c.id
                GROUP BY c.id
                ORDER BY COALESCE(c.sort_order, 1000000), c.name
            """).fetchall()
            companies = [dict(row) for row in companies_rows]
    except Exception:
        companies = []

    return templates.TemplateResponse(request, "experience/companies_list.html",
        {"request": request, "companies": companies, "companies_payload": companies},
    )


@app.post("/admin/experience/companies/reorder")
async def experience_companies_reorder(request: Request) -> JSONResponse:
    """Persist manual ordering for companies."""
    payload = await request.json()
    order = payload.get("order") if isinstance(payload, dict) else payload
    if not isinstance(order, list) or not all(isinstance(item, int) for item in order):
        return JSONResponse({"ok": False, "error": "Invalid order payload."}, status_code=400)

    with get_conn() as conn:
        conn.executemany(
            "UPDATE experience_companies SET sort_order = ?, updated_at = datetime('now') WHERE id = ?",
            [(idx + 1, company_id) for idx, company_id in enumerate(order)],
        )

    return JSONResponse({"ok": True})


@app.get("/admin/experience/companies/new")
def experience_company_new(request: Request) -> Any:
    """New company form"""
    return templates.TemplateResponse(request, "experience/company_edit.html",
        {"request": request, "company": None},
    )


@app.get("/admin/experience/companies/{company_id}")
def experience_company_edit(request: Request, company_id: int) -> Any:
    """Edit company form"""
    with get_conn() as conn:
        company = conn.execute(
            "SELECT * FROM experience_companies WHERE id = ?", (company_id,)
        ).fetchone()
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")

    return templates.TemplateResponse(request, "experience/company_edit.html",
        {"request": request, "company": company},
    )


@app.post("/admin/experience/companies/save")
def experience_company_save(
    request: Request,
    company_id: str | None = Form(None),
    name: str = Form(...),
    logo_url: str | None = Form(None),
    description: str | None = Form(None),
    website: str | None = Form(None),
    location: str | None = Form(None),
) -> RedirectResponse:
    """Save company"""
    company_pk = _optional_int(company_id)

    with get_conn() as conn:
        cur = conn.cursor()
        if company_pk is None:
            next_sort = cur.execute(
                "SELECT COALESCE(MAX(sort_order), 0) + 1 FROM experience_companies"
            ).fetchone()[0]
            cur.execute("""
                INSERT INTO experience_companies (name, logo_url, description, website, location, sort_order)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                name.strip(),
                logo_url.strip() if logo_url else None,
                description.strip() if description else None,
                website.strip() if website else None,
                location.strip() if location else None,
                next_sort,
            ))
            company_pk = cur.lastrowid
        else:
            cur.execute("""
                UPDATE experience_companies SET
                    name = ?,
                    logo_url = ?,
                    description = ?,
                    website = ?,
                    location = ?,
                    updated_at = datetime('now')
                WHERE id = ?
            """, (
                name.strip(),
                logo_url.strip() if logo_url else None,
                description.strip() if description else None,
                website.strip() if website else None,
                location.strip() if location else None,
                company_pk,
            ))
        conn.commit()

    return RedirectResponse(url="/admin/experience/companies", status_code=303)


def list_logo_images() -> List[dict]:
    """List all images in the logos directory"""
    images = []
    if LOGO_IMG_ROOT.exists():
        for ext in IMAGE_EXTENSIONS:
            for img_file in LOGO_IMG_ROOT.rglob(f"*{ext}"):
                rel_path = img_file.relative_to(ROOT)
                url = "/" + str(rel_path).replace("\\", "/")
                images.append({
                    "url": url,
                    "filename": img_file.name,
                    "path": str(rel_path),
                })
    return sorted(images, key=lambda x: x["filename"])


@app.get("/admin/experience/companies/images/browse")
def experience_companies_images_browse() -> JSONResponse:
    """API endpoint to browse existing logo images"""
    images = list_logo_images()
    return JSONResponse(content={"images": images})


@app.get("/admin/experience/skills")
def experience_skills_list(request: Request) -> Any:
    """List all skills sets"""
    try:
        with get_conn() as conn:
            skills_rows = conn.execute("SELECT * FROM experience_skills_sets ORDER BY name").fetchall()
            skills = [dict(row) for row in skills_rows]
    except Exception:
        skills = []

    return templates.TemplateResponse(request, "experience/skills_list.html",
        {"request": request, "skills": skills, "skills_payload": skills},
    )


@app.get("/admin/experience/skills/new")
def experience_skill_new(request: Request) -> Any:
    """New skill form"""
    return templates.TemplateResponse(request, "experience/skill_edit.html",
        {"request": request, "skill": None},
    )


@app.get("/admin/experience/skills/{skill_id}")
def experience_skill_edit(request: Request, skill_id: int) -> Any:
    """Edit skill form"""
    with get_conn() as conn:
        skill = conn.execute(
            "SELECT * FROM experience_skills_sets WHERE id = ?", (skill_id,)
        ).fetchone()
        if not skill:
            raise HTTPException(status_code=404, detail="Skill not found")

    return templates.TemplateResponse(request, "experience/skill_edit.html",
        {"request": request, "skill": skill},
    )


@app.post("/admin/experience/skills/save")
def experience_skill_save(
    request: Request,
    skill_id: str | None = Form(None),
    name: str = Form(...),
    icon: str | None = Form(None),
    description: str | None = Form(None),
    category: str | None = Form(None),
    color: str | None = Form(None),
) -> RedirectResponse:
    """Save skill"""
    skill_pk = _optional_int(skill_id)

    try:
        with get_conn() as conn:
            cur = conn.cursor()
            if skill_pk is None:
                cur.execute("""
                    INSERT INTO experience_skills_sets (name, icon, description, category, color)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    name.strip(),
                    icon.strip() if icon else None,
                    description.strip() if description else None,
                    category.strip() if category else None,
                    color.strip() if color else None,
                ))
            else:
                cur.execute("""
                    UPDATE experience_skills_sets SET
                        name = ?,
                        icon = ?,
                        description = ?,
                        category = ?,
                        color = ?,
                        updated_at = datetime('now')
                    WHERE id = ?
                """, (
                    name.strip(),
                    icon.strip() if icon else None,
                    description.strip() if description else None,
                    category.strip() if category else None,
                    color.strip() if color else None,
                    skill_pk,
                ))
            conn.commit()
    except sqlite3.IntegrityError:
        return _experience_unique_name_redirect(
            base_path="/admin/experience/skills",
            record_id=skill_pk,
            name=name,
        )

    return RedirectResponse(url="/admin/experience/skills", status_code=303)


@app.get("/admin/experience/tools")
def experience_tools_list(request: Request) -> Any:
    """List all tools"""
    try:
        with get_conn() as conn:
            tools_rows = conn.execute("SELECT * FROM experience_tools ORDER BY name").fetchall()
            tools = [dict(row) for row in tools_rows]
    except Exception:
        tools = []

    return templates.TemplateResponse(request, "experience/tools_list.html",
        {"request": request, "tools": tools, "tools_payload": tools},
    )


@app.get("/admin/experience/tools/new")
def experience_tool_new(request: Request) -> Any:
    """New tool form"""
    return templates.TemplateResponse(request, "experience/tool_edit.html",
        {"request": request, "tool": None},
    )


@app.get("/admin/experience/tools/{tool_id}")
def experience_tool_edit(request: Request, tool_id: int) -> Any:
    """Edit tool form"""
    with get_conn() as conn:
        tool = conn.execute(
            "SELECT * FROM experience_tools WHERE id = ?", (tool_id,)
        ).fetchone()
        if not tool:
            raise HTTPException(status_code=404, detail="Tool not found")

    return templates.TemplateResponse(request, "experience/tool_edit.html",
        {"request": request, "tool": tool},
    )


@app.post("/admin/experience/tools/save")
def experience_tool_save(
    request: Request,
    tool_id: str | None = Form(None),
    name: str = Form(...),
    icon: str | None = Form(None),
) -> RedirectResponse:
    """Save tool"""
    tool_pk = _optional_int(tool_id)

    try:
        with get_conn() as conn:
            cur = conn.cursor()
            if tool_pk is None:
                cur.execute("""
                    INSERT INTO experience_tools (name, icon)
                    VALUES (?, ?)
                """, (
                    name.strip(),
                    icon.strip() if icon else None,
                ))
            else:
                cur.execute("""
                    UPDATE experience_tools SET
                        name = ?,
                        icon = ?,
                        updated_at = datetime('now')
                    WHERE id = ?
                """, (
                    name.strip(),
                    icon.strip() if icon else None,
                    tool_pk,
                ))
            conn.commit()
    except sqlite3.IntegrityError:
        return _experience_unique_name_redirect(
            base_path="/admin/experience/tools",
            record_id=tool_pk,
            name=name,
        )

    return RedirectResponse(url="/admin/experience/tools", status_code=303)


@app.get("/admin/experience/soft-skills")
def experience_soft_skills_list(request: Request) -> Any:
    """List all soft skills"""
    try:
        with get_conn() as conn:
            skills_rows = conn.execute("SELECT * FROM experience_soft_skills ORDER BY name").fetchall()
            skills = [dict(row) for row in skills_rows]
    except Exception:
        skills = []

    return templates.TemplateResponse(request, "experience/soft_skills_list.html",
        {"request": request, "skills": skills, "skills_payload": skills},
    )


@app.get("/admin/experience/soft-skills/new")
def experience_soft_skill_new(request: Request) -> Any:
    """New soft skill form"""
    return templates.TemplateResponse(request, "experience/soft_skill_edit.html",
        {"request": request, "skill": None},
    )


@app.get("/admin/experience/soft-skills/{skill_id}")
def experience_soft_skill_edit(request: Request, skill_id: int) -> Any:
    """Edit soft skill form"""
    with get_conn() as conn:
        skill = conn.execute(
            "SELECT * FROM experience_soft_skills WHERE id = ?", (skill_id,)
        ).fetchone()
        if not skill:
            raise HTTPException(status_code=404, detail="Soft skill not found")

    return templates.TemplateResponse(request, "experience/soft_skill_edit.html",
        {"request": request, "skill": skill},
    )


@app.post("/admin/experience/soft-skills/save")
def experience_soft_skill_save(
    request: Request,
    skill_id: str | None = Form(None),
    name: str = Form(...),
    icon: str | None = Form(None),
) -> RedirectResponse:
    """Save soft skill"""
    skill_pk = _optional_int(skill_id)

    try:
        with get_conn() as conn:
            cur = conn.cursor()
            if skill_pk is None:
                cur.execute("""
                    INSERT INTO experience_soft_skills (name, icon)
                    VALUES (?, ?)
                """, (
                    name.strip(),
                    icon.strip() if icon else None,
                ))
            else:
                cur.execute("""
                    UPDATE experience_soft_skills SET
                        name = ?,
                        icon = ?,
                        updated_at = datetime('now')
                    WHERE id = ?
                """, (
                    name.strip(),
                    icon.strip() if icon else None,
                    skill_pk,
                ))
            conn.commit()
    except sqlite3.IntegrityError:
        return _experience_unique_name_redirect(
            base_path="/admin/experience/soft-skills",
            record_id=skill_pk,
            name=name,
        )

    return RedirectResponse(url="/admin/experience/soft-skills", status_code=303)


@app.post("/admin/experience/soft-skills/delete")
def experience_soft_skill_delete(
    request: Request,
    skill_id: str = Form(...),
) -> RedirectResponse:
    """Delete a soft skill"""
    skill_pk = _optional_int(skill_id)

    if not skill_pk:
        raise HTTPException(status_code=400, detail="Soft skill ID is required")

    with get_conn() as conn:
        # Check if skill is used in any job experiences
        usage_count = conn.execute("""
            SELECT COUNT(*) as count FROM experience_job_experience_soft_skills
            WHERE soft_skill_id = ?
        """, (skill_pk,)).fetchone()

        if usage_count["count"] > 0:
            return _form_error_redirect(
                "/admin/experience/soft-skills",
                "Cannot delete soft skill that is assigned to job experiences",
            )

        conn.execute("DELETE FROM experience_soft_skills WHERE id = ?", (skill_pk,))
        conn.commit()

    return RedirectResponse(url="/admin/experience/soft-skills", status_code=303)


@app.get("/admin/experience/education")
def experience_education_list(request: Request) -> Any:
    """List all education entries"""
    try:
        with get_conn() as conn:
            education_rows = conn.execute("""
                SELECT * FROM experience_education
                ORDER BY timeline_date DESC
            """).fetchall()
            education = [dict(row) for row in education_rows]
    except Exception:
        education = []

    return templates.TemplateResponse(request, "experience/education_list.html",
        {"request": request, "education": education},
    )


@app.get("/admin/experience/education/new")
def experience_education_new(request: Request) -> Any:
    """New education form"""
    return templates.TemplateResponse(request, "experience/education_edit.html",
        {"request": request, "edu": None},
    )


@app.get("/admin/experience/education/{edu_id}")
def experience_education_edit(request: Request, edu_id: int) -> Any:
    """Edit education form"""
    with get_conn() as conn:
        edu = conn.execute(
            "SELECT * FROM experience_education WHERE id = ?", (edu_id,)
        ).fetchone()
        if not edu:
            raise HTTPException(status_code=404, detail="Education entry not found")

    return templates.TemplateResponse(request, "experience/education_edit.html",
        {"request": request, "edu": edu},
    )


@app.post("/admin/experience/education/save")
def experience_education_save(
    request: Request,
    edu_id: str | None = Form(None),
    certificate_name: str = Form(...),
    subtitle: str | None = Form(None),
    school_name: str = Form(...),
    location: str | None = Form(None),
    start_year: str | None = Form(None),
    end_year: str | None = Form(None),
    timeline_date: str = Form(...),
    description: str | None = Form(None),
    honors_memberships: str | None = Form(None),
) -> RedirectResponse:
    """Save education entry"""
    edu_pk = _optional_int(edu_id)

    # Parse honors/memberships JSON
    honors_json = "[]"
    if honors_memberships:
        try:
            parsed = json.loads(honors_memberships)
            honors_json = json.dumps(parsed, ensure_ascii=False)
        except json.JSONDecodeError:
            honors_json = "[]"

    with get_conn() as conn:
        cur = conn.cursor()
        if edu_pk is None:
            cur.execute("""
                INSERT INTO experience_education
                (certificate_name, subtitle, school_name, location, start_year, end_year,
                 timeline_date, description, honors_memberships)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                certificate_name.strip(),
                subtitle.strip() if subtitle else None,
                school_name.strip(),
                location.strip() if location else None,
                start_year.strip() if start_year else None,
                end_year.strip() if end_year else None,
                timeline_date.strip(),
                description.strip() if description else None,
                honors_json,
            ))
            edu_pk = cur.lastrowid
        else:
            cur.execute("""
                UPDATE experience_education SET
                    certificate_name = ?,
                    subtitle = ?,
                    school_name = ?,
                    location = ?,
                    start_year = ?,
                    end_year = ?,
                    timeline_date = ?,
                    description = ?,
                    honors_memberships = ?,
                    updated_at = datetime('now')
                WHERE id = ?
            """, (
                certificate_name.strip(),
                subtitle.strip() if subtitle else None,
                school_name.strip(),
                location.strip() if location else None,
                start_year.strip() if start_year else None,
                end_year.strip() if end_year else None,
                timeline_date.strip(),
                description.strip() if description else None,
                honors_json,
                edu_pk,
            ))
        conn.commit()

    return RedirectResponse(url="/admin/experience/education", status_code=303)


@app.post("/admin/experience/education/delete")
def experience_education_delete(
    request: Request,
    edu_id: str = Form(...),
) -> RedirectResponse:
    """Delete an education entry"""
    edu_pk = _optional_int(edu_id)

    if not edu_pk:
        raise HTTPException(status_code=400, detail="Education ID is required")

    with get_conn() as conn:
        conn.execute("DELETE FROM experience_education WHERE id = ?", (edu_pk,))
        conn.commit()

    return RedirectResponse(url="/admin/experience/education", status_code=303)


@app.get("/admin/experience/{job_id}")
def experience_edit(request: Request, job_id: int) -> Any:
    """Edit job experience form"""
    with get_conn() as conn:
        job = conn.execute(
            "SELECT * FROM experience_job_experiences WHERE id = ?", (job_id,)
        ).fetchone()
        if not job:
            raise HTTPException(status_code=404, detail="Job experience not found")

        # Get projects/accomplishments
        projects = conn.execute(
            "SELECT * FROM experience_job_projects WHERE job_experience_id = ? ORDER BY sort_order, month_year",
            (job_id,)
        ).fetchall()

        # Get selected skills, tools, soft skills
        selected_skills = [row["skill_id"] for row in conn.execute(
            "SELECT skill_id FROM experience_job_experience_skills WHERE job_experience_id = ?",
            (job_id,)
        ).fetchall()]

        selected_tools = [row["tool_id"] for row in conn.execute(
            "SELECT tool_id FROM experience_job_experience_tools WHERE job_experience_id = ?",
            (job_id,)
        ).fetchall()]

        selected_soft_skills = [row["soft_skill_id"] for row in conn.execute(
            "SELECT soft_skill_id FROM experience_job_experience_soft_skills WHERE job_experience_id = ?",
            (job_id,)
        ).fetchall()]

        companies = conn.execute("SELECT * FROM experience_companies ORDER BY name").fetchall()
        skills = conn.execute("SELECT * FROM experience_skills_sets ORDER BY name").fetchall()
        tools = conn.execute("SELECT * FROM experience_tools ORDER BY name").fetchall()
        soft_skills = conn.execute("SELECT * FROM experience_soft_skills ORDER BY name").fetchall()

        # Convert job Row to dict and parse JSON fields
        job_dict = dict(job) if job else None
        if job_dict:
            # Parse key_achievements JSON string to list
            if job_dict.get("key_achievements"):
                try:
                    job_dict["key_achievements"] = json.loads(job_dict["key_achievements"])
                except json.JSONDecodeError:
                    job_dict["key_achievements"] = []
            else:
                job_dict["key_achievements"] = []

            # Parse key_responsibilities JSON string to list
            if job_dict.get("key_responsibilities"):
                try:
                    job_dict["key_responsibilities"] = json.loads(job_dict["key_responsibilities"])
                except json.JSONDecodeError:
                    job_dict["key_responsibilities"] = []
            else:
                job_dict["key_responsibilities"] = []

        # Convert projects Row objects to dicts
        projects_list = [dict(row) for row in projects] if projects else []

    return templates.TemplateResponse(request, "experience/experience_edit.html",
        {
            "request": request,
            "job": job_dict,
            "projects": projects_list,
            "selected_skills": selected_skills,
            "selected_tools": selected_tools,
            "selected_soft_skills": selected_soft_skills,
            "companies": companies,
            "skills": skills,
            "tools": tools,
            "soft_skills": soft_skills,
        },
    )


@app.get("/api/experience")
def api_experience() -> JSONResponse:
    """API endpoint to fetch all experience data for frontend"""
    try:
        # ensure_experience_database() - Now handled by unified database
        with get_conn() as conn:
            # Check if tables exist
            try:
                # Get companies
                companies_rows = conn.execute("""
                    SELECT * FROM experience_companies
                    ORDER BY COALESCE(sort_order, 1000000), name
                """).fetchall()
                companies = [dict(row) for row in companies_rows]
            except sqlite3.OperationalError:
                companies = []

            # Get job experiences with all related data
            try:
                jobs_rows = conn.execute("""
                    SELECT je.*, c.name as company_name, c.logo_url, c.description as company_description, c.location as company_location
                    FROM experience_job_experiences je
                    LEFT JOIN experience_companies c ON c.id = je.company_id
                    ORDER BY je.start_date DESC
                """).fetchall()
            except sqlite3.OperationalError:
                jobs_rows = []

            jobs_list = []
            for job_row in jobs_rows:
                job = dict(job_row)
                job_id = job["id"]

                # Get projects
                projects_rows = conn.execute("""
                    SELECT * FROM experience_job_projects
                    WHERE job_experience_id = ?
                    ORDER BY sort_order, month_year
                """, (job_id,)).fetchall()
                job["projects"] = [dict(row) for row in projects_rows]

                # Get skills
                skills_rows = conn.execute("""
                    SELECT s.* FROM experience_skills_sets s
                    JOIN experience_job_experience_skills jes ON jes.skill_id = s.id
                    WHERE jes.job_experience_id = ?
                    ORDER BY s.name
                """, (job_id,)).fetchall()
                job["skills"] = [dict(row) for row in skills_rows]

                # Get tools
                tools_rows = conn.execute("""
                    SELECT t.* FROM experience_tools t
                    JOIN experience_job_experience_tools jet ON jet.tool_id = t.id
                    WHERE jet.job_experience_id = ?
                    ORDER BY t.name
                """, (job_id,)).fetchall()
                job["tools"] = [dict(row) for row in tools_rows]

                # Get soft skills
                soft_skills_rows = conn.execute("""
                    SELECT ss.* FROM experience_soft_skills ss
                    JOIN experience_job_experience_soft_skills jess ON jess.soft_skill_id = ss.id
                    WHERE jess.job_experience_id = ?
                    ORDER BY ss.name
                """, (job_id,)).fetchall()
                job["soft_skills"] = [dict(row) for row in soft_skills_rows]

                # Parse JSON fields
                if job.get("key_achievements"):
                    try:
                        job["key_achievements"] = json.loads(job["key_achievements"])
                    except json.JSONDecodeError:
                        job["key_achievements"] = []
                else:
                    job["key_achievements"] = []

                if job.get("key_responsibilities"):
                    try:
                        job["key_responsibilities"] = json.loads(job["key_responsibilities"])
                    except json.JSONDecodeError:
                        job["key_responsibilities"] = []
                else:
                    job["key_responsibilities"] = []

                # Calculate duration
                job["duration"] = calculate_duration(job["start_date"], job.get("end_date"))

                jobs_list.append(job)

            # Get education
            try:
                education_rows = conn.execute("""
                    SELECT * FROM experience_education
                    ORDER BY timeline_date DESC
                """).fetchall()
                education_list = []
                for edu_row in education_rows:
                    edu = dict(edu_row)
                    if edu.get("honors_memberships"):
                        try:
                            edu["honors_memberships"] = json.loads(edu["honors_memberships"])
                        except json.JSONDecodeError:
                            edu["honors_memberships"] = []
                    else:
                        edu["honors_memberships"] = []
                    education_list.append(edu)
            except sqlite3.OperationalError:
                education_list = []

            # Get certifications
            try:
                certification_rows = conn.execute("""
                    SELECT * FROM experience_certifications
                    ORDER BY sort_order, issued_date DESC, name
                """).fetchall()
                certifications_list = [dict(row) for row in certification_rows]
            except sqlite3.OperationalError:
                certifications_list = []

            # Group jobs by company
            companies_dict = {}
            for company in companies:
                companies_dict[company["id"]] = {
                    "id": company["id"],
                    "name": company["name"],
                    "logo": company.get("logo_url") or "",
                    "description": company.get("description") or "",
                    "location": company.get("location") or "",
                    "positions": []
                }

            # Add jobs to companies (jobs_list is already sorted by start_date DESC)
            for job in jobs_list:
                company_id = job["company_id"]
                if company_id in companies_dict:
                    companies_dict[company_id]["positions"].append(job)

            # Calculate total duration per company and ensure positions are sorted
            for company_id, company_data in companies_dict.items():
                if company_data["positions"]:
                    # Ensure positions are sorted by start_date DESC (newest first)
                    company_data["positions"].sort(key=lambda x: x["start_date"], reverse=True)

                    # Find earliest start and latest end
                    starts = [pos["start_date"] for pos in company_data["positions"]]
                    ends = [pos.get("end_date") for pos in company_data["positions"] if pos.get("end_date")]
                    earliest_start = min(starts)
                    latest_end = max(ends) if ends else None
                    company_data["total_duration"] = calculate_duration(earliest_start, latest_end)
                else:
                    company_data["total_duration"] = ""

            # Sort companies by most recent job start_date (newest first)
            companies_list = list(companies_dict.values())
            companies_list.sort(key=lambda c: (
                max([pos["start_date"] for pos in c["positions"]]) if c["positions"] else "0000-01-01"
            ), reverse=True)

            return JSONResponse(content={
                "companies": companies_list,
                "education": education_list,
                "certifications": certifications_list
            })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.get("/api/cms/blocks")
def api_cms_blocks() -> JSONResponse:
    """API endpoint to fetch all active CMS blocks for frontend"""
    try:
        with get_conn() as conn:
            # Select all columns including image_position, image_description, and gallery_images
            blocks_rows = conn.execute("""
                SELECT block_id, title, content, content_format, description, image,
                       image_position, image_description, gallery_images
                FROM cms_blocks
                WHERE is_active = 1
                ORDER BY sort_order, title
            """).fetchall()
            blocks = {}
            for row in blocks_rows:
                row_dict = row_to_dict(row)

                # Parse gallery_images JSON if present
                gallery_images = []
                if row_dict.get("gallery_images"):
                    try:
                        gallery_images = json.loads(row_dict["gallery_images"])
                        if not isinstance(gallery_images, list):
                            gallery_images = []
                    except (json.JSONDecodeError, ValueError):
                        gallery_images = []

                blocks[row_dict["block_id"]] = {
                    "block_id": row_dict["block_id"],
                    "title": row_dict["title"],
                    "content": row_dict["content"],
                    "content_format": row_dict.get("content_format") or "html",
                    "description": row_dict.get("description") or "",
                    "image": row_dict.get("image") or "",
                    "image_position": row_dict.get("image_position") or "right",
                    "image_description": row_dict.get("image_description") or "",
                    "gallery_images": gallery_images,
                }
        return JSONResponse(content={
            "success": True,
            "blocks": blocks
        })
    except Exception as e:
        return JSONResponse(content={
            "success": False,
            "error": str(e),
            "blocks": {}
        })


@app.get("/api/cms/settings")
def api_cms_settings() -> JSONResponse:
    """API endpoint to fetch all site settings for frontend"""
    try:
        with get_conn() as conn:
            settings_rows = conn.execute("""
                SELECT setting_key, setting_value, setting_type
                FROM cms_site_settings
                ORDER BY setting_key
            """).fetchall()
            settings = {}
            for row in settings_rows:
                value = row["setting_value"]
                # Parse JSON if type is json
                if row["setting_type"] == "json":
                    try:
                        value = json.loads(value)
                    except json.JSONDecodeError:
                        pass
                settings[row["setting_key"]] = value
        return JSONResponse(content={
            "success": True,
            "settings": settings
        })
    except Exception as e:
        return JSONResponse(content={
            "success": False,
            "error": str(e),
            "settings": {}
        })


@app.get("/api/cms/contact")
def api_cms_contact() -> JSONResponse:
    """API endpoint to fetch all public contact info for frontend"""
    try:
        with get_conn() as conn:
            # Ensure new columns exist (for migration)
            try:
                conn.execute("ALTER TABLE cms_contact_info ADD COLUMN description TEXT")
                conn.commit()
            except sqlite3.OperationalError:
                pass
            try:
                conn.execute("ALTER TABLE cms_contact_info ADD COLUMN show_in_get_in_touch INTEGER DEFAULT 0")
                conn.commit()
            except sqlite3.OperationalError:
                pass
            try:
                conn.execute("ALTER TABLE cms_contact_info ADD COLUMN get_in_touch_title TEXT")
                conn.commit()
            except sqlite3.OperationalError:
                pass
            try:
                conn.execute("ALTER TABLE cms_contact_info ADD COLUMN get_in_touch_description TEXT")
                conn.commit()
            except sqlite3.OperationalError:
                pass

            contact_rows = conn.execute("""
                SELECT field_name, label, value, field_type, icon, description,
                       show_in_get_in_touch, get_in_touch_title, get_in_touch_description
                FROM cms_contact_info
                WHERE is_public = 1
                ORDER BY sort_order, field_name
            """).fetchall()
            contact_fields = []
            for row in contact_rows:
                # Handle fields that may not exist in older databases
                description = ""
                show_in_get_in_touch = 0
                get_in_touch_title = ""
                get_in_touch_description = ""
                try:
                    description = row["description"] or ""
                except (KeyError, IndexError):
                    pass
                try:
                    show_in_get_in_touch = row["show_in_get_in_touch"] or 0
                except (KeyError, IndexError):
                    pass
                try:
                    get_in_touch_title = row["get_in_touch_title"] or ""
                except (KeyError, IndexError):
                    pass
                try:
                    get_in_touch_description = row["get_in_touch_description"] or ""
                except (KeyError, IndexError):
                    pass

                contact_fields.append({
                    "field_name": row["field_name"],
                    "label": row["label"],
                    "value": row["value"],
                    "field_type": row["field_type"],
                    "icon": row["icon"] or "",
                    "description": description,
                    "show_in_get_in_touch": show_in_get_in_touch,
                    "get_in_touch_title": get_in_touch_title,
                    "get_in_touch_description": get_in_touch_description,
                })
        return JSONResponse(content={
            "success": True,
            "contact_fields": contact_fields
        })
    except Exception as e:
        return JSONResponse(content={
            "success": False,
            "error": str(e),
            "contact_fields": []
        })


# ============================================================================
# Blog System Routes
# ============================================================================

@app.get("/blog/posts.json")
def blog_posts_json() -> JSONResponse:
    """Legacy endpoint: Serve blog posts as JSON (for backward compatibility with blog post HTML files)"""
    return api_blog_posts()


@app.get("/api/blog/posts")
def api_blog_posts() -> JSONResponse:
    """API endpoint to fetch all blog posts for frontend"""
    try:
        with get_conn() as conn:
            posts_rows = conn.execute("""
                SELECT bp.id, bp.slug, bp.title, bp.excerpt, bp.author, bp.date,
                       bp.tags, bp.featured, bp.read_time, bp.cover_image, bp.created_at, bp.updated_at, bp.status,
                       bc.label as category, bc.code as category_code, bc.id as category_id
                FROM blog_posts bp
                LEFT JOIN blog_categories bc ON bp.category_id = bc.id
                WHERE bp.status = 'Published' OR bp.status IS NULL
                ORDER BY bp.date DESC, bp.created_at DESC
            """).fetchall()

            posts = []
            for row in posts_rows:
                post = dict(row)
                # Parse tags JSON
                if post.get("tags"):
                    try:
                        post["tags"] = json.loads(post["tags"])
                    except:
                        post["tags"] = []
                else:
                    post["tags"] = []
                posts.append(post)

        return JSONResponse(content={"posts": posts})
    except Exception as e:
        return JSONResponse(content={"posts": [], "error": str(e)}, status_code=500)


@app.get("/admin/blog")
def blog_list(request: Request) -> Any:
    """List all blog posts"""
    try:
        with get_conn() as conn:
            posts_rows = conn.execute("""
                SELECT bp.id, bp.slug, bp.title, bp.excerpt, bp.author, bp.date,
                       bp.tags, bp.featured, bp.read_time, bp.cover_image, bp.created_at, bp.updated_at, bp.status,
                       bc.label as category, bc.id as category_id
                FROM blog_posts bp
                LEFT JOIN blog_categories bc ON bp.category_id = bc.id
                ORDER BY bp.date DESC, bp.created_at DESC
            """).fetchall()
            posts = [dict(row) for row in posts_rows]
            # Parse tags JSON and set default status
            for post in posts:
                if post.get("tags"):
                    try:
                        post["tags"] = json.loads(post["tags"])
                    except:
                        post["tags"] = []
                else:
                    post["tags"] = []
                if not post.get("status"):
                    post["status"] = "Published"

            # Fetch categories for filter dropdown
            categories_rows = conn.execute("""
                SELECT id, code, label, icon
                FROM blog_categories
                ORDER BY display_order, label
            """).fetchall()
            categories = [dict(row) for row in categories_rows]
    except Exception as e:
        posts = []
        categories = []

    return templates.TemplateResponse(request, "blog/blog_list.html",
        {"request": request, "posts": posts, "categories": categories},
    )


@app.post("/admin/blog/regenerate")
def blog_regenerate(request: Request) -> RedirectResponse:
    blog_mgr = BLOG_MANAGER if HAS_BLOG_MANAGER and BLOG_MANAGER else None
    if not blog_mgr:
        blog_mgr = _load_blog_manager()

    with get_conn() as conn:
        rows = conn.execute("""
            SELECT bp.id, bp.slug, bp.title, bp.excerpt, bp.author, bp.date,
                   bp.tags, bp.cover_image, bp.content_html, bp.content_markdown, bp.status,
                   bc.label as category
            FROM blog_posts bp
            LEFT JOIN blog_categories bc ON bp.category_id = bc.id
            WHERE bp.status = 'Published'
            ORDER BY bp.id
        """).fetchall()

    for row in rows:
        tags_list = []
        if row["tags"]:
            try:
                tags_list = json.loads(row["tags"])
            except Exception:
                tags_list = [tag.strip() for tag in row["tags"].split(",") if tag.strip()]

        metadata = {
            "title": row["title"],
            "slug": row["slug"],
            "excerpt": row["excerpt"] or "",
            "author": row["author"] or "Bradley R. Clampitt",
            "date": row["date"] or "",
            "category": row["category"] or "",
            "tags": tags_list,
            "cover_image": row["cover_image"] or "",
        }

        html_body = row["content_html"] or ""
        if blog_mgr and row["content_markdown"]:
            try:
                html_body = blog_mgr.markdown_to_html(row["content_markdown"])
            except Exception as e:
                print(f"Warning: Failed to reprocess markdown for {row['slug']}: {e}")

        if blog_mgr:
            try:
                blog_mgr.generate_post_html_from_db(metadata, html_body, row["slug"])
            except Exception as e:
                print(f"Warning: Failed to regenerate blog post {row['slug']}: {e}")

    return RedirectResponse(url=f"{request.url_for('blog_list')}?success=posts_regenerated", status_code=303)


@app.get("/admin/blog/new")
def blog_new(request: Request) -> Any:
    """New blog post form"""
    with get_conn() as conn:
        categories_rows = conn.execute("""
            SELECT id, code, label, description, icon, display_order
            FROM blog_categories
            ORDER BY display_order, label
        """).fetchall()
        categories = [dict(row) for row in categories_rows]

    return templates.TemplateResponse(request, "blog/blog_edit.html",
        {"request": request, "post": None, "categories": categories},
    )


@app.get("/admin/blog/categories")
def blog_categories_list(request: Request) -> Any:
    """List all blog categories"""
    try:
        with get_conn() as conn:
            categories_rows = conn.execute("""
                SELECT bc.id, bc.code, bc.label, bc.description, bc.icon, bc.display_order,
                       COUNT(bp.id) as post_count
                FROM blog_categories bc
                LEFT JOIN blog_posts bp ON bp.category_id = bc.id
                GROUP BY bc.id
                ORDER BY bc.display_order, bc.label
            """).fetchall()
            categories = [dict(row) for row in categories_rows]
    except Exception as e:
        categories = []

    return templates.TemplateResponse(request, "blog/blog_categories_list.html",
        {"request": request, "categories": categories},
    )


@app.post("/admin/blog/categories/save")
def blog_category_save(
    request: Request,
    category_id: str | None = Form(None),
    code: str = Form(...),
    label: str = Form(...),
    description: str | None = Form(None),
    icon: str | None = Form(None),
    display_order: str | None = Form(None),
) -> RedirectResponse:
    """Save blog category"""
    category_pk = _optional_int(category_id)
    display_order_int = _optional_int(display_order) or 0

    with get_conn() as conn:
        cur = conn.cursor()
        if category_pk is None:
            cur.execute("""
                INSERT INTO blog_categories (code, label, description, icon, display_order)
                VALUES (?, ?, ?, ?, ?)
            """, (
                code.strip().lower(),
                label.strip(),
                description.strip() if description else None,
                icon.strip() if icon else None,
                display_order_int,
            ))
        else:
            cur.execute("""
                UPDATE blog_categories SET
                    code = ?,
                    label = ?,
                    description = ?,
                    icon = ?,
                    display_order = ?,
                    updated_at = datetime('now')
                WHERE id = ?
            """, (
                code.strip().lower(),
                label.strip(),
                description.strip() if description else None,
                icon.strip() if icon else None,
                display_order_int,
                category_pk,
            ))
        conn.commit()

    return RedirectResponse(url="/admin/blog/categories", status_code=303)


@app.post("/admin/blog/categories/reorder")
def blog_categories_reorder(
    request: Request,
    category_orders: str = Form(...),  # JSON string: {"1": 1, "2": 2, ...}
) -> JSONResponse:
    import json
    from datetime import datetime
    
    try:
        orders = json.loads(category_orders)
        with get_conn() as conn:
            now = datetime.now().isoformat()
            for cat_id, order in orders.items():
                conn.execute("""
                    UPDATE blog_categories
                    SET display_order = ?, updated_at = ?
                    WHERE id = ?
                """, (order, now, int(cat_id)))
            conn.commit()
        return JSONResponse(content={"success": True})
    except Exception as e:
        return JSONResponse(content={"success": False, "error": str(e)}, status_code=500)


@app.post("/admin/blog/categories/delete")
def blog_category_delete(
    request: Request,
    category_id: str = Form(...),
) -> RedirectResponse:
    """Delete a blog category"""
    category_pk = _optional_int(category_id)

    if not category_pk:
        raise HTTPException(status_code=400, detail="Category ID is required")

    with get_conn() as conn:
        # Check if category is used in any posts
        usage_count = conn.execute("""
            SELECT COUNT(*) as count FROM blog_posts
            WHERE category_id = ?
        """, (category_pk,)).fetchone()

        if usage_count["count"] > 0:
            return RedirectResponse(
                url="/admin/blog/categories?error=Cannot delete category that is assigned to blog posts",
                status_code=303
            )

        conn.execute("DELETE FROM blog_categories WHERE id = ?", (category_pk,))
        conn.commit()

    return RedirectResponse(url="/admin/blog/categories", status_code=303)


@app.get("/admin/blog/{post_id}")
def blog_edit(request: Request, post_id: int) -> Any:
    """Edit blog post form"""
    with get_conn() as conn:
        post = conn.execute(
            "SELECT * FROM blog_posts WHERE id = ?", (post_id,)
        ).fetchone()
        if not post:
            raise HTTPException(status_code=404, detail="Blog post not found")

        # Get categories for dropdown
        categories_rows = conn.execute("""
            SELECT id, code, label, description, icon, display_order
            FROM blog_categories
            ORDER BY display_order, label
        """).fetchall()
        categories = [dict(row) for row in categories_rows]

        post_dict = dict(post)
        # Parse tags JSON
        if post_dict.get("tags"):
            try:
                post_dict["tags"] = json.loads(post_dict["tags"])
            except:
                post_dict["tags"] = []
        else:
            post_dict["tags"] = []

    return templates.TemplateResponse(request, "blog/blog_edit.html",
        {"request": request, "post": post_dict, "categories": categories},
    )


@app.post("/admin/blog/save")
def blog_save(
    request: Request,
    post_id: str | None = Form(None),
    title: str = Form(...),
    slug: str | None = Form(None),
    excerpt: str | None = Form(None),
    content_markdown: str = Form(...),
    author: str = Form(...),
    date: str = Form(...),
    category_id: str | None = Form(None),
    tags: str | None = Form(None),
    featured: str | None = Form(None),
    cover_image: str | None = Form(None),
    status: str = Form("Published"),
) -> RedirectResponse:
    """Save blog post"""
    post_pk = _optional_int(post_id)
    category_pk = _optional_int(category_id)

    # Generate slug if not provided
    if not slug or not slug.strip():
        slug = magento_slugify(title)

    # Process tags
    tags_list = []
    if tags:
        # Handle comma-separated tags
        tags_list = [tag.strip() for tag in tags.split(",") if tag.strip()]
    tags_json = json.dumps(tags_list) if tags_list else None

    # Process markdown to HTML using BlogManager
    # Reload BlogManager module to ensure we have the latest code changes
    content_html = ""
    blog_manager_instance = None
    try:
        blog_manager_path = BLOG_RESOURCES / "blog-manager.py"
        if blog_manager_path.exists():
            # Force reload by using a unique module name with timestamp to avoid caching
            # This ensures we always get the latest code from disk
            import time
            unique_name = f"blog_manager_{int(time.time() * 1000000)}"
            spec = importlib.util.spec_from_file_location(unique_name, str(blog_manager_path))
            blog_manager_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(blog_manager_module)
            # BlogManager expects the blog root directory (where HTML files are generated), not the resources directory
            blog_manager_instance = blog_manager_module.BlogManager(str(ROOT / "blog"))
            content_html = blog_manager_instance.markdown_to_html(content_markdown.strip())
        else:
            raise ImportError("BlogManager file not found")
    except Exception as e:
        print(f"Error processing markdown with reloaded BlogManager: {e}")
        # Fallback to cached BLOG_MANAGER if available
        if HAS_BLOG_MANAGER and BLOG_MANAGER:
            try:
                content_html = BLOG_MANAGER.markdown_to_html(content_markdown.strip())
            except Exception as e2:
                print(f"Error with cached BlogManager: {e2}")
                # Fallback to basic markdown processing
                import markdown
                content_html = markdown.markdown(content_markdown.strip(), extensions=['extra', 'attr_list', 'md_in_html'])
        else:
            # Fallback if BlogManager not available
            import markdown
            content_html = markdown.markdown(content_markdown.strip(), extensions=['extra', 'attr_list', 'md_in_html'])

    # Calculate read time
    words = len(content_markdown.split())
    read_time = f"{max(1, round(words / 220))} min read"

    with get_conn() as conn:
        cur = conn.cursor()
        if post_pk is None:
            cur.execute("""
                INSERT INTO blog_posts (slug, title, excerpt, content_markdown, content_html, author, date, category_id, tags, featured, read_time, cover_image, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                slug.strip(),
                title.strip(),
                excerpt.strip() if excerpt else None,
                content_markdown.strip(),
                content_html,
                author.strip(),
                date.strip(),
                category_pk,
                tags_json,
                1 if featured == "on" or featured == "1" else 0,
                read_time,
                cover_image.strip() if cover_image else None,
                status,
            ))
        else:
            # Get old slug before updating (to delete old HTML file if slug changed)
            old_post_row = conn.execute("SELECT slug FROM blog_posts WHERE id = ?", (post_pk,)).fetchone()
            old_slug = old_post_row[0] if old_post_row else None

            cur.execute("""
                UPDATE blog_posts SET
                    slug = ?,
                    title = ?,
                    excerpt = ?,
                    content_markdown = ?,
                    content_html = ?,
                    author = ?,
                    date = ?,
                    category_id = ?,
                    tags = ?,
                    featured = ?,
                    read_time = ?,
                    cover_image = ?,
                    status = ?,
                    updated_at = datetime('now')
                WHERE id = ?
            """, (
                slug.strip(),
                title.strip(),
                excerpt.strip() if excerpt else None,
                content_markdown.strip(),
                content_html,
                author.strip(),
                date.strip(),
                category_pk,
                tags_json,
                1 if featured == "on" or featured == "1" else 0,
                read_time,
                cover_image.strip() if cover_image else None,
                status,
                post_pk,
            ))

            # Delete old HTML file if slug changed
            # Use reloaded instance if available, otherwise cached
            blog_mgr_for_delete = blog_manager_instance if blog_manager_instance else (BLOG_MANAGER if HAS_BLOG_MANAGER and BLOG_MANAGER else None)
            if old_slug and old_slug != slug.strip() and blog_mgr_for_delete:
                old_html_file = blog_mgr_for_delete.posts_html_dir / f"{old_slug}.html"
                if old_html_file.exists():
                    try:
                        old_html_file.unlink()
                        print(f"Deleted old HTML file: {old_html_file}")
                    except Exception as e:
                        print(f"Warning: Failed to delete old HTML file {old_html_file}: {e}")

        # Get the post ID (for new posts, get the last insert rowid)
        if post_pk is None:
            post_pk = cur.lastrowid

        # Get category label if category_id exists
        category_label = None
        if category_pk:
            category_row = conn.execute("SELECT label FROM blog_categories WHERE id = ?", (category_pk,)).fetchone()
            if category_row:
                category_label = category_row[0]

        conn.commit()

        # Generate static HTML file only if status is "Published"
        # Use the reloaded blog_manager_instance if available, otherwise fall back to cached BLOG_MANAGER
        blog_mgr = blog_manager_instance if blog_manager_instance else (BLOG_MANAGER if HAS_BLOG_MANAGER and BLOG_MANAGER else None)

        if blog_mgr and status == 'Published':
            try:
                # Prepare metadata dict for HTML generation
                metadata = {
                    'title': title.strip(),
                    'slug': slug.strip(),
                    'excerpt': excerpt.strip() if excerpt else None,
                    'author': author.strip(),
                    'date': date.strip(),
                    'category': category_label or '',
                    'tags': tags_list,
                    'featured': 1 if featured == "on" or featured == "1" else 0,
                    'readTime': read_time,
                    'cover_image': cover_image.strip() if cover_image else None,
                }

                # Generate HTML file
                success, output_path = blog_mgr.generate_post_html_from_db(
                    metadata,
                    content_html,
                    slug.strip()
                )

                if not success:
                    print(f"Warning: Failed to generate HTML file for post {post_pk}")
                    return RedirectResponse(url=f"/admin/blog?error=html_generation_failed", status_code=303)
                else:
                    print(f"Successfully generated HTML file: {output_path}")
            except Exception as e:
                print(f"Error generating HTML file: {e}")
                import traceback
                traceback.print_exc()
                return RedirectResponse(url=f"/admin/blog?error=html_generation_error", status_code=303)
        elif status != 'Published':
            # Remove generated HTML when switching a post to Draft (or any non-published state)
            posts_html_dir = blog_mgr.posts_html_dir if blog_mgr else (ROOT / "blog" / "posts")
            draft_html_file = posts_html_dir / f"{slug.strip()}.html"
            if draft_html_file.exists():
                try:
                    draft_html_file.unlink()
                    print(f"Deleted draft HTML file: {draft_html_file}")
                except Exception as e:
                    print(f"Warning: Failed to delete draft HTML file {draft_html_file}: {e}")

        # Regenerate posts.json from database (only Published posts) - always regenerate after save
        try:
            regenerate_posts_json(conn)
        except Exception as e:
            print(f"Warning: Failed to regenerate posts.json: {e}")

    return RedirectResponse(url=f"/admin/blog?success=saved&post_id={post_pk}", status_code=303)

    return RedirectResponse(url="/admin/blog", status_code=303)


def regenerate_posts_json(conn: sqlite3.Connection) -> None:
    """Regenerate blog/posts.json from database, excluding drafts"""
    try:
        posts_rows = conn.execute("""
            SELECT bp.id, bp.slug, bp.title, bp.excerpt, bp.author, bp.date,
                   bp.tags, bp.featured, bp.read_time, bp.cover_image,
                   bc.label as category
            FROM blog_posts bp
            LEFT JOIN blog_categories bc ON bp.category_id = bc.id
            WHERE bp.status = 'Published' OR bp.status IS NULL
            ORDER BY bp.date DESC, bp.created_at DESC
        """).fetchall()

        posts = []
        for row in posts_rows:
            post = dict(row)
            # Parse tags JSON
            if post.get("tags"):
                try:
                    post["tags"] = json.loads(post["tags"])
                except:
                    post["tags"] = []
            else:
                post["tags"] = []

            # Format for posts.json
            posts.append({
                "id": post["id"],
                "slug": post["slug"],
                "title": post["title"],
                "excerpt": post.get("excerpt") or "",
                "author": post.get("author") or "Bradley R. Clampitt",
                "date": post.get("date") or "",
                "category": post.get("category") or "",
                "tags": post["tags"],
                "featured": bool(post.get("featured", 0)),
                "readTime": post.get("read_time") or "",
                "coverImage": post.get("cover_image") or "",
            })

        # Write posts.json
        posts_json_path = BLOG_RESOURCES / "posts.json"
        with open(posts_json_path, 'w', encoding='utf-8') as f:
            json.dump({"posts": posts}, f, indent=2)

        print(f"Regenerated posts.json with {len(posts)} published posts")
    except Exception as e:
        print(f"Error regenerating posts.json: {e}")
        import traceback
        traceback.print_exc()


@app.post("/admin/blog/images/upload")
async def blog_image_upload(
    post_id: int = Form(...),
    file: UploadFile = File(...),
    is_cover: bool = Form(False),
) -> RedirectResponse:
    """Upload an image for a blog post"""
    # Validate image upload
    content, ext, error_msg = await _validate_image_upload(file)
    if error_msg:
        return RedirectResponse(
            url=f"/admin/blog/{post_id}?error={error_msg.replace(' ', '+')}",
            status_code=303
        )

    # Create blog images directory for this post
    post_img_dir = BLOG_MEDIA / str(post_id)
    post_img_dir.mkdir(parents=True, exist_ok=True)

    # Generate safe filename
    safe_filename = secrets.token_urlsafe(16) + ext
    file_path = post_img_dir / safe_filename
    
    # Ensure we're writing within the intended directory
    try:
        file_path.resolve().relative_to(post_img_dir.resolve())
    except ValueError:
        return RedirectResponse(
            url=f"/admin/blog/{post_id}?error=Invalid+file+path",
            status_code=303
        )
    
    url = f"/assets/images/blog/{post_id}/{safe_filename}"

    # Save file
    try:
        with file_path.open("wb") as f:
            f.write(content)
    except Exception as e:
        import sys
        print(f"Error writing file: {e}", file=sys.stderr)
        return RedirectResponse(
            url=f"/admin/blog/{post_id}?error=Error+saving+file",
            status_code=303
        )

    # If this is a cover image, update the blog post
    if is_cover:
        with get_conn() as conn:
            conn.execute("""
                UPDATE blog_posts SET cover_image = ? WHERE id = ?
            """, (url, post_id))
            conn.commit()

    return RedirectResponse(url=f"/admin/blog/{post_id}?success=Image+uploaded+successfully", status_code=303)


@app.get("/admin/projects/images/browse")
def projects_images_browse() -> JSONResponse:
    """List all available images from assets/images/portfolio directory"""
    images = []
    portfolio_dir = ROOT / "assets" / "images" / "portfolio"

    if portfolio_dir.exists() and portfolio_dir.is_dir():
        # Scan all subdirectories recursively
        for item in portfolio_dir.rglob("*"):
            if item.is_file() and item.suffix.lower() in IMAGE_EXTENSIONS:
                # Get relative path from assets/images directory
                relative_path = item.relative_to(ROOT / "assets" / "images")
                url = f"/assets/images/{relative_path.as_posix()}"
                images.append({
                    "url": url,
                    "filename": item.name,
                    "path": str(relative_path),
                    "size": item.stat().st_size
                })

    # Sort by filename
    images.sort(key=lambda x: x["filename"].lower())

    return JSONResponse(content={"images": images})


@app.get("/admin/blog/images/browse")
def blog_images_browse() -> JSONResponse:
    """List all available images from assets/images/blog directory"""
    images = []
    blog_dir = BLOG_MEDIA

    if blog_dir.exists() and blog_dir.is_dir():
        # Scan all subdirectories recursively
        for item in blog_dir.rglob("*"):
            if item.is_file() and item.suffix.lower() in IMAGE_EXTENSIONS:
                # Get relative path from assets/images directory
                relative_path = item.relative_to(ROOT / "assets" / "images")
                url = f"/assets/images/{relative_path.as_posix()}"
                images.append({
                    "url": url,
                    "filename": item.name,
                    "path": str(relative_path),
                    "size": item.stat().st_size
                })

    # Sort by filename
    images.sort(key=lambda x: x["filename"].lower())

    return JSONResponse(content={"images": images})


@app.get("/admin/cms/blocks/images/browse")
def cms_blocks_images_browse() -> JSONResponse:
    """List all available images from assets/images/personal and assets/images directories"""
    images = []

    # Scan assets/images/personal directory
    personal_dir = ROOT / "assets" / "images" / "personal"
    if personal_dir.exists() and personal_dir.is_dir():
        for item in personal_dir.rglob("*"):
            if item.is_file() and item.suffix.lower() in IMAGE_EXTENSIONS:
                relative_path = item.relative_to(ROOT / "assets" / "images")
                url = f"/assets/images/{relative_path.as_posix()}"
                images.append({
                    "url": url,
                    "filename": item.name,
                    "path": str(relative_path),
                    "size": item.stat().st_size,
                    "directory": "personal"
                })

    # Scan assets/images directory (root level only, not subdirectories)
    images_dir = ROOT / "assets" / "images"
    if images_dir.exists() and images_dir.is_dir():
        for item in images_dir.iterdir():
            if item.is_file() and item.suffix.lower() in IMAGE_EXTENSIONS:
                relative_path = item.relative_to(ROOT / "assets" / "images")
                url = f"/assets/images/{relative_path.as_posix()}"
                images.append({
                    "url": url,
                    "filename": item.name,
                    "path": str(relative_path),
                    "size": item.stat().st_size,
                    "directory": "root"
                })

    # Sort by directory, then filename
    images.sort(key=lambda x: (x["directory"], x["filename"].lower()))

    return JSONResponse(content={"images": images})


@app.post("/admin/cms/blocks/images/upload")
async def cms_blocks_image_upload(
    block_id: int = Form(...),
    file: UploadFile = File(...),
) -> RedirectResponse:
    """Upload an image for a CMS block"""
    # Validate image upload
    content, ext, error_msg = await _validate_image_upload(file)
    if error_msg:
        return RedirectResponse(
            url=f"/admin/cms/blocks/{block_id}?error={error_msg.replace(' ', '+')}",
            status_code=303
        )

    # Create CMS blocks images directory
    cms_img_dir = ROOT / "assets" / "images" / "cms-blocks"
    cms_img_dir.mkdir(parents=True, exist_ok=True)

    # Generate safe filename
    safe_filename = secrets.token_urlsafe(16) + ext
    file_path = cms_img_dir / safe_filename
    
    # Ensure we're writing within the intended directory
    try:
        file_path.resolve().relative_to(cms_img_dir.resolve())
    except ValueError:
        return RedirectResponse(
            url=f"/admin/cms/blocks/{block_id}?error=Invalid+file+path",
            status_code=303
        )
    
    url = f"/assets/images/cms-blocks/{safe_filename}"

    # Save file
    try:
        with file_path.open("wb") as f:
            f.write(content)
    except Exception as e:
        import sys
        print(f"Error writing file: {e}", file=sys.stderr)
        return RedirectResponse(
            url=f"/admin/cms/blocks/{block_id}?error=Error+saving+file",
            status_code=303
        )

    # Update the CMS block with the image URL
    with get_conn() as conn:
        conn.execute("""
            UPDATE cms_blocks SET image = ? WHERE id = ?
        """, (url, block_id))
        conn.commit()

    return RedirectResponse(url=f"/admin/cms/blocks/{block_id}?success=Image+uploaded+successfully", status_code=303)


@app.post("/admin/blog/images/set-cover")
def blog_image_set_cover(
    post_id: int = Form(...),
    cover_image: str = Form(...),
) -> RedirectResponse:
    """Set cover image from existing uploaded image"""
    with get_conn() as conn:
        conn.execute("""
            UPDATE blog_posts SET cover_image = ? WHERE id = ?
        """, (cover_image, post_id))
        conn.commit()

    return RedirectResponse(url=f"/admin/blog/{post_id}", status_code=303)


@app.post("/admin/blog/images/remove-cover")
def blog_image_remove_cover(
    post_id: int = Form(...),
) -> RedirectResponse:
    """Remove cover image from a blog post"""
    with get_conn() as conn:
        conn.execute("""
            UPDATE blog_posts SET cover_image = NULL WHERE id = ?
        """, (post_id,))
        conn.commit()

    return RedirectResponse(url=f"/admin/blog/{post_id}", status_code=303)


@app.post("/admin/blog/delete")
def blog_delete(
    request: Request,
    post_id: str = Form(...),
) -> RedirectResponse:
    """Delete a blog post"""
    post_pk = _optional_int(post_id)

    if not post_pk:
        raise HTTPException(status_code=400, detail="Blog post ID is required")

    with get_conn() as conn:
        # Get slug before deleting
        post_row = conn.execute("SELECT slug FROM blog_posts WHERE id = ?", (post_pk,)).fetchone()
        slug = post_row[0] if post_row else None

        # Delete from database
        conn.execute("DELETE FROM blog_posts WHERE id = ?", (post_pk,))
        conn.commit()

    # Delete HTML file if it exists
    if slug and HAS_BLOG_MANAGER and BLOG_MANAGER:
        html_file = BLOG_MANAGER.posts_html_dir / f"{slug}.html"
        if html_file.exists():
            try:
                html_file.unlink()
                print(f"Deleted HTML file: {html_file}")
            except Exception as e:
                print(f"Warning: Failed to delete HTML file {html_file}: {e}")

    return RedirectResponse(url="/admin/blog", status_code=303)


@app.post("/admin/blog/preview")
async def blog_preview(
    request: Request,
    content_markdown: str = Form(...),
) -> dict:
    """
    Preview endpoint that processes markdown using BlogManager.
    Returns the processed HTML that matches the frontend rendering exactly.
    """
    if not content_markdown or not content_markdown.strip():
        return {"html": "<p class='text-slate-500 italic'>No content to preview.</p>"}

    if not HAS_BLOG_MANAGER or not BLOG_MANAGER:
        return {
            "html": "<p class='text-red-600'>BlogManager not available. Preview unavailable.</p>",
            "error": "BlogManager not available"
        }

    try:
        # Process markdown using BlogManager (same as frontend)
        processed_html = BLOG_MANAGER.markdown_to_html(content_markdown.strip())
        return {"html": processed_html}
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {
            "html": f"<p class='text-red-600'>Error processing markdown: {str(e)}</p>",
            "error": str(e)
        }
