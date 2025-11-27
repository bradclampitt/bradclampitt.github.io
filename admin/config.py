"""
Centralized configuration for the admin application.
All paths and settings are defined here.
"""
from pathlib import Path

# Base paths
ROOT = Path(__file__).resolve().parents[1]
ADMIN_ROOT = Path(__file__).resolve().parent

# Database paths
DATABASE_DIR = ADMIN_ROOT / "database"
DATABASE_PATH = DATABASE_DIR / "unified.sqlite"
DEMO_DATABASE_PATH = DATABASE_DIR / "demo.sqlite"
SCHEMA_PATH = DATABASE_DIR / "schema.sql"

# Resources (section folders)
RESOURCES_DIR = ADMIN_ROOT / "resources"

# Templates & Static
TEMPLATES_DIR = ADMIN_ROOT / "templates"
STATIC_DIR = ADMIN_ROOT / "static"

# Media directories (keep in assets for frontend access)
MEDIA_ROOT = ROOT / "assets" / "images"

# Section-specific media paths
BLOG_MEDIA = MEDIA_ROOT / "blog"
DOCUMENTS_MEDIA = MEDIA_ROOT / "documents"
PORTFOLIO_MEDIA = MEDIA_ROOT / "portfolio"
PROJECTS_MEDIA = MEDIA_ROOT / "projects"
MAGENTO_MEDIA = MEDIA_ROOT / "magento"
PHOTOGRAPHY_MEDIA = MEDIA_ROOT / "photography"
LOGO_MEDIA = MEDIA_ROOT / "logos"

# Section resource paths (for backward compatibility during migration)
BLOG_RESOURCES = RESOURCES_DIR / "blog"
DOCUMENTS_RESOURCES = RESOURCES_DIR / "documents"
PORTFOLIOS_RESOURCES = RESOURCES_DIR / "portfolios"
REFERENCES_RESOURCES = RESOURCES_DIR / "references"
TECH_SKILLS_RESOURCES = RESOURCES_DIR / "tech-skills"
SIDE_PROJECTS_RESOURCES = RESOURCES_DIR / "side-projects"
MAGENTO_RESOURCES = RESOURCES_DIR / "magento"
PHOTOGRAPHY_RESOURCES = RESOURCES_DIR / "photography"
EXPERIENCE_RESOURCES = RESOURCES_DIR / "experience"
CMS_RESOURCES = RESOURCES_DIR / "cms"

# Legacy paths (for migration - will be removed after consolidation)
LEGACY_BLOG_DIR = ROOT / "blog"
LEGACY_DOC_DIR = ROOT / "documents"
LEGACY_PORTFOLIO_DIR = ROOT / "portfolios"
LEGACY_REF_DIR = ROOT / "references"
LEGACY_TECH_SKILLS_DIR = ROOT / "tech-skills"
LEGACY_SIDE_PROJECTS_DIR = ROOT / "side-projects"
LEGACY_MAGENTO_DIR = ROOT / "magento"
LEGACY_PHOTOGRAPHY_DIR = ROOT / "photography"
LEGACY_EXPERIENCE_DIR = ROOT / "experience"
LEGACY_CMS_DIR = ROOT / "cms"

# Image extensions
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"}

# Status defaults
STATUS_DEFAULTS = [
    "",
    "Active",
    "Updated",
    "Archived",
    "Future",
    "Shutdown",
    "Revised by Ultrasun NL",
]

