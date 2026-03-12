# Complete Server Setup Guide

This guide will help you replicate this project setup on a new Proxmox VM or similar Linux server.

## System Requirements

- **Operating System**: Linux (Ubuntu 22.04+ / Debian 11+ recommended)
- **Python**: 3.8+ (currently using Python 3.12.3)
- **Node.js**: 16+ (currently using Node.js v20.19.2)
- **npm**: 10+ (currently using npm 10.8.2)
- **Web Server**: Nginx (recommended) or Apache for reverse proxy
- **Database**: SQLite3 (included with Python)

## Step 1: Initial Server Setup

### 1.1 Update System Packages
```bash
sudo apt update
sudo apt upgrade -y
```

### 1.2 Install Base Dependencies
```bash
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    nodejs \
    npm \
    git \
    sqlite3 \
    nginx \
    curl \
    wget \
    build-essential
```

### 1.3 Verify Installations
```bash
python3 --version  # Should show 3.8+
node --version     # Should show 16+
npm --version      # Should show 6+
```

## Step 2: Create Project Directory Structure

### 2.1 Create Web Directory
```bash
sudo mkdir -p /var/www/projectmanager.test
sudo chown -R $USER:$USER /var/www/projectmanager.test
cd /var/www/projectmanager.test
```

### 2.2 Clone or Copy Repository
```bash
# If using Git:
git clone <your-repo-url> github_v2
cd github_v2

# Or copy files manually to /var/www/projectmanager.test/github_v2
```

## Step 3: Python Environment Setup

### 3.1 Create Virtual Environment
```bash
cd /var/www/projectmanager.test/github_v2/admin
python3 -m venv venv
source venv/bin/activate
```

### 3.2 Install Python Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Python Dependencies** (from `admin/requirements.txt`):
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `jinja2` - Template engine
- `markdown` - Markdown processing
- `python-multipart` - Form data handling

### 3.3 Verify Python Setup
```bash
python -c "import fastapi, uvicorn, jinja2; print('All packages installed successfully')"
```

## Step 4: Node.js Dependencies Setup

### 4.1 Install Node.js Dependencies
```bash
cd /var/www/projectmanager.test/github_v2
npm install
```

**Node.js Dependencies** (from `package.json`):
- `tailwindcss` ^3.4.1 - CSS framework

### 4.2 Build Tailwind CSS
```bash
npm run build
```

This creates `assets/css/tailwind-built.css` from `assets/css/tailwind.css`.

## Step 5: Database Setup

### 5.1 Initialize Database
```bash
cd /var/www/projectmanager.test/github_v2/admin
sqlite3 database/unified.sqlite < database/schema.sql
```

### 5.2 Set Permissions
```bash
chmod 664 database/unified.sqlite
chmod 775 database/
```

## Step 6: File Permissions

### 6.1 Set Proper Ownership
```bash
cd /var/www/projectmanager.test
sudo chown -R $USER:$USER github_v2
chmod -R 755 github_v2
chmod -R 775 github_v2/admin/database
chmod -R 775 github_v2/assets/images
```

### 6.2 Make Admin Script Executable
```bash
chmod +x github_v2/admin/admin-panel.sh
```

## Step 7: Configure Nginx (Reverse Proxy)

The admin panel runs on `127.0.0.1:8000` (localhost only for security) and is accessed through Nginx reverse proxy. This allows you to access it via your domain name while keeping the FastAPI app secure.

### 7.1 Create Nginx Configuration
```bash
sudo nano /etc/nginx/sites-available/projectmanager.test
```

Add the following configuration:
```nginx
server {
    listen 80;
    server_name projectmanager.test;

    # Increase body size for file uploads
    client_max_body_size 50M;

    # Frontend static files (served directly by Nginx for better performance)
    root /var/www/projectmanager.test/github_v2;
    index index.html;

    # Admin panel routes - proxy to FastAPI backend
    location /admin {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-Port $server_port;

        # WebSocket support (if needed in future)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # API endpoints - proxy to FastAPI backend
    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Admin static files (CSS, JS) - proxy to FastAPI
    location /admin/static {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Assets served by FastAPI (blog, documents, etc.)
    # These are proxied to FastAPI which handles them
    location ~ ^/(assets|blog|documents|docs|portfolios) {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;

        # Cache static assets
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Frontend HTML files (served directly by Nginx)
    location / {
        try_files $uri $uri/ =404;
    }

    # Favicon
    location /favicon.ico {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
    }
}
```

