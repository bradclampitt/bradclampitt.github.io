---
id: confluence-style-features
title: Enhanced Blog with Confluence-Style Markdown Elements
slug: confluence-style-features
excerpt: Discover the new Confluence-style markdown features in our blog system, including info boxes, enhanced image handling, and professional content formatting.
author: Bradley R. Clampitt
date: 2025-01-01
category: tutorial
tags: ["Markdown", "Content", "Features"]
featured: true
readTime: "5 min read"
---

# Enhanced Blog with Confluence-Style Markdown Elements

Welcome to the future of technical blogging! Our blog system now supports **Confluence-style elements** that make your content more engaging, professional, and easy to read.

^ info
All Confluence-style features are now active and ready to use. These elements work seamlessly with our existing PrismJS syntax highlighting and responsive design.

## 🎯 **Info Boxes and Callouts**

Let's explore the different types of informational callouts available:

### Information Callouts
^ info
This is an **information** callout. Perfect for providing helpful context, background information, or additional details that enrich your content without interrupting the main flow.

### Warning Callouts  
! warning
**Important:** This is a **warning** callout. Use these to highlight crucial information, potential pitfalls, or things users should be careful about. They grab attention with their yellow coloring.

### Success Callouts
✓ success
**Excellent!** This is a **success** callout. Great for celebrating achievements, confirming completed tasks, or highlighting positive outcomes. The green color provides positive reinforcement.

### Error Callouts
✗ error
**Attention required:** This is an **error** callout. Use these to explain what went wrong, common mistakes to avoid, or critical issues that need immediate attention.

### Tip Callouts
💡 tip
**Pro tip:** This is a **tip** callout. Perfect for sharing shortcuts, best practices, insider knowledge, or helpful hints that make your content more valuable.

## 🖼️ **Enhanced Image Capabilities**

![Confluence-style features overview](placeholder:overview-diagram){: .center}

### Image Placeholders

Our system now supports **image placeholders** for content planning:

<!-- Centered group of placeholders -->
![Dashboard screenshot](placeholder:dashboard-ui)
![Code editor view](placeholder:editor-screenshot)
![Mobile responsive view](placeholder:mobile-layout)

<!-- Small inline placeholder (thumbnail) -->
![User interface example](placeholder:ui-components){: .small}

Each placeholder above shows a simple planning block. Replace them with final images when you're ready. Below are examples showing alignment and wrapping behavior.

💡 tip
**Content planning tip:** Use placeholders to plan your visuals before creating final images. They provide visual context during writing and can be easily replaced later.

### Image Alignment Options

Here's how **left-aligned images** work with text wrapping:

![Documentation example](placeholder:doc-example){: .left}

When you use left alignment, the image floats to the left side and the paragraph text wraps beside it. This is ideal for shorter images placed alongside explanatory text.

Example: the image below is left-aligned and the following paragraph demonstrates how text will wrap around it. Note how on narrow screens the image will stack above the content.

![Documentation example](placeholder:doc-example){: .left}

Lorem ipsum dolor sit amet, consectetur adipiscing elit. Integer nec odio. Praesent libero. Sed cursus ante dapibus diam. Sed nisi. Nulla quis sem at nibh elementum imperdiet. Duis sagittis ipsum. Praesent mauris. Fusce nec tellus sed augue semper porta. Mauris massa.

This paragraph continues the example and will flow alongside the left-aligned placeholder on wider screens, demonstrating natural text wrapping.

Now a right-aligned example. The image will float to the right and text will wrap on its left side.

![Workflow diagram](placeholder:workflow-graph){: .right}

Pro tip: place the image at the beginning of the paragraph you want to wrap around to control how the flow behaves.

✓ success
**Layout achievement:** Your images now have professional placement options that rival Confluence's visual presentation.

## 🚀 **Mixed Content Example**

Let's see how all these elements work together:

```javascript
// Example: Enhanced component with proper styling
const InfoBox = ({ type, children }) => {
  const styles = {
    'info': 'border-blue-400 bg-blue-50',
    'warning': 'border-yellow-400 bg-yellow-50',
    'success': 'border-green-400 bg-green-50',
    'error': 'border-red-400 bg-red-50',
    'tip': 'border-indigo-400 bg-indigo-50'
  };
  
  return (
    <div className={`border-l-4 p-4 rounded-r-lg ${styles[type]}`}>
      {children}
    </div>
  );
};
```

^ info
**Technical note:** The code above demonstrates how our blog's styling system works under the hood. All Confluence-style elements use consistent Tailwind CSS classes.

! warning
**Performance consideration:** While these features add visual appeal, they're lightweight and won't impact page load times.

### Mobile Responsiveness

![Mobile layout preview](placeholder:mobile-preview){: .center}

### Real image examples (wrapping vs non-wrapping)

Below are examples using a real image shipped with the repository at `blog/posts/media/images/placeholder_image.png`.

Left-aligned (with caption):
![Left captioned image](media/images/placeholder_image.png){: .left}

this is some jibberish text in between images to see if it helps.
this is some jibberish text in between images to see if it helps.
this is some jibberish text in between images to see if it helps.
this is some jibberish text in between images to see if it helps.
this is some jibberish text in between images to see if it helps.
this is some jibberish text in between images to see if it helps.

Right-aligned (no caption):

![ ](media/images/placeholder_image.png){: .right}

this is some jibberish text in between images to see if it helps.
this is some jibberish text in between images to see if it helps.
this is some jibberish text in between images to see if it helps.
this is some jibberish text in between images to see if it helps.
this is some jibberish text in between images to see if it helps.
this is some jibberish text in between images to see if it helps.
this is some jibberish text in between images to see if it helps.
this is some jibberish text in between images to see if it helps.
this is some jibberish text in between images to see if it helps.

