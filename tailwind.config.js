/** @type {import('tailwindcss').Config} */
module.exports = {
    // Narrow content globs to the generated posts, templates, and top-level HTML/MD files
    // This avoids scanning node_modules and improves build performance.
    content: [
      './*.html',
      './blog/**/*.html',
      './blog/posts.md/*.md',
      './documents/**/*.html',
      './assets/includes/*.html'
    ],
    theme: {
      extend: {},
    },
    plugins: [],
}