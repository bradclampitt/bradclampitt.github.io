# Unused Files Analysis

This document identifies files that are no longer being used after the backend and frontend consolidation.

## Summary

After migrating to a unified database (`admin/database/unified.sqlite`) and consolidating the backend, several categories of files are no longer actively used:

---

## 1. Old Separate Database Files

**Status**: Replaced by `admin/database/unified.sqlite`

These individual database files are no longer used by the application:

- `admin/resources/blog/blog.sqlite` (if exists)
- `admin/resources/documents/documents.sqlite`
- `admin/resources/portfolios/portfolios.sqlite` (if exists)
- `admin/resources/references/references.sqlite` (if exists)
- `admin/resources/tech-skills/tech-skills.sqlite`
- `admin/resources/side-projects/side-projects.sqlite` (if exists)
- `admin/resources/magento/magento.sqlite`
- `admin/resources/photography/photography.sqlite` (if exists)
- `admin/resources/experience/experience.sqlite` (if exists)
- `admin/resources/cms/cms.sqlite`
- `admin/resources/cms/cms.db`
- `admin/database/cms.db`

**Note**: These may still be referenced by the migration script (`admin/database/migrations/migrate_unified.py`) but are not used by the running application.

---

## 2. Database Backup Files

**Status**: Migration backups - can be safely removed after verification

Found **50 backup files** from the migration on 2025-11-23:

### CMS Backups (5 files)
- `admin/resources/cms/cms_backup_20251123_205208.sqlite`
- `admin/resources/cms/cms_backup_20251123_205337.sqlite`
- `admin/resources/cms/cms_backup_20251123_205346.sqlite`
- `admin/resources/cms/cms_backup_20251123_205354.sqlite`
- `admin/resources/cms/cms_backup_20251123_205410.sqlite`

### Documents Backups (5 files)
- `admin/resources/documents/documents_backup_20251123_205208.sqlite`
- `admin/resources/documents/documents_backup_20251123_205337.sqlite`
- `admin/resources/documents/documents_backup_20251123_205346.sqlite`
- `admin/resources/documents/documents_backup_20251123_205354.sqlite`
- `admin/resources/documents/documents_backup_20251123_205410.sqlite`

### Magento Backups (6 files)
- `admin/resources/magento/magento_backup_20251123_*.sqlite` (6 files)

### Tech Skills Backups (6 files)
- `admin/resources/tech-skills/tech-skills_backup_20251123_*.sqlite` (6 files)

### Other Section Backups
- Similar backup files exist for other sections (portfolios, references, side-projects, photography, experience, blog)

**Recommendation**: Keep backups for 30 days, then remove after confirming unified database is working correctly.

---

## 3. Old Schema Files

**Status**: Consolidated into `admin/database/schema.sql`

These individual schema files are kept for reference but are not used by the application:

- `admin/resources/blog/schema.sql`
- `admin/resources/cms/schema.sql`
- `admin/resources/documents/schema.sql`
- `admin/resources/experience/schema.sql`
- `admin/resources/magento/schema.sql`
- `admin/resources/photography/schema.sql`
- `admin/resources/portfolios/schema.sql`
- `admin/resources/references/schema.sql`
- `admin/resources/side-projects/schema.sql`
- `admin/resources/tech-skills/schema.sql`

**Note**: These may be useful for reference or documentation, but the application uses `admin/database/schema.sql` exclusively.

---

## 4. Template Files (Potentially Unused)

**Status**: Not referenced in `admin/app.py`

These template files don't appear to be referenced in the application code:

- `admin/resources/blog/post-template.html`
- `admin/resources/documents/document-template.html`

**Note**: These might be used for manual content creation or as reference templates. Verify before deletion.

---

## 5. Old Migration Scripts

**Status**: Already executed - can be archived or removed

These migration scripts have already been run and are no longer needed:

- `admin/migrate_blog_categories.py`
- `admin/migrate_blog_categories_icon.py`
- `admin/migrate_blog_cover_image.py`
- `admin/migrate_blog_posts.py`

**Note**: The unified migration script (`admin/database/migrations/migrate_unified.py`) is still relevant and should be kept.

---

## 6. Archive Files

