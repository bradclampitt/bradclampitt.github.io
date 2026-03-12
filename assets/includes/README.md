# Shared Sidebar Navigation

This directory contains shared components that are loaded dynamically into all frontend pages.

## Files

- `sidebar.html` - Contains both desktop and mobile sidebar navigation HTML

## How It Works

1. **Sidebar Loader Script** (`/assets/js/sidebar-loader.js`) automatically:
   - Fetches the sidebar HTML from `/assets/includes/sidebar.html`
   - Injects it into placeholder divs on each page
   - Highlights the active page based on current URL
   - Fixes relative paths for subdirectories (e.g., blog/posts/, documents/posts/)

## How to Update Pages

### Step 1: Add the Script Tag

Add this script tag to the `<head>` section of your HTML file (before closing `</head>`):

```html
<!-- Sidebar Loader - Loads shared sidebar navigation -->
<script src="assets/js/sidebar-loader.js"></script>
```

**Note:** For pages in subdirectories (like `blog/posts/` or `documents/posts/`), use:
```html
<script src="../../assets/js/sidebar-loader.js"></script>
```

### Step 2: Replace Hardcoded Sidebars

Replace both the desktop and mobile sidebar sections with these placeholder divs:

```html
<!-- Desktop Sidebar - Loaded dynamically -->
<div id="sidebar-desktop" class="hidden lg:flex w-64 bg-gray-700 text-white flex-col h-full flex-shrink-0">
    <!-- Sidebar will be injected here by sidebar-loader.js -->
    <div class="p-6 border-b border-gray-700">
        <h2 class="text-2xl font-semibold">Bradley C.</h2>
    </div>
    <nav class="flex-1 px-4 py-6 space-y-2">
        <div class="text-gray-400 text-sm">Loading navigation...</div>
    </nav>
</div>

<!-- Mobile Sidebar - Loaded dynamically -->
<div id="sidebar-mobile" x-show="sidebarOpen" x-transition:enter="transition ease-out duration-300" x-transition:enter-start="opacity-0 transform -translate-x-full" x-transition:enter-end="opacity-100 transform translate-x-0" x-transition:leave="transition ease-in duration-300" x-transition:leave-start="opacity-100 transform translate-x-0" x-transition:leave-end="opacity-0 transform -translate-x-full" class="lg:hidden w-64 bg-gray-700 text-white flex flex-col h-full fixed inset-y-0 left-0 z-50">
    <!-- Sidebar will be injected here by sidebar-loader.js -->
    <div class="p-6 border-b border-gray-700 flex justify-between items-center">
        <h2 class="text-2xl font-semibold pl-10">Bradley C.</h2>
        <button @click="sidebarOpen = false" class="text-gray-300 hover:text-white">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
        </button>
    </div>
    <nav class="flex-1 px-4 py-6 space-y-2">
        <div class="text-gray-400 text-sm">Loading navigation...</div>
    </nav>
</div>
```

### Step 3: Update Sidebar Content

To update the navigation links, edit **only** `/assets/includes/sidebar.html`. Changes will automatically appear on all pages.

## Page Identification

The loader identifies the current page from the URL:
- `index.html` → `index`
- `blog.html` → `blog`
- `blog/posts/article.html` → `blog` (handles subdirectories)
- `documents/posts/doc.html` → `documents` (handles subdirectories)

The active page is automatically highlighted in the sidebar.

## Benefits

✅ **Single Source of Truth** - Edit sidebar once, updates everywhere  
✅ **GitHub Pages Compatible** - Works with static hosting  
✅ **Automatic Active Page Highlighting** - No manual class management  
✅ **Relative Path Handling** - Works in subdirectories automatically  
✅ **No Build Step Required** - Pure JavaScript, works immediately  

