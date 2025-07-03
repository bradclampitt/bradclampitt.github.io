# Blog System Documentation

This is a JSON-based static blog system for Bradley R. Clampitt's portfolio website. It provides dynamic functionality while maintaining compatibility with static hosting platforms like GitHub Pages.

## System Overview

The blog system consists of:
- **JSON Data Store** (`posts.json`) - Contains all blog post metadata
- **Individual Post Files** - HTML files for each blog post
- **Dynamic Blog Index** (`blog.html`) - Main blog page with filtering and search
- **Template System** - Reusable templates for creating new posts

## File Structure

```
blog/
├── posts.json              # Blog posts metadata
├── post-template.html      # Template for creating new posts
├── README.md              # This documentation
└── posts/
    ├── post-slug.html     # Individual blog post pages
    └── ...
```

## Adding New Blog Posts

### Step 1: Add Post Metadata to posts.json

Add a new post object to the `posts` array in `posts.json`:

```json
{
  "id": "unique-post-id",
  "title": "Your Blog Post Title",
  "slug": "url-friendly-slug",
  "excerpt": "Brief description of the post content...",
  "content": "blog/posts/your-post-slug.html",
  "author": "Bradley R. Clampitt",
  "date": "YYYY-MM-DD",
  "category": "magento|devops|tutorials|aws|security",
  "tags": ["Tag1", "Tag2", "Tag3"],
  "featured": false,
  "readTime": "X min read"
}
```

### Step 2: Create the Blog Post HTML File

1. Copy `post-template.html` to `posts/your-post-slug.html`
2. Replace `[POST_TITLE]` in the title tag
3. Update the header section with your post details
4. Add your content in the article body

### Step 3: Update Navigation Paths

Ensure all navigation links in your post file have the correct relative paths:
- `../../blog.html` - Back to blog
- `../../index.html` - Home page
- `../../experience.html` - Experience page
- `../../portfolio.html` - Portfolio page

## Categories and Tags

### Available Categories:
- `magento` - Magento 2 related content
- `devops` - DevOps, infrastructure, automation
- `tutorials` - Step-by-step guides and tutorials
- `aws` - Amazon Web Services content
- `security` - Security-related topics

### Tag Color Coding:
The system automatically applies color coding to tags based on technology:
- **Purple**: Magento 2
- **Orange**: AWS
- **Blue**: Docker
- **Green**: DevOps
- **Indigo**: PHP
- **Pink**: Development
- And many more...

## Features

### Search Functionality
- Real-time search through post titles, excerpts, and tags
- Case-insensitive matching
- Instant results as you type

### Category Filtering
- Filter posts by category using the tab system
- Dynamic post count updates
- Maintains search query when switching categories

### Responsive Design
- Mobile-friendly layout
- Optimized for all screen sizes
- Touch-friendly navigation

### SEO Optimized
- Semantic HTML structure
- Proper meta tags
- Clean URLs for individual posts

## Customization

### Adding New Categories
1. Add the category to the filter buttons in `blog.html`
2. Update the `getCategoryColor()` function with appropriate styling
3. Add the category to this documentation

### Modifying Post Layout
- Edit `post-template.html` for new posts
- Update existing posts individually as needed
- Maintain consistent styling with Tailwind CSS classes

### Extending Functionality
The system uses Alpine.js for interactivity. Key functions:
- `blogApp()` - Main application logic
- `loadPosts()` - Fetches post data from JSON
- `filterPosts()` - Handles search and category filtering
- `formatDate()` - Formats post dates
- `getCategoryColor()` - Returns category styling
- `getTagColor()` - Returns tag styling

## Best Practices

### Content Guidelines
- Keep excerpts between 100-200 characters
- Use descriptive, SEO-friendly titles
- Include relevant tags for discoverability
- Maintain consistent formatting in post content

### Technical Guidelines
- Always test new posts locally before publishing
- Ensure all relative links work correctly
- Optimize images and code blocks for performance
- Follow accessibility best practices

### Maintenance
- Regularly review and update post metadata
- Keep the JSON file properly formatted
- Monitor for broken links in post content
- Update copyright dates in footers

## Troubleshooting

### Posts Not Appearing
- Check JSON syntax in `posts.json`
- Verify the post HTML file exists at the specified path
- Ensure the post date format is correct (YYYY-MM-DD)

### Broken Links
- Verify relative paths in navigation
- Check that CSS and JS files are accessible
- Ensure image paths are correct

### Styling Issues
- Confirm Tailwind CSS classes are available
- Check for conflicting CSS rules
- Verify Alpine.js is loading correctly

## Future Enhancements

Potential improvements to consider:
- RSS feed generation
- Social sharing buttons
- Comment system integration (Disqus, GitHub Issues)
- Related posts functionality
- Post analytics
- Dark mode support
- Print-friendly styling

## Support

For questions or issues with the blog system, refer to:
- This documentation
- Tailwind CSS documentation for styling
- Alpine.js documentation for interactivity
- MDN Web Docs for HTML/CSS/JavaScript reference 