**Important Notes:**
- The FastAPI app continues to run on `127.0.0.1:8000` (localhost only) for security
- Nginx acts as a reverse proxy, forwarding requests to the FastAPI backend
- Static files can be served directly by Nginx OR proxied to FastAPI (both work)
- No changes needed to the repository files - this is all server configuration

### 7.2 Enable Site
```bash
sudo ln -s /etc/nginx/sites-available/projectmanager.test /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 7.3 Update /etc/hosts (for local testing)
```bash
echo "127.0.0.1 projectmanager.test" | sudo tee -a /etc/hosts
```

## Step 8: Start Admin Panel

### 8.1 Using the Management Script (Recommended)
```bash
cd /var/www/projectmanager.test/github_v2/admin
./admin-panel.sh start
```

### 8.2 Verify It's Running
```bash
./admin-panel.sh status
```

You should see output like:
```
[SUCCESS] Admin panel is RUNNING
  PID: 12345
  Port: 8000
  URL: http://127.0.0.1:8000/admin
```

### 8.3 Access Admin Panel Through Nginx

**Primary Access Method (via Nginx):**
- `http://projectmanager.test/admin` - Access through domain name
- `http://your-server-ip/admin` - Access via IP (if DNS not configured)

**Direct Access (localhost only - for testing):**
- `http://127.0.0.1:8000/admin` - Only works on the server itself

**Important**: The FastAPI app runs on `127.0.0.1:8000` (localhost only) for security. You access it through Nginx which acts as a reverse proxy. This means:
- ✅ The admin panel is accessible via your domain name
- ✅ The FastAPI app is not directly exposed to the internet
- ✅ You can add SSL/HTTPS through Nginx
- ✅ No changes needed to repository files

## Step 9: Create Systemd Service (Optional - for auto-start)

### 9.1 Create Service File
```bash
sudo nano /etc/systemd/system/admin-panel.service
```

Add:
```ini
[Unit]
Description=Admin Panel FastAPI Application
After=network.target

[Service]
Type=simple
User=webadmin
WorkingDirectory=/var/www/projectmanager.test/github_v2/admin
Environment="PATH=/var/www/projectmanager.test/github_v2/admin/venv/bin"
ExecStart=/var/www/projectmanager.test/github_v2/admin/venv/bin/uvicorn app:app --host 127.0.0.1 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 9.2 Enable and Start Service
```bash
sudo systemctl daemon-reload
sudo systemctl enable admin-panel
sudo systemctl start admin-panel
sudo systemctl status admin-panel
```

## Step 10: Firewall Configuration

### 10.1 Allow HTTP/HTTPS (if using UFW)
```bash
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 22/tcp  # SSH
sudo ufw enable
```

## Step 11: SSL/HTTPS Setup (Optional but Recommended)

### 11.1 Install Certbot
```bash
sudo apt install certbot python3-certbot-nginx
```

### 11.2 Obtain SSL Certificate
```bash
sudo certbot --nginx -d projectmanager.test
```

## Complete Package List

### System Packages
- `python3` (3.12.3)
- `python3-pip`
- `python3-venv`
- `nodejs` (v20.19.2)
- `npm` (10.8.2)
- `git`
- `sqlite3`
- `nginx`
- `build-essential`

### Python Packages (in venv)
- `fastapi`
- `uvicorn[standard]`
- `jinja2`
- `markdown`
- `python-multipart`

### Node.js Packages
- `tailwindcss` ^3.4.1

### Frontend Libraries (CDN)
- Alpine.js (via CDN)
- PrismJS (via CDN)
- Font Awesome (via CDN)
- Toast UI Editor (via CDN)
- sql.js (WebAssembly SQLite)

## Directory Structure

```
/var/www/projectmanager.test/github_v2/
├── admin/                    # Backend FastAPI application
│   ├── app.py               # Main application
│   ├── config.py            # Configuration
│   ├── database/            # SQLite databases
│   │   ├── unified.sqlite   # Production database
│   │   └── schema.sql       # Database schema
│   ├── resources/           # Section-specific resources
│   ├── templates/           # Jinja2 templates
│   ├── static/              # Admin static files
│   ├── venv/                # Python virtual environment
│   └── requirements.txt     # Python dependencies
├── assets/                   # Frontend static assets
│   ├── css/                 # Compiled CSS
│   ├── js/                  # JavaScript libraries
│   └── images/              # Media files
├── blog/                     # Blog posts (generated HTML)
├── documents/                # Document pages
├── *.html                    # Frontend pages
├── package.json              # Node.js dependencies
└── tailwind.config.js        # Tailwind configuration
```

## Environment Variables

Currently, the project doesn't use environment variables, but you may want to add:
- `ADMIN_SECRET_KEY` - For session security
- `DATABASE_PATH` - Database location
- `PORT` - Admin panel port (default: 8000)

## Stopping the Admin Panel

### Method 1: Using the Management Script (Recommended)
```bash
cd /var/www/projectmanager.test/github_v2/admin
./admin-panel.sh kill
# Or
./admin-panel.sh stop
```

### Method 2: Find and Kill Process Manually
```bash
# Find the process
lsof -ti:8000
# Or
ps aux | grep uvicorn