Centered (no wrapping):

![Centered image](media/images/placeholder_image.png){: .center}

this is some jibberish text in between images to see if it helps.
this is some jibberish text in between images to see if it helps.
this is some jibberish text in between images to see if it helps.
this is some jibberish text in between images to see if it helps.
this is some jibberish text in between images to see if it helps.
this is some jibberish text in between images to see if it helps.
this is some jibberish text in between images to see if it helps.

Small thumbnail (inline):

![Thumbnail](media/images/placeholder_image.png){: .small}

✓ success
**Mobile optimized:** All Confluence-style elements are fully responsive and work perfectly on mobile devices.

## 📊 **Usage Guidelines**

### Best Practices

^ info
**Recommendation:** Use info boxes sparingly. They're most effective when they provide genuinely helpful additional information.

! warning
**Avoid overuse:** Too many warning boxes can make your content feel alarmist. Reserve them for truly important cautions.

✓ success
**Quality tip:** Success boxes work best when acknowledging reader achievements or celebrating milestones in your content.

💡 tip
**Pro tip:** Mix different callout types strategically to create visually engaging and informative content flows.

### Content Planning

When planning your blog posts:

1. **Identify key points** that would benefit from callouts
2. **Plan your visuals** using image placeholders
3. **Test alignment** with different image positioning
4. **Review on mobile** to ensure responsive behavior

![Content planning checklist](placeholder:planning-checklist){: .small}

✗ error
**Common mistake:** Don't use placeholder images in your final posts - always replace them with real visuals.

## 🎉 **Getting Started**

Ready to enhance your blog posts? Here's how to add these features:

### Basic Callout Syntax
Here are live examples of each callout type:

^ info
This is an **information** callout. Perfect for providing helpful context, background information, or additional details that enrich your content without interrupting the main flow.

! warning
**Important:** This is a **warning** callout. Use this for critical information, important caveats, or potential issues that readers need to be aware of. Great for highlighting gotchas or breaking changes.

✓ success
**Success!** This is a **success** callout. Perfect for completed tasks, achievements, or positive outcomes. Use this to celebrate milestones or confirm that something has been completed successfully.

✗ error
**Error:** This is an **error** callout. Essential for highlighting problems, failures, or things that went wrong. This helps readers understand common pitfalls and learn from failures.

💡 tip
**Pro tip:** This is a **tip** callout. Excellent for sharing practical advice, shortcuts, or helpful hints that can improve the reader's workflow or understanding. Use this for expert-level insights.

#### Markdown Syntax Reference
```markdown
^ info
Your informational content here

! warning
Your warning content here

check success
Your success content here

x error
Your error content here

tip
Your tip content here
```

### Image Placeholder Syntax
```markdown
![Description](placeholder:unique-id)
![Small image](placeholder:tiny-icon){: .small}
![Centered image](placeholder:hero-image){: .center}
```

✓ success
**You're all set!** Your blog now has professional Confluence-style capabilities that will significantly enhance your content presentation and reader engagement.

---

**Transform your technical blog with these powerful Confluence-style features and create content that stands out in the developer community!**

---

> **[**Note**]:** This is a comment line.

- Bulletin
  - Child Bullet

---

## Collapisble Section in Markdown

### Customize Clicakble Text

<details>
  <summary><i>Wow, so fancy</i></summary>
  <b>WOW, SO BOLD</b>
</details>

---

### Nested Collapsible Sections

<details>
  <summary>Section A</summary>
    <details>
      <summary>Section A.B</summary>
        <details>
          <summary>Section A.B.C</summary>
            <details>
              <summary>Section A.B.C.D</summary>
                Done!
            </details>
        </details>
    </details>
</details>

---

### With a Table

<details>

<summary>Click me</summary>

| Header 1 | Header 2 |
| -------- | -------- |
| Row 1    | Row 1    |
| Row 2    | Row 2    |
  
</details>

---

### Code Highlighting.

<details>
<summary>Contents of <code>file.txt</code></summary>

```
[File contents inside code block]
```
</details>

---

### Code/Markdown

<details>
  <summary>Click me</summary>
  
  ### Heading
  1. Foo
  2. Bar
     * Baz
     * Qux

  ### Some Javascript
  ```js
  function logSomething(something) {
    console.log('Something', something);
  }
  ```
</details>

---

**Embeddings**

!embed https://www.youtube.com/watch?v=dQw4w9WgXcQ "Launch teaser"
!embed[simple] https://docs.readme.com/rdmd/docs/embeds "RDMD Embed Docs"
!embed[card] https://example.com

---

### Tasks Lists

- [ ] Here is a Task
    - [x] Here is a sub task completed
- [x] Here is another task completed
- [ ] Another task
- [ ] And Another Task
- [x] And anotehr task (completed)
- [ ] And another one that is not.

---

## Tabs

::: tabs
@tab Overview
High-level summary…

@tab[badge=New icon=🚀] Deep Dive
Long-form explanation with markdown.
Secondline
3rd Line
4th Line
:::

---

## Columns

::: columns
@column "Problem"
Explain the challenge.
@column[span=2] "Solution"
wrap-up content here.
:::

---

## Cards

::: cards
@card[link=https://example.com icon=✨ accent=blue] Example Card
Supports full markdown in the body.
@card Another Card
No link? it will render as a static card.
:::

---

## Quotes

::: quote "Clarity" - Jane Doe
Great quotes deserve the spotlight.
:::


More to come....
