# Shared Markdown Processing and Styling

This document explains how the shared markdown processing and styling system works for both the blog and documents systems.

## Overview

Both the blog system and documents system now use:
1. **Shared Markdown Processor** (`shared/markdown_processor.py`) - Processes markdown with Confluence-style extensions
2. **Shared CSS** (`assets/css/confluence-markdown.css`) - Styles all custom markdown components

## Architecture

### Shared Markdown Processor

The `SharedMarkdownProcessor` class wraps `BlogManager`'s markdown processing functionality, making it available to both systems:

```python
from shared.markdown_processor import SharedMarkdownProcessor

processor = SharedMarkdownProcessor()
html = processor.markdown_to_html(markdown_text)
```

**Features:**
- Confluence-style callouts (`^ info`, `! warning`, `✓ success`, etc.)
- Info panels (`::: panel info "Title"`)
- Collapsible sections (`::: collapse Title`)
- Tabs (`::: tabs` with `@tab`)
- Columns (`::: columns` with `@column`)
- Cards (`::: cards` with `@card`)
- Quotes (`::: quote`)
- Embeds (`!embed [variant] url "title"`)
- Pipe tables
- Task lists (`- [ ]` and `- [x]`)
- Custom image handling with alignment
- Code block protection and styling

### Shared CSS

The CSS file (`assets/css/confluence-markdown.css`) contains all styling for:
- Code blocks with line numbers
- Callout boxes (info, warning, success, tip, error)
- Details/collapsible panels
- Tabs, columns, cards
- Task lists
- Tables
- Embeds
- And more...

## Integration

### Backend (Documents System)

The `admin/app.py` file now:
1. Imports the shared markdown processor
2. Processes markdown when saving documents (if `content_format` is `markdown`)
3. Stores the processed HTML in `content_html`

**Code:**
```python
from shared.markdown_processor import SharedMarkdownProcessor
MARKDOWN_PROCESSOR = SharedMarkdownProcessor()

# In document_save():
if content_format == 'markdown' and content_markdown:
    processed_html = MARKDOWN_PROCESSOR.markdown_to_html(content_markdown.strip())
    # Store processed_html in content_html field
```

### Frontend (Documents System)

The `documents/document.html` file now:
1. Includes the shared CSS file
2. Prefers backend-processed HTML over client-side rendering
3. Falls back to client-side `marked.js` for file-based content

**Changes:**
- Added `<link rel="stylesheet" href="/assets/css/confluence-markdown.css">`
- Updated content display logic to prefer `content_html` when available
- Client-side processing only used as fallback

### Blog System

The blog system already uses `BlogManager` which has all the markdown processing built-in. To use the shared CSS:

1. Update `blog/post-template.html` to link to the shared CSS instead of inline styles
2. Or keep inline styles (they're identical to the shared CSS)

## Usage Examples

### In Documents

When editing a document in the admin:
1. Select "Markdown" as the content format
2. Enter markdown with Confluence-style syntax:

```markdown
^ This is an info callout

::: panel warning "Important"
This is a warning panel with a title.
:::

::: collapse Click to expand
Hidden content here
:::
```

3. Save the document
4. The backend processes the markdown and stores HTML in `content_html`
5. The frontend displays the processed HTML with all styling applied

### In Blog Posts

Blog posts work the same way - use Confluence-style markdown syntax and it will be processed when building posts.

## Benefits

1. **Consistency**: Same markdown syntax and styling across blog and documents
2. **Maintainability**: One place to update markdown processing logic
3. **Performance**: Backend processing means faster frontend rendering
4. **Features**: Rich components (callouts, tabs, etc.) available everywhere

## Files Created/Modified

**Created:**
- `shared/markdown_processor.py` - Shared markdown processor wrapper
- `shared/__init__.py` - Module initialization
- `assets/css/confluence-markdown.css` - Shared CSS styles

**Modified:**
- `admin/app.py` - Added markdown processing on document save
- `documents/document.html` - Added CSS link and updated content display logic

## Next Steps

1. Test document creation/editing with Confluence-style markdown
2. Verify styling matches blog posts
3. Optionally update blog template to use shared CSS file instead of inline styles
4. Consider adding PrismJS for syntax highlighting in documents (already in blog)