# Kill by PID (replace 12345 with actual PID)
kill -TERM 12345

# If that doesn't work, force kill
kill -KILL 12345
```

### Method 3: Kill All uvicorn Processes
```bash
# Find all uvicorn processes
pkill -f "uvicorn.*app:app"

# Or more specifically
pkill -f "uvicorn.*app:app.*--port.*8000"
```

### Method 4: Kill by Port (macOS/Linux)
```bash
# Find process using port 8000
lsof -ti:8000 | xargs kill -TERM

# Force kill if needed
lsof -ti:8000 | xargs kill -KILL
```

## Running Admin Panel for Network Access (macOS/Local Development)

By default, the admin panel runs on `127.0.0.1` (localhost only), which means it's only accessible from the same machine. To access it from other machines on your network:

### Option 1: Run with 0.0.0.0 (All Interfaces)
```bash
cd /var/www/projectmanager.test/github_v2/admin
source venv/bin/activate
uvicorn app:app --reload --port 8000 --host 0.0.0.0
```

Then access from other machines using:
- `http://<your-mac-ip>:8000/admin` (e.g., `http://192.168.1.100:8000/admin`)

**Find your Mac's IP address:**
```bash
# macOS
ifconfig | grep "inet " | grep -v 127.0.0.1
# Or
ipconfig getifaddr en0  # For Wi-Fi
ipconfig getifaddr en1  # For Ethernet
```

### Option 2: Modify admin-panel.sh Temporarily

Edit the script to use `0.0.0.0` instead of `127.0.0.1`:

```bash
cd /var/www/projectmanager.test/github_v2/admin
nano admin-panel.sh
# Change line 10: HOST="127.0.0.1" to HOST="0.0.0.0"
# Save and exit
./admin-panel.sh restart
```

**Security Note**: Using `0.0.0.0` makes the admin panel accessible from your local network. Only use this on trusted networks (home/office), not on public networks.

### Option 3: Use SSH Port Forwarding (Most Secure)

**Note**: SSH must be enabled on the Mac Studio first. See "Enabling SSH on macOS" section below.

If you want to keep it on localhost but access from another machine:

**On your Mac Studio (where admin runs):**
```bash
# Keep admin running on 127.0.0.1:8000
uvicorn app:app --reload --port 8000 --host 127.0.0.1
```

**On your MacBook Air:**
```bash
# Create SSH tunnel
ssh -L 8000:localhost:8000 bradclampitt@10.0.11.197

# Then access via: http://localhost:8000/admin
# Keep the SSH session open while using the admin panel
```

### Enabling SSH on macOS (for Option 3)

If you get "Connection refused" when trying to SSH:

1. **Enable SSH via System Settings:**
   - Open **System Settings** (or **System Preferences** on older macOS)
   - Go to **General** → **Sharing**
   - Enable **Remote Login**
   - Note: You may need to allow your user account or set it to "All users"

2. **Or enable via Terminal:**
   ```bash
   sudo systemsetup -setremotelogin on
   ```

3. **Verify SSH is running:**
   ```bash
   sudo launchctl list | grep ssh
   # Should show: com.openssh.sshd
   ```

4. **Check firewall (if enabled):**
   - System Settings → Network → Firewall → Options
   - Make sure "Block all incoming connections" is OFF
   - Or add SSH to allowed apps

5. **Test SSH connection:**
   ```bash
   # From MacBook Air, test connection
   ssh bradclampitt@10.0.11.197
   ```

## Troubleshooting

### Admin Panel Won't Start
```bash
cd /var/www/projectmanager.test/github_v2/admin
source venv/bin/activate
python -c "import fastapi; print('FastAPI installed')"
uvicorn app:app --reload --port 8000 --host 127.0.0.1
```

