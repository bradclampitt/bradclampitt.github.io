# Installation Guide

Comprehensive installation instructions for development environments, tools, and technologies used across projects.

## 🖥️ Operating System Setup

### Ubuntu/Debian Linux

#### System Update
```bash
# Update package lists
sudo apt update

# Upgrade existing packages
sudo apt upgrade -y

# Install essential packages
sudo apt install -y curl wget git vim build-essential software-properties-common apt-transport-https ca-certificates gnupg lsb-release
```

#### Additional Tools
```bash
# Install useful utilities
sudo apt install -y htop tree unzip zip jq httpie
```

### macOS

#### Homebrew Installation
```bash
# Install Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Add to PATH
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
eval "$(/opt/homebrew/bin/brew shellenv)"

# Install essential tools
brew install curl wget git vim htop tree jq httpie
```

## 🐘 PHP Development Environment

### PHP Installation

#### Ubuntu/Debian
```bash
# Add PHP repository
sudo add-apt-repository ppa:ondrej/php -y
sudo apt update

# Install PHP 8.1 and extensions
sudo apt install -y php8.1 php8.1-cli php8.1-fpm php8.1-mysql php8.1-xml php8.1-curl php8.1-gd php8.1-mbstring php8.1-zip php8.1-intl php8.1-bcmath php8.1-soap php8.1-xsl php8.1-redis

# Verify installation
php -v
```

#### macOS
```bash
# Install PHP via Homebrew
brew install php@8.1

# Link PHP
brew link php@8.1 --force

# Add to PATH
echo 'export PATH="/opt/homebrew/opt/php@8.1/bin:$PATH"' >> ~/.zprofile
```

### Composer Installation
```bash
# Download and install Composer
curl -sS https://getcomposer.org/installer | php
sudo mv composer.phar /usr/local/bin/composer

# Make executable
sudo chmod +x /usr/local/bin/composer

# Verify installation
composer --version

# Update to latest version
composer self-update
```

### PHP Configuration
```bash
# Find PHP configuration file
php --ini

# Edit php.ini for development
sudo vim /etc/php/8.1/cli/php.ini
sudo vim /etc/php/8.1/fpm/php.ini
```

#### Recommended PHP Settings
```ini
; Memory and execution limits
memory_limit = 2G
max_execution_time = 300
max_input_time = 300

; File uploads
upload_max_filesize = 64M
post_max_size = 64M

; Error reporting (development)
display_errors = On
error_reporting = E_ALL

; OPcache settings
opcache.enable = 1
opcache.memory_consumption = 256
opcache.interned_strings_buffer = 12
opcache.max_accelerated_files = 60000
opcache.validate_timestamps = 1
opcache.revalidate_freq = 2

; Date and timezone
date.timezone = America/Chicago
```

## 🗄️ Database Systems

### MySQL Installation

#### Ubuntu/Debian
```bash
# Install MySQL Server
sudo apt install -y mysql-server

# Secure installation
sudo mysql_secure_installation

# Start and enable MySQL
sudo systemctl start mysql
sudo systemctl enable mysql

# Create development user
sudo mysql -e "CREATE USER 'developer'@'localhost' IDENTIFIED BY 'password';"
sudo mysql -e "GRANT ALL PRIVILEGES ON *.* TO 'developer'@'localhost';"
sudo mysql -e "FLUSH PRIVILEGES;"
```

#### macOS
```bash
# Install MySQL via Homebrew
brew install mysql

# Start MySQL service
brew services start mysql

# Secure installation
mysql_secure_installation
```

### PostgreSQL Installation

#### Ubuntu/Debian
```bash
# Install PostgreSQL
sudo apt install -y postgresql postgresql-contrib

# Start and enable PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Create development user
sudo -u postgres createuser --interactive
sudo -u postgres createdb development_db
```

#### macOS
```bash
# Install PostgreSQL via Homebrew
brew install postgresql

# Start PostgreSQL service
brew services start postgresql

# Create development database
createdb development_db
```

