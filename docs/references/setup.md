# Project Setup Guide

Comprehensive guide for setting up different types of development projects, from initial scaffolding to production deployment.

## 🚀 Quick Start Templates

### Magento 2 Project Setup

#### New Magento 2 Project
```bash
# Create project directory
mkdir my-magento-project
cd my-magento-project

# Install Magento 2 via Composer
composer create-project --repository-url=https://repo.magento.com/ magento/project-community-edition .

# Set up environment file
cp app/etc/env.php.sample app/etc/env.php

# Configure database and cache settings
vim app/etc/env.php
```

#### Magento 2 Development Environment
```bash
# Enable developer mode
bin/magento deploy:mode:set developer

# Disable cache for development
bin/magento cache:disable

# Set file permissions
find var generated vendor pub/static pub/media app/etc -type f -exec chmod g+w {} +
find var generated vendor pub/static pub/media app/etc -type d -exec chmod g+ws {} +

# Create admin user
bin/magento admin:user:create \
    --admin-user=admin \
    --admin-password=admin123 \
    --admin-email=admin@example.com \
    --admin-firstname=Admin \
    --admin-lastname=User
```

### React/Next.js Project Setup

#### Create React App
```bash
# Create new React app
npx create-react-app my-react-app --template typescript
cd my-react-app

# Install additional dependencies
npm install @tailwindcss/forms @headlessui/react @heroicons/react

# Set up Tailwind CSS
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

#### Next.js Project
```bash
# Create Next.js app
npx create-next-app@latest my-next-app --typescript --tailwind --eslint --app
cd my-next-app

# Install additional packages
npm install @next/font lucide-react
npm install -D @types/node

# Set up environment variables
cp .env.local.example .env.local
```

### Node.js API Project Setup

#### Express.js API
```bash
# Create project directory
mkdir my-api-project
cd my-api-project

# Initialize package.json
npm init -y

# Install dependencies
npm install express cors helmet morgan dotenv
npm install -D nodemon @types/node @types/express typescript ts-node

# Create basic structure
mkdir src routes middleware models controllers
touch src/app.ts src/server.ts .env .gitignore
```

#### Basic Express Setup
```typescript
// src/app.ts
import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import morgan from 'morgan';
import dotenv from 'dotenv';

dotenv.config();

const app = express();

// Middleware
app.use(helmet());
app.use(cors());
app.use(morgan('combined'));
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Routes
app.get('/health', (req, res) => {
  res.json({ status: 'OK', timestamp: new Date().toISOString() });
});

export default app;
```

### Vue.js Project Setup

#### Vue 3 with Vite
```bash
# Create Vue project
npm create vue@latest my-vue-app
cd my-vue-app

# Install dependencies
npm install

# Add additional packages
npm install @vueuse/core pinia
npm install -D @types/node vite-plugin-eslint
```

## 🐳 Docker Development Setup

### Docker Compose for Full Stack

#### LAMP Stack (docker-compose.yml)
```yaml
version: '3.8'

services:
  web:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./src:/var/www/html
      - ./docker/nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./docker/nginx/sites:/etc/nginx/sites-available
    depends_on:
      - php
      - mysql

  php:
    build: ./docker/php
    volumes:
      - ./src:/var/www/html
    environment:
      - PHP_IDE_CONFIG=serverName=localhost
    depends_on:
      - mysql
      - redis

  mysql:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: root
      MYSQL_DATABASE: development
      MYSQL_USER: developer
      MYSQL_PASSWORD: password
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql
      - ./docker/mysql/init:/docker-entrypoint-initdb.d

  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  phpmyadmin:
    image: phpmyadmin/phpmyadmin
    environment:
      PMA_HOST: mysql
      PMA_USER: root
      PMA_PASSWORD: root
    ports:
      - "8080:80"
    depends_on:
      - mysql

volumes:
  mysql_data:
  redis_data:
```

#### Node.js Development Stack
```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "3000:3000"
    volumes:
      - .:/app
      - /app/node_modules
    environment:
      - NODE_ENV=development
      - CHOKIDAR_USEPOLLING=true
    depends_on:
      - postgres
      - redis

  postgres:
    image: postgres:14
    environment:
      POSTGRES_DB: development
      POSTGRES_USER: developer
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

### Dockerfile Examples

#### PHP Development Dockerfile
```dockerfile
FROM php:8.1-fpm

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    libpng-dev \
    libonig-dev \
    libxml2-dev \
    libzip-dev \
    zip \
    unzip \
    && docker-php-ext-install pdo_mysql mbstring exif pcntl bcmath gd zip

# Install Composer
COPY --from=composer:latest /usr/bin/composer /usr/bin/composer

# Set working directory
WORKDIR /var/www/html

# Copy application files
COPY . .

# Install PHP dependencies
RUN composer install --no-dev --optimize-autoloader

# Set permissions
RUN chown -R www-data:www-data /var/www/html \
    && chmod -R 755 /var/www/html

EXPOSE 9000
CMD ["php-fpm"]
```

