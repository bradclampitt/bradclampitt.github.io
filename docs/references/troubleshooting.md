# Troubleshooting Guide

Common issues, solutions, and debugging techniques for development and production environments.

## 🚨 General Troubleshooting Methodology

### Step-by-Step Approach
1. **Reproduce the Issue** - Ensure you can consistently recreate the problem
2. **Check Recent Changes** - What was changed recently that might cause this?
3. **Review Logs** - Check application, server, and system logs
4. **Isolate the Problem** - Narrow down to the specific component or code
5. **Test Solutions** - Try fixes in development environment first
6. **Document the Solution** - Record what worked for future reference

### Essential Commands
```bash
# Check system resources
top
htop
df -h
free -m

# Monitor logs in real-time
tail -f /var/log/nginx/error.log
tail -f /var/log/apache2/error.log
tail -f storage/logs/laravel.log

# Check running processes
ps aux | grep php
ps aux | grep nginx
ps aux | grep mysql

# Network connectivity
ping google.com
telnet hostname 80
netstat -tulpn | grep :80
```

## 🐘 PHP & Magento 2 Issues

### Memory Issues

#### Problem: PHP Fatal error: Allowed memory size exhausted
```
PHP Fatal error: Allowed memory size of 134217728 bytes exhausted
```

**Solutions:**
```bash
# Increase PHP memory limit
echo "memory_limit = 2G" >> /etc/php/8.1/cli/php.ini
echo "memory_limit = 2G" >> /etc/php/8.1/fpm/php.ini

# For Magento CLI commands
php -d memory_limit=2G bin/magento cache:clean

# Check current memory limit
php -r "echo ini_get('memory_limit');"
```

#### Problem: Magento setup:upgrade runs out of memory
**Solutions:**
```bash
# Use unlimited memory for setup commands
php -d memory_limit=-1 bin/magento setup:upgrade

# Or increase specific to need
php -d memory_limit=4G bin/magento setup:upgrade
```

### Permission Issues

#### Problem: Permission denied errors
```
Warning: file_put_contents(/var/www/html/var/cache/...): failed to open stream: Permission denied
```

**Solutions:**
```bash
# Fix Magento 2 permissions
find . -type f -exec chmod 644 {} \;
find . -type d -exec chmod 755 {} \;
find ./var -type d -exec chmod 777 {} \;
find ./pub/media -type d -exec chmod 777 {} \;
find ./pub/static -type d -exec chmod 777 {} \;
chmod 777 ./app/etc
chmod 644 ./app/etc/*.xml

# Set proper ownership
chown -R www-data:www-data /var/www/html/
```

### Cache Issues

#### Problem: Changes not reflecting on frontend
**Solutions:**
```bash
# Clear all Magento caches
bin/magento cache:clean
bin/magento cache:flush

# Remove generated files
rm -rf generated/* var/cache/* var/page_cache/* var/session/*

# Regenerate static content
bin/magento setup:static-content:deploy -f

# Clear browser cache and hard refresh (Ctrl+Shift+R)
```

#### Problem: Redis connection errors
```
RedisException: Redis server went away
```

**Solutions:**
```bash
# Check Redis status
redis-cli ping

# Restart Redis
sudo systemctl restart redis-server

# Check Redis configuration
redis-cli config get maxmemory
redis-cli config get timeout

# Clear Redis cache
redis-cli flushall
```

### Database Issues

#### Problem: MySQL connection errors
```
SQLSTATE[HY000] [2002] No such file or directory
```

**Solutions:**
```bash
# Check MySQL status
sudo systemctl status mysql

# Start MySQL
sudo systemctl start mysql

# Check MySQL configuration
mysql -u root -p -e "SHOW VARIABLES LIKE 'socket';"

# Test connection
mysql -u username -p -h localhost database_name
```

#### Problem: Database is locked or corrupted
**Solutions:**
```bash
# Check for locked tables
mysql -u root -p -e "SHOW PROCESSLIST;"

# Kill long-running queries
mysql -u root -p -e "KILL 123;"

# Repair tables
mysql -u root -p database_name -e "REPAIR TABLE table_name;"

# Check table integrity
mysql -u root -p database_name -e "CHECK TABLE table_name;"
```

## 🌐 Web Server Issues

### Nginx Issues

#### Problem: 502 Bad Gateway
**Common Causes & Solutions:**
```bash
# Check if PHP-FPM is running
sudo systemctl status php8.1-fpm

# Restart PHP-FPM
sudo systemctl restart php8.1-fpm

# Check Nginx error logs
tail -f /var/log/nginx/error.log

# Check upstream configuration
nginx -t
```

