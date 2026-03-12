/** @type {import('tailwindcss').Config} */
module.exports = {
    // Narrow content globs to the generated posts, templates, and top-level HTML/MD files
    // This avoids scanning node_modules and improves build performance.
    content: [
      './blog/posts/*.html',
      './blog/posts.md/*.md',
      './blog/**/*.html',
      './*.html',
      './blog/**/*.md'
    ],
    theme: {
      extend: {},
    },
    plugins: [],
}