#### Node.js Development Dockerfile
```dockerfile
FROM node:18-alpine

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy application files
COPY . .

# Build application
RUN npm run build

# Create non-root user
RUN addgroup -g 1001 -S nodejs
RUN adduser -S nextjs -u 1001

# Change ownership
RUN chown -R nextjs:nodejs /app
USER nextjs

EXPOSE 3000

CMD ["npm", "start"]
```

## 🛠️ Development Environment Configuration

### VS Code Workspace Setup

#### .vscode/settings.json
```json
{
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true,
    "source.organizeImports": true
  },
  "emmet.includeLanguages": {
    "javascript": "javascriptreact",
    "typescript": "typescriptreact"
  },
  "files.associations": {
    "*.phtml": "php"
  },
  "php.validate.executablePath": "/usr/bin/php",
  "typescript.preferences.importModuleSpecifier": "relative",
  "tailwindCSS.includeLanguages": {
    "plaintext": "html"
  }
}
```

#### .vscode/extensions.json
```json
{
  "recommendations": [
    "ms-vscode.vscode-typescript-next",
    "esbenp.prettier-vscode",
    "ms-vscode.vscode-eslint",
    "bradlc.vscode-tailwindcss",
    "bmewburn.vscode-intelephense-client",
    "ms-vscode.vscode-docker",
    "ms-vscode.vscode-json"
  ]
}
```

### Git Configuration

#### .gitignore Templates

**PHP/Magento .gitignore**
```gitignore
# IDE
.idea/
.vscode/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Dependencies
/vendor/
/node_modules/

# Environment
.env
.env.local
.env.*.local

# Magento specific
/var/*
!/var/.htaccess
/generated/*
/pub/media/*
!/pub/media/.htaccess
/pub/static/*
!/pub/static/.htaccess
/app/etc/env.php
/app/etc/config.php

# Logs
*.log
/var/log/*

# Cache
/var/cache/*
/var/page_cache/*
/var/session/*
```

**Node.js .gitignore**
```gitignore
# Dependencies
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Production builds
/build/
/dist/
/.next/
/out/

# Environment variables
.env
.env.local
.env.development.local
.env.test.local
.env.production.local

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db

# Logs
logs/
*.log

# Runtime data
pids/
*.pid
*.seed
*.pid.lock

# Coverage directory used by tools like istanbul
coverage/
.nyc_output/
```

#### Git Hooks Setup
```bash
# Create pre-commit hook
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/sh
# Run linting before commit
npm run lint
if [ $? -ne 0 ]; then
  echo "Linting failed. Please fix the issues before committing."
  exit 1
fi

# Run tests
npm test
if [ $? -ne 0 ]; then
  echo "Tests failed. Please fix the issues before committing."
  exit 1
fi
EOF

chmod +x .git/hooks/pre-commit
```

## 📦 Package Management

### NPM/Yarn Configuration

#### .npmrc
```ini
# Registry configuration
registry=https://registry.npmjs.org/

# Save exact versions
save-exact=true

# Security settings
audit-level=moderate

# Performance
prefer-offline=true
progress=true

# Development settings
fund=false
```

#### package.json Scripts
```json
{
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint",
    "lint:fix": "next lint --fix",
    "type-check": "tsc --noEmit",
    "test": "jest",
    "test:watch": "jest --watch",
    "test:coverage": "jest --coverage",
    "prepare": "husky install"
  }
}
```

### Composer Configuration

#### composer.json for PHP Projects
```json
{
  "require": {
    "php": ">=8.1",
    "ext-json": "*",
    "ext-mbstring": "*"
  },
  "require-dev": {
    "phpunit/phpunit": "^9.0",
    "friendsofphp/php-cs-fixer": "^3.0",
    "phpstan/phpstan": "^1.0"
  },
  "autoload": {
    "psr-4": {
      "App\\": "src/"
    }
  },
  "autoload-dev": {
    "psr-4": {
      "Tests\\": "tests/"
    }
  },
  "scripts": {
    "test": "phpunit",
    "cs-fix": "php-cs-fixer fix",
    "analyze": "phpstan analyse"
  }
}
```

## 🔧 Configuration Files

### ESLint Configuration

#### .eslintrc.js
```javascript
module.exports = {
  env: {
    browser: true,
    es2021: true,
    node: true,
  },
  extends: [
    'eslint:recommended',
    '@typescript-eslint/recommended',
    'next/core-web-vitals',
    'prettier',
  ],
  parser: '@typescript-eslint/parser',
  parserOptions: {
    ecmaFeatures: {
      jsx: true,
    },
    ecmaVersion: 12,
    sourceType: 'module',
  },
  plugins: ['@typescript-eslint'],
  rules: {
    '@typescript-eslint/no-unused-vars': 'error',
    '@typescript-eslint/explicit-function-return-type': 'warn',
    'prefer-const': 'error',
    'no-var': 'error',
  },
};
```

### Prettier Configuration

#### .prettierrc
```json
{
  "semi": true,
  "trailingComma": "es5",
  "singleQuote": true,
  "printWidth": 80,
  "tabWidth": 2,
  "useTabs": false,
  "bracketSpacing": true,
  "arrowParens": "avoid"
}
```

