# Technical Reference Guide

## Table of Contents
1. [API Reference](#api-reference)
2. [Configuration Reference](#configuration-reference)
3. [Command Line Reference](#command-line-reference)
4. [Database Schema Reference](#database-schema-reference)
5. [Environment Variables](#environment-variables)
6. [Error Codes](#error-codes)
7. [HTTP Status Codes](#http-status-codes)
8. [Security Headers](#security-headers)
9. [Performance Metrics](#performance-metrics)
10. [File Structure](#file-structure)
11. [Coding Standards](#coding-standards)
12. [Quick Reference](#quick-reference)

## API Reference

### Authentication Endpoints

#### POST /api/auth/login
**Description**: Authenticate user and return JWT token

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "password123",
  "remember": true
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "user": {
      "id": 1,
      "name": "John Doe",
      "email": "user@example.com",
      "role": "admin"
    },
    "expires_at": "2024-12-31T23:59:59Z"
  }
}
```

**Error Responses**:
- `401`: Invalid credentials
- `422`: Validation errors
- `429`: Too many login attempts

#### POST /api/auth/logout
**Description**: Invalidate current JWT token

**Headers**:
```
Authorization: Bearer {token}
```

**Response**:
```json
{
  "success": true,
  "message": "Successfully logged out"
}
```

#### POST /api/auth/refresh
**Description**: Refresh JWT token

**Headers**:
```
Authorization: Bearer {token}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "expires_at": "2024-12-31T23:59:59Z"
  }
}
```

### User Management Endpoints

#### GET /api/users
**Description**: Retrieve paginated list of users

**Query Parameters**:
- `page` (integer): Page number (default: 1)
- `per_page` (integer): Items per page (default: 15, max: 100)
- `search` (string): Search term for name/email
- `role` (string): Filter by user role
- `status` (string): Filter by status (active/inactive)
- `sort` (string): Sort field (name, email, created_at)
- `order` (string): Sort order (asc/desc)

**Response**:
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "John Doe",
      "email": "john@example.com",
      "role": "admin",
      "status": "active",
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ],
  "meta": {
    "current_page": 1,
    "per_page": 15,
    "total": 100,
    "last_page": 7
  }
}
```

#### POST /api/users
**Description**: Create new user

**Request Body**:
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "password123",
  "password_confirmation": "password123",
  "role": "user",
  "status": "active"
}
```

**Validation Rules**:
- `name`: required, string, max:255
- `email`: required, email, unique:users
- `password`: required, string, min:8, confirmed
- `role`: required, in:admin,user,moderator
- `status`: required, in:active,inactive

#### PUT /api/users/{id}
**Description**: Update existing user

**Request Body**:
```json
{
  "name": "John Doe Updated",
  "email": "john.updated@example.com",
  "role": "admin",
  "status": "active"
}
```

#### DELETE /api/users/{id}
**Description**: Delete user (soft delete)

**Response**:
```json
{
  "success": true,
  "message": "User deleted successfully"
}
```

### Content Management Endpoints

#### GET /api/posts
**Description**: Retrieve paginated list of posts

**Query Parameters**:
- `page` (integer): Page number
- `per_page` (integer): Items per page
- `status` (string): Filter by status (published/draft/archived)
- `category` (integer): Filter by category ID
- `author` (integer): Filter by author ID
- `search` (string): Search in title/content
- `sort` (string): Sort field (title, created_at, updated_at)
- `order` (string): Sort order (asc/desc)

#### POST /api/posts
**Description**: Create new post

**Request Body**:
```json
{
  "title": "Post Title",
  "slug": "post-title",
  "content": "Post content here...",
  "excerpt": "Short excerpt",
  "status": "published",
  "category_id": 1,
  "tags": ["tag1", "tag2"],
  "meta_title": "SEO Title",
  "meta_description": "SEO Description",
  "featured_image": "image.jpg",
  "published_at": "2024-01-01T00:00:00Z"
}
```

### File Upload Endpoints

#### POST /api/upload
**Description**: Upload single file

**Request**: Multipart form data
- `file`: File to upload
- `folder`: Target folder (optional)
- `public`: Make file public (boolean, optional)

**Response**:
```json
{
  "success": true,
  "data": {
    "id": 1,
    "filename": "document.pdf",
    "original_name": "My Document.pdf",
    "path": "/storage/uploads/2024/01/document.pdf",
    "url": "https://example.com/storage/uploads/2024/01/document.pdf",
    "size": 1024000,
    "mime_type": "application/pdf",
    "uploaded_at": "2024-01-01T00:00:00Z"
  }
}
```

#### POST /api/upload/multiple
**Description**: Upload multiple files

**Request**: Multipart form data
- `files[]`: Array of files to upload
- `folder`: Target folder (optional)

## Configuration Reference

### Application Configuration

#### config/app.php
```php
return [
    'name' => env('APP_NAME', 'Laravel'),
    'env' => env('APP_ENV', 'production'),
    'debug' => env('APP_DEBUG', false),
    'url' => env('APP_URL', 'http://localhost'),
    'timezone' => 'UTC',
    'locale' => 'en',
    'fallback_locale' => 'en',
    'faker_locale' => 'en_US',
    'key' => env('APP_KEY'),
    'cipher' => 'AES-256-CBC',
];
```

#### config/database.php
```php
'connections' => [
    'mysql' => [
        'driver' => 'mysql',
        'host' => env('DB_HOST', '127.0.0.1'),
        'port' => env('DB_PORT', '3306'),
        'database' => env('DB_DATABASE', 'forge'),
        'username' => env('DB_USERNAME', 'forge'),
        'password' => env('DB_PASSWORD', ''),
        'charset' => 'utf8mb4',
        'collation' => 'utf8mb4_unicode_ci',
        'options' => [
            PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
            PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
            PDO::ATTR_EMULATE_PREPARES => false,
        ],
    ],
];
```

#### config/cache.php
```php
'stores' => [
    'redis' => [
        'driver' => 'redis',
        'connection' => 'cache',
        'lock_connection' => 'default',
    ],
    'file' => [
        'driver' => 'file',
        'path' => storage_path('framework/cache/data'),
    ],
];
```

### Web Server Configuration

#### Nginx Configuration
```nginx
server {
    listen 80;
    listen [::]:80;
    server_name example.com www.example.com;
    root /var/www/html/public;
    index index.php index.html;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;

    # Main location block
    location / {
        try_files $uri $uri/ /index.php?$query_string;
    }

    # PHP processing
    location ~ \.php$ {
        fastcgi_pass unix:/var/run/php/php8.1-fpm.sock;
        fastcgi_param SCRIPT_FILENAME $realpath_root$fastcgi_script_name;
        include fastcgi_params;
        fastcgi_hide_header X-Powered-By;
    }

    # Static assets caching
    location ~* \.(css|js|jpg|jpeg|png|gif|ico|svg|woff|woff2)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Deny access to sensitive files
    location ~ /\. {
        deny all;
    }
}
```

#### Apache Configuration
```apache
<VirtualHost *:80>
    ServerName example.com
    ServerAlias www.example.com
    DocumentRoot /var/www/html/public
    
    <Directory /var/www/html/public>
        AllowOverride All
        Require all granted
    </Directory>
    
    # Security headers
    Header always set X-Frame-Options "SAMEORIGIN"
    Header always set X-Content-Type-Options "nosniff"
    Header always set X-XSS-Protection "1; mode=block"
    
    # Compression
    LoadModule deflate_module modules/mod_deflate.so
    <Location />
        SetOutputFilter DEFLATE
    </Location>
    
    ErrorLog ${APACHE_LOG_DIR}/error.log
    CustomLog ${APACHE_LOG_DIR}/access.log combined
</VirtualHost>
```

## Command Line Reference

### Artisan Commands

#### Application Management
```bash
# Generate application key
php artisan key:generate

# Clear all caches
php artisan optimize:clear

# Cache configuration
php artisan config:cache

# Cache routes
php artisan route:cache

# Cache views
php artisan view:cache

# Enable maintenance mode
php artisan down --message="Maintenance in progress"

# Disable maintenance mode
php artisan up
```

#### Database Commands
```bash
# Run migrations
php artisan migrate

# Rollback migrations
php artisan migrate:rollback

# Reset database
php artisan migrate:reset

# Refresh database with seeders
php artisan migrate:refresh --seed

# Check migration status
php artisan migrate:status

# Create new migration
php artisan make:migration create_users_table

# Create new seeder
php artisan make:seeder UserSeeder

# Run specific seeder
php artisan db:seed --class=UserSeeder
```

#### Queue Management
```bash
# Process queue jobs
php artisan queue:work

# Process queue with timeout
php artisan queue:work --timeout=60

# Process specific queue
php artisan queue:work --queue=high,default

# List failed jobs
php artisan queue:failed

# Retry failed job
php artisan queue:retry 1

# Retry all failed jobs
php artisan queue:retry all

# Clear failed jobs
php artisan queue:flush
```

#### Code Generation
```bash
# Create controller
php artisan make:controller UserController

# Create model with migration
php artisan make:model User -m

# Create resource controller
php artisan make:controller UserController --resource

# Create API resource controller
php artisan make:controller UserController --api

# Create middleware
php artisan make:middleware AuthMiddleware

# Create request validation
php artisan make:request UserRequest

# Create job
php artisan make:job ProcessUser

# Create event
php artisan make:event UserRegistered

# Create listener
php artisan make:listener SendWelcomeEmail
```

### Composer Commands
```bash
# Install dependencies
composer install

# Install production dependencies only
composer install --no-dev --optimize-autoloader

# Update dependencies
composer update

# Update specific package
composer update vendor/package

# Add new package
composer require vendor/package

# Add development package
composer require --dev vendor/package

# Remove package
composer remove vendor/package

# Dump autoloader
composer dump-autoload

# Show installed packages
composer show

# Validate composer.json
composer validate
```

### NPM/Yarn Commands
```bash
# Install dependencies
npm install
yarn install

# Install production dependencies
npm ci --production
yarn install --production

# Add package
npm install package-name
yarn add package-name

# Add development package
npm install --save-dev package-name
yarn add --dev package-name

# Remove package
npm uninstall package-name
yarn remove package-name

# Update packages
npm update
yarn upgrade

# Run scripts
npm run dev
yarn dev

# Build for production
npm run build
yarn build

# Audit packages
npm audit
yarn audit
```

### Docker Commands
```bash
# Build image
docker build -t app-name .

# Run container
docker run -d -p 8000:80 app-name

# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# Execute command in container
docker-compose exec app bash

# Rebuild services
docker-compose up -d --build

# Scale services
docker-compose up -d --scale worker=3
```

## Database Schema Reference

### Users Table
```sql
CREATE TABLE users (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    email_verified_at TIMESTAMP NULL,
    password VARCHAR(255) NOT NULL,
    role ENUM('admin', 'user', 'moderator') DEFAULT 'user',
    status ENUM('active', 'inactive', 'suspended') DEFAULT 'active',
    avatar VARCHAR(255) NULL,
    last_login_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP NULL,
    
    INDEX idx_email (email),
    INDEX idx_role (role),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
);
```

### Posts Table
```sql
CREATE TABLE posts (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    slug VARCHAR(255) NOT NULL UNIQUE,
    content LONGTEXT NOT NULL,
    excerpt TEXT NULL,
    status ENUM('draft', 'published', 'archived') DEFAULT 'draft',
    author_id BIGINT UNSIGNED NOT NULL,
    category_id BIGINT UNSIGNED NULL,
    featured_image VARCHAR(255) NULL,
    meta_title VARCHAR(255) NULL,
    meta_description TEXT NULL,
    view_count INT UNSIGNED DEFAULT 0,
    published_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP NULL,
    
    FOREIGN KEY (author_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL,
    INDEX idx_slug (slug),
    INDEX idx_status (status),
    INDEX idx_author (author_id),
    INDEX idx_category (category_id),
    INDEX idx_published_at (published_at),
    FULLTEXT idx_search (title, content)
);
```

### Categories Table
```sql
CREATE TABLE categories (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(255) NOT NULL UNIQUE,
    description TEXT NULL,
    parent_id BIGINT UNSIGNED NULL,
    sort_order INT DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (parent_id) REFERENCES categories(id) ON DELETE SET NULL,
    INDEX idx_slug (slug),
    INDEX idx_parent (parent_id),
    INDEX idx_active (is_active)
);
```

## Environment Variables

### Core Application
```bash
# Application
APP_NAME="My Application"
APP_ENV=production
APP_KEY=base64:generated-key-here
APP_DEBUG=false
APP_URL=https://example.com

# Database
DB_CONNECTION=mysql
DB_HOST=127.0.0.1
DB_PORT=3306
DB_DATABASE=my_database
DB_USERNAME=my_user
DB_PASSWORD=secure_password

# Cache
CACHE_DRIVER=redis
SESSION_DRIVER=redis
QUEUE_CONNECTION=redis

# Redis
REDIS_HOST=127.0.0.1
REDIS_PASSWORD=null
REDIS_PORT=6379

# Mail
MAIL_MAILER=smtp
MAIL_HOST=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_ENCRYPTION=tls
MAIL_FROM_ADDRESS=noreply@example.com
MAIL_FROM_NAME="${APP_NAME}"

# AWS S3
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_DEFAULT_REGION=us-east-1
AWS_BUCKET=your-bucket-name

# JWT
JWT_SECRET=your-jwt-secret
JWT_TTL=1440
JWT_REFRESH_TTL=20160

# Social Login
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
FACEBOOK_CLIENT_ID=your-facebook-client-id
FACEBOOK_CLIENT_SECRET=your-facebook-client-secret

# Analytics
GOOGLE_ANALYTICS_ID=GA-XXXXXXXXX
```

## Error Codes

### Application Error Codes
| Code | Description | HTTP Status |
|------|-------------|-------------|
| 1000 | General application error | 500 |
| 1001 | Database connection failed | 500 |
| 1002 | Configuration error | 500 |
| 1003 | Service unavailable | 503 |
| 2000 | Authentication required | 401 |
| 2001 | Invalid credentials | 401 |
| 2002 | Token expired | 401 |
| 2003 | Token invalid | 401 |
| 2004 | Account suspended | 403 |
| 2005 | Insufficient permissions | 403 |
| 3000 | Validation failed | 422 |
| 3001 | Required field missing | 422 |
| 3002 | Invalid format | 422 |
| 3003 | Duplicate entry | 422 |
| 4000 | Resource not found | 404 |
| 4001 | User not found | 404 |
| 4002 | Post not found | 404 |
| 5000 | Rate limit exceeded | 429 |
| 5001 | Upload limit exceeded | 413 |
| 5002 | File type not allowed | 415 |

### Database Error Codes
| MySQL Code | Description |
|------------|-------------|
| 1045 | Access denied for user |
| 1049 | Unknown database |
| 1062 | Duplicate entry for key |
| 1146 | Table doesn't exist |
| 1264 | Out of range value |
| 1406 | Data too long for column |

## HTTP Status Codes

### Success Codes (2xx)
- **200 OK**: Request successful
- **201 Created**: Resource created successfully
- **202 Accepted**: Request accepted for processing
- **204 No Content**: Request successful, no content returned

### Client Error Codes (4xx)
- **400 Bad Request**: Invalid request syntax
- **401 Unauthorized**: Authentication required
- **403 Forbidden**: Access denied
- **404 Not Found**: Resource not found
- **405 Method Not Allowed**: HTTP method not supported
- **409 Conflict**: Resource conflict
- **422 Unprocessable Entity**: Validation failed
- **429 Too Many Requests**: Rate limit exceeded

### Server Error Codes (5xx)
- **500 Internal Server Error**: General server error
- **502 Bad Gateway**: Invalid response from upstream
- **503 Service Unavailable**: Service temporarily unavailable
- **504 Gateway Timeout**: Upstream server timeout

## Security Headers

### Recommended Security Headers
```
X-Frame-Options: SAMEORIGIN
X-Content-Type-Options: nosniff
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000; includeSubDomains
Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: geolocation=(), microphone=(), camera=()
```

### CORS Headers
```
Access-Control-Allow-Origin: https://example.com
Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
Access-Control-Allow-Headers: Content-Type, Authorization, X-Requested-With
Access-Control-Max-Age: 86400
```

## Performance Metrics

### Response Time Targets
- **API Endpoints**: < 200ms (95th percentile)
- **Web Pages**: < 1s (First Contentful Paint)
- **Database Queries**: < 100ms (average)
- **File Uploads**: < 5s (for files up to 10MB)

### Resource Limits
- **Memory Usage**: < 512MB per process
- **CPU Usage**: < 80% average
- **Disk I/O**: < 1000 IOPS
- **Network Bandwidth**: < 100Mbps

### Caching TTL
- **Static Assets**: 1 year
- **API Responses**: 5 minutes
- **Database Queries**: 1 hour
- **User Sessions**: 2 hours

## File Structure

### Laravel Application Structure
```
project/
├── app/
│   ├── Console/
│   │   ├── Http/
│   │   │   ├── Controllers/
│   │   │   ├── Middleware/
│   │   │   └── Requests/
│   │   ├── Models/
│   │   ├── Providers/
│   │   └── Services/
│   ├── bootstrap/
│   ├── config/
│   ├── database/
│   │   ├── migrations/
│   │   ├── seeders/
│   │   └── factories/
│   ├── public/
│   ├── resources/
│   │   ├── views/
│   │   ├── css/
│   │   └── js/
│   ├── routes/
│   ├── storage/
│   │   ├── app/
│   │   ├── framework/
│   │   └── logs/
│   ├── tests/
│   └── vendor/
```

### Frontend Structure
```
resources/
├── js/
│   ├── components/
│   ├── pages/
│   ├── utils/
│   └── app.js
├── css/
│   ├── components/
│   ├── base/
│   └── app.css
└── views/
    ├── layouts/
    ├── components/
    └── pages/
```

## Coding Standards

### PHP Coding Standards (PSR-12)
```php
<?php

declare(strict_types=1);

namespace App\Http\Controllers;

use App\Models\User;
use Illuminate\Http\Request;
use Illuminate\Http\JsonResponse;

class UserController extends Controller
{
    public function index(Request $request): JsonResponse
    {
        $users = User::query()
            ->when($request->search, function ($query, $search) {
                return $query->where('name', 'like', "%{$search}%");
            })
            ->paginate($request->per_page ?? 15);

        return response()->json([
            'success' => true,
            'data' => $users,
        ]);
    }
}
```

### JavaScript Coding Standards (ES6+)
```javascript
// Use const/let instead of var
const API_BASE_URL = '/api';
let currentUser = null;

// Use arrow functions
const fetchUsers = async (params = {}) => {
    try {
        const response = await fetch(`${API_BASE_URL}/users`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${getToken()}`,
            },
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('Failed to fetch users:', error);
        throw error;
    }
};

// Use destructuring
const { data: users, meta } = await fetchUsers();
```

### CSS/SCSS Standards
```scss
// Use BEM methodology
.user-card {
    padding: 1rem;
    border: 1px solid #e5e7eb;
    border-radius: 0.5rem;
    
    &__header {
        display: flex;
        justify-content: space-between;
        margin-bottom: 1rem;
    }
    
    &__title {
        font-size: 1.25rem;
        font-weight: 600;
        color: #374151;
    }
    
    &--featured {
        border-color: #3b82f6;
        background-color: #eff6ff;
    }
}
```

## Quick Reference

### Common Artisan Commands
```bash
# Most used commands
php artisan serve                    # Start development server
php artisan make:controller Name     # Create controller
php artisan make:model Name -m       # Create model with migration
php artisan migrate                  # Run migrations
php artisan tinker                   # Interactive shell
php artisan route:list               # List all routes
php artisan cache:clear              # Clear application cache
php artisan config:clear             # Clear config cache
```

### Git Workflow
```bash
# Feature branch workflow
git checkout -b feature/new-feature
git add .
git commit -m "feat: add new feature"
git push origin feature/new-feature
# Create pull request
git checkout main
git pull origin main
git branch -d feature/new-feature
```

### MySQL Quick Commands
```sql
-- Common queries
SHOW DATABASES;
USE database_name;
SHOW TABLES;
DESCRIBE table_name;
SHOW PROCESSLIST;
SHOW VARIABLES LIKE 'max_connections';

-- Performance queries
SHOW ENGINE INNODB STATUS;
SELECT * FROM INFORMATION_SCHEMA.PROCESSLIST;
EXPLAIN SELECT * FROM users WHERE email = 'user@example.com';
```

### Redis Commands
```bash
# Connection
redis-cli
redis-cli -h hostname -p port

# Common commands
KEYS *
GET key_name
SET key_name value
DEL key_name
FLUSHALL
INFO memory
```

---

*This reference guide is maintained and updated regularly. For the most current information, please refer to the official documentation of each technology.* 