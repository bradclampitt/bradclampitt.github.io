#!/bin/bash
# Admin Panel Management Script
# Easy command-line tools for managing the admin panel server

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ADMIN_ROOT="$SCRIPT_DIR"
VENV_PATH="$ADMIN_ROOT/venv"
PID_FILE="$ADMIN_ROOT/admin.pid"
LOG_FILE="$ADMIN_ROOT/admin.log"
PORT=8000
HOST="127.0.0.1"

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

# Function to find the admin panel process
find_process() {
    # Helper: check if PID exists without relying on ps -p (BusyBox)
    pid_running() {
        [ -n "$1" ] && [ -d "/proc/$1" ]
    }

    # Try to find by PID file first
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        if pid_running "$pid"; then
            echo "$pid"
            return 0
        else
            # PID file exists but process is dead, clean it up
            rm -f "$PID_FILE"
        fi
    fi

    # Find by port
    local port_pid=$(lsof -ti:$PORT 2>/dev/null)
    if [ -n "$port_pid" ]; then
        # Verify it's actually uvicorn running app:app
        if ps -o pid,args | awk -v pid="$port_pid" '$1==pid {print $0}' | grep -q "uvicorn.*app:app"; then
            echo "$port_pid"
            return 0
        fi
    fi

    # Find by process name/command
    local cmd_pid=$(pgrep -f "uvicorn.*app:app.*--port.*$PORT" 2>/dev/null | head -n1)
    if [ -n "$cmd_pid" ]; then
        echo "$cmd_pid"
        return 0
    fi

    return 1
}

# Function to check status
check_status() {
    print_info "Checking admin panel status..."

    local pid=$(find_process)

    if [ -n "$pid" ]; then
        print_success "Admin panel is RUNNING"
        echo "  PID: $pid"
        echo "  Port: $PORT"
        echo "  URL: http://$HOST:$PORT/admin"

        # Show process details
        if command -v ps > /dev/null; then
            echo ""
            echo "Process details:"
            # BusyBox-compatible process output
            ps -o pid,args | awk -v pid="$pid" '$1==pid {print}' || echo "  (Unable to display process details)"
        fi

        # Check if it's responding
        if command -v curl > /dev/null; then
            echo ""
            print_info "Checking if server is responding..."
            if curl -s -o /dev/null -w "%{http_code}" "http://$HOST:$PORT/admin" | grep -q "200\|301\|302"; then
                print_success "Server is responding correctly"
            else
                print_warning "Server may not be responding correctly"
            fi
        fi

        return 0
    else
        print_warning "Admin panel is NOT running"
        return 1
    fi
}

# Function to kill the admin panel
kill_admin() {
    print_info "Stopping admin panel..."

    local pid=$(find_process)

    if [ -z "$pid" ]; then
        print_warning "Admin panel is not running"
        # Clean up PID file if it exists
        [ -f "$PID_FILE" ] && rm -f "$PID_FILE"
        return 0
    fi

    print_info "Found process with PID: $pid"

    # Try graceful shutdown first (SIGTERM)
    print_info "Sending SIGTERM signal..."
    kill -TERM "$pid" 2>/dev/null

    # Wait up to 10 seconds for graceful shutdown
    local count=0
    while [ $count -lt 10 ]; do
        if [ ! -d "/proc/$pid" ]; then
            print_success "Admin panel stopped gracefully"
            rm -f "$PID_FILE"
            return 0
        fi
        sleep 1
        count=$((count + 1))
    done

    # If still running, force kill
    if [ -d "/proc/$pid" ]; then
        print_warning "Process did not stop gracefully, forcing shutdown..."
        kill -KILL "$pid" 2>/dev/null
        sleep 1

        if [ ! -d "/proc/$pid" ]; then
            print_success "Admin panel stopped (forced)"
            rm -f "$PID_FILE"
            return 0
        else
            print_error "Failed to stop admin panel"
            return 1
        fi
    fi

    rm -f "$PID_FILE"
    return 0
}