**Status**: Old versions - can be removed

### Blog Manager Archive Files
Located in `admin/resources/blog/archive/`:

- `blog-manager_backup2.py`
- `blog-manager_backup.py`
- `blog-managera.py`
- `blog-manager-finalb.py`
- `blog-manager-complete.py.txt`
- `blog-manager-new.py.txt`
- `blog-manager-final.py`
- `blog-manager-final.py.tmp`
- `blog-manager-new.py`
- `blog-manager-complete.py`
- `blog-manager-fixed.py`
- `blog-manager-broken.py`

**Note**: The current `blog-manager.py` is in `admin/resources/blog/blog-manager.py` and is actively used.

---

## 7. Duplicate Documentation Files

**Status**: Duplicate/outdated - can be removed

- `docs/CONSOLIDATION_ANALYSIS copy.md` - Duplicate of `docs/CONSOLIDATION_OPTIONS.md`

**Note**: According to deleted_files history, these were already removed:
- `cms/CMS_BLOCKS_GUIDE.md`
- `cms/QUICK_START.md`

But they may still exist in `admin/resources/cms/`:
- `admin/resources/cms/CMS_BLOCKS_GUIDE.md` (if exists)
- `admin/resources/cms/QUICK_START.md` (if exists)

---

## 8. Potentially Unused Template Files

**Status**: Verify usage before removal

- `admin/templates/categories_list.html` - May be replaced by section-specific category lists

**Note**: The application uses section-specific category templates:
- `blog/blog_categories_list.html`
- `doc_categories_list.html`
- `tech_skill_categories_list.html`
- etc.

---

## 9. Duplicate HTML Files

**Status**: Check if these are duplicates

Some HTML files exist in both root and `admin/resources/`:

- `blog/posts/*.html` vs `admin/resources/blog/posts/*.html`
- `documents/document.html` vs `admin/resources/documents/document.html`

**Note**: The application serves from root directories (`/blog`, `/documents`), so files in `admin/resources/` may be source files or duplicates.

---

## 10. Backup HTML Files

**Status**: Old backup - can be removed

- `backups/documents.html` - Appears to be an old backup file

---

## Recommendations

### Safe to Remove Immediately:
1. ✅ All `*_backup_*.sqlite` files (after 30-day retention period)
2. ✅ Archive files in `admin/resources/blog/archive/`
3. ✅ Old migration scripts (`migrate_blog_*.py`)
4. ✅ Duplicate documentation (`CONSOLIDATION_ANALYSIS copy.md`)
5. ✅ `backups/documents.html`

### Keep for Reference (Optional):
1. ⚠️ Old schema files in `admin/resources/*/schema.sql` (useful for documentation)
2. ⚠️ Template files (`post-template.html`, `document-template.html`) if used for manual content creation

### Verify Before Removing:
1. ❓ Old separate database files (may be needed for rollback)
2. ❓ Duplicate HTML files (verify which are source vs generated)
3. ❓ `admin/templates/categories_list.html` (check if still referenced)

---

## Files Still in Use

### Critical Files (DO NOT REMOVE):
- `admin/database/unified.sqlite` - **Active database**
- `admin/database/schema.sql` - **Active schema**
- `admin/database/migrations/migrate_unified.py` - **Migration script**
- `admin/resources/blog/blog-manager.py` - **Active blog processor**
- `admin/app.py` - **Main application**
- `admin/config.py` - **Configuration**
- All files in `admin/templates/` (except `categories_list.html` - verify)
- All frontend HTML files in root (`*.html`)
- `shared/markdown_processor.py` - **Shared module**

---

## Cleanup Script

To safely remove unused files, you can use:

```bash
# Remove backup databases (after verification period)
find admin/resources -name "*_backup_*.sqlite" -delete

# Remove archive files
rm -rf admin/resources/blog/archive/

# Remove old migration scripts
rm admin/migrate_blog_*.py

# Remove duplicate documentation
rm "docs/CONSOLIDATION_ANALYSIS copy.md"

# Remove backup HTML
rm backups/documents.html
```

**⚠️ Always backup before running cleanup scripts!**

---

*Last Updated: 2025-01-XX*
*Based on analysis of codebase after unified database migration*