### TypeScript Configuration

#### tsconfig.json
```json
{
  "compilerOptions": {
    "target": "es5",
    "lib": ["dom", "dom.iterable", "es6"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "forceConsistentCasingInFileNames": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "node",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "plugins": [
      {
        "name": "next"
      }
    ],
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"],
      "@/components/*": ["./src/components/*"],
      "@/utils/*": ["./src/utils/*"]
    }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}
```

## 🚀 CI/CD Setup

### GitHub Actions

#### .github/workflows/ci.yml
```yaml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest

    strategy:
      matrix:
        node-version: [16.x, 18.x]

    steps:
      - uses: actions/checkout@v3

      - name: Use Node.js ${{ matrix.node-version }}
        uses: actions/setup-node@v3
        with:
          node-version: ${{ matrix.node-version }}
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Run linting
        run: npm run lint

      - name: Run type checking
        run: npm run type-check

      - name: Run tests
        run: npm test -- --coverage

      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
```

#### .github/workflows/deploy.yml
```yaml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Build application
        run: npm run build

      - name: Deploy to production
        run: |
          # Add your deployment script here
          echo "Deploying to production..."
```

## 🔒 Environment Variables

### Environment File Templates

#### .env.example
```bash
# Database
DB_HOST=localhost
DB_PORT=3306
DB_NAME=development
DB_USER=developer
DB_PASSWORD=password

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=

# API Keys
API_KEY=your_api_key_here
JWT_SECRET=your_jwt_secret_here

# External Services
STRIPE_PUBLIC_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...

# Email
MAIL_HOST=smtp.mailtrap.io
MAIL_PORT=2525
MAIL_USERNAME=
MAIL_PASSWORD=

# Application
APP_ENV=development
APP_DEBUG=true
APP_URL=http://localhost:3000
```

### Environment Validation

#### env-validation.js
```javascript
const requiredEnvVars = [
  'DB_HOST',
  'DB_NAME',
  'DB_USER',
  'DB_PASSWORD',
  'JWT_SECRET',
];

function validateEnvironment() {
  const missingVars = requiredEnvVars.filter(
    varName => !process.env[varName]
  );

  if (missingVars.length > 0) {
    console.error('Missing required environment variables:');
    missingVars.forEach(varName => console.error(`- ${varName}`));
    process.exit(1);
  }

  console.log('Environment validation passed ✓');
}

module.exports = { validateEnvironment };
```

## 📝 Documentation Setup

### README Template

#### README.md
```markdown
# Project Name

Brief description of what this project does and who it's for.

## 🚀 Getting Started

### Prerequisites

- Node.js 18+ or PHP 8.1+
- MySQL 8.0+
- Redis (optional)

### Installation

1. Clone the repository
   ```bash
   git clone https://github.com/username/project-name.git
   cd project-name
   ```

2. Install dependencies
   ```bash
   npm install
   # or
   composer install
   ```

3. Set up environment variables
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. Run migrations
   ```bash
   npm run migrate
   # or
   php artisan migrate
   ```

5. Start the development server
   ```bash
   npm run dev
   # or
   php artisan serve
   ```

## 📖 API Documentation

API documentation is available at `/docs` when running in development mode.

## 🧪 Testing

```bash
# Run all tests
npm test

# Run with coverage
npm run test:coverage

# Run specific test file
npm test -- filename.test.js
```

## 🚀 Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for deployment instructions.

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines.

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file.
```

## 🎯 Project-Specific Setups

### E-commerce Store Setup

#### Magento 2 Store Configuration
```bash
# Configure store settings
bin/magento config:set web/unsecure/base_url "http://localhost/"
bin/magento config:set web/secure/base_url "https://localhost/"

# Set up sample data
bin/magento sampledata:deploy
bin/magento setup:upgrade

# Configure payment methods
bin/magento config:set payment/checkmo/active 1
bin/magento config:set payment/banktransfer/active 1

# Set up cron jobs
bin/magento cron:install
```

### API-First Project Setup

#### OpenAPI Documentation
```yaml
openapi: 3.0.0
info:
  title: API Documentation
  version: 1.0.0
  description: Comprehensive API documentation

servers:
  - url: http://localhost:3000/api
    description: Development server

paths:
  /users:
    get:
      summary: Get all users
      responses:
        '200':
          description: Successful response
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/User'

components:
  schemas:
    User:
      type: object
      properties:
        id:
          type: integer
        name:
          type: string
        email:
          type: string
```

## ✅ Setup Checklist

After completing project setup, verify:

- [ ] Dependencies installed successfully
- [ ] Environment variables configured
- [ ] Database connection working
- [ ] Development server starts without errors
- [ ] Linting and formatting tools configured
- [ ] Git hooks set up
- [ ] CI/CD pipeline configured
- [ ] Documentation updated
- [ ] Tests running successfully
- [ ] Security configurations in place

---

*This setup guide is maintained to reflect current best practices and tools. Update as needed for new projects and technologies.* 