# Function to start the admin panel
start_admin() {
    print_info "Starting admin panel..."

    # Check if already running
    local pid=$(find_process)
    if [ -n "$pid" ]; then
        print_warning "Admin panel is already running (PID: $pid)"
        echo "Use '$0 restart' to restart it, or '$0 kill' to stop it first"
        return 1
    fi

    # Check if virtual environment exists
    if [ ! -d "$VENV_PATH" ]; then
        print_error "Virtual environment not found at $VENV_PATH"
        echo "Please create it first: cd $ADMIN_ROOT && python3 -m venv venv"
        return 1
    fi

    # Check if uvicorn is available
    if [ ! -f "$VENV_PATH/bin/uvicorn" ]; then
        print_error "uvicorn not found in virtual environment"
        echo "Please install dependencies: cd $ADMIN_ROOT && source venv/bin/activate && pip install -r requirements.txt"
        return 1
    fi

    # Change to admin directory
    cd "$ADMIN_ROOT" || {
        print_error "Failed to change to admin directory"
        return 1
    }

    # Start the server in background
    print_info "Starting uvicorn server on $HOST:$PORT..."
    print_info "Logs will be written to: $LOG_FILE"

    # Activate venv and start uvicorn in background
    nohup bash -c "source $VENV_PATH/bin/activate && uvicorn app:app --reload --port $PORT --host $HOST" > "$LOG_FILE" 2>&1 &

    local new_pid=$!

    # Wait a moment to see if it starts successfully
    sleep 2

    # Check if process is still running
    if [ -d "/proc/$new_pid" ]; then
        # Save PID
        echo "$new_pid" > "$PID_FILE"
        print_success "Admin panel started successfully"
        echo "  PID: $new_pid"
        echo "  Port: $PORT"
        echo "  URL: http://$HOST:$PORT/admin"
        echo "  Logs: $LOG_FILE"
        echo ""
        print_info "Use '$0 status' to check status or '$0 logs' to view logs"
        return 0
    else
        print_error "Failed to start admin panel"
        echo "Check the log file for errors: $LOG_FILE"
        rm -f "$PID_FILE"
        return 1
    fi
}

# Function to restart the admin panel
restart_admin() {
    print_info "Restarting admin panel..."
    kill_admin
    sleep 1
    start_admin
}

# Function to show logs
show_logs() {
    if [ ! -f "$LOG_FILE" ]; then
        print_warning "Log file not found: $LOG_FILE"
        return 1
    fi

    print_info "Showing admin panel logs (last 50 lines)..."
    echo "=========================================="
    tail -n 50 "$LOG_FILE"
    echo ""
    print_info "To follow logs in real-time, use: tail -f $LOG_FILE"
}

# Function to show full logs
show_full_logs() {
    if [ ! -f "$LOG_FILE" ]; then
        print_warning "Log file not found: $LOG_FILE"
        return 1
    fi

    print_info "Showing full admin panel logs..."
    echo "=========================================="
    cat "$LOG_FILE"
}

# Main function
main() {
    case "$1" in
        "status"|"check")
            check_status
            ;;
        "start")
            start_admin
            ;;
        "kill"|"stop")
            kill_admin
            ;;
        "restart")
            restart_admin
            ;;
        "logs")
            show_logs
            ;;
        "log")
            show_full_logs
            ;;
        *)
            echo "Admin Panel Management Script"
            echo "============================"
            echo ""
            echo "Available commands:"
            echo "  $0 status          Check if admin panel is running"
            echo "  $0 start           Start the admin panel server"
            echo "  $0 kill            Stop the admin panel server"
            echo "  $0 restart         Restart the admin panel server"
            echo "  $0 logs            Show last 50 lines of logs"
            echo "  $0 log             Show full log file"
            echo ""
            echo "Examples:"
            echo "  $0 start           # Start the server"
            echo "  $0 status          # Check if it's running"
            echo "  $0 logs            # View recent logs"
            echo "  $0 restart        # Restart the server"
            echo ""
            echo "Configuration:"
            echo "  Admin Root: $ADMIN_ROOT"
            echo "  Port: $PORT"
            echo "  Host: $HOST"
            echo "  PID File: $PID_FILE"
            echo "  Log File: $LOG_FILE"
            ;;
    esac
}

# Run main function with all arguments
main "$@"
