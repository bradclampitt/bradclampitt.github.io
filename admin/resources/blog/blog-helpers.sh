#!/bin/bash
# Blog Management Helper Scripts for Bradley R. Clampitt's Portfolio
# Easy command-line tools for blog management

BLOG_ROOT="/var/www/projectmanager.test/github_v2/blog"
POSTS_MD_DIR="$BLOG_ROOT/posts.md"
POSTS_HTML_DIR="$BLOG_ROOT/posts"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to build blog (call Python script)
build_blog() {
    print_info "Building blog posts..."
    cd "$BLOG_ROOT"
    
    # Check if Python script exists
    if [ ! -f "blog-manager.py" ]; then
        print_error "blog-manager.py not found"
        return 1
    fi
    
    # Run the build
    python3 blog-manager.py --build
    if [ $? -eq 0 ]; then
        print_success "Blog built successfully!"
    else
        print_error "Blog build failed"
        return 1
    fi
}

# Function to create a new blog post
new_post() {
    local title="$1"
    local category="${2:-general}"
    
    if [ -z "$title" ]; then
        print_error "Please provide a title for the new post"
        echo "Usage: $0 new 'My Blog Post Title' [category]"
        return 1
    fi
    
    print_info "Creating new blog post: '$title'"
    cd "$BLOG_ROOT"
    
    python3 blog-manager.py --new "$title" --category "$category"
    
    echo ""
    print_success "New post created! Here's what to do next:"
    echo "1. Edit the markdown file in $POSTS_MD_DIR"
    echo "2. Add your content using Markdown syntax"
    echo "3. Run: $0 build"
    echo "4. Commit and push to GitHub"
}

# Function to open the latest post for editing
edit_latest() {
    local latest_file=$(ls -t "$POSTS_MD_DIR"/*.md 2>/dev/null | head -n1)
    
    if [ -z "$latest_file" ]; then
        print_error "No markdown files found in $POSTS_MD_DIR"
        return 1
    fi
    
    print_info "Opening latest post for editing: $(basename "$latest_file")"
    ${EDITOR:-nano} "$latest_file"
}

# Function to preview blog locally
preview_blog() {
    print_info "Starting local preview server..."
    cd "/var/www/projectmanager.test/github_v2"
    
    # Use Python's built-in HTTP server
    if command -v python3 &> /dev/null; then
        print_info "Server starting at: http://localhost:8000"
        print_info "Press Ctrl+C to stop the server"
        python3 -m http.server 8000
    else
        print_error "Python3 not found. Please install Python3 to use preview."
        return 1
    fi
}

# Function to deploy to GitHub
deploy_to_github() {
    print_info "Deploying blog to GitHub..."
    cd "/var/www/projectmanager.test/github_v2"
    
    # Build blog first
    "$BLOG_ROOT/blog-helpers.sh" build
    
    if [ $? -ne 0 ]; then
        print_error "Build failed. Aborting deployment."
        return 1
    fi
    
    # Check git status
    git status --porcelain
    if [ $? -eq 0 ]; then
        print_info "Checking for changes..."
        CHANGES=$(git status --porcelain)
        if [ -z "$CHANGES" ]; then
            print_warning "No changes to commit"
            return 0
        fi
        
        print_info "Changes detected. Ready to commit and push."
        echo "Changed files:"
        echo "$CHANGES"
        echo ""
        read -p "Do you want to commit and push these changes? (y/N): " -n 1 -r
        echo ""
        
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            git add .
            git commit -m "Update blog: $(date '+%Y-%m-%d %H:%M')"
            git push origin main
            print_success "Deployed to GitHub successfully!"
        else
            print_info "Deployment cancelled"
        fi
    else
        print_error "Not a git repository or git error"
        return 1
    fi
}

# Function to show blog statistics
show_stats() {
    print_info "Blog Statistics"
    echo "================"
    
    local md_count=$(find "$POSTS_MD_DIR" -name "*.md" 2>/dev/null | wc -l)
    local html_count=$(find "$POSTS_HTML_DIR" -name "*.html" | wc -l)
    
    echo "📝 Markdown files: $md_count"
    echo "🌐 HTML files: $html_count"
    echo ""
    
    if [ -f "$BLOG_ROOT/posts.json" ]; then
        local json_posts=$(python3 -c "import json; data=json.load(open('$BLOG_ROOT/posts.json')); print(len(data['posts']))")
        echo "📊 Posts in JSON: $json_posts"
    fi
    
    echo ""
    echo "📁 Directory structure:"
    tree -L 3 "$BLOG_ROOT" 2>/dev/null || ls -la "$BLOG_ROOT"
}

# Function to clean up HTML files
clean_html() {
    print_info "Cleaning generated HTML files..."
    rm -f "$POSTS_HTML_DIR"/*.html
    print_success "HTML files cleaned"
}

# Main function
main() {
    case "$1" in
        "build")
            build_blog
            ;;
        "new")
            new_post "$2" "$3"
            ;;
        "edit")
            edit_latest
            ;;
        "preview")
            preview_blog
            ;;
        "deploy")
            deploy_to_github
            ;;
        "stats")
            show_stats
            ;;
        "clean")
            clean_html
            ;;
        *)
            echo "Blog Management Helper Scripts"
            echo "=============================="
            echo ""
            echo "Available commands:"
            echo "  $0 build                    Build all blog posts"
            echo "  $0 new 'Title' [category]   Create new blog post"
            echo "  $0 edit                     Edit the latest post"
            echo "  $0 preview                  Start local preview server"
            echo "  $0 deploy                   Build and deploy to GitHub"
            echo "  $0 stats                    Show blog statistics"
            echo "  $0 clean                    Clean generated HTML files"
            echo ""
            echo "Examples:"
            echo "  $0 new 'My Awesome Post' magento"
            echo "  $0 build && $0 deploy"
            ;;
    esac
}

# Run main function with all arguments
main "$@"