### Redis Installation

#### Ubuntu/Debian
```bash
# Install Redis
sudo apt install -y redis-server

# Configure Redis
sudo vim /etc/redis/redis.conf

# Start and enable Redis
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Test Redis
redis-cli ping
```

#### macOS
```bash
# Install Redis via Homebrew
brew install redis

# Start Redis service
brew services start redis

# Test Redis
redis-cli ping
```

## 🌐 Web Servers

### Nginx Installation

#### Ubuntu/Debian
```bash
# Install Nginx
sudo apt install -y nginx

# Start and enable Nginx
sudo systemctl start nginx
sudo systemctl enable nginx

# Test configuration
sudo nginx -t

# Create development site
sudo vim /etc/nginx/sites-available/development
```

#### Sample Nginx Configuration
```nginx
server {
    listen 80;
    server_name development.local;
    root /var/www/html;
    index index.php index.html;

    location / {
        try_files $uri $uri/ /index.php?$query_string;
    }

    location ~ \.php$ {
        fastcgi_pass unix:/var/run/php/php8.1-fpm.sock;
        fastcgi_index index.php;
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
        include fastcgi_params;
    }

    location ~ /\.ht {
        deny all;
    }
}
```

#### macOS
```bash
# Install Nginx via Homebrew
brew install nginx

# Start Nginx service
brew services start nginx

# Configuration location
/opt/homebrew/etc/nginx/nginx.conf
```

### Apache Installation

#### Ubuntu/Debian
```bash
# Install Apache
sudo apt install -y apache2

# Enable modules
sudo a2enmod rewrite
sudo a2enmod ssl

# Start and enable Apache
sudo systemctl start apache2
sudo systemctl enable apache2

# Create virtual host
sudo vim /etc/apache2/sites-available/development.conf
```

#### Sample Apache Virtual Host
```apache
<VirtualHost *:80>
    ServerName development.local
    DocumentRoot /var/www/html
    
    <Directory /var/www/html>
        AllowOverride All
        Require all granted
    </Directory>
    
    ErrorLog ${APACHE_LOG_DIR}/development_error.log
    CustomLog ${APACHE_LOG_DIR}/development_access.log combined
</VirtualHost>
```

## 🚀 Node.js and Frontend Tools

### Node.js Installation

#### Using Node Version Manager (NVM)
```bash
# Install NVM
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash

# Reload shell
source ~/.bashrc

# Install latest LTS Node.js
nvm install --lts
nvm use --lts

# Verify installation
node --version
npm --version
```

#### Direct Installation (Ubuntu/Debian)
```bash
# Add NodeSource repository
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -

# Install Node.js
sudo apt install -y nodejs

# Verify installation
node --version
npm --version
```

#### macOS
```bash
# Install Node.js via Homebrew
brew install node

# Verify installation
node --version
npm --version
```

### Global NPM Packages
```bash
# Install useful global packages
npm install -g yarn pnpm
npm install -g @vue/cli create-react-app
npm install -g typescript ts-node
npm install -g eslint prettier
npm install -g nodemon pm2
npm install -g http-server serve
```

## 🐳 Docker Installation

### Ubuntu/Debian
```bash
# Remove old versions
sudo apt remove docker docker-engine docker.io containerd runc

# Install dependencies
sudo apt update
sudo apt install -y ca-certificates curl gnupg lsb-release

# Add Docker GPG key
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Add Docker repository
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Add user to docker group
sudo usermod -aG docker $USER

# Start and enable Docker
sudo systemctl start docker
sudo systemctl enable docker

# Test installation
docker --version
docker compose version
```

### macOS
```bash
# Install Docker Desktop via Homebrew
brew install --cask docker

# Or download from https://www.docker.com/products/docker-desktop
```

### Docker Compose Installation (if not included)
```bash
# Download Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# Make executable
sudo chmod +x /usr/local/bin/docker-compose

# Verify installation
docker-compose --version
```

## 🛠️ Magento 2 Installation

