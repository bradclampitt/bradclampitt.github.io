#!/usr/bin/env python3
"""
Migration script to consolidate all section databases into unified.sqlite.

This script:
1. Creates the unified database with the combined schema
2. Migrates data from each section database with proper table namespacing
3. Handles foreign key references and maintains data integrity
4. Creates backups of original databases

Usage:
    python admin/database/migrations/migrate_unified.py
"""
import sqlite3
import shutil
from pathlib import Path
from datetime import datetime
import sys

# Add admin directory to path
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "admin"))

from admin.config import (
    DATABASE_PATH, SCHEMA_PATH, DATABASE_DIR,
    BLOG_RESOURCES, DOCUMENTS_RESOURCES, PORTFOLIOS_RESOURCES,
    REFERENCES_RESOURCES, TECH_SKILLS_RESOURCES, SIDE_PROJECTS_RESOURCES,
    MAGENTO_RESOURCES, PHOTOGRAPHY_RESOURCES, EXPERIENCE_RESOURCES,
    CMS_RESOURCES
)


# Mapping of section database paths to namespace prefixes
# Note: Databases are now in admin/resources/*/ directories
SECTION_MAPPINGS = [
    ("blog", BLOG_RESOURCES / "blog.sqlite", "blog"),
    ("documents", DOCUMENTS_RESOURCES / "documents.sqlite", "doc"),
    ("portfolios", PORTFOLIOS_RESOURCES / "portfolios.sqlite", "portfolio"),
    ("references", REFERENCES_RESOURCES / "references.sqlite", "ref"),
    ("tech-skills", TECH_SKILLS_RESOURCES / "tech-skills.sqlite", "tech_skill"),
    ("side-projects", SIDE_PROJECTS_RESOURCES / "side-projects.sqlite", "side_project"),
    ("magento", MAGENTO_RESOURCES / "magento.sqlite", "magento"),
    ("photography", PHOTOGRAPHY_RESOURCES / "photography.sqlite", "photography"),
    ("experience", EXPERIENCE_RESOURCES / "experience.sqlite", "experience"),
    ("cms", CMS_RESOURCES / "cms.sqlite", "cms"),
]

# Table name mappings for each section (old_name -> new_name)
TABLE_MAPPINGS = {
    "blog": {
        "blog_categories": "blog_categories",
        "blog_posts": "blog_posts",
    },
    "documents": {
        "doc_categories": "doc_categories",
        "doc_types": "doc_types",
        "doc_tabs": "doc_tabs",
        "documents": "documents",
        "document_tabs": "document_tabs",
        "document_images": "document_images",
        "document_links": "document_links",
    },
    "portfolios": {
        "clients": "portfolio_clients",
        "project_types": "portfolio_project_types",
        "portfolio_tabs": "portfolio_tabs",
        "projects": "portfolio_projects",
        "project_tabs": "portfolio_project_tabs",
        "project_images": "portfolio_project_images",
        "project_links": "portfolio_project_links",
        "project_features": "portfolio_project_features",
        "tech_tags": "portfolio_tech_tags",
        "project_tech_tags": "portfolio_project_tech_tags",
    },
    "references": {
        "reference_entries": "ref_entries",
    },
    "tech-skills": {
        "tech_skill_categories": "tech_skill_categories",
        "tech_skills": "tech_skills",
    },
    "side-projects": {
        "side_project_categories": "side_project_categories",
        "side_projects": "side_projects",
        "side_project_technologies": "side_project_technologies",
        "side_project_features": "side_project_features",
        "side_project_technical_details": "side_project_technical_details",
        "side_project_images": "side_project_images",
    },
    "magento": {
        "magento_module_categories": "magento_module_categories",
        "magento_modules": "magento_modules",
        "magento_module_technologies": "magento_module_technologies",
        "magento_module_features": "magento_module_features",
        "magento_module_technical_details": "magento_module_technical_details",
        "magento_module_images": "magento_module_images",
    },
    "photography": {
        "photography_categories": "photography_categories",
        "photography": "photography",
    },
    "experience": {
        "companies": "experience_companies",
        "job_experiences": "experience_job_experiences",
        "job_projects": "experience_job_projects",
        "skills_sets": "experience_skills_sets",
        "tools": "experience_tools",
        "soft_skills": "experience_soft_skills",
        "education": "experience_education",
        "job_experience_skills": "experience_job_experience_skills",
        "job_experience_tools": "experience_job_experience_tools",
        "job_experience_soft_skills": "experience_job_experience_soft_skills",
    },
    "cms": {
        "cms_blocks": "cms_blocks",
        "site_settings": "cms_site_settings",
        "contact_info": "cms_contact_info",
    },
}


def create_backup(source_path: Path) -> Path:
    """Create a timestamped backup of a database file."""
    if not source_path.exists():
        return None
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = source_path.parent / f"{source_path.stem}_backup_{timestamp}.sqlite"
    shutil.copy2(source_path, backup_path)
    return backup_path


