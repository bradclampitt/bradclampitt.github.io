<!--
	FEATURES.md
	Consolidated reference of supported Markdown extensions and Confluence-style elements
	for the blog generator.
-->

# Blog Markdown Features (Consolidated)

This document combines the Confluence-style callout patterns and the enhanced Markdown features
supported by the blog generator. It includes usage examples, rendering notes, and implementation
details so authors and maintainers know what syntax is supported and how it behaves.

## Table of contents
- Confluence-style callouts
- Images & placeholders
- Code blocks & syntax highlighting
- Text formatting, headings, and spacing
- Implementation notes and writing tips

---

## Confluence-style callouts

Supported callouts use a single-line marker followed by the callout body on subsequent lines.
They render as styled boxes with an icon, color band, and body content.

Markers (leading character + keyword):

- Info
	```markdown
	^ info
	This is an informational callout.
	```
- Warning
	```markdown
	! warning
	This is a warning callout.
	```
- Success
	```markdown
	✓ success
	This is a success callout.
	```
- Error
	```markdown
	✗ error
	This is an error callout.
	```
- Tip
	```markdown
	💡 tip
	A small tip to help readers.
	```

Notes:
- Callouts can contain multiple paragraphs, lists and code blocks.
- Callouts terminate at the next horizontal rule (`---`), another callout, a top-level heading, or an explicit block boundary. This prevents them from swallowing separators.
- The HTML output uses safe icon markup (emoji or small inline SVGs) to avoid malformed SVG path blobs.

---

## Images & placeholders

The generator supports enhanced image alignment, placeholders (for planning), and captions. There are two classes of images:

1. Placeholder images (src starts with `placeholder:`) — these are intended for planning and will render as dashed boxes that can float left/right and allow text wrapping.
2. Real images (normal src paths) — rendered as block-level `<figure>` elements with optional `<figcaption>`; real images do not allow inline text wrapping (text appears above or below only).

Syntax examples:

- Standard (centered by default):
	```markdown
	![Alt text](images/example.jpg)
	```

- Explicit center:
	```markdown
	![Alt text](images/example.jpg){: .center}
	```

- Left-aligned placeholder (text wraps):
	```markdown
	![Screenshot](placeholder:dashboard){: .left}
	```

- Right-aligned placeholder (text wraps):
	```markdown
	![Diagram](placeholder:diagram){: .right}
	```

- Small image variant:
	```markdown
	![Icon](images/icon.png){: .small}
	```

- No-wrap token (useful for real images which are block-level by default but also respected when present):
	```markdown
	![Large diagram](diagram.png){: .nowrap}
	```

Rendering behaviors:
- Placeholders: float behavior (left/right) is preserved so you can prototype text wrapping and layout.
- Real images: output as `<figure class="figure-center/figure-left/figure-right ...">` with the `<img>` inside and `<figcaption>` (if caption provided) below the image. They do not allow inline text wrapping.
- Captions: if a caption is provided (via alt text or explicit caption syntax), it's rendered inside `<figcaption>` beneath the image or placeholder.

---

## Code blocks & syntax highlighting

Fenced code blocks are preserved verbatim and wrapped for syntax highlighting. The generator preserves language tags and applies classes for Prism or other highlighter usage.

Usage:
```markdown
```php
<?php
namespace Vendor\Module;
class MyClass {
		public function example() {
				return "Hello World";
		}
}
```
```

Rendering notes:
- Language tag is preserved and shown above the block.
- Line numbers are supported and rendered alongside code blocks.
- Code blocks are protected during intermediate transformations to prevent accidental modification.

Common languages and the visual color hints used by the theme:
- php, javascript/js, python, bash, sql, html, css, json/yaml, markdown, xml

---

## Text formatting, headings, lists, and spacing

- Bold: `**bold**` → `<strong>`
- Italic: `*italic*` → `<em>`
- Inline code: `` `code` `` → `<code>` styled

Headings:
- H1/H2/H3/H4 supported; `####` emits H4 and headings clear floats so they don't wrap around images.

Lists and block elements:
- Contiguous list items generate `<ul>` or `<ol>` as expected; the generator collapses list item runs into a single list block.

Paragraphs and spacing:
- Paragraphs are wrapped with a small horizontal padding class (`px-10`) for consistent breathing room.
- Headings and code blocks have tuned margins for better reading rhythm on mobile and desktop.

---

## Examples (combined)

Example post fragment showing callouts, code and images:

```markdown
# Getting Started

^ info
Make sure you have a local PHP dev environment.

! warning
**Important:** Backup your DB before migrations.

```bash
composer install
php bin/magento setup:upgrade
```

![Install finished](placeholder:install-success){: .center}

✓ success
The setup completed successfully.

![Architecture diagram](images/arch.png){: .nowrap}

Continue to the next section...
```

---

## Implementation notes (for maintainers)

- The generator follows a Protect → Transform → Restore pipeline:
	- Protect fenced code blocks (replace with placeholders) to avoid accidental rewrites during regex transformations.
	- Transform markdown elements (callouts, headings, images, paragraphs).
	- Restore protected code blocks into final HTML.
- Tailwind CSS classes are used for styling; the `post-template.html` includes helper classes for figures, placeholders, callouts, and spacing.
- Avoid emitting raw, untrusted inline SVG path data — icons use safe emoji or small sanitized SVGs.

## Writing tips

1. Prefer using placeholders during drafting for layout planning — replace with real images before publishing.
2. Specify code block languages for accurate highlighting.
3. Use `{: .left}` / `{: .right}` for prototype layout but remember real images are block-level and won't wrap text.
4. Keep callouts concise; they support multiple paragraphs and inline code.

---

## See also
- `blog/README.md` — usage and build instructions
- `blog/blog-manager.py` — the generator script (local tool used to generate static HTML)

If you'd like, I can now move the original `CONFLUENCE-STYLE-MARKDOWN.md` and `MARKDOWN-FEATURES.md` into `blog/archive/` (so the repository keeps the consolidated `blog/FEATURES.md` as the canonical doc). 

Real images are emitted as `<figure>` with `<figcaption>` below. Placeholders retain float behavior for layout testing.

## Code Blocks
- Fenced code blocks preserved and HTML-escaped
- Language class is applied: ```php
- Prism-compatible markup with line-numbers wrapper is used

## Text Formatting
- `**bold**`, `*italic*` are supported
- Lists (`- item` or `1.`) convert to `<li>` elements and are collapsed into `<ol>` when contiguous

## Spacing & Layout
- Paragraphs are wrapped with `px-10` padding for horizontal breathing room
- Headings clear floats to avoid wrapping around images

## Notes
- For full examples, keep `CONFLUENCE-STYLE-MARKDOWN.md` and `MARKDOWN-FEATURES.md` in the repo or read `blog/README.md` which links to them.