#### Problem: 404 Not Found for admin URLs
**Solution for Magento:**
```nginx
# Add to Nginx configuration
location ~* ^/setup($|/) {
    root $MAGE_ROOT;
    location ~ ^/setup/index.php {
        fastcgi_pass   fastcgi_backend;
        fastcgi_param  PHP_FLAG  "session.auto_start=off \n suhosin.session.cryptua=off";
        fastcgi_param  PHP_VALUE "memory_limit=756M \n max_execution_time=600";
        fastcgi_read_timeout 600s;
        fastcgi_connect_timeout 600s;
        fastcgi_param  MAGE_MODE $MAGE_MODE;
        fastcgi_param  SCRIPT_FILENAME  $document_root$fastcgi_script_name;
        include        fastcgi_params;
    }
}
```

### Apache Issues

#### Problem: .htaccess not working
**Solutions:**
```apache
# Enable mod_rewrite
sudo a2enmod rewrite

# Check AllowOverride in virtual host
<Directory /var/www/html>
    AllowOverride All
    Require all granted
</Directory>

# Restart Apache
sudo systemctl restart apache2
```

#### Problem: 500 Internal Server Error
**Check:**
```bash
# Apache error logs
tail -f /var/log/apache2/error.log

# Check .htaccess syntax
apache2ctl configtest

# Verify file permissions
ls -la .htaccess
```

## 💾 Database Performance Issues

### Slow Queries

#### Problem: MySQL queries taking too long
**Debugging:**
```sql
-- Enable slow query log
SET GLOBAL slow_query_log = 'ON';
SET GLOBAL long_query_time = 2;

-- Check running processes
SHOW PROCESSLIST;

-- Analyze slow queries
EXPLAIN SELECT * FROM catalog_product_entity WHERE sku = 'test';

-- Check table status
SHOW TABLE STATUS LIKE 'catalog_product_entity';
```

**Solutions:**
```sql
-- Add indexes for frequently queried columns
CREATE INDEX idx_sku ON catalog_product_entity(sku);
CREATE INDEX idx_created_at ON sales_order(created_at);

-- Optimize tables
OPTIMIZE TABLE catalog_product_entity;

-- Update table statistics
ANALYZE TABLE catalog_product_entity;
```

### Connection Issues

#### Problem: Too many connections
```
ERROR 1040 (HY000): Too many connections
```

**Solutions:**
```sql
-- Check current connections
SHOW STATUS LIKE 'Threads_connected';
SHOW VARIABLES LIKE 'max_connections';

-- Increase max connections (temporarily)
SET GLOBAL max_connections = 500;

-- Kill idle connections
SELECT id, user, host, db, command, time, state 
FROM information_schema.processlist 
WHERE command = 'Sleep' AND time > 300;

-- Kill specific connection
KILL 123;
```

## 🚀 Performance Issues

### Frontend Performance

#### Problem: Slow page load times
**Debugging:**
```bash
# Check network tab in browser dev tools
# Look for:
# - Large file sizes
# - Many HTTP requests
# - Slow server response times
# - Render-blocking resources

# Use tools:
# - Google PageSpeed Insights
# - GTmetrix
# - WebPageTest
```

**Solutions:**
```bash
# Enable Magento production mode
bin/magento deploy:mode:set production

# Enable compression
bin/magento config:set dev/js/merge_files 1
bin/magento config:set dev/css/merge_css_files 1
bin/magento config:set dev/js/minify_files 1
bin/magento config:set dev/css/minify_files 1

# Enable full page cache
bin/magento config:set system/full_page_cache/caching_application 2

# Optimize images
bin/magento catalog:images:resize
```

### Backend Performance

#### Problem: High server load
**Debugging:**
```bash
# Check system load
uptime
top
htop

# Check disk I/O
iotop
iostat -x 1

# Check memory usage
free -m
cat /proc/meminfo

# Check PHP-FPM status
curl http://localhost/php-fpm-status
```

**Solutions:**
```bash
# Increase PHP-FPM workers
# Edit /etc/php/8.1/fpm/pool.d/www.conf
pm.max_children = 50
pm.start_servers = 5
pm.min_spare_servers = 5
pm.max_spare_servers = 35

# Enable OPcache
echo "opcache.enable=1" >> /etc/php/8.1/fpm/php.ini
echo "opcache.memory_consumption=256" >> /etc/php/8.1/fpm/php.ini

# Restart services
sudo systemctl restart php8.1-fpm nginx
```

## 🔐 Security Issues

### SSL/TLS Issues

