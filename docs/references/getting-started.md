# Getting Started Guide

Welcome! This guide will help you get up and running quickly with our development environment and workflows.

## 🎯 Quick Start Checklist

- [ ] Set up development environment
- [ ] Clone repositories and install dependencies
- [ ] Configure local services (database, cache, etc.)
- [ ] Run your first successful build
- [ ] Complete onboarding tasks

## 💻 Development Environment Setup

### Required Software

#### Essential Tools
```bash
# Node.js (LTS version recommended)
curl -fsSL https://nodejs.org/dist/v18.19.0/node-v18.19.0-linux-x64.tar.xz

# PHP 8.1+ for Magento development
sudo apt install php8.1 php8.1-cli php8.1-common php8.1-mysql php8.1-xml php8.1-curl

# Composer for PHP dependency management
curl -sS https://getcomposer.org/installer | php
sudo mv composer.phar /usr/local/bin/composer
```

#### Database Systems
```bash
# MySQL 8.0+ (for Magento)
sudo apt install mysql-server-8.0

# PostgreSQL 14+ (for other projects)
sudo apt install postgresql-14 postgresql-client-14

# Redis (for caching)
sudo apt install redis-server
```

#### Development Tools
```bash
# Git (version control)
sudo apt install git

# Docker (containerization)
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# VS Code (recommended editor)
# Download from https://code.visualstudio.com/
```

### Recommended VS Code Extensions
```json
{
  "recommendations": [
    "ms-vscode.vscode-json",
    "bradlc.vscode-tailwindcss",
    "ms-vscode.vscode-typescript-next",
    "esbenp.prettier-vscode",
    "ms-python.python",
    "ms-vscode.vscode-eslint",
    "bmewburn.vscode-intelephense-client"
  ]
}
```

## 🏗️ Project Setup

### 1. Clone Repositories
```bash
# Main project repository
git clone https://github.com/bradclampitt/projectmanager.test.git
cd projectmanager.test

# Clone additional repositories as needed
git clone https://github.com/bradclampitt/magento-modules.git
```

### 2. Environment Configuration
```bash
# Copy environment template
cp .env.example .env

# Edit configuration (use your preferred editor)
nano .env
```

#### Common Environment Variables
```env
# Database Configuration
DB_HOST=localhost
DB_PORT=3306
DB_DATABASE=magento2
DB_USERNAME=root
DB_PASSWORD=your_password

# Application Settings
APP_ENV=local
APP_DEBUG=true
APP_URL=http://localhost:8000

# Cache Configuration
REDIS_HOST=127.0.0.1
REDIS_PORT=6379
REDIS_PASSWORD=null

# Mail Configuration (for development)
MAIL_MAILER=log
MAIL_HOST=localhost
MAIL_PORT=1025
```

### 3. Install Dependencies
```bash
# Install PHP dependencies
composer install

# Install Node.js dependencies
npm install

# Install global tools
npm install -g @magento/pwa-studio-cli
```

### 4. Database Setup
```bash
# Create database
mysql -u root -p -e "CREATE DATABASE magento2;"

# Run migrations (if applicable)
php bin/magento setup:install \
  --base-url=http://localhost/ \
  --db-host=localhost \
  --db-name=magento2 \
  --db-user=root \
  --db-password=your_password \
  --admin-firstname=Admin \
  --admin-lastname=User \
  --admin-email=admin@example.com \
  --admin-user=admin \
  --admin-password=admin123 \
  --language=en_US \
  --currency=USD \
  --timezone=America/Chicago
```

### 5. Build and Start Services
```bash
# Build frontend assets
npm run build

# Start development server
npm run dev

# Or for Magento projects
bin/magento setup:static-content:deploy
bin/magento cache:flush
```

## 🔧 Development Workflow

### Daily Workflow
1. **Pull latest changes**
   ```bash
   git pull origin main
   ```

2. **Create feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make changes and commit**
   ```bash
   git add .
   git commit -m "feat: add new feature description"
   ```

4. **Push and create PR**
   ```bash
   git push origin feature/your-feature-name
   ```

### Code Standards
- **PHP**: Follow PSR-12 coding standards
- **JavaScript**: Use ESLint and Prettier configuration
- **CSS**: Use Tailwind CSS utility classes
- **Commits**: Follow conventional commit format

### Testing
```bash
# Run PHP tests
./vendor/bin/phpunit

# Run JavaScript tests
npm test

# Run linting
npm run lint

# Fix code style issues
npm run lint:fix
```

## 🚀 Common Tasks

### Magento 2 Development
```bash
# Clear cache
bin/magento cache:clean

# Reindex data
bin/magento indexer:reindex

# Deploy static content
bin/magento setup:static-content:deploy

# Enable developer mode
bin/magento deploy:mode:set developer

# Create new module
bin/magento module:status
```

### Frontend Development
```bash
# Start development server with hot reload
npm run dev

# Build for production
npm run build

# Run Tailwind CSS compilation
npm run css:build

# Optimize images
npm run images:optimize
```

### Database Operations
```bash
# Create database backup
mysqldump -u root -p magento2 > backup_$(date +%Y%m%d).sql

# Restore database
mysql -u root -p magento2 < backup_20240115.sql

# Reset database (development only)
bin/magento setup:uninstall
```

## 🐛 Troubleshooting

### Common Issues

#### Permission Issues
```bash
# Fix Magento file permissions
find . -type f -exec chmod 644 {} \;
find . -type d -exec chmod 755 {} \;
chmod u+x bin/magento
```

#### Cache Issues
```bash
# Clear all caches
bin/magento cache:flush
rm -rf generated/* var/cache/* var/page_cache/*
```

#### Composer Issues
```bash
# Clear Composer cache
composer clear-cache

# Update dependencies
composer update --with-dependencies
```

#### Node.js Issues
```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

### Getting Help
1. **Check documentation** - Start with project README and docs
2. **Search existing issues** - Look for similar problems in GitHub issues
3. **Ask team members** - Use team chat channels for quick questions
4. **Create detailed issue** - If problem persists, create GitHub issue with:
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details
   - Error messages/logs

## 📚 Learning Resources

### Essential Reading
- [Magento 2 Developer Documentation](https://devdocs.magento.com/)
- [PHP Best Practices](https://phptherightway.com/)
- [Modern JavaScript Guide](https://javascript.info/)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)

### Video Tutorials
- [Magento 2 Development Course](https://www.youtube.com/watch?v=example)
- [Modern PHP Development](https://laracasts.com/)
- [JavaScript ES6+ Features](https://www.youtube.com/watch?v=example)

### Tools and Extensions
- **Browser Extensions**: Vue DevTools, React DevTools
- **Database Tools**: phpMyAdmin, MySQL Workbench, TablePlus
- **API Testing**: Postman, Insomnia
- **Performance**: New Relic, Blackfire.io

## 🎯 Next Steps

### Week 1 Goals
- [ ] Complete environment setup
- [ ] Successfully run all projects locally
- [ ] Make first code contribution (documentation update)
- [ ] Attend team standup meetings

### Month 1 Goals
- [ ] Complete first feature implementation
- [ ] Understand codebase architecture
- [ ] Set up monitoring and debugging tools
- [ ] Contribute to code reviews

### Ongoing Learning
- [ ] Stay updated with technology changes
- [ ] Participate in team knowledge sharing
- [ ] Contribute to documentation improvements
- [ ] Explore new tools and techniques

---

*Welcome to the team! Don't hesitate to ask questions and seek help when needed. We're here to support your success.* 