### Prerequisites Check
```bash
# Check PHP version (8.1+ required)
php -v

# Check required PHP extensions
php -m | grep -E "(curl|dom|gd|intl|mbstring|mysql|soap|xml|xsl|zip|bcmath)"

# Check Composer
composer --version

# Check MySQL
mysql --version
```

### Magento 2 Installation via Composer
```bash
# Create project directory
mkdir magento2-project
cd magento2-project

# Install Magento 2 (replace with your access keys)
composer create-project --repository-url=https://repo.magento.com/ magento/project-community-edition .

# Set file permissions
find var generated vendor pub/static pub/media app/etc -type f -exec chmod g+w {} +
find var generated vendor pub/static pub/media app/etc -type d -exec chmod g+ws {} +
chown -R :www-data .
chmod u+x bin/magento

# Install Magento
bin/magento setup:install \
    --base-url=http://magento2.local/ \
    --db-host=localhost \
    --db-name=magento2 \
    --db-user=developer \
    --db-password=password \
    --admin-firstname=Admin \
    --admin-lastname=User \
    --admin-email=admin@example.com \
    --admin-user=admin \
    --admin-password=admin123 \
    --language=en_US \
    --currency=USD \
    --timezone=America/Chicago \
    --use-rewrites=1 \
    --search-engine=elasticsearch7 \
    --elasticsearch-host=localhost \
    --elasticsearch-port=9200

# Enable developer mode
bin/magento deploy:mode:set developer

# Clear caches
bin/magento cache:clean
bin/magento cache:flush
```

### Magento 2 Docker Setup
```yaml
# docker-compose.yml
version: '3.8'

services:
  web:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./:/var/www/html
      - ./docker/nginx/default.conf:/etc/nginx/conf.d/default.conf
    depends_on:
      - php
      - mysql

  php:
    build: ./docker/php
    volumes:
      - ./:/var/www/html
    depends_on:
      - mysql
      - redis

  mysql:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: root
      MYSQL_DATABASE: magento2
      MYSQL_USER: magento
      MYSQL_PASSWORD: magento
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql

  redis:
    image: redis:alpine
    ports:
      - "6379:6379"

  elasticsearch:
    image: elasticsearch:7.17.0
    environment:
      - discovery.type=single-node
      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
    ports:
      - "9200:9200"
    volumes:
      - es_data:/usr/share/elasticsearch/data

volumes:
  mysql_data:
  es_data:
```

## 🔧 Development Tools

### Git Configuration
```bash
# Set global configuration
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# Set default branch name
git config --global init.defaultBranch main

# Useful aliases
git config --global alias.st status
git config --global alias.co checkout
git config --global alias.br branch
git config --global alias.ci commit
git config --global alias.unstage 'reset HEAD --'
git config --global alias.last 'log -1 HEAD'
git config --global alias.visual '!gitk'
```

### VS Code Installation

#### Ubuntu/Debian
```bash
# Add Microsoft GPG key
wget -qO- https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > packages.microsoft.gpg
sudo install -o root -g root -m 644 packages.microsoft.gpg /etc/apt/trusted.gpg.d/
sudo sh -c 'echo "deb [arch=amd64,arm64,armhf signed-by=/etc/apt/trusted.gpg.d/packages.microsoft.gpg] https://packages.microsoft.com/repos/code stable main" > /etc/apt/sources.list.d/vscode.list'

# Install VS Code
sudo apt update
sudo apt install -y code
```

#### macOS
```bash
# Install VS Code via Homebrew
brew install --cask visual-studio-code
```

### Essential VS Code Extensions
```bash
# Install extensions via command line
code --install-extension ms-vscode.vscode-json
code --install-extension bradlc.vscode-tailwindcss
code --install-extension ms-vscode.vscode-typescript-next
code --install-extension esbenp.prettier-vscode
code --install-extension ms-python.python
code --install-extension ms-vscode.vscode-eslint
code --install-extension bmewburn.vscode-intelephense-client
code --install-extension ms-vscode.vscode-docker
code --install-extension GitLab.gitlab-workflow
```