def migrate_section(source_db: Path, section_name: str, namespace: str, target_conn: sqlite3.Connection):
    """Migrate a section database to unified database."""
    if not source_db.exists():
        print(f"⚠️  Skipping {section_name}: database not found at {source_db}")
        return 0
    
    print(f"📦 Migrating {section_name}...")
    
    # Create backup
    backup_path = create_backup(source_db)
    if backup_path:
        print(f"   💾 Backup created: {backup_path.name}")
    
    source_conn = sqlite3.connect(source_db)
    source_conn.row_factory = sqlite3.Row
    
    # Get all tables
    cursor = source_conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    tables = [row[0] for row in cursor.fetchall()]
    
    if not tables:
        print(f"   ⚠️  No tables found in {section_name}")
        source_conn.close()
        return 0
    
    table_mapping = TABLE_MAPPINGS.get(section_name, {})
    migrated_count = 0
    
    # Migrate each table
    for table in tables:
        # Check if table is in mapping first
        if table in table_mapping:
            new_table_name = table_mapping[table]
        elif namespace:
            # Auto-namespace if not in mapping
            new_table_name = f"{namespace}_{table}"
        else:
            new_table_name = table
        
        try:
            # Get table schema
            cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table}'")
            schema_row = cursor.fetchone()
            if not schema_row or not schema_row[0]:
                print(f"   ⚠️  Could not get schema for {table}")
                continue
            
            schema = schema_row[0]
            
            # Update table name in schema
            schema = schema.replace(f"CREATE TABLE {table}", f"CREATE TABLE {new_table_name}")
            schema = schema.replace(f"CREATE TABLE IF NOT EXISTS {table}", f"CREATE TABLE IF NOT EXISTS {new_table_name}")
            
            # Update foreign key references in schema
            for old_ref, new_ref in table_mapping.items():
                schema = schema.replace(f"REFERENCES {old_ref}(", f"REFERENCES {new_ref}(")
            
            # Create table in target (ignore if exists - schema.sql already created it)
            try:
                target_conn.execute(schema)
            except sqlite3.OperationalError as e:
                if "already exists" not in str(e).lower():
                    print(f"   ⚠️  Error creating table {new_table_name}: {e}")
                    continue
            
            # Copy data - only copy columns that exist in both tables
            cursor.execute(f"SELECT * FROM {table}")
            rows = cursor.fetchall()
            
            if rows:
                # Get column names from source
                source_columns = [desc[0] for desc in cursor.description]
                
                # Get column names from target table
                target_cursor = target_conn.cursor()
                target_cursor.execute(f"PRAGMA table_info({new_table_name})")
                target_columns = [row[1] for row in target_cursor.fetchall()]
                
                # Find common columns (only copy columns that exist in both)
                common_columns = [col for col in source_columns if col in target_columns]
                
                if not common_columns:
                    print(f"   ⚠️  No common columns between {table} and {new_table_name}")
                    continue
                
                # Build INSERT with only common columns
                placeholders = ','.join(['?' for _ in common_columns])
                column_list = ','.join(common_columns)
                insert_sql = f"INSERT OR IGNORE INTO {new_table_name} ({column_list}) VALUES ({placeholders})"
                
                migrated_rows = 0
                for row in rows:
                    try:
                        # Map row values to common columns only
                        row_dict = dict(zip(source_columns, row))
                        values = [row_dict[col] for col in common_columns]
                        target_conn.execute(insert_sql, values)
                        migrated_rows += 1
                    except sqlite3.IntegrityError:
                        # Skip duplicates silently
                        continue
                    except Exception as e:
                        print(f"   ⚠️  Error inserting row: {e}")
                        continue
                
                if migrated_rows > 0:
                    skipped = len(rows) - migrated_rows
                    if skipped > 0:
                        print(f"   ✅ Migrated {table} -> {new_table_name} ({migrated_rows} rows, skipped {skipped} duplicates/errors, {len(common_columns)}/{len(source_columns)} columns)")
                    else:
                        print(f"   ✅ Migrated {table} -> {new_table_name} ({migrated_rows} rows, {len(common_columns)}/{len(source_columns)} columns)")
                else:
                    print(f"   ⚠️  No rows migrated from {table} -> {new_table_name}")
                migrated_count += 1
            else:
                print(f"   ℹ️  Table {table} -> {new_table_name} (empty)")
                migrated_count += 1
                
        except Exception as e:
            print(f"   ❌ Error migrating {table}: {e}")
            import traceback
            traceback.print_exc()
            continue
    
    source_conn.close()
    print(f"   ✅ Completed {section_name}: {migrated_count} tables migrated\n")
    return migrated_count


def main():
    """Main migration function."""
    print("=" * 70)
    print("Database Consolidation Migration")
    print("=" * 70)
    print()
    
    # Check if unified database already exists
    database_exists = DATABASE_PATH.exists()
    
    if not database_exists:
        # Create unified database with schema
        print("📋 Creating unified database with schema...")
        DATABASE_DIR.mkdir(parents=True, exist_ok=True)
        
        if not SCHEMA_PATH.exists():
            print(f"❌ Schema file not found at {SCHEMA_PATH}")
            return
        
        with sqlite3.connect(DATABASE_PATH) as conn, \
             SCHEMA_PATH.open("r", encoding="utf-8") as fh:
            conn.executescript(fh.read())
        
        print("✅ Unified database created\n")
    else:
        print(f"ℹ️  Unified database already exists at {DATABASE_PATH}")
        print("   Will migrate data into existing database (using INSERT OR IGNORE)\n")
    
    # Migrate each section
    target_conn = sqlite3.connect(DATABASE_PATH)
    target_conn.row_factory = sqlite3.Row
    
    total_tables = 0
    for section_name, source_db, namespace in SECTION_MAPPINGS:
        count = migrate_section(source_db, section_name, namespace, target_conn)
        total_tables += count
    
    target_conn.commit()
    target_conn.close()
    
    print("=" * 70)
    print(f"✅ Migration complete! Migrated {total_tables} tables total")
    print(f"📁 Unified database: {DATABASE_PATH}")
    print("=" * 70)
    print("\n⚠️  Original databases have been backed up with timestamps.")
    print("   You can safely remove them after verifying the migration.")


if __name__ == "__main__":
    main()
