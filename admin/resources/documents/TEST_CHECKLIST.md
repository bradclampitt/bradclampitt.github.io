# Test Checklist

Use this checklist to verify the documents system is working correctly.

## Database Setup

- [ ] `documents/documents.sqlite` is created on first admin run using `schema.sql`
- [ ] Database schema includes all required tables (doc_categories, doc_types, doc_tabs, documents, document_tabs, document_images, document_links)

## Admin Backend

- [ ] Can access admin dashboard at `http://localhost:8000/admin`
- [ ] Dashboard shows correct counts for documents, categories, and types
- [ ] Can create a category via `/admin/categories`
  - [ ] Category code is unique
  - [ ] Category appears in the list after creation
- [ ] Can create a document type via `/admin/types`
  - [ ] Type code is unique
  - [ ] Type appears in the list after creation
- [ ] Can create a document via `/admin/documents/new` with:
  - [ ] Title (required)
  - [ ] Slug (auto-generated if missing)
  - [ ] Category and type selection
  - [ ] Summary
  - [ ] Markdown content (inline)
  - [ ] Created / Posted / Last Edited dates (auto-filled if missing)
  - [ ] Effective dates (optional)
  - [ ] Tab assignments (Resumes, Articles, KBase, Guides, Others)
  - [ ] Tags (comma-separated)
- [ ] Can edit an existing document via `/admin/documents/{id}`
- [ ] Can upload a cover image; it appears under `assets/images/documents/{document_id}/...`
- [ ] Can upload additional images for a document
- [ ] Can add external links to a document
- [ ] All form validations work correctly

## Frontend (Static Pages)

- [ ] `documents.html` loads without errors
- [ ] `documents.html` loads `documents/documents.sqlite` via sql.js
- [ ] Documents list displays correctly with:
  - [ ] Document cards showing title, summary, category, type
  - [ ] Cover images (if present)
  - [ ] Tags
  - [ ] Tab badges
- [ ] Tab filtering works:
  - [ ] "All" tab shows all documents
  - [ ] "Resumes" tab shows only documents assigned to Resumes tab
  - [ ] "Articles" tab shows only documents assigned to Articles tab
  - [ ] "KBase" tab shows only documents assigned to KBase tab
  - [ ] "Guides" tab shows only documents assigned to Guides tab
  - [ ] "Others" tab shows only documents assigned to Others tab
- [ ] Each document card links to `document.html?slug={slug}`
- [ ] `document.html` loads and displays:
  - [ ] Document title, category, type, tab badges
  - [ ] Metadata (dates: created, posted, updated, effective)
  - [ ] Summary
  - [ ] Tags
  - [ ] Cover image (if present)
  - [ ] Content (HTML, markdown rendered, or file content)
  - [ ] Image gallery (if images exist)
  - [ ] External links (if links exist)
- [ ] Markdown content renders correctly (if `content_markdown` is present)
- [ ] File-referenced content loads correctly (if `content_path` is present)

## GitHub Pages Compatibility

- [ ] All pages function from GitHub Pages (static hosting only; no backend required to view)
- [ ] Database file loads correctly from `/documents/documents.sqlite`
- [ ] Images load correctly from `/assets/images/documents/...`
- [ ] No CORS errors in browser console
- [ ] sql.js WASM file loads correctly

## Edge Cases

- [ ] Documents without categories/types display correctly
- [ ] Documents without tabs display correctly
- [ ] Documents without images display correctly
- [ ] Documents without links display correctly
- [ ] Empty states display correctly (no documents, no categories, etc.)
- [ ] Error handling works (invalid slug, missing database, etc.)

## Performance

- [ ] Database loads reasonably fast (< 2 seconds for typical dataset)
- [ ] Page renders quickly after database load
- [ ] Images load efficiently

## Browser Compatibility

- [ ] Works in Chrome/Edge
- [ ] Works in Firefox
- [ ] Works in Safari
- [ ] Works on mobile browsers

## Notes

- Test with at least 5-10 sample documents
- Test with various content types (markdown, HTML, file references)
- Test with documents in multiple tabs
- Test image uploads of different formats (PNG, JPG, WebP)
- Test with documents that have all fields populated and documents with minimal fields