## 🔍 Testing and Quality Tools

### PHPUnit Installation
```bash
# Install PHPUnit via Composer (project-specific)
composer require --dev phpunit/phpunit

# Or install globally
composer global require phpunit/phpunit

# Verify installation
./vendor/bin/phpunit --version
```

### Code Quality Tools
```bash
# Install PHP CS Fixer
composer global require friendsofphp/php-cs-fixer

# Install PHPMD (PHP Mess Detector)
composer global require phpmd/phpmd

# Install PHPStan
composer global require phpstan/phpstan

# Add to PATH
echo 'export PATH="$PATH:$HOME/.composer/vendor/bin"' >> ~/.bashrc
```

### Node.js Testing Tools
```bash
# Install Jest for JavaScript testing
npm install -g jest

# Install Cypress for E2E testing
npm install -g cypress

# Install ESLint and Prettier
npm install -g eslint prettier
```

## 🚀 Performance and Monitoring

### Elasticsearch Installation

#### Ubuntu/Debian
```bash
# Add Elasticsearch repository
wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | sudo apt-key add -
sudo sh -c 'echo "deb https://artifacts.elastic.co/packages/7.x/apt stable main" > /etc/apt/sources.list.d/elastic-7.x.list'

# Install Elasticsearch
sudo apt update
sudo apt install -y elasticsearch

# Configure Elasticsearch
sudo vim /etc/elasticsearch/elasticsearch.yml

# Start and enable Elasticsearch
sudo systemctl start elasticsearch
sudo systemctl enable elasticsearch

# Test Elasticsearch
curl -X GET "localhost:9200/"
```

#### macOS
```bash
# Install Elasticsearch via Homebrew
brew install elasticsearch

# Start Elasticsearch service
brew services start elasticsearch
```

## 🔐 SSL/TLS Setup

### Let's Encrypt with Certbot

#### Ubuntu/Debian
```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Obtain SSL certificate
sudo certbot --nginx -d yourdomain.com

# Set up automatic renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

### Self-Signed Certificates (Development)
```bash
# Create self-signed certificate
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/ssl/private/selfsigned.key \
    -out /etc/ssl/certs/selfsigned.crt \
    -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"

# Create DH parameters
sudo openssl dhparam -out /etc/ssl/certs/dhparam.pem 2048
```

## 🧹 Post-Installation Cleanup

### System Cleanup
```bash
# Remove unnecessary packages
sudo apt autoremove -y

# Clean package cache
sudo apt autoclean

# Update locate database
sudo updatedb
```

### Security Hardening
```bash
# Configure firewall
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443

# Disable root login (if applicable)
sudo passwd -l root

# Set up fail2ban
sudo apt install -y fail2ban
sudo systemctl enable fail2ban
```

## 📋 Verification Checklist

After installation, verify everything is working:

- [ ] PHP version and extensions
- [ ] Composer functionality
- [ ] Database connectivity
- [ ] Web server response
- [ ] Node.js and npm
- [ ] Docker containers
- [ ] Git configuration
- [ ] Development tools (VS Code, etc.)
- [ ] SSL certificates (if applicable)
- [ ] File permissions
- [ ] Service startup scripts

## 🆘 Troubleshooting

### Common Issues

#### Permission Denied Errors
```bash
# Fix ownership
sudo chown -R $USER:$USER /path/to/directory

# Fix permissions
chmod 755 /path/to/directory
chmod 644 /path/to/file
```

#### Service Won't Start
```bash
# Check service status
sudo systemctl status service-name

# Check logs
sudo journalctl -u service-name -f

# Restart service
sudo systemctl restart service-name
```

#### Port Already in Use
```bash
# Find process using port
sudo netstat -tulpn | grep :80
sudo lsof -i :80

# Kill process
sudo kill -9 PID
```

---

*This installation guide is regularly updated to reflect the latest versions and best practices. Always verify the latest installation instructions from official documentation.* 