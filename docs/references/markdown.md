# Markdown Reference Guide

A comprehensive reference for Markdown syntax and formatting options.

## Headers

```markdown
# H1 Header
## H2 Header
### H3 Header
#### H4 Header
##### H5 Header
###### H6 Header
```

## Text Formatting

### Basic Formatting
```markdown
**Bold text**
*Italic text*
***Bold and italic***
~~Strikethrough~~
`Inline code`
```

### Blockquotes
```markdown
> This is a blockquote
> 
> Multiple lines in blockquote
```

## Lists

### Unordered Lists
```markdown
- Item 1
- Item 2
  - Nested item
  - Another nested item
- Item 3
```

### Ordered Lists
```markdown
1. First item
2. Second item
   1. Nested numbered item
   2. Another nested item
3. Third item
```

### Task Lists
```markdown
- [x] Completed task
- [ ] Incomplete task
- [ ] Another task
```

## Links and Images

### Links
```markdown
[Link text](https://example.com)
[Link with title](https://example.com "Title")
[Reference link][ref]

[ref]: https://example.com
```

### Images
```markdown
![Alt text](image.jpg)
![Alt text](image.jpg "Title")
```

## Code

### Inline Code
```markdown
Use `git status` to check repository status.
```

### Code Blocks
````markdown
```javascript
function hello() {
    console.log("Hello, World!");
}
```
````

### Code Blocks with Language
````markdown
```php
<?php
class Example {
    public function greet($name) {
        return "Hello, " . $name;
    }
}
```
````

## Tables

```markdown
| Column 1 | Column 2 | Column 3 |
|----------|----------|----------|
| Row 1    | Data     | More     |
| Row 2    | Data     | More     |
```

### Table Alignment
```markdown
| Left | Center | Right |
|:-----|:------:|------:|
| Text | Text   | Text  |
```

## Horizontal Rules

```markdown
---
***
___
```

## Line Breaks

```markdown
End a line with two spaces  
to create a line break.

Or use a blank line

to create a paragraph break.
```

## Escaping Characters

```markdown
\*Not italic\*
\`Not code\`
\# Not a header
```

## Advanced Features

### Footnotes
```markdown
Here's a sentence with a footnote[^1].

[^1]: This is the footnote.
```

### Definition Lists
```markdown
Term 1
:   Definition 1

Term 2
:   Definition 2a
:   Definition 2b
```

### Abbreviations
```markdown
*[HTML]: Hyper Text Markup Language
*[W3C]:  World Wide Web Consortium

The HTML specification is maintained by the W3C.
```

## GitHub Flavored Markdown

### Mentions
```markdown
@username
```

### Issue References
```markdown
#123
user/repo#123
```

### Emoji
```markdown
:smile: :heart: :thumbsup:
```

### Syntax Highlighting
````markdown
```diff
- removed line
+ added line
```
````

## Best Practices

### Document Structure
1. Start with a clear H1 title
2. Use H2 for main sections
3. Use H3-H6 for subsections
4. Keep paragraphs short and focused

### Formatting Tips
- Use **bold** for important terms
- Use *italic* for emphasis
- Use `code` for technical terms
- Use > blockquotes for important notes

### Link Guidelines
- Use descriptive link text
- Avoid "click here" or "read more"
- Use reference links for repeated URLs
- Include titles for additional context

### Code Documentation
- Always specify language for code blocks
- Include comments in code examples
- Use inline code for commands and file names
- Group related code examples together

## Common Patterns

### Documentation Header
```markdown
# Project Name

Brief description of the project.

## Table of Contents
- [Installation](#installation)
- [Usage](#usage)
- [API Reference](#api-reference)
```

### API Documentation
```markdown
## GET /api/users

Returns a list of users.

### Parameters
- `limit` (integer) - Maximum number of users to return
- `offset` (integer) - Number of users to skip

### Response
```json
{
  "users": [
    {"id": 1, "name": "John Doe"}
  ]
}
```
````

### Changelog Format
```markdown
## [1.2.0] - 2023-12-01

### Added
- New feature X
- Support for Y

### Changed
- Improved performance of Z

### Fixed
- Bug in feature A
```

---

*This reference guide covers the most commonly used Markdown syntax. For more advanced features, consult the specific Markdown flavor documentation.* 