**Note**: The admin panel MUST run on `127.0.0.1` (localhost) for security. Access it through Nginx at `http://projectmanager.test/admin` or `http://your-domain.com/admin`.

### Admin Panel Accessible Through Nginx

If you've configured Nginx correctly, you should be able to access:
- `http://projectmanager.test/admin` - Admin dashboard
- `http://projectmanager.test/api/...` - API endpoints
- `http://projectmanager.test/` - Frontend pages

The FastAPI app running on `127.0.0.1:8000` is only accessible through the Nginx reverse proxy, which provides:
- Security (app not directly exposed)
- SSL/HTTPS termination
- Better performance for static files
- Domain name access instead of IP:port

### Admin Panel Appears Running But Not Accessible

**Symptoms**: Process shows as running but browser can't connect

**Common Causes:**

1. **Running on wrong host**: Check if it's bound to `127.0.0.1` (localhost only)
   ```bash
   # Check what's listening on port 8000
   lsof -i :8000
   # Should show: *:8000 (LISTEN) for network access
   # Or: 127.0.0.1:8000 (LISTEN) for localhost only
   ```

2. **Firewall blocking**: macOS firewall might be blocking connections
   ```bash
   # Check firewall status
   /usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate

   # Temporarily disable for testing (not recommended for production)
   sudo /usr/libexec/ApplicationFirewall/socketfilterfw --setglobalstate off
   ```

3. **Wrong IP address**: Make sure you're using the correct IP
   ```bash
   # Get your Mac's IP address
   ifconfig | grep "inet " | grep -v 127.0.0.1
   ```

4. **Port already in use**: Another process might be using port 8000
   ```bash
   # Check what's using port 8000
   lsof -i :8000
   # Kill any processes using that port
   lsof -ti:8000 | xargs kill -9
   ```

5. **Process crashed**: Check logs for errors
   ```bash
   tail -f admin/admin.log
   # Or if running manually, check terminal output
   ```

### Database Issues
```bash
sqlite3 admin/database/unified.sqlite
.tables
.schema
```

### Nginx Issues

**Test Configuration:**
```bash
sudo nginx -t
```

**Check Nginx Status:**
```bash
sudo systemctl status nginx
```

**View Error Logs:**
```bash
sudo tail -f /var/log/nginx/error.log
```

**View Access Logs:**
```bash
sudo tail -f /var/log/nginx/access.log
```

**Common Issues:**

1. **502 Bad Gateway**: FastAPI app not running
   ```bash
   cd /var/www/projectmanager.test/github_v2/admin
   ./admin-panel.sh status
   # If not running, start it:
   ./admin-panel.sh start
   ```

2. **404 Not Found**: Check that proxy_pass URL matches FastAPI port
   ```bash
   # Verify FastAPI is running on port 8000
   netstat -tlnp | grep 8000
   # Or
   lsof -i :8000
   ```

3. **Permission Denied**: Check file permissions
   ```bash
   sudo chown -R $USER:$USER /var/www/projectmanager.test/github_v2
   ```

4. **Static Files Not Loading**: Ensure FastAPI is serving them or serve directly via Nginx

### Permission Issues
```bash
sudo chown -R $USER:$USER /var/www/projectmanager.test/github_v2
chmod -R 755 /var/www/projectmanager.test/github_v2
chmod -R 775 /var/www/projectmanager.test/github_v2/admin/database
```

## Maintenance Commands

### Update Python Packages
```bash
cd /var/www/projectmanager.test/github_v2/admin
source venv/bin/activate
pip install --upgrade -r requirements.txt
```

### Rebuild Tailwind CSS
```bash
cd /var/www/projectmanager.test/github_v2
npm run build
```

### Backup Database
```bash
cp admin/database/unified.sqlite admin/database/unified.sqlite.backup.$(date +%Y%m%d_%H%M%S)
```

### View Logs
```bash
tail -f admin/admin.log
# Or if using systemd:
sudo journalctl -u admin-panel -f
```

## Security Considerations

1. **Admin Panel Access**: Currently runs on localhost (127.0.0.1) - only accessible via Nginx reverse proxy
2. **Database**: SQLite file should have restricted permissions (664)
3. **File Uploads**: Validate all uploaded files
4. **HTTPS**: Use SSL certificates for production
5. **Firewall**: Only expose necessary ports (80, 443, 22)

## Next Steps

1. Configure domain name DNS to point to your server IP
2. Set up SSL certificates with Let's Encrypt
3. Configure automated backups
4. Set up monitoring/logging
5. Configure firewall rules
6. Set up git deployment workflow