#### Problem: SSL certificate errors
**Debugging:**
```bash
# Check certificate details
openssl x509 -in certificate.crt -text -noout

# Test SSL connection
openssl s_client -connect domain.com:443

# Check certificate chain
curl -I https://domain.com
```

**Solutions:**
```bash
# Renew Let's Encrypt certificate
certbot renew

# Force HTTPS in Magento
bin/magento config:set web/secure/use_in_frontend 1
bin/magento config:set web/secure/use_in_adminhtml 1

# Update base URLs
bin/magento config:set web/secure/base_url https://domain.com/
```

### File Permission Security

#### Problem: Overly permissive file permissions
**Solutions:**
```bash
# Secure file permissions
find . -type f -exec chmod 644 {} \;
find . -type d -exec chmod 755 {} \;

# Restrict sensitive files
chmod 600 app/etc/env.php
chmod 600 .env

# Remove execute permissions from uploads
find pub/media -type f -exec chmod 644 {} \;
```

## 🔧 Development Environment Issues

### Docker Issues

#### Problem: Container won't start
**Debugging:**
```bash
# Check container logs
docker logs container_name

# Check container status
docker ps -a

# Check resource usage
docker stats

# Check Docker daemon
sudo systemctl status docker
```

**Solutions:**
```bash
# Restart Docker service
sudo systemctl restart docker

# Clean up Docker resources
docker system prune -a

# Rebuild containers
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Git Issues

#### Problem: Merge conflicts
**Solutions:**
```bash
# View conflicted files
git status

# Open merge tool
git mergetool

# Manual resolution
git add resolved_file.php
git commit

# Abort merge if needed
git merge --abort
```

#### Problem: Accidentally committed sensitive data
**Solutions:**
```bash
# Remove from last commit
git reset --soft HEAD~1
git reset HEAD sensitive_file
git commit

# Remove from history (dangerous)
git filter-branch --force --index-filter \
'git rm --cached --ignore-unmatch sensitive_file' \
--prune-empty --tag-name-filter cat -- --all
```

## 📱 Mobile/Responsive Issues

### Common Problems
- Layout breaks on mobile devices
- Touch targets too small
- Content overflow
- Slow loading on mobile networks

**Debugging Tools:**
```bash
# Browser dev tools device simulation
# Chrome: F12 → Device Toolbar
# Firefox: F12 → Responsive Design Mode

# Real device testing
# BrowserStack
# Device labs
# Physical devices
```

**Solutions:**
```css
/* Responsive breakpoints */
@media (max-width: 768px) {
    .desktop-only { display: none; }
    .mobile-menu { display: block; }
}

/* Touch-friendly buttons */
.button {
    min-height: 44px;
    min-width: 44px;
}

/* Prevent horizontal scroll */
body {
    overflow-x: hidden;
}
```

## 🆘 Emergency Procedures

### Site Down - Quick Recovery
```bash
# 1. Check if server is responding
ping your-domain.com

# 2. Check web server status
sudo systemctl status nginx
sudo systemctl status apache2

# 3. Check database
mysql -u root -p -e "SELECT 1;"

# 4. Check disk space
df -h

# 5. Check error logs
tail -100 /var/log/nginx/error.log

# 6. Quick fixes
sudo systemctl restart nginx
sudo systemctl restart php8.1-fpm
bin/magento cache:flush
```

### Database Recovery
```bash
# 1. Stop application
sudo systemctl stop nginx

# 2. Backup current state
mysqldump -u root -p database_name > emergency_backup.sql

# 3. Restore from backup
mysql -u root -p database_name < last_good_backup.sql

# 4. Start application
sudo systemctl start nginx
```

### Rollback Deployment
```bash
# 1. Switch to previous release
cd /var/www/releases
ln -sfn previous_release /var/www/html

# 2. Clear caches
bin/magento cache:flush

# 3. Restart services
sudo systemctl restart php8.1-fpm nginx
```

## 📞 Getting Help

### Information to Gather
When reporting issues, include:
- **Error messages** (exact text)
- **Steps to reproduce**
- **Environment details** (OS, PHP version, etc.)
- **Recent changes** made to the system
- **Log files** (relevant portions)
- **Screenshots** (if applicable)

### Useful Commands for System Info
```bash
# System information
uname -a
lsb_release -a

# PHP information
php -v
php -m | grep -i extension_name

# Web server version
nginx -v
apache2 -v

# Database version
mysql --version

# Disk space and memory
df -h
free -m

# Network configuration
ip addr show
```

---

*This troubleshooting guide is continuously updated with new issues and solutions. Contribute your findings to help the team resolve problems faster.*