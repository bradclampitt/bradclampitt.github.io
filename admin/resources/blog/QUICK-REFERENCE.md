# 🚀 Blog Management Quick Reference

## Essential Commands

| Command | Description | Example |
|---------|-------------|---------|
| `./blog-helpers.sh new "Title"` | Create new post | `./blog-helpers.sh new "My Magento Post" magento` |
| `./blog-helpers.sh edit` | Edit latest post | Currently opens `nano` editor |
| `./blog-helpers.sh build` | Build all posts | Generates HTML from Markdown |
| `./blog-helpers.sh preview` | Preview locally | Starts server on port 8000 |
| `./blog-helpers.sh deploy` | Deploy to GitHub | Builds + commits + pushes |
| `./blog-helpers.sh stats` | Show statistics | Displays file counts |

## Post Structure

```markdown
---
id: unique-identifier
title: Your Blog Post Title
slug: url-friendly-slug
excerpt: Brief description for homepage...
author: Bradley R. Clampitt
date: 2024-12-25
category: magento|devops|tutorials|aws|security|general
tags: ["Magento 2", "AWS", "Docker"]
featured: true|false
readTime: "X min read"
---

# Your Blog Post Title

Content here using **Markdown**...

## Code Example

```php
class Example {
    public function hello() {
        return 'Hello World';
    }
}
```

## Conclusion

Summarize your post here.
```

## Workflow

1. **Create**: `./blog-helpers.sh new "Title" category`
2. **Edit**: `nano posts.md/YYYY-MM-DD-title.md`
3. **Preview**: `./blog-helpers.sh preview`
4. **Deploy**: `./blog-helpers.sh deploy`

## Categories & Tags

**Categories**: `magento`, `devops`, `tutorials`, `aws`, `security`, `general`

**Popular Tags**: `Magento 2`, `AWS`, `Docker`, `DevOps`, `PHP`, `Development`

**Auto-Colors**: Tags get styled automatically (purple for Magento, orange for AWS, etc.)

## File Locations

- **Write posts**: `blog/posts.md/`
- **Generated HTML**: `blog/posts/` (don't edit manually)
- **Media**: `blog/posts/media/images/`
- **Configuration**: `blog/posts.json` (auto-updated)

## Image placeholders & alignment (Confluence-style)

This blog system supports special placeholder images for planning and real images with the same alignment syntax. Use these in your Markdown posts.

- Basic placeholder (centered by default):
    - `![Alt text](placeholder:unique-id)`
- Alignment attribute (can be on same line or the next line):
    - Left (text wraps around on wide screens): `![Alt](placeholder:id){: .left}` or on next line `{: .left}`
    - Right (text wraps on the left): `![Alt](placeholder:id){: .right}` or `{: .right}`
    - Center: `{: .center}`
    - Small (thumbnail): `{: .small}`

Examples:

```
![Documentation example](placeholder:doc-example){: .left}

Some paragraph text that will flow beside the left-aligned placeholder on wide screens.

![Workflow diagram](placeholder:workflow-graph){: .right}

Some more text that will wrap on the left of the right-aligned placeholder.

![Centered hero](placeholder:hero-image){: .center}

![Thumbnail](placeholder:tiny-icon){: .small}
```

Notes:
- Left/right use CSS floats so text wraps naturally on wider screens. On narrow screens (mobile) placeholders stack full-width.
- For real images, the generator emits a `<figure>` with a `<figcaption>` containing the alt text. For placeholders the generator writes a small caption like "Image Placeholder: <id>" which you can replace with real images later.

## Build steps (full)

1. Rebuild the Tailwind CSS so utilities used in generated posts are present in `assets/css/tailwind-built.css`:

```bash
npm run build
```

2. Regenerate the HTML from your Markdown posts:

```bash
python3 blog/blog-manager-final.py --build
```

3. Preview the generated HTML locally (open the file in your browser):

```bash
xdg-open blog/posts/<slug>.html
# or use VS Code live preview
```

4. Commit and push the static files you'll publish to GitHub (include `blog/posts/`, `assets/css/tailwind-built.css`, and any images in `assets/images/` or `blog/posts/media/`):

```bash
git add -A
git commit -m "Publish blog posts and built CSS"
git push origin main
```

## Publishing to GitHub Pages

- If you publish to a GitHub Pages repo (user.github.io), push the built static files to the repository's default branch (usually `main`).
- If you publish to a project site, enable GitHub Pages on the `gh-pages` branch or the `docs/` folder and push the static site there.
- Make sure `assets/css/tailwind-built.css` and generated `blog/posts/*.html` are present in the repo branch you publish from.

## Troubleshooting / FAQ

- Q: Images don't wrap or float as expected
    - A: Ensure you've added `{: .left}` or `{: .right}` either inline or on the next line after the image. Rebuild Tailwind then regenerate posts.

- Q: Some Tailwind utilities aren't present after building
    - A: Tailwind scans your files using `tailwind.config.js`. If you're adding new utility classes in generated content ensure the `content` globs include those files (we set it to `./**/*.{html,md}`). You can narrow this glob to reduce scanning overhead if desired.

---
*Keep this quick-reference near your editor for fast posting.*

## Tips

✅ **Do**: Use clear titles, add tags, write in Markdown  
❌ **Don't**: Edit HTML files directly, skip building before deploy  
🔄 **Always**: Test with `preview` before `deploy`

---
*For detailed documentation, see `MANAGEMENT.md`*
