#!/usr/bin/env python3
"""
Final Blog Manager with Protected Code Blocks and Block Image Handling
"""
import markdown
import json
import re
import os
from datetime import datetime
from pathlib import Path
import html  # For escaping
from urllib.parse import urlparse, parse_qs, urljoin
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from html.parser import HTMLParser
import textwrap

class BlogManager:
    def __init__(self, blog_root="/var/www/projectmanager.test/github_v2/blog"):
        self.blog_root = Path(blog_root)
        self.posts_md_dir = self.blog_root / "posts.md"
        self.posts_html_dir = self.blog_root / "posts"
        # Template file is in the resources directory, not the blog root
        # Calculate the correct path: from blog_root (/var/www/.../blog) go up to root, then to admin/resources/blog
        blog_root_path = Path(blog_root)
        # If blog_root is /var/www/.../blog, go to /var/www/.../github_v2/admin/resources/blog/post-template.html
        root_dir = blog_root_path.parent  # /var/www/.../github_v2
        resources_template = root_dir / "admin" / "resources" / "blog" / "post-template.html"
        blog_root_template = self.blog_root / "post-template.html"
        self.template_file = resources_template if resources_template.exists() else blog_root_template
        self.posts_json_file = self.blog_root / "posts.json"
        self._embed_metadata_cache = {}
        self._tab_counter = 0

        # Create directories if they don't exist
        self.posts_md_dir.mkdir(exist_ok=True)
        self.posts_html_dir.mkdir(exist_ok=True)

    def parse_frontmatter(self, content):
        """Parse frontmatter from markdown content"""
        if not content.startswith('---'):
            return {}, content
        parts = content.split('---', 2)
        if len(parts) < 3:
            return {}, content

        frontmatter_text = parts[1].strip()
        content_text = parts[2].strip()

        frontmatter = {}
        for line in frontmatter_text.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip().strip('"\'')
                if value.startswith('[') and value.endswith(']'):
                    value = [tag.strip().strip('"\'') for tag in value[1:-1].split(',')]
                    value = [tag for tag in value if tag]
                elif value.lower() in ['true', 'false']:
                    value = value.lower() == 'true'
                frontmatter[key] = value

        return frontmatter, content_text


    def markdown_to_html(self, markdown_text):
        processed = markdown_text

        # 1) Protect fenced code blocks first
        processed, code_block_placeholders = self.protect_code_blocks(processed)

        # 2) Protect inline code early
        processed, inline_code_placeholders = self.protect_inline_code(processed)

        # 3) Your custom preprocessors
        processed = self.process_confluence_callouts(processed)
        processed = self.process_info_panels(processed)
        processed = self.process_collapsibles(processed)
        processed = self.process_note_blocks(processed)
        processed = self.process_tabs(processed)
        processed = self.process_columns(processed)
        processed = self.process_cards(processed)
        processed = self.process_quotes(processed)
        processed = self.process_embeds(processed)
        processed = self.process_pipe_tables(processed)
        processed = self.normalize_plain_details(processed)
        processed = self.process_headers(processed)
        processed = self.process_images(processed)

        # 4) ✂️ Drop pre-Markdown emphasis/link regexes — let Markdown do it.
        # processed = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', processed)
        # processed = re.sub(r'\*([^*]+)\*', r'<em>\1</em>', processed)
        # processed = re.sub(r'^---$', r'<hr class="my-4 border-gray-300 hr-spaced">', processed, flags=re.MULTILINE)
        # processed = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2" class="text-blue-600 hover:underline">\1</a>', processed)

        # 5) (Leave process_paragraphs disabled)

        # 6) Restore fenced code blocks
        processed, extra_placeholders = self.protect_code_blocks(processed)
        code_block_placeholders.update(extra_placeholders)
        processed = self.restore_code_blocks(processed, code_block_placeholders)

        # 7) Restore inline code
        processed = self.restore_inline_code(processed, inline_code_placeholders)

        # ✅ NEW: make sure lists are separated by a blank line
        processed = self.ensure_list_separation(processed)

        processed = self.ensure_colon_list_break(processed)

        # 8) Final Markdown render
        processed = markdown.markdown(
            processed,
            extensions=['extra', 'attr_list', 'md_in_html', 'nl2br']
        )

        # 9) Post-style paragraphs AFTER Markdown
        processed = self._style_paragraphs_post(processed)

        processed = self.style_task_lists(processed)

        # 10) Fix any fenced code that slipped into paragraphs
        processed = self.fix_fenced_code_in_paragraphs(processed)
        
        # 11) Post-process markdown links with @embed in title attribute
        processed = self.process_embed_links_post(processed)

        return processed

    def process_info_panels(self, text):
        """
        Confluence-style info panels:

        Fenced:
        ::: panel <kind> "Optional Title"
        ...markdown body...
        :::
        (also supports `:::panel` without the space)

        Simple/inline:
        >>> info "Optional Title" One-line body
        >>> warning "Title"
        Multi-line body...
        (blank line ends)
        """
        import re, markdown

        kind_map = {
            'info':    ('info',    'Info',      'fa-solid fa-circle-info'),
            'warning': ('warning', 'Important', 'fa-solid fa-triangle-exclamation'),
            'error':   ('error',   'Error',     'fa-solid fa-circle-xmark'),
            'success': ('success', 'Success',   'fa-solid fa-circle-check'),
            'tip':     ('tip',     'Pro tip',   'fa-solid fa-lightbulb'),
        }

        def render_panel(kind: str, title: str, body_md: str) -> str:
            """Render a panel using the same HTML skeleton as callouts."""
            kind_key = (kind or 'info').lower().strip()
            cclass, default_title, icon = kind_map.get(kind_key, kind_map['info'])
            title_text = title.strip() if title else default_title

            # Let Markdown handle headings/lists/code/etc.
            body_html = markdown.markdown(body_md or '', extensions=['extra', 'attr_list', 'md_in_html'])

            # Keep true one-liners in a single line (no paragraph box)
            if body_html.startswith("<p>") and body_html.endswith("</p>") and body_html.count("<p>") == 1:
                body_html = body_html[3:-4].strip()

            return (
                f'<div class="callout {cclass}">'
                f'  <div class="row">'
                f'    <span class="icon"><i class="{icon}"></i></span>'
                f'    <div class="body"><span class="title">{title_text}:</span> {body_html}</div>'
                f'  </div>'
                f'</div>'
            )

        lines = text.split('\n')
        out = []
        i = 0

        # ---------- Pass A: fenced panels (::: panel kind "Title" ... :::) ----------
        fenced_start = re.compile(
            r'^\s*:::\s*panel\s+([a-zA-Z]+)(?:\s+"([^"]*)")?\s*$|^\s*:::panel\s+([a-zA-Z]+)(?:\s+"([^"]*)")?\s*$'
        )
        fenced_end = re.compile(r'^\s*:::\s*$')

        while i < len(lines):
            m = fenced_start.match(lines[i])
            if m:
                # groups: (kind1, title1, kind2, title2) – only one pair will be set
                kind = m.group(1) or m.group(3)
                title = m.group(2) or m.group(4) or ''

                # collect body until ::: on its own line
                j = i + 1
                body_lines = []
                while j < len(lines) and not fenced_end.match(lines[j]):
                    body_lines.append(lines[j])
                    j += 1

                body_md = '\n'.join(body_lines).rstrip('\n')
                out.append(render_panel(kind, title, body_md))

                # skip the closing ::: if present
                i = j + 1 if j < len(lines) else j
                continue

            out.append(lines[i])
            i += 1

        text = '\n'.join(out)

        # ---------- Pass B: simple/inline (>>> kind "Title" [one-line or multi-line]) ----------
        lines = text.split('\n')
        out = []
        i = 0
        simple_start = re.compile(r'^\s*>>>\s*([a-zA-Z]+)(?:\s+"([^"]*)")?(?:\s+(.*))?\s*$')

        while i < len(lines):
            m = simple_start.match(lines[i])
            if m:
                kind, title, tail = m.group(1), (m.group(2) or ''), (m.group(3) or '')

                if tail.strip():
                    # one-line form on same line
                    out.append(render_panel(kind, title, tail.strip()))
                    i += 1
                    continue

                # multi-line: collect until blank line (or EOF)
                j = i + 1
                body_lines = []
                while j < len(lines) and lines[j].strip() != '':
                    body_lines.append(lines[j])
                    j += 1

                body_md = '\n'.join(body_lines).rstrip('\n')
                out.append(render_panel(kind, title, body_md))
                i = j  # skip blank that ends the block
                # keep the blank line (if any) to separate from next block
                if i < len(lines) and lines[i].strip() == '':
                    out.append(lines[i])
                    i += 1
                continue

            out.append(lines[i])
            i += 1

        return '\n'.join(out)

    def process_collapsibles(self, text):
        """Parse collapsible blocks marked with '::: collapse Title' and ending with ':::'"""
        pattern_start = re.compile(r'^:::\s*collapse\s*(.*)$', re.IGNORECASE)
        lines = text.split('\n')
        new_lines = []
        i = 0
        while i < len(lines):
            m = pattern_start.match(lines[i])
            if m:
                title = m.group(1).strip() or 'Details'
                content_lines = []
                j = i + 1
                while j < len(lines):
                    if lines[j].strip() == ':::' :
                        break
                    content_lines.append(lines[j])
                    j += 1
                body = '\n'.join(content_lines).strip()
                # Wrap the body through the markdown pipeline recursively for inner content
                inner_html = self.markdown_to_html(body) if body else ''
                details_html = (
                    f'<details class="details-panel">\n'
                    f'  <summary><span class="summary-icon"><svg width="14" height="14" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true"><path d="M6 8L10 12L14 8" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg></span><span class="summary-title">{title}</span></summary>\n'
                    f'  <div class="details-content">{inner_html}</div>\n'
                    f'</details>'
                )
                new_lines.append(details_html)
                i = j + 1
                continue
            new_lines.append(lines[i])
            i += 1
        return '\n'.join(new_lines)

    def process_tabs(self, text):
        """Convert ::: tabs blocks into interactive tab sets."""
        start_re = re.compile(r'^\s*:::\s*tabs\b.*$', re.IGNORECASE)
        end_re = re.compile(r'^\s*:::\s*$')
        tab_re = re.compile(r'^\s*@tab(?:\[(?P<attrs>[^\]]+)\])?(?:\s+(?P<title>.*))?\s*$')

        lines = text.split('\n')
        output = []
        i = 0
        while i < len(lines):
            if not start_re.match(lines[i]):
                output.append(lines[i])
                i += 1
                continue

            j = i + 1
            tabs = []
            current = None
            while j < len(lines):
                if end_re.match(lines[j]):
                    if current:
                        current['body'] = '\n'.join(current['body']).strip()
                        tabs.append(current)
                    break
                tab_match = tab_re.match(lines[j])
                if tab_match:
                    if current:
                        current['body'] = '\n'.join(current['body']).strip()
                        tabs.append(current)
                    attrs = self._parse_bracket_attributes(tab_match.group('attrs') or '')
                    title = (tab_match.group('title') or '').strip() or f'Tab {len(tabs)+1}'
                    current = {'title': title, 'attrs': attrs, 'body': []}
                else:
                    if current:
                        current['body'].append(lines[j])
                j += 1

            if j >= len(lines) or not tabs:
                output.append(lines[i])
                i += 1
                continue

            self._tab_counter += 1
            group_id = f'tabs-{self._tab_counter}'
            tab_html = [f'<div class="tab-set" data-tab-group="{group_id}">']
            for idx, tab in enumerate(tabs):
                input_id = f'{group_id}-tab-{idx}'
                checked = ' checked' if idx == 0 else ''
                tab_html.append(f'  <input type="radio" name="{group_id}" id="{input_id}"{checked}>')
                label_fragments = []
                icon = tab['attrs'].get('icon')
                if icon:
                    label_fragments.append(f'<span class="tab-icon">{html.escape(icon, quote=False)}</span>')
                label_fragments.append(f'<span class="tab-label">{html.escape(tab["title"], quote=False)}</span>')
                badge = tab['attrs'].get('badge')
                if badge:
                    label_fragments.append(f'<span class="tab-badge">{html.escape(badge, quote=False)}</span>')
                tab_html.append(f'  <label class="tab-trigger" for="{input_id}">{"".join(label_fragments)}</label>')
                panel_body = self._render_markdown_block(tab['body'])
                tab_html.append(f'  <div class="tab-panel">{panel_body}</div>')
            tab_html.append('</div>')
            output.append('\n'.join(tab_html))
            i = j + 1

        return '\n'.join(output)

    def process_columns(self, text):
        """Convert ::: columns blocks into responsive column layouts."""
        start_re = re.compile(r'^\s*:::\s*columns\b.*$', re.IGNORECASE)
        end_re = re.compile(r'^\s*:::\s*$')
        column_re = re.compile(r'^\s*@column(?:\[(?P<attrs>[^\]]+)\])?(?:\s+(?P<title>.*))?\s*$')

        lines = text.split('\n')
        output = []
        i = 0
        while i < len(lines):
            if not start_re.match(lines[i]):
                output.append(lines[i])
                i += 1
                continue

            j = i + 1
            columns = []
            current = None
            while j < len(lines):
                if end_re.match(lines[j]):
                    if current:
                        current['body'] = '\n'.join(current['body']).strip()
                        columns.append(current)
                    break
                column_match = column_re.match(lines[j])
                if column_match:
                    if current:
                        current['body'] = '\n'.join(current['body']).strip()
                        columns.append(current)
                    attrs = self._parse_bracket_attributes(column_match.group('attrs') or '')
                    title = (column_match.group('title') or '').strip()
                    current = {'title': title, 'attrs': attrs, 'body': []}
                else:
                    if current:
                        current['body'].append(lines[j])
                j += 1

            if j >= len(lines) or not columns:
                output.append(lines[i])
                i += 1
                continue

            col_html = ['<div class="column-set">']
            for col in columns:
                classes = ['column-item']
                span = col['attrs'].get('span') or col['attrs'].get('width')
                if span and span.isdigit():
                    classes.append(f'column-span-{span}')
                col_html.append(f'  <div class="{" ".join(classes)}">')
                if col['title']:
                    title_html = self._render_markdown_compact(col['title'])
                    col_html.append(f'    <div class="column-title">{title_html}</div>')
                body_html = self._render_markdown_block(col['body'])
                col_html.append(f'    <div class="column-body">{body_html}</div>')
                col_html.append('  </div>')
            col_html.append('</div>')
            output.append('\n'.join(col_html))
            i = j + 1

        return '\n'.join(output)

    def process_cards(self, text):
        """Convert ::: cards blocks into card grids."""
        start_re = re.compile(r'^\s*:::\s*cards\b.*$', re.IGNORECASE)
        end_re = re.compile(r'^\s*:::\s*$')
        card_re = re.compile(r'^\s*@card(?:\[(?P<attrs>[^\]]+)\])?(?:\s+(?P<title>.*))?\s*$')

        lines = text.split('\n')
        output = []
        i = 0
        while i < len(lines):
            if not start_re.match(lines[i]):
                output.append(lines[i])
                i += 1
                continue

            j = i + 1
            cards = []
            current = None
            while j < len(lines):
                if end_re.match(lines[j]):
                    if current:
                        current['body'] = '\n'.join(current['body']).strip()
                        cards.append(current)
                    break
                card_match = card_re.match(lines[j])
                if card_match:
                    if current:
                        current['body'] = '\n'.join(current['body']).strip()
                        cards.append(current)
                    attrs = self._parse_bracket_attributes(card_match.group('attrs') or '')
                    title = (card_match.group('title') or '').strip()
                    current = {'title': title, 'attrs': attrs, 'body': []}
                else:
                    if current:
                        current['body'].append(lines[j])
                j += 1

            if j >= len(lines) or not cards:
                output.append(lines[i])
                i += 1
                continue

            card_group = ['<div class="card-grid">']
            for card in cards:
                link = card['attrs'].get('link') or card['attrs'].get('url')
                icon = card['attrs'].get('icon')
                accent = card['attrs'].get('accent')
                classes = ['card-item']
                if accent:
                    classes.append(f'card-accent-{re.sub(r"[^a-z0-9-]", "", accent.lower())}')
                tag_open = ''
                tag_close = ''
                if link:
                    href = html.escape(link, quote=True)
                    target = card['attrs'].get('target') or '_blank'
                    rel = 'noopener noreferrer'
                    tag_open = f'<a class="{" ".join(classes)}" href="{href}" target="{html.escape(target, quote=True)}" rel="{rel}">'
                    tag_close = '</a>'
                else:
                    tag_open = f'<div class="{" ".join(classes)}">'
                    tag_close = '</div>'
                card_group.append(f'  {tag_open}')
                if icon:
                    card_group.append(f'    <div class="card-icon">{html.escape(icon, quote=False)}</div>')
                if card['title']:
                    title_html = self._render_markdown_compact(card['title'])
                    card_group.append(f'    <div class="card-title">{title_html}</div>')
                body_html = self._render_markdown_block(card['body'])
                card_group.append(f'    <div class="card-body">{body_html}</div>')
                cta = card['attrs'].get('cta')
                if cta and not link:
                    cta_html = self._render_markdown_compact(cta)
                    card_group.append(f'    <div class="card-cta">{cta_html}</div>')
                card_group.append(f'  {tag_close}')
            card_group.append('</div>')
            output.append('\n'.join(card_group))
            i = j + 1

        return '\n'.join(output)

    def process_quotes(self, text):
        """Convert ::: quote blocks into styled quotes."""
        start_re = re.compile(r'^\s*:::\s*quote(?:\s+"([^"]*)")?(?:\s+-\s*(.*))?\s*$', re.IGNORECASE)
        end_re = re.compile(r'^\s*:::\s*$')

        lines = text.split('\n')
        output = []
        i = 0
        while i < len(lines):
            start_match = start_re.match(lines[i])
            if not start_match:
                output.append(lines[i])
                i += 1
                continue

            title = start_match.group(1) or ''
            author = start_match.group(2) or ''
            j = i + 1
            body_lines = []
            while j < len(lines) and not end_re.match(lines[j]):
                body_lines.append(lines[j])
                j += 1

            if j >= len(lines):
                output.append(lines[i])
                i += 1
                continue

            body_md = '\n'.join(body_lines).strip()
            body_html = self._render_markdown_block(body_md)
            quote_fragments = ['<figure class="quote-block">', f'  <blockquote>{body_html}</blockquote>']
            if title or author:
                caption_parts = []
                if title:
                    caption_parts.append(f'<span class="quote-cite-title">{html.escape(title, quote=False)}</span>')
                if author:
                    caption_parts.append(f'<span class="quote-cite-author">{html.escape(author, quote=False)}</span>')
                quote_fragments.append(f'  <figcaption>{" · ".join(caption_parts)}</figcaption>')
            quote_fragments.append('</figure>')
            output.append('\n'.join(quote_fragments))
            i = j + 1

        return '\n'.join(output)

    def process_embeds(self, text):
        """Convert !embed syntax into rich HTML embeds."""
        embed_pattern = re.compile(
            r'^\s*!embed(?:\[(?P<variant>[^\]]+)\])?\s+(?P<url>\S+)(?:\s+"(?P<title>[^"]+)")?\s*$',
            re.IGNORECASE
        )
        lines = text.split('\n')
        transformed = []
        for line in lines:
            match = embed_pattern.match(line)
            if match:
                variant = (match.group('variant') or '').strip()
                url = (match.group('url') or '').strip()
                title = (match.group('title') or '').strip()
                embed_html = self.render_embed(url, variant, title)
                if embed_html:
                    transformed.append(embed_html)
                    continue
            transformed.append(line)
        return '\n'.join(transformed)

    def render_embed(self, url, variant, title):
        """Return the HTML snippet for a single embed command."""
        if not url or not url.lower().startswith(('http://', 'https://')):
            return None

        normalized_variant = (variant or '').lower()
        youtube_id = self.extract_youtube_id(url)
        if normalized_variant in ('youtube', 'video') and not youtube_id:
            youtube_id = self.extract_youtube_id(url)
        if youtube_id:
            return self.render_youtube_embed(url, youtube_id, title)

        if normalized_variant in ('simple', 'minimal', 'compact'):
            return self.render_simple_embed(url, title)

        return self.render_card_embed(url, title, normalized_variant)

    def render_youtube_embed(self, url, video_id, title):
        """Render a responsive YouTube iframe."""
        embed_src = f'https://www.youtube.com/embed/{video_id}'
        iframe_title = html.escape(title or 'YouTube video', quote=False)

        parts = [
            '<div class="embed embed-youtube">',
            '  <div class="embed-media">',
            f'    <iframe src="{embed_src}" title="{iframe_title}" loading="lazy" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>',
            '  </div>'
        ]
        if title:
            caption = html.escape(title, quote=False)
            parts.append(f'  <p class="embed-caption">{caption}</p>')
        parts.append('</div>')
        return '\n'.join(parts)

    def render_simple_embed(self, url, title):
        """Render a lightweight text link preview."""
        metadata = self.fetch_link_metadata(url)
        display_title = title or metadata.get('title') or self.extract_domain(url)
        description = metadata.get('description', '')
        site_name = metadata.get('site_name') or self.extract_domain(url)

        parts = [
            '<div class="embed-block">',
            f'  <a class="embed embed-simple" href="{html.escape(url, quote=True)}" target="_blank" rel="noopener noreferrer">'
        ]
        if display_title:
            parts.append(f'    <span class="embed-simple-title">{html.escape(display_title, quote=False)}</span>')
        if description:
            parts.append(f'    <span class="embed-simple-description">{html.escape(self.truncate_text(description, 160), quote=False)}</span>')
        parts.append(f'    <span class="embed-simple-domain">{html.escape(site_name, quote=False)}</span>')
        parts.append('  </a>')
        parts.append('</div>')
        return '\n'.join(parts)

    def render_card_embed(self, url, title, variant):
        """Render a detailed link preview with metadata."""
        metadata = self.fetch_link_metadata(url)
        site_name = metadata.get('site_name') or self.extract_domain(url)
        fallback_title = self.extract_domain(url) if url else ''
        card_title = title or metadata.get('title') or fallback_title or url
        description = metadata.get('description', '')
        image_url = metadata.get('image')

        parts = [
            '<div class="embed-block">',
            f'  <a class="embed embed-card" href="{html.escape(url, quote=True)}" target="_blank" rel="noopener noreferrer">'
        ]
        if image_url:
            parts.extend([
                '    <div class="embed-card-media">',
                f'      <img src="{html.escape(image_url, quote=True)}" alt="{html.escape(card_title, quote=False)} preview" loading="lazy">',
                '    </div>'
            ])
        else:
            placeholder = site_name[:1].upper() if site_name else '↗'
            parts.append(f'    <div class="embed-card-placeholder">{html.escape(placeholder, quote=False)}</div>')

        parts.append('    <div class="embed-card-body">')
        parts.append(f'      <span class="embed-card-site">{html.escape(site_name, quote=False)}</span>')
        parts.append(f'      <span class="embed-card-title">{html.escape(card_title, quote=False)}</span>')
        if description:
            parts.append(f'      <span class="embed-card-description">{html.escape(self.truncate_text(description, 220), quote=False)}</span>')
        parts.append('    </div>')
        parts.append('  </a>')
        parts.append('</div>')
        return '\n'.join(parts)

    def fetch_link_metadata(self, url):
        """Fetch OpenGraph/Twitter metadata for a link to power rich previews."""
        if url in self._embed_metadata_cache:
            return self._embed_metadata_cache[url]

        metadata = {}
        try:
            request = Request(url, headers={'User-Agent': 'Mozilla/5.0 (compatible; BlogManager/1.0)'})
            with urlopen(request, timeout=6) as response:
                status = getattr(response, 'status', None) or response.getcode()
                if status and status >= 400:
                    self._embed_metadata_cache[url] = {}
                    return {}
                content_type = response.headers.get('Content-Type', '')
                charset_match = re.search(r'charset=([\w-]+)', content_type or '', re.IGNORECASE)
                charset = charset_match.group(1) if charset_match else 'utf-8'
                raw = response.read(300000)
                html_text = raw.decode(charset, errors='ignore')
        except (HTTPError, URLError, ValueError, TimeoutError):
            self._embed_metadata_cache[url] = {}
            return {}
        except Exception:
            self._embed_metadata_cache[url] = {}
            return {}

        class _MetaParser(HTMLParser):
            def __init__(self):
                super().__init__()
                self.meta = {}

            def handle_starttag(self, tag, attrs):
                if tag.lower() != 'meta':
                    return
                attr_dict = {k.lower(): v for k, v in attrs if k and v}
                name = (attr_dict.get('property') or attr_dict.get('name') or '').lower()
                content = attr_dict.get('content')
                if name and content:
                    self.meta[name] = content

        parser = _MetaParser()
        try:
            parser.feed(html_text)
        except Exception:
            pass
        meta_map = parser.meta

        field_map = {
            'title': ['og:title', 'twitter:title'],
            'description': ['og:description', 'twitter:description', 'description'],
            'image': ['og:image', 'twitter:image'],
            'site_name': ['og:site_name', 'twitter:site']
        }

        for field, keys in field_map.items():
            for key in keys:
                value = meta_map.get(key.lower())
                if value:
                    metadata[field] = html.unescape(value.strip())
                    break

        if 'title' not in metadata:
            title_match = re.search(r'<title[^>]*>(.*?)</title>', html_text, re.IGNORECASE | re.DOTALL)
            if title_match:
                raw_title = re.sub(r'\s+', ' ', title_match.group(1)).strip()
                if raw_title:
                    metadata['title'] = html.unescape(raw_title)

        image_url = metadata.get('image')
        if image_url:
            metadata['image'] = urljoin(url, image_url)

        metadata.setdefault('site_name', self.extract_domain(url))
        metadata = {k: v for k, v in metadata.items() if v}
        self._embed_metadata_cache[url] = metadata
        return metadata

    def extract_youtube_id(self, url):
        """Return the YouTube video ID if the URL is a YouTube link."""
        try:
            parsed = urlparse(url)
        except ValueError:
            return ''

        host = parsed.netloc.lower()
        video_id = ''

        if 'youtu.be' in host:
            video_id = parsed.path.lstrip('/')
        elif 'youtube.com' in host:
            if parsed.path.startswith('/watch'):
                query = parse_qs(parsed.query)
                video_id = (query.get('v') or [''])[0]
            elif parsed.path.startswith('/embed/'):
                video_id = parsed.path.split('/')[2] if len(parsed.path.split('/')) > 2 else ''
            elif parsed.path.startswith('/shorts/'):
                video_id = parsed.path.split('/')[2] if len(parsed.path.split('/')) > 2 else ''

        video_id = video_id.split('?')[0].split('&')[0] if video_id else ''
        if video_id and re.match(r'^[\w-]{6,}$', video_id):
            return video_id
        return ''

    def extract_domain(self, url):
        """Return a cleaned domain name for display."""
        try:
            domain = urlparse(url).netloc
        except ValueError:
            return url
        if domain.startswith('www.'):
            domain = domain[4:]
        return domain or url

    def truncate_text(self, value, limit=180):
        """Return value truncated to limit with ellipsis."""
        if not value:
            return ''
        value = re.sub(r'\s+', ' ', value.strip())
        if len(value) <= limit:
            return value
        return value[:limit - 1].rstrip() + '…'

    def _parse_bracket_attributes(self, attr_text):
        """Parse key=value pairs from a bracket attribute string."""
        attrs = {}
        if not attr_text:
            return attrs
        for match in re.finditer(r'(\w+)\s*=\s*(?:"([^"]*)"|\'([^\']*)\'|([^\s]+))', attr_text):
            key = match.group(1).lower()
            value = match.group(2) or match.group(3) or match.group(4) or ''
            attrs[key] = value
        return attrs

    def _render_markdown_block(self, text):
        """Render markdown into HTML without stripping block wrappers."""
        return markdown.markdown(text or '', extensions=['extra', 'attr_list', 'md_in_html'])

    def _render_markdown_compact(self, text):
        """Render markdown and strip single paragraph wrapper."""
        html_text = self._render_markdown_block(text)
        if html_text.startswith('<p>') and html_text.endswith('</p>') and html_text.count('<p>') == 1:
            return html_text[3:-4].strip()
        return html_text

    def process_note_blocks(self, text):
        """Convert > **[**Label**]:** blocks into highlighted note callouts with optional lists."""
        note_re = re.compile(
            r'^\s*>\s*\*\*\[\*\*(?P<label>[^\*]+)\*\*\]:\*\*\s*(?P<body>.*)$'
        )
        simple_note_re = re.compile(r'^\s*>\s*\[(?P<label>[^\]]+)\]:\s*(?P<body>.*)$')
        lines = text.split('\n')
        output = []
        i = 0
        while i < len(lines):
            match = note_re.match(lines[i]) or simple_note_re.match(lines[i])
            if not match:
                output.append(lines[i])
                i += 1
                continue

            label = (match.group('label') or 'Note').strip()
            comment = (match.group('body') or '').strip()
            j = i + 1
            # Skip a single blank line after the note header
            if j < len(lines) and lines[j].strip() == '':
                j += 1

            collected = []
            while j < len(lines):
                stripped = lines[j].lstrip()
                if not stripped:
                    # Allow single blank line within the note body
                    # Stop if we have 2+ consecutive blank lines
                    lookahead = j + 1
                    blank_count = 1
                    while lookahead < len(lines) and lines[lookahead].strip() == '':
                        blank_count += 1
                        lookahead += 1
                    # If we have 2+ consecutive blank lines, stop collecting
                    if blank_count >= 2:
                        break
                    # If next non-blank line starts a new top-level block element, stop
                    if lookahead < len(lines):
                        la_stripped = lines[lookahead].lstrip()
                        # Stop if next line starts a new block (heading, new note block, code block, callout, etc.)
                        # But allow regular blockquotes and indented content (continuation of lists, etc.)
                        if (la_stripped.startswith('#') or 
                            (la_stripped.startswith('>') and (note_re.match(lines[lookahead]) or simple_note_re.match(lines[lookahead]))) or
                            la_stripped.startswith('```') or
                            la_stripped.startswith(':::') or
                            la_stripped.startswith('---')):
                            break
                    # Single blank line is OK, collect it
                    collected.append(lines[j])
                    j += 1
                    continue
                # Collect all non-blank lines (paragraphs, lists, etc.)
                collected.append(lines[j])
                j += 1
                continue

            body_sections = []
            if collected:
                body_sections.append('\n'.join(collected))
            body_html = self._render_markdown_block('\n\n'.join(body_sections)) if body_sections else ''
            header_text = self._render_markdown_compact(comment) if comment else ''

            block = [
                '<div class="note-block">',
                '  <div class="note-header">',
                f'    <span class="note-badge">{html.escape(label, quote=False)}</span>'
            ]
            if header_text:
                block.append(f'    <span class="note-text">{header_text}</span>')
            block.append('  </div>')
            if body_html:
                block.append(f'  <div class="note-body">{body_html}</div>')
            block.append('</div>')
            output.append('\n'.join(block))
            i = j
        return '\n'.join(output)

    def _ensure_class_on_tag(self, tag_html, class_name):
        """Ensure the provided HTML tag string contains class_name."""
        if not class_name:
            return tag_html
        match = re.match(r'(<\w+)([^>]*)(>)', tag_html)
        if not match:
            return tag_html
        start, attrs, close = match.groups()
        remainder = tag_html[match.end():]
        if 'class=' in attrs:
            def repl(m):
                quote = m.group(1)
                classes = m.group(2).split()
                if class_name not in classes:
                    classes.append(class_name)
                return f'class={quote}{" ".join(classes)}{quote}'
            new_attrs = re.sub(r'class=(["\'])(.*?)\1', repl, attrs, count=1)
        else:
            new_attrs = f'{attrs} class="{class_name}"'
        return f'{start}{new_attrs}{close}{remainder}'

    def style_task_lists(self, html_text):
        """Transform markdown-style [ ] lists into rich checkbox task lists."""
        task_pattern = re.compile(
            r'(?P<open><li[^>]*>\s*)(?:<p[^>]*>)?\s*\[(?P<state>[ xX])\]\s*(?P<body>.*?)(?:</p>)?(?=\s*(?:<ul|</li>))',
            re.DOTALL
        )

        def replace_task(match):
            li_open = match.group('open')
            li_open = self._ensure_class_on_tag(li_open, 'task-list-item')
            state = match.group('state').lower()
            body = match.group('body').strip()
            status_class = 'task-complete' if state == 'x' else 'task-open'
            return (
                f'{li_open}'
                f'<div class="task-item {status_class}">'
                f'  <span class="task-checkbox" aria-hidden="true"></span>'
                f'  <span class="task-text">{body}</span>'
                f'</div>\n'
            )

        styled = task_pattern.sub(replace_task, html_text)
        styled = re.sub(
            r'<ul>(?=\s*<li[^>]*>\s*<div class="task-item)',
            '<ul class="task-list">',
            styled
        )
        styled = re.sub(
            r'<ol>(?=\s*<li[^>]*>\s*<div class="task-item)',
            '<ol class="task-list ordered">',
            styled
        )
        return styled

    def process_pipe_tables(self, text):
        """Convert simple pipe-delimited markdown tables into HTML tables with class confluence-table"""
        lines = text.split('\n')
        new_lines = []
        i = 0
        def render_cell_html(cell_text, is_header=False):
            """Render inline markdown inside table cells before wrapping."""
            cell_text = cell_text.strip()
            if not cell_text:
                return '<th></th>' if is_header else '<td></td>'

            cell_html = markdown.markdown(
                cell_text,
                extensions=['extra', 'attr_list', 'md_in_html']
            )
            if cell_html.startswith('<p>') and cell_html.endswith('</p>'):
                cell_html = cell_html[3:-4].strip()

            tag = 'th' if is_header else 'td'
            return f'<{tag}>{cell_html}</{tag}>'

        while i < len(lines):
            if '|' in lines[i]:
                # detect a table header followed by a separator like |---|
                if i+1 < len(lines) and re.match(r'^[\s|:-]+$', lines[i+1]):
                    header = [c.strip() for c in lines[i].strip().strip('|').split('|')]
                    # consume header and separator
                    i += 2
                    rows = []
                    while i < len(lines) and '|' in lines[i] and not re.match(r'^\s*$', lines[i]):
                        row = [c.strip() for c in lines[i].strip().strip('|').split('|')]
                        rows.append(row)
                        i += 1
                    # build table
                    ths = ''.join([render_cell_html(h, is_header=True) for h in header])
                    trs_parts = []
                    for row in rows:
                        row_cells = ''.join([render_cell_html(cell) for cell in row])
                        trs_parts.append(f'<tr>{row_cells}</tr>')
                    trs = '\n'.join(trs_parts)
                    table_html = f'<table class="confluence-table">\n<thead><tr>{ths}</tr></thead>\n<tbody>{trs}</tbody>\n</table>'
                    new_lines.append(table_html)
                    continue
            new_lines.append(lines[i])
            i += 1
        return '\n'.join(new_lines)

    def normalize_plain_details(self, text):
        """Nested-aware normalization of <details> tags.
        This finds the innermost <details>..</details> blocks and wraps their post-summary
        content in a <div class="details-content"> and ensures the <details> has class details-panel.
        """
        # Linear scan approach: find the next <details ...> and its matching </details>
        lower = text.lower()
        out = ''
        idx = 0
        while True:
            open_pos = lower.find('<details', idx)
            if open_pos == -1:
                out += text[idx:]
                break

            out += text[idx:open_pos]
            open_tag_end = text.find('>', open_pos)
            if open_tag_end == -1:
                out += text[open_pos:]
                break

            # Find matching closing tag with nesting awareness
            scan_pos = open_tag_end + 1
            depth = 1
            while depth > 0:
                next_open = lower.find('<details', scan_pos)
                next_close = lower.find('</details>', scan_pos)
                if next_close == -1:
                    out += text[open_pos:]
                    scan_pos = len(text)
                    break
                if next_open != -1 and next_open < next_close:
                    depth += 1
                    scan_pos = next_open + 8
                else:
                    depth -= 1
                    scan_pos = next_close + len('</details>')
            if scan_pos > len(text):
                break

            block = text[open_pos:scan_pos]
            open_tag = text[open_pos:open_tag_end+1]
            inner_html = block[len(open_tag):-len('</details>')]

            # Recursively normalize nested details inside the inner HTML
            inner_html = self.normalize_plain_details(inner_html)

            # Ensure the outer <details> has expected class
            if 'class=' in open_tag.lower():
                if 'details-panel' not in open_tag:
                    open_tag = re.sub(
                        r'(class=\"|class=\')(.*?)\1',
                        lambda m: f'class="details-panel {m.group(2)}"',
                        open_tag,
                        count=1
                    )
            else:
                open_tag = open_tag[:-1] + ' class="details-panel">'

            # Extract summary if present
            summary_match = re.match(
                r'(\s*<summary\b[^>]*>.*?</summary>)(.*)',
                inner_html,
                flags=re.DOTALL | re.IGNORECASE
            )
            if summary_match:
                summary_html = summary_match.group(1)
                rest_html = summary_match.group(2)
            else:
                summary_html = ''
                rest_html = inner_html

            if summary_html:
                if 'summary-icon' not in summary_html:
                    sm = re.match(
                        r'\s*<summary\b([^>]*)>(.*)</summary>',
                        summary_html,
                        flags=re.DOTALL | re.IGNORECASE
                    )
                    if sm:
                        attrs = sm.group(1)
                        inner_summary = sm.group(2).strip()
                        summary_html = (
                            f'<summary{attrs}>'
                            f'<span class="summary-icon"><svg width="14" height="14" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true"><path d="M6 8L10 12L14 8" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg></span>'
                            f'<span class="summary-title">{inner_summary}</span>'
                            f'</summary>'
                        )
            else:
                summary_html = (
                    '<summary>'
                    '<span class="summary-icon"><svg width="14" height="14" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true"><path d="M6 8L10 12L14 8" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg></span>'
                    '<span class="summary-title">Details</span>'
                    '</summary>'
                )

            rest_html = textwrap.dedent(rest_html).strip()
            if rest_html:
                fixed_lines = []
                for line in rest_html.splitlines():
                    stripped_line = line.lstrip()
                    indent = len(line) - len(stripped_line)
                    if stripped_line.startswith(('* ', '- ', '+ ')) and 0 < indent < 4:
                        line = ' ' * 4 + stripped_line
                    fixed_lines.append(line)
                rest_html = '\n'.join(fixed_lines)
            content_body = rest_html
            if rest_html and '<details' not in rest_html.lower():
                if rest_html.startswith('<') and not rest_html.startswith('<p>'):
                    content_body = rest_html
                else:
                    need_render = (
                        '```' in rest_html or
                        'CODE_BLOCK_PLACEHOLDER_' in rest_html or
                        re.search(r'(^|\n)\s*#{1,6}\s', rest_html) or
                        re.search(r'(^|\n)\s*[\-*+]\s', rest_html) or
                        re.search(r'(^|\n)\s*\d+\.\s', rest_html)
                    )
                    if need_render or not rest_html.startswith('<'):
                        content_body = self._render_markdown_block(rest_html)
            if content_body:
                stripped_body = content_body.lstrip()
                if stripped_body.startswith('<div') and re.search(r'class=["\']details-content', stripped_body.split('>', 1)[0]):
                    content_html = content_body
                else:
                    content_html = f'<div class="details-content">{content_body}</div>'
            else:
                content_html = '<div class="details-content"></div>'

            new_block = f'{open_tag}{summary_html}{content_html}</details>'
            out += new_block
            idx = scan_pos

        return out

    def fix_fenced_code_in_paragraphs(self, text):
        """Convert paragraphs that contain literal fenced code (rendered with <br>) back into code blocks.
        Matches patterns like: <p ...>```lang<br>...<br>```</p>
        """
        pattern = re.compile(
            r'<p([^>]*)>```(\w+)?(?:<br\s*/?>)(.*?)(?:<br\s*/?>)```</p>',
            flags=re.DOTALL
        )
        def repl(m):
            attrs = m.group(1) or ''
            lang = m.group(2) or ''
            code_html = m.group(3)
            # convert <br> variations to newlines and unescape common entities
            code_text = re.sub(r'<br\s*/?>', '\n', code_html)
            code_text = code_text.replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&')
            lang_class = f'language-{lang}' if lang else ''
            escaped = html.escape(code_text)  # Already correct, but ensure import is at top
            return f'<div class="cust-border-lg border-blue-500 cust-rounded-lg code-block mb-6 lg:mb-8">\n<pre class="line-numbers {lang_class}"><code class="{lang_class}">{escaped}</code></pre>\n</div>'
        return re.sub(pattern, repl, text)

    def protect_code_blocks(self, text):
        code_block_placeholders = {}
        counter = 0

        def repl(m):
            nonlocal counter
            counter += 1
            pid = f'CODE_BLOCK_PLACEHOLDER_{counter}'
            lang = m.group(1) or ''
            code = m.group(2)
            escaped = html.escape(code)
            lang_class = f'language-{lang}' if lang else ''
            # Updated: Add lang_class to <pre> for proper Prism integration; structure matches desired <pre><span rows></span><code></code></pre> after Prism
            code_block_placeholders[pid] = f'<div class="cust-border-lg border-blue-500 cust-rounded-lg code-block mb-6 lg:mb-8"><pre class="line-numbers {lang_class}"><code class="{lang_class}">{escaped}</code></pre></div>'
            return f"\n{pid}\n"

        # Match code blocks: ```lang\ncontent\n``` followed by newline or end of string
        # Allow optional leading/trailing whitespace around backticks to handle indented code blocks
        # Use positive lookahead to ensure we don't capture trailing content like </details>
        fence_pattern = r"\s*```(\w+)?\r?\n(.*?)\r?\n\s*```(?=\r?\n|$)"
        modified = re.sub(fence_pattern, repl, text, flags=re.DOTALL)
        return modified, code_block_placeholders

    def restore_code_blocks(self, text, placeholders):
        for k, v in placeholders.items():
            text = text.replace(k, v)
        return text

    def protect_inline_code(self, text: str):
        """
        Protect single-backtick inline code spans from earlier regex transforms.
        Returns (protected_text, placeholders_dict).
        """
        import re
        placeholders = {}
        idx = 0
        # single-backtick spans; avoid matching ``code`` pairs
        pattern = re.compile(r'(?<!`)`([^`\n]+?)`(?!`)')

        def repl(m):
            nonlocal idx
            key = f"__INLINE_CODE_{idx}__"
            # keep backticks so Markdown converts later
            placeholders[key] = f"`{m.group(1)}`"
            idx += 1
            return key

        protected = pattern.sub(repl, text)
        return protected, placeholders

    def restore_inline_code(self, text: str, placeholders: dict):
        """Restore backticked inline code just before the final Markdown render."""
        for k, v in placeholders.items():
            text = text.replace(k, v)
        return text
    
    def process_embed_links_post(self, html: str) -> str:
        """
        Post-process HTML to convert links with @embed in title attribute to embed blocks.
        This runs AFTER markdown conversion, so it processes the HTML <a> tags.
        """
        import re
        
        # Pattern to match <a> tags with @embed in title attribute
        # Matches: <a href="url" title="@embed">text</a> or <a href="url" title="something @embed">text</a>
        pattern = re.compile(
            r'<a\s+([^>]*href=["\']([^"\']+)["\'][^>]*title=["\'][^"\']*@embed[^"\']*["\'][^>]*)>(.*?)</a>',
            re.IGNORECASE | re.DOTALL
        )
        
        def repl(match):
            attrs = match.group(1)
            url = match.group(2)
            link_text = match.group(3).strip()
            
            # Extract title from attributes
            title_match = re.search(r'title=["\']([^"\']+)["\']', attrs, re.IGNORECASE)
            title_attr = title_match.group(1) if title_match else ''
            
            # Determine if it's YouTube
            youtube_id = self.extract_youtube_id(url)
            if youtube_id:
                return self.render_youtube_embed(url, youtube_id, link_text or title_attr.replace('@embed', '').strip())
            
            # Use simple embed (matches blog behavior for non-YouTube links)
            return self.render_simple_embed(url, link_text or title_attr.replace('@embed', '').strip())
        
        return pattern.sub(repl, html)

    def _render_inline_md(self, text: str) -> str:
        """Render a small inline Markdown fragment and strip the wrapping <p>."""
        html_frag = markdown.markdown(text, extensions=['extra', 'attr_list', 'md_in_html'])
        if html_frag.startswith('<p>') and html_frag.endswith('</p>'):
            html_frag = html_frag[3:-4]
        return html_frag

    def ensure_colon_list_break(self, text: str) -> str:
        """
        When a paragraph ends with ':' and is immediately followed by a list,
        ensure there's exactly one blank line after the paragraph.
        """
        lines = text.split('\n')
        out = []
        i = 0
        while i < len(lines):
            out.append(lines[i])
            if lines[i].rstrip().endswith(':'):
                # If next line starts a list and there is no blank line, insert one
                if i + 1 < len(lines) and (
                    lines[i+1].startswith('- ') or lines[i+1].startswith('* ') or re.match(r'^\d+\.\s', lines[i+1] or '') is not None
                ):
                    if out[-1] != '':
                        out.append('')
            i += 1
        return '\n'.join(out)

    def ensure_list_separation(self, text: str) -> str:
        """
        Ensure there's a blank line before any top-level list marker so the Markdown
        renderer reliably treats it as a list. This fixes cases where a preceding
        blank line was removed earlier in the pipeline.
        """
        lines = text.split('\n')
        out = []
        for i, line in enumerate(lines):
            is_list_start = (
                line.startswith('- ') or
                line.startswith('* ') or
                re.match(r'^\d+\.\s', line) is not None
            )
            if is_list_start:
                # if previous line exists and is NOT blank and NOT already a list item,
                # insert a blank line to start a new list block
                if out and out[-1].strip() != '' and not (
                    out[-1].startswith('- ') or
                    out[-1].startswith('* ') or
                    re.match(r'^\d+\.\s', out[-1] or '') is not None
                ):
                    out.append('')  # inject a blank line
            out.append(line)
        return '\n'.join(out)

    def _style_paragraphs_post(self, html: str) -> str:
        """
        Add your paragraph classes to plain <p> tags AFTER Markdown conversion.
        Avoid touching <p> that already have a class.
        """
        return re.sub(
            r'<p(?![^>]*\bclass=)>',
            '<p class="mb-3 lg:mb-4 text-sm lg:text-base leading-relaxed px-10">',
            html
        )

    def collapse_list_items(self, text):
        # No-op: let Markdown handle lists (<ul>/<ol>) naturally
        return text

    def process_confluence_callouts(self, text):
        """
        Convert leading-line callouts into HTML blocks.

        Markers at line start:
        '^ ' -> info
        '! ' -> warning
        '✓ ' -> success
        '✗ ' -> error
        '💡 ' -> tip

        A callout ends at the first blank line or a clear block boundary.
        """
        import re, markdown
        kind_map = {
            '^':  ('info',    'Info',      'fa-solid fa-circle-info'),
            '!':  ('warning', 'Important', 'fa-solid fa-triangle-exclamation'),
            '✓':  ('success', 'Success',   'fa-solid fa-circle-check'),
            '✗':  ('error',   'Error',     'fa-solid fa-circle-xmark'),
            '💡': ('tip',     'Pro tip',   'fa-solid fa-lightbulb'),
        }

        def is_boundary(line: str) -> bool:
            s = line.strip()
            return (
                s == ""                                   # blank line ends callout
                or s.startswith(('#', '---', '***'))      # headings / hr
                or s.startswith(('```', '~~~'))           # fenced code
                or s.startswith(('^ ', '! ', '✓ ', '✗ ', '💡 '))  # next callout
                or s.startswith(('<details', '</details', '<figure', '<img', '<table', '<div'))
                or s.startswith('![')                     # markdown image
            )

        def strip_leading_label(body: str, label: str) -> str:
            if not body.strip():
                return body
            lines = body.split('\n')
            first = lines[0].strip()
            pattern = rf'^(\*\*\s*)?{re.escape(label)}(\s*\*\*)?\s*:\s*'
            if re.match(pattern, first, flags=re.IGNORECASE):
                lines[0] = re.sub(pattern, '', first, flags=re.IGNORECASE)
            return '\n'.join(lines)

        lines = text.split('\n')
        out = []
        i = 0
        while i < len(lines):
            raw = lines[i]
            s = raw.lstrip()

            if s.startswith(('^ ', '! ', '✓ ', '✗ ', '💡 ')):
                marker = s[0]
                cclass, label, icon = kind_map.get(marker, ('info', 'Info', 'fa-solid fa-circle-info'))

                # collect body until boundary
                j = i + 1
                body_lines = []
                while j < len(lines) and not is_boundary(lines[j]):
                    body_lines.append(lines[j])
                    j += 1

                body_md = strip_leading_label('\n'.join(body_lines).rstrip('\n'), label)
                # Render just the callout body with Markdown so **bold**, links, etc. work
                body_html = markdown.markdown(body_md, extensions=['extra','attr_list','md_in_html'])

                # ➜ Keep one-line layout: if the body is a single <p>, unwrap it
                if body_html.startswith("<p>") and body_html.endswith("</p>") and body_html.count("<p>") == 1:
                    body_html = body_html[3:-4].strip()

                out.append(
                    f'<div class="callout {cclass}">'
                    f'  <div class="row">'
                    f'    <span class="icon"><i class="{icon}"></i></span>'
                    f'    <div class="body"><span class="title">{label}:</span> {body_html}</div>'
                    f'  </div>'
                    f'</div>'
                )

                i = j
                continue

            out.append(raw)
            i += 1

        return '\n'.join(out)

    def process_headers(self, text):
        lines = text.split('\n')
        new_lines = []
        for line in lines:
            s = line.strip()
            if s.startswith('#### '):
                content_html = self._render_inline_md(s[5:])
                line = f'<h4 class="text-sm lg:text-sm font-semibold mt-3 mb-2 text-gray-800">{content_html}</h4>'
            elif s.startswith('### '):
                content_html = self._render_inline_md(s[4:])
                line = '<div style="clear:both"></div>' + \
                    f'<h3 class="text-base lg:text-lg font-semibold mt-4 lg:mt-6 mb-2 lg:mb-3">{content_html}</h3>'
            elif s.startswith('## '):
                content_html = self._render_inline_md(s[3:])
                line = '<div style="clear:both"></div>' + \
                    f'<h2 class="text-lg lg:text-xl font-bold text-gray-900 mt-6 lg:mt-8 mb-3 lg:mb-4">{content_html}</h2>'
            elif s.startswith('# '):
                content_html = self._render_inline_md(s[2:])
                line = f'<h1 class="text-xl lg:text-2xl font-bold text-gray-900 mt-8 lg:mt-10 mb-4 lg:mb-6">{content_html}</h1>'
            new_lines.append(line)
        return '\n'.join(new_lines)

    def process_images(self, text):
        """Process images: placeholders continue to float; real images render as block-level figures with captions below."""
        lines = text.split('\n')
        new_lines = []
        i = 0
        while i < len(lines):
            line = lines[i]
            # Skip code placeholders
            if line.strip().startswith('CODE_BLOCK_PLACEHOLDER_'):
                new_lines.append(line)
                i += 1
                continue

            img_match = re.search(r'!\[([^\]]*)\]\(([^)]+)\)', line)
            if img_match:
                alt = img_match.group(1)
                src = img_match.group(2)

                # detect inline attr
                attr = None
                remainder = line[img_match.end():].strip()
                skip_next = False
                if remainder.startswith('{:') and '}' in remainder:
                    attr = remainder
                else:
                    if i+1 < len(lines) and lines[i+1].strip().startswith('{:'):
                        attr = lines[i+1].strip()
                        skip_next = True

                alignment = 'center'
                if attr == '{: .left}':
                    alignment = 'left'
                elif attr == '{: .right}':
                    alignment = 'right'
                elif attr == '{: .small}':
                    alignment = 'small'
                elif attr == '{: .nowrap}':
                    alignment = 'nowrap'

                # Build inner HTML
                if src.startswith('placeholder:'):
                    ph_id = src.replace('placeholder:', '')
                    ph_class = 'placeholder-inner default'
                    placeholder_inner = (
                        f'<div class="w-full h-full flex items-center justify-center text-gray-500 mx-auto {ph_class}">' 
                        f'<div class="text-center text-gray-500 font-medium">PLACEHOLDER FOR IMAGE</div>'
                        '</div>'
                    )
                    inner = placeholder_inner
                else:
                    # Fix relative image paths for blog posts
                    # Blog posts are at blog/posts/[slug].html, so media/images/ needs to be ../media/images/
                    # Only adjust relative paths that start with 'media/' and aren't already absolute URLs
                    original_src = src
                    if src.startswith('media/') and not (src.startswith('../') or src.startswith('/') or src.startswith('http://') or src.startswith('https://')):
                        src = '../' + src
                        # Debug: log the fix (can be removed in production)
                        # print(f"Fixed image path: {original_src} -> {src}")
                    img_tag = f'<img src="{src}" alt="{alt}" class="rounded-lg shadow-md max-w-full h-auto" onclick="openImageModal(this)">'
                    inner = f'<div class="fig-inner-pad">{img_tag}</div>'

                # Default fig_class
                fig_class = 'block mx-auto my-6 mt-6 overflow-hidden'
                clear_wrapper = ''

                if alignment == 'left':
                    if src.startswith('placeholder:'):
                        fig_class = 'float-left mr-8 mb-6 mt-6 w-5/12 lg:w-5/12 float-left-force placeholder-mr'
                        clear_wrapper = '<div class="clear-left"></div>'
                    else:
                        fig_class = 'figure-left my-6 mt-6 figure-max-600'
                elif alignment == 'right':
                    if src.startswith('placeholder:'):
                        fig_class = 'float-right ml-16 mb-6 mt-12 w-5/12 lg:w-5/12 float-right-force placeholder-ml'
                        clear_wrapper = '<div class="clear-right"></div>'
                    else:
                        fig_class = 'figure-right my-6 mt-6 figure-max-600'
                elif alignment == 'small':
                    if src.startswith('placeholder:'):
                        fig_class = 'inline-block w-40 mr-4 mb-6 mt-6 overflow-hidden'
                    else:
                        fig_class = 'figure-center my-6 mt-6 figure-max-300'
                elif alignment == 'nowrap':
                    if src.startswith('placeholder:'):
                        fig_class = 'block mx-auto my-6 mt-6 w-full overflow-hidden'
                        clear_wrapper = '<div class="clear-both"></div>'
                    else:
                        fig_class = 'figure-center my-6 mt-6 figure-max-600'

                caption = ''
                if src.startswith('placeholder:'):
                    if alt.strip():
                        caption = alt.strip()
                    else:
                        caption = f'Image Placeholder: {ph_id}'
                else:
                    if alt.strip():
                        caption = alt.strip()

                # Append classes for max width
                if alignment == 'small':
                    fig_class += ' figure-max-300'
                elif alignment in ('center', 'nowrap'):
                    fig_class += ' figure-max-600'

                if caption:
                    caption_align = 'text-center'
                    if alignment == 'left':
                        caption_align = 'text-left'
                    elif alignment == 'right':
                        caption_align = 'text-right'
                    wrapped = (
                        f'<figure class="{fig_class}">{inner}<div class="w-full block"><figcaption class="block w-full text-xs text-gray-500 mt-2 mb-4 {caption_align}">{caption}</figcaption></div></figure>'
                    )
                else:
                    wrapped = f'<figure class="{fig_class}">{inner}</figure>'

                if clear_wrapper:
                    new_lines.append(clear_wrapper + wrapped)
                else:
                    new_lines.append(wrapped)

                # Skip next attr line if we consumed it
                if skip_next:
                    i += 2
                else:
                    i += 1
                continue

            new_lines.append(line)
            i += 1

        return '\n'.join(new_lines)

    def process_paragraphs(self, text):
        lines = text.split('\n')
        new_lines = []
        current = []
        for line in lines:
            if line.strip() == '':
                if current:
                    new_lines.append('<p class="mb-3 lg:mb-4 text-sm lg:text-base leading-relaxed px-10">' + '<br>'.join(current) + '</p>')
                    current = []
                new_lines.append('')
            elif any(line.strip().startswith(p) for p in ['<', 'CODE_BLOCK_PLACEHOLDER_']):
                if current:
                    new_lines.append('<p class="mb-3 lg:mb-4 text-sm lg:text-base leading-relaxed px-10">' + '<br>'.join(current) + '</p>')
                    current = []
                new_lines.append(line)
            else:
                if line.strip():
                    current.append(line.strip())
                else:
                    if current:
                        new_lines.append('<p class="mb-3 lg:mb-4 text-sm lg:text-base leading-relaxed px-10">' + '<br>'.join(current) + '</p>')
                        current = []
                    new_lines.append('')
        if current:
            new_lines.append('<p class="mb-3 lg:mb-4 text-sm lg:text-base leading-relaxed px-10">' + '<br>'.join(current) + '</p>')
        return '\n'.join(new_lines)

    def build_posts(self):
        print("🏗️  Building blog (final version)...")
        md_files = list(self.posts_md_dir.glob("*.md"))
        if not md_files:
            print("❌ No markdown files found")
            return

        succeeded = failed = sanity_failures = 0
        index_records = []

        for md in md_files:
            try:
                ok, out_path = self.generate_post_html(md)
                if ok:
                    succeeded += 1
                    # parse metadata + html again for index (or refactor generate_post_html to return them)
                    with open(md, "r", encoding="utf-8") as f:
                        raw = f.read()
                    meta, body_md = self.parse_frontmatter(raw)
                    body_html = self.markdown_to_html(body_md)
                    index_records.append(self._collect_post_record(md, meta, body_html))
                    print(f"Generated: {out_path}")
                else:
                    failed += 1
            except Exception as e:
                failed += 1
                print(f"❌ Error building {md}: {e}")

        # write posts.json
        if index_records:
            self._write_posts_json(index_records)

        total = len(md_files)
        print(f"✅ Processed {total} posts: {succeeded} succeeded, {failed} failed, {sanity_failures} sanity failures")

    def generate_post_html(self, md_file):
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
        metadata, markdown_content = self.parse_frontmatter(content)
        html_content = self.markdown_to_html(markdown_content)
        slug = metadata.get('slug', metadata.get('id'))
        with open(self.template_file, 'r', encoding='utf-8') as f:
            template = f.read()
        html_content = self.format_post_html(metadata, html_content)
        html_file = template.replace('[POST_TITLE]', metadata.get('title', 'Untitled'))
        blog_content_pattern = r'<div id="blog-content">.*?<!-- Content will be dynamically loaded here -->.*?</div>'
        html_file = re.sub(blog_content_pattern, html_content, html_file, flags=re.DOTALL)
        output_path = self.posts_html_dir / f"{slug}.html"
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_file)
            print(f"Generated: {output_path}")
            return True, str(output_path)
        except Exception as e:
            print(f"❌ Failed to write {output_path}: {e}")
            return False, None

    def format_post_html(self, metadata, content):
        return f"""<div id="blog-content" class="space-y-4 lg:space-y-6 leading-relaxed">{content}</div>"""
    
    def generate_post_html_from_db(self, metadata_dict, html_content, slug):
        """
        Generate HTML file from database data (metadata dict and HTML content).
        
        Args:
            metadata_dict: Dictionary with post metadata (title, date, author, etc.)
            html_content: Pre-processed HTML content (already converted from markdown)
            slug: Post slug for filename
        
        Returns:
            tuple: (success: bool, output_path: str or None)
        """
        try:
            # Fix image paths in HTML content (for backward compatibility with old HTML)
            # This ensures old HTML files get updated paths when regenerated
            # Blog posts are at blog/posts/[slug].html, so media/images/ needs to be ../media/images/
            
            # First, fix all media/images/ paths (most common case)
            html_content = re.sub(
                r'src=(["\'])media/images/([^"\']+)\1',
                r'src=\1../media/images/\2\1',
                html_content
            )
            
            # Also fix any remaining media/ paths that aren't already ../media/ or absolute URLs
            # This catches any other media/ paths that might exist
            html_content = re.sub(
                r'src=(["\'])(?!\.\./|/|https?://)(media/[^"\']+)\1',
                r'src=\1../\2\1',
                html_content
            )
            
            # Debug: Print if we found and fixed any paths (can be removed in production)
            # if 'media/images/' in html_content and '../media/images/' not in html_content:
            #     print(f"Warning: Found media/images/ paths that weren't fixed in HTML for {slug}")
            
            # Load template
            with open(self.template_file, 'r', encoding='utf-8') as f:
                template = f.read()
            
            # Format HTML content
            formatted_content = self.format_post_html(metadata_dict, html_content)
            
            # Replace title placeholder
            html_file = template.replace('[POST_TITLE]', metadata_dict.get('title', 'Untitled'))
            
            # Replace blog-content div
            blog_content_pattern = r'<div id="blog-content">.*?<!-- Content will be dynamically loaded here -->.*?</div>'
            html_file = re.sub(blog_content_pattern, formatted_content, html_file, flags=re.DOTALL)
            
            # Write output file
            output_path = self.posts_html_dir / f"{slug}.html"
            # Ensure we write with a new file handle to avoid caching issues
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_file)
                f.flush()
                os.fsync(f.fileno())  # Force write to disk
            
            print(f"Generated HTML: {output_path}")
            return True, str(output_path)
        except Exception as e:
            print(f"❌ Failed to generate HTML for {slug}: {e}")
            import traceback
            traceback.print_exc()
            return False, None

    def generate_document_html_from_db(self, metadata_dict, html_content, slug, documents_root="/var/www/projectmanager.test/github_v2/documents"):
        """
        Generate HTML file for a document from database data (similar to blog posts).
        
        Args:
            metadata_dict: Dictionary with document metadata (title, date, author, etc.)
            html_content: Pre-processed HTML content (already converted from markdown)
            slug: Document slug for filename
            documents_root: Root directory for documents system
        
        Returns:
            tuple: (success: bool, output_path: str or None)
        """
        try:
            documents_path = Path(documents_root)
            posts_html_dir = documents_path / "posts"
            template_file = documents_path / "document-template.html"
            
            # Create posts directory if it doesn't exist
            posts_html_dir.mkdir(exist_ok=True)
            
            # Load template
            if not template_file.exists():
                raise FileNotFoundError(f"Document template not found: {template_file}")
            
            with open(template_file, 'r', encoding='utf-8') as f:
                template = f.read()
            
            # Format HTML content (similar to blog posts)
            formatted_content = f"""<div id="document-content" class="space-y-4 lg:space-y-6 leading-relaxed">{html_content}</div>"""
            
            # Replace title placeholder
            html_file = template.replace('[DOCUMENT_TITLE]', metadata_dict.get('title', 'Untitled'))
            
            # Replace document-content div
            document_content_pattern = r'<div id="document-content">.*?<!-- Content will be dynamically loaded here -->.*?</div>'
            html_file = re.sub(document_content_pattern, formatted_content, html_file, flags=re.DOTALL)
            
            # Write output file
            output_path = posts_html_dir / f"{slug}.html"
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_file)
                f.flush()
                os.fsync(f.fileno())  # Force write to disk
            
            print(f"Generated document HTML: {output_path}")
            return True, str(output_path)
        except Exception as e:
            print(f"❌ Failed to generate document HTML for {slug}: {e}")
            import traceback
            traceback.print_exc()
            return False, None

    def _estimate_read_time(self, text, wpm=220):
        words = len(text.split())
        mins = max(1, round(words / wpm))
        return f"{mins} min read"

    def _safe_slug(self, meta, md_path):
        # prefer frontmatter: slug -> id -> filename stem
        return (meta.get("slug") or meta.get("id") or Path(md_path).stem).strip()

    def _collect_post_record(self, md_path, metadata, body_html):
        slug = self._safe_slug(metadata, md_path)
        return {
            "id": metadata.get("id", slug),
            "title": metadata.get("title", "Untitled"),
            "slug": slug,
            "excerpt": metadata.get("excerpt", ""),
            "content": f"blog/posts/{slug}.html",
            "author": metadata.get("author", "Bradley R. Clampitt"),
            "date": metadata.get("date", ""),
            "category": metadata.get("category", "").lower().strip(),  # normalize
            "tags": metadata.get("tags", []),
            "featured": bool(metadata.get("featured", False)),
            "readTime": metadata.get("readTime") or self._estimate_read_time(body_html)
        }

    def _write_posts_json(self, records):
        # sort by date desc if present
        def _key(r): return r.get("date", "")
        records_sorted = sorted(records, key=_key, reverse=True)
        data = {"posts": records_sorted}
        with open(self.posts_json_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        print(f"📝 Updated index: {self.posts_json_file}")

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Final Blog Manager with Protected Code Blocks")
    parser.add_argument('--build', action='store_true', help='Build all blog posts')
    args = parser.parse_args()  # Fixed: Added 'parse_'
    bm = BlogManager()
    if args.build:
        bm.build_posts()
    else:
        print("Final Blog Manager with Protected Code Blocks")
        print("Use --build to rebuild all posts")

if __name__ == '__main__':
    main()
