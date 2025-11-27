# Tutorial Guide

Step-by-step tutorials for common development tasks, workflows, and implementation patterns. Each tutorial includes practical examples and real-world scenarios.

## 🚀 Getting Started Tutorials

### Tutorial 1: Setting Up a Modern PHP Development Environment

#### Prerequisites
- Computer running Windows, macOS, or Linux
- Basic command line knowledge
- Internet connection

#### Step 1: Install PHP and Composer

**On Ubuntu/Debian:**
```bash
# Update package list
sudo apt update

# Install PHP and required extensions
sudo apt install php8.1 php8.1-cli php8.1-fpm php8.1-mysql php8.1-xml php8.1-curl php8.1-gd php8.1-mbstring php8.1-zip

# Verify PHP installation
php --version

# Install Composer
curl -sS https://getcomposer.org/installer | php
sudo mv composer.phar /usr/local/bin/composer
composer --version
```

**On macOS:**
```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install PHP
brew install php@8.1

# Install Composer
brew install composer
```

#### Step 2: Set Up Your First Project
```bash
# Create a new directory for your project
mkdir my-php-project
cd my-php-project

# Initialize Composer
composer init

# Follow the interactive prompts:
# - Package name: your-name/my-php-project
# - Description: My first PHP project
# - Author: Your Name <your.email@example.com>
# - Minimum Stability: stable
# - License: MIT
```

#### Step 3: Create Project Structure
```bash
# Create directory structure
mkdir -p src tests public config

# Create basic files
touch src/App.php
touch public/index.php
touch tests/AppTest.php
touch config/database.php
```

#### Step 4: Set Up Autoloading
Edit `composer.json` to add autoloading:
```json
{
    "autoload": {
        "psr-4": {
            "App\\": "src/"
        }
    },
    "autoload-dev": {
        "psr-4": {
            "Tests\\": "tests/"
        }
    }
}
```

Generate autoloader:
```bash
composer dump-autoload
```

#### Step 5: Create Your First Class
Create `src/App.php`:
```php
<?php

namespace App;

class App
{
    private string $name;
    
    public function __construct(string $name = 'My PHP App')
    {
        $this->name = $name;
    }
    
    public function getName(): string
    {
        return $this->name;
    }
    
    public function greet(string $user = 'World'): string
    {
        return "Hello, {$user}! Welcome to {$this->name}.";
    }
}
```

#### Step 6: Create Entry Point
Create `public/index.php`:
```php
<?php

require_once __DIR__ . '/../vendor/autoload.php';

use App\App;

$app = new App('My Awesome PHP Project');

echo "<h1>" . $app->getName() . "</h1>";
echo "<p>" . $app->greet('Developer') . "</p>";
```

#### Step 7: Test Your Application
```bash
# Start PHP built-in server
php -S localhost:8000 -t public

# Open browser and navigate to http://localhost:8000
```

**Expected Result:** You should see your application running with the greeting message.

---

### Tutorial 2: Building a RESTful API with PHP

#### Prerequisites
- Completed Tutorial 1
- Basic understanding of HTTP methods
- Understanding of JSON format

#### Step 1: Install Dependencies
```bash
# Install required packages
composer require slim/slim:"4.*"
composer require slim/psr7
composer require --dev phpunit/phpunit
```

#### Step 2: Create API Structure
```bash
# Create API directories
mkdir -p src/Controllers src/Models src/Middleware
touch src/Controllers/UserController.php
touch src/Models/User.php
touch src/routes.php
```

#### Step 3: Set Up Slim Framework
Create `public/index.php`:
```php
<?php

use Slim\Factory\AppFactory;
use Psr\Http\Message\ResponseInterface as Response;
use Psr\Http\Message\ServerRequestInterface as Request;

require __DIR__ . '/../vendor/autoload.php';

// Create Slim app
$app = AppFactory::create();

// Add error middleware
$app->addErrorMiddleware(true, true, true);

// Add routes
$app->get('/api/users', function (Request $request, Response $response) {
    $users = [
        ['id' => 1, 'name' => 'John Doe', 'email' => 'john@example.com'],
        ['id' => 2, 'name' => 'Jane Smith', 'email' => 'jane@example.com']
    ];
    
    $response->getBody()->write(json_encode($users));
    return $response->withHeader('Content-Type', 'application/json');
});

$app->get('/api/users/{id}', function (Request $request, Response $response, $args) {
    $id = (int) $args['id'];
    
    // Simulate database lookup
    $user = ['id' => $id, 'name' => 'User ' . $id, 'email' => 'user' . $id . '@example.com'];
    
    $response->getBody()->write(json_encode($user));
    return $response->withHeader('Content-Type', 'application/json');
});

$app->post('/api/users', function (Request $request, Response $response) {
    $data = json_decode($request->getBody()->getContents(), true);
    
    // Simulate creating user
    $user = [
        'id' => rand(100, 999),
        'name' => $data['name'] ?? 'Unknown',
        'email' => $data['email'] ?? 'unknown@example.com',
        'created_at' => date('Y-m-d H:i:s')
    ];
    
    $response->getBody()->write(json_encode($user));
    return $response->withHeader('Content-Type', 'application/json')->withStatus(201);
});

$app->run();
```

#### Step 4: Test Your API
```bash
# Start the server
php -S localhost:8000 -t public

# Test GET request (in another terminal)
curl http://localhost:8000/api/users

# Test POST request
curl -X POST http://localhost:8000/api/users \
  -H "Content-Type: application/json" \
  -d '{"name":"New User","email":"newuser@example.com"}'
```

#### Step 5: Add User Controller
Create `src/Controllers/UserController.php`:
```php
<?php

namespace App\Controllers;

use Psr\Http\Message\ResponseInterface as Response;
use Psr\Http\Message\ServerRequestInterface as Request;

class UserController
{
    public function index(Request $request, Response $response): Response
    {
        $users = $this->getAllUsers();
        
        $response->getBody()->write(json_encode($users));
        return $response->withHeader('Content-Type', 'application/json');
    }
    
    public function show(Request $request, Response $response, array $args): Response
    {
        $id = (int) $args['id'];
        $user = $this->getUserById($id);
        
        if (!$user) {
            $error = ['error' => 'User not found'];
            $response->getBody()->write(json_encode($error));
            return $response->withHeader('Content-Type', 'application/json')->withStatus(404);
        }
        
        $response->getBody()->write(json_encode($user));
        return $response->withHeader('Content-Type', 'application/json');
    }
    
    public function create(Request $request, Response $response): Response
    {
        $data = json_decode($request->getBody()->getContents(), true);
        
        // Validate input
        if (empty($data['name']) || empty($data['email'])) {
            $error = ['error' => 'Name and email are required'];
            $response->getBody()->write(json_encode($error));
            return $response->withHeader('Content-Type', 'application/json')->withStatus(400);
        }
        
        $user = $this->createUser($data);
        
        $response->getBody()->write(json_encode($user));
        return $response->withHeader('Content-Type', 'application/json')->withStatus(201);
    }
    
    private function getAllUsers(): array
    {
        // Simulate database query
        return [
            ['id' => 1, 'name' => 'John Doe', 'email' => 'john@example.com'],
            ['id' => 2, 'name' => 'Jane Smith', 'email' => 'jane@example.com']
        ];
    }
    
    private function getUserById(int $id): ?array
    {
        $users = $this->getAllUsers();
        foreach ($users as $user) {
            if ($user['id'] === $id) {
                return $user;
            }
        }
        return null;
    }
    
    private function createUser(array $data): array
    {
        return [
            'id' => rand(100, 999),
            'name' => $data['name'],
            'email' => $data['email'],
            'created_at' => date('Y-m-d H:i:s')
        ];
    }
}
```

#### Step 6: Update Routes to Use Controller
Update `public/index.php`:
```php
<?php

use Slim\Factory\AppFactory;
use App\Controllers\UserController;

require __DIR__ . '/../vendor/autoload.php';

$app = AppFactory::create();
$app->addErrorMiddleware(true, true, true);

// User routes
$app->get('/api/users', [UserController::class, 'index']);
$app->get('/api/users/{id}', [UserController::class, 'show']);
$app->post('/api/users', [UserController::class, 'create']);

$app->run();
```

**Expected Result:** A working RESTful API with proper error handling and validation.

---

### Tutorial 3: Creating a Modern JavaScript Application with Alpine.js

#### Prerequisites
- Basic HTML, CSS, and JavaScript knowledge
- Text editor or IDE
- Web browser

#### Step 1: Set Up Project Structure
```bash
# Create project directory
mkdir alpine-todo-app
cd alpine-todo-app

# Create files
touch index.html
touch style.css
touch app.js
```

#### Step 2: Create Basic HTML Structure
Create `index.html`:
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Alpine.js Todo App</title>
    <script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js"></script>
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
    <link rel="stylesheet" href="style.css">
</head>
<body class="bg-gray-100 min-h-screen py-8">
    <div class="container mx-auto max-w-md">
        <h1 class="text-3xl font-bold text-center mb-8 text-gray-800">Todo App</h1>
        
        <div x-data="todoApp()" class="bg-white rounded-lg shadow-md p-6">
            <!-- Add Todo Form -->
            <form @submit.prevent="addTodo()" class="mb-6">
                <div class="flex gap-2">
                    <input 
                        type="text" 
                        x-model="newTodo"
                        placeholder="Add a new todo..."
                        class="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                        required
                    >
                    <button 
                        type="submit"
                        class="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                        Add
                    </button>
                </div>
            </form>
            
            <!-- Filter Buttons -->
            <div class="flex gap-2 mb-4">
                <button 
                    @click="filter = 'all'"
                    :class="filter === 'all' ? 'bg-blue-500 text-white' : 'bg-gray-200 text-gray-700'"
                    class="px-4 py-2 rounded-lg"
                >
                    All (<span x-text="todos.length"></span>)
                </button>
                <button 
                    @click="filter = 'active'"
                    :class="filter === 'active' ? 'bg-blue-500 text-white' : 'bg-gray-200 text-gray-700'"
                    class="px-4 py-2 rounded-lg"
                >
                    Active (<span x-text="activeTodos.length"></span>)
                </button>
                <button 
                    @click="filter = 'completed'"
                    :class="filter === 'completed' ? 'bg-blue-500 text-white' : 'bg-gray-200 text-gray-700'"
                    class="px-4 py-2 rounded-lg"
                >
                    Completed (<span x-text="completedTodos.length"></span>)
                </button>
            </div>
            
            <!-- Todo List -->
            <div class="space-y-2">
                <template x-for="todo in filteredTodos" :key="todo.id">
                    <div class="flex items-center gap-3 p-3 border border-gray-200 rounded-lg">
                        <input 
                            type="checkbox" 
                            x-model="todo.completed"
                            class="w-5 h-5 text-blue-600"
                        >
                        <span 
                            :class="todo.completed ? 'line-through text-gray-500' : 'text-gray-800'"
                            class="flex-1"
                            x-text="todo.text"
                        ></span>
                        <button 
                            @click="removeTodo(todo.id)"
                            class="px-3 py-1 bg-red-500 text-white rounded hover:bg-red-600"
                        >
                            Delete
                        </button>
                    </div>
                </template>
            </div>
            
            <!-- Empty State -->
            <div x-show="filteredTodos.length === 0" class="text-center py-8 text-gray-500">
                <p x-text="emptyMessage"></p>
            </div>
            
            <!-- Clear Completed -->
            <div x-show="completedTodos.length > 0" class="mt-4 text-center">
                <button 
                    @click="clearCompleted()"
                    class="px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600"
                >
                    Clear Completed
                </button>
            </div>
        </div>
    </div>
    
    <script src="app.js"></script>
</body>
</html>
```

#### Step 3: Create Alpine.js Component
Create `app.js`:
```javascript
function todoApp() {
    return {
        newTodo: '',
        filter: 'all',
        todos: [
            { id: 1, text: 'Learn Alpine.js', completed: false },
            { id: 2, text: 'Build a todo app', completed: false },
            { id: 3, text: 'Master JavaScript', completed: true }
        ],
        
        get activeTodos() {
            return this.todos.filter(todo => !todo.completed);
        },
        
        get completedTodos() {
            return this.todos.filter(todo => todo.completed);
        },
        
        get filteredTodos() {
            switch (this.filter) {
                case 'active':
                    return this.activeTodos;
                case 'completed':
                    return this.completedTodos;
                default:
                    return this.todos;
            }
        },
        
        get emptyMessage() {
            switch (this.filter) {
                case 'active':
                    return 'No active todos';
                case 'completed':
                    return 'No completed todos';
                default:
                    return 'No todos yet';
            }
        },
        
        addTodo() {
            if (this.newTodo.trim()) {
                this.todos.push({
                    id: Date.now(),
                    text: this.newTodo.trim(),
                    completed: false
                });
                this.newTodo = '';
                this.saveTodos();
            }
        },
        
        removeTodo(id) {
            this.todos = this.todos.filter(todo => todo.id !== id);
            this.saveTodos();
        },
        
        clearCompleted() {
            this.todos = this.activeTodos;
            this.saveTodos();
        },
        
        saveTodos() {
            localStorage.setItem('alpine-todos', JSON.stringify(this.todos));
        },
        
        loadTodos() {
            const saved = localStorage.getItem('alpine-todos');
            if (saved) {
                this.todos = JSON.parse(saved);
            }
        },
        
        init() {
            this.loadTodos();
        }
    }
}
```

#### Step 4: Add Custom Styles
Create `style.css`:
```css
/* Custom styles for the todo app */
.container {
    animation: fadeIn 0.5s ease-in;
}

@keyframes fadeIn {
    from {
        opacity: 0;
        transform: translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

/* Smooth transitions */
input[type="checkbox"] {
    transition: all 0.2s ease;
}

button {
    transition: all 0.2s ease;
}

/* Custom checkbox styling */
input[type="checkbox"]:checked {
    transform: scale(1.1);
}

/* Todo item animations */
.todo-item {
    transition: all 0.3s ease;
}

.todo-item:hover {
    transform: translateX(4px);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}
```

#### Step 5: Test Your Application
```bash
# Open index.html in your web browser
# Or use a simple HTTP server:

# Python 3
python -m http.server 8000

# Node.js (if you have http-server installed)
npx http-server

# Navigate to http://localhost:8000
```

#### Step 6: Add Advanced Features
Enhance your app with additional features:

**Add drag and drop reordering:**
```javascript
// Add to your todoApp function
dragStart(event, todo) {
    event.dataTransfer.setData('text/plain', todo.id);
},

dragOver(event) {
    event.preventDefault();
},

drop(event, targetTodo) {
    event.preventDefault();
    const draggedId = parseInt(event.dataTransfer.getData('text/plain'));
    const draggedIndex = this.todos.findIndex(todo => todo.id === draggedId);
    const targetIndex = this.todos.findIndex(todo => todo.id === targetTodo.id);
    
    if (draggedIndex !== -1 && targetIndex !== -1) {
        const draggedTodo = this.todos.splice(draggedIndex, 1)[0];
        this.todos.splice(targetIndex, 0, draggedTodo);
        this.saveTodos();
    }
}
```

**Add todo categories:**
```javascript
// Extend the todo object structure
{
    id: Date.now(),
    text: this.newTodo.trim(),
    completed: false,
    category: this.selectedCategory || 'general',
    priority: this.selectedPriority || 'medium',
    createdAt: new Date().toISOString(),
    dueDate: this.dueDate || null
}
```

**Expected Result:** A fully functional todo application with modern UI, local storage persistence, and interactive features.

---

### Tutorial 4: Database Integration with PDO

#### Prerequisites
- Completed previous PHP tutorials
- MySQL or SQLite installed
- Basic SQL knowledge

#### Step 1: Set Up Database
Create a MySQL database and table:
```sql
CREATE DATABASE todo_app;
USE todo_app;

CREATE TABLE todos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

INSERT INTO todos (title, description) VALUES 
('Learn PHP', 'Master PHP programming language'),
('Build a web app', 'Create a full-stack web application'),
('Deploy to production', 'Learn about deployment and DevOps');
```

#### Step 2: Create Database Configuration
Create `config/database.php`:
```php
<?php

return [
    'host' => 'localhost',
    'dbname' => 'todo_app',
    'username' => 'your_username',
    'password' => 'your_password',
    'charset' => 'utf8mb4',
    'options' => [
        PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
        PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
        PDO::ATTR_EMULATE_PREPARES => false,
    ]
];
```

#### Step 3: Create Database Connection Class
Create `src/Database/Connection.php`:
```php
<?php

namespace App\Database;

use PDO;
use PDOException;

class Connection
{
    private static ?PDO $instance = null;
    
    public static function getInstance(): PDO
    {
        if (self::$instance === null) {
            $config = require __DIR__ . '/../../config/database.php';
            
            try {
                $dsn = "mysql:host={$config['host']};dbname={$config['dbname']};charset={$config['charset']}";
                
                self::$instance = new PDO(
                    $dsn,
                    $config['username'],
                    $config['password'],
                    $config['options']
                );
            } catch (PDOException $e) {
                throw new PDOException("Connection failed: " . $e->getMessage());
            }
        }
        
        return self::$instance;
    }
    
    private function __construct() {}
    private function __clone() {}
    public function __wakeup() {}
}
```

#### Step 4: Create Todo Model
Create `src/Models/Todo.php`:
```php
<?php

namespace App\Models;

use App\Database\Connection;
use PDO;

class Todo
{
    private PDO $db;
    
    public function __construct()
    {
        $this->db = Connection::getInstance();
    }
    
    public function getAll(): array
    {
        $stmt = $this->db->query("
            SELECT id, title, description, completed, created_at, updated_at 
            FROM todos 
            ORDER BY created_at DESC
        ");
        
        return $stmt->fetchAll();
    }
    
    public function getById(int $id): ?array
    {
        $stmt = $this->db->prepare("
            SELECT id, title, description, completed, created_at, updated_at 
            FROM todos 
            WHERE id = ?
        ");
        
        $stmt->execute([$id]);
        $result = $stmt->fetch();
        
        return $result ?: null;
    }
    
    public function create(array $data): array
    {
        $stmt = $this->db->prepare("
            INSERT INTO todos (title, description, completed) 
            VALUES (?, ?, ?)
        ");
        
        $stmt->execute([
            $data['title'],
            $data['description'] ?? '',
            $data['completed'] ?? false
        ]);
        
        $id = $this->db->lastInsertId();
        return $this->getById((int) $id);
    }
    
    public function update(int $id, array $data): ?array
    {
        $fields = [];
        $values = [];
        
        if (isset($data['title'])) {
            $fields[] = 'title = ?';
            $values[] = $data['title'];
        }
        
        if (isset($data['description'])) {
            $fields[] = 'description = ?';
            $values[] = $data['description'];
        }
        
        if (isset($data['completed'])) {
            $fields[] = 'completed = ?';
            $values[] = $data['completed'];
        }
        
        if (empty($fields)) {
            return $this->getById($id);
        }
        
        $values[] = $id;
        
        $stmt = $this->db->prepare("
            UPDATE todos 
            SET " . implode(', ', $fields) . " 
            WHERE id = ?
        ");
        
        $stmt->execute($values);
        
        return $this->getById($id);
    }
    
    public function delete(int $id): bool
    {
        $stmt = $this->db->prepare("DELETE FROM todos WHERE id = ?");
        return $stmt->execute([$id]);
    }
    
    public function getCompleted(): array
    {
        $stmt = $this->db->query("
            SELECT id, title, description, completed, created_at, updated_at 
            FROM todos 
            WHERE completed = 1 
            ORDER BY updated_at DESC
        ");
        
        return $stmt->fetchAll();
    }
    
    public function getPending(): array
    {
        $stmt = $this->db->query("
            SELECT id, title, description, completed, created_at, updated_at 
            FROM todos 
            WHERE completed = 0 
            ORDER BY created_at DESC
        ");
        
        return $stmt->fetchAll();
    }
}
```

#### Step 5: Update Controller to Use Database
Update `src/Controllers/TodoController.php`:
```php
<?php

namespace App\Controllers;

use App\Models\Todo;
use Psr\Http\Message\ResponseInterface as Response;
use Psr\Http\Message\ServerRequestInterface as Request;

class TodoController
{
    private Todo $todoModel;
    
    public function __construct()
    {
        $this->todoModel = new Todo();
    }
    
    public function index(Request $request, Response $response): Response
    {
        try {
            $todos = $this->todoModel->getAll();
            
            $response->getBody()->write(json_encode([
                'success' => true,
                'data' => $todos
            ]));
            
            return $response->withHeader('Content-Type', 'application/json');
        } catch (\Exception $e) {
            return $this->errorResponse($response, 'Failed to fetch todos', 500);
        }
    }
    
    public function show(Request $request, Response $response, array $args): Response
    {
        try {
            $id = (int) $args['id'];
            $todo = $this->todoModel->getById($id);
            
            if (!$todo) {
                return $this->errorResponse($response, 'Todo not found', 404);
            }
            
            $response->getBody()->write(json_encode([
                'success' => true,
                'data' => $todo
            ]));
            
            return $response->withHeader('Content-Type', 'application/json');
        } catch (\Exception $e) {
            return $this->errorResponse($response, 'Failed to fetch todo', 500);
        }
    }
    
    public function create(Request $request, Response $response): Response
    {
        try {
            $data = json_decode($request->getBody()->getContents(), true);
            
            // Validate input
            if (empty($data['title'])) {
                return $this->errorResponse($response, 'Title is required', 400);
            }
            
            $todo = $this->todoModel->create($data);
            
            $response->getBody()->write(json_encode([
                'success' => true,
                'data' => $todo,
                'message' => 'Todo created successfully'
            ]));
            
            return $response->withHeader('Content-Type', 'application/json')->withStatus(201);
        } catch (\Exception $e) {
            return $this->errorResponse($response, 'Failed to create todo', 500);
        }
    }
    
    public function update(Request $request, Response $response, array $args): Response
    {
        try {
            $id = (int) $args['id'];
            $data = json_decode($request->getBody()->getContents(), true);
            
            $todo = $this->todoModel->update($id, $data);
            
            if (!$todo) {
                return $this->errorResponse($response, 'Todo not found', 404);
            }
            
            $response->getBody()->write(json_encode([
                'success' => true,
                'data' => $todo,
                'message' => 'Todo updated successfully'
            ]));
            
            return $response->withHeader('Content-Type', 'application/json');
        } catch (\Exception $e) {
            return $this->errorResponse($response, 'Failed to update todo', 500);
        }
    }
    
    public function delete(Request $request, Response $response, array $args): Response
    {
        try {
            $id = (int) $args['id'];
            
            if (!$this->todoModel->getById($id)) {
                return $this->errorResponse($response, 'Todo not found', 404);
            }
            
            $this->todoModel->delete($id);
            
            $response->getBody()->write(json_encode([
                'success' => true,
                'message' => 'Todo deleted successfully'
            ]));
            
            return $response->withHeader('Content-Type', 'application/json');
        } catch (\Exception $e) {
            return $this->errorResponse($response, 'Failed to delete todo', 500);
        }
    }
    
    private function errorResponse(Response $response, string $message, int $status): Response
    {
        $error = [
            'success' => false,
            'error' => $message
        ];
        
        $response->getBody()->write(json_encode($error));
        return $response->withHeader('Content-Type', 'application/json')->withStatus($status);
    }
}
```

#### Step 6: Test Database Integration
```bash
# Test creating a todo
curl -X POST http://localhost:8000/api/todos \
  -H "Content-Type: application/json" \
  -d '{"title":"Test Database Todo","description":"Testing database integration"}'

# Test getting all todos
curl http://localhost:8000/api/todos

# Test updating a todo
curl -X PUT http://localhost:8000/api/todos/1 \
  -H "Content-Type: application/json" \
  -d '{"completed":true}'

# Test deleting a todo
curl -X DELETE http://localhost:8000/api/todos/1
```

**Expected Result:** A fully functional API with database persistence, proper error handling, and CRUD operations.

---

## 🎯 Advanced Tutorials

### Tutorial 5: Implementing Authentication with JWT

#### Step 1: Install JWT Library
```bash
composer require firebase/php-jwt
```

#### Step 2: Create User Model
Create `src/Models/User.php`:
```php
<?php

namespace App\Models;

use App\Database\Connection;
use PDO;

class User
{
    private PDO $db;
    
    public function __construct()
    {
        $this->db = Connection::getInstance();
    }
    
    public function create(array $data): array
    {
        $hashedPassword = password_hash($data['password'], PASSWORD_DEFAULT);
        
        $stmt = $this->db->prepare("
            INSERT INTO users (name, email, password) 
            VALUES (?, ?, ?)
        ");
        
        $stmt->execute([
            $data['name'],
            $data['email'],
            $hashedPassword
        ]);
        
        $id = $this->db->lastInsertId();
        return $this->getById((int) $id);
    }
    
    public function getByEmail(string $email): ?array
    {
        $stmt = $this->db->prepare("
            SELECT id, name, email, password, created_at 
            FROM users 
            WHERE email = ?
        ");
        
        $stmt->execute([$email]);
        $result = $stmt->fetch();
        
        return $result ?: null;
    }
    
    public function getById(int $id): ?array
    {
        $stmt = $this->db->prepare("
            SELECT id, name, email, created_at 
            FROM users 
            WHERE id = ?
        ");
        
        $stmt->execute([$id]);
        $result = $stmt->fetch();
        
        return $result ?: null;
    }
    
    public function verifyPassword(string $password, string $hash): bool
    {
        return password_verify($password, $hash);
    }
}
```

#### Step 3: Create JWT Service
Create `src/Services/JWTService.php`:
```php
<?php

namespace App\Services;

use Firebase\JWT\JWT;
use Firebase\JWT\Key;
use Exception;

class JWTService
{
    private string $secretKey;
    private string $algorithm;
    
    public function __construct()
    {
        $this->secretKey = $_ENV['JWT_SECRET'] ?? 'your-secret-key';
        $this->algorithm = 'HS256';
    }
    
    public function generateToken(array $payload): string
    {
        $payload['iat'] = time();
        $payload['exp'] = time() + (24 * 60 * 60); // 24 hours
        
        return JWT::encode($payload, $this->secretKey, $this->algorithm);
    }
    
    public function validateToken(string $token): ?array
    {
        try {
            $decoded = JWT::decode($token, new Key($this->secretKey, $this->algorithm));
            return (array) $decoded;
        } catch (Exception $e) {
            return null;
        }
    }
}
```

#### Step 4: Create Auth Controller
Create `src/Controllers/AuthController.php`:
```php
<?php

namespace App\Controllers;

use App\Models\User;
use App\Services\JWTService;
use Psr\Http\Message\ResponseInterface as Response;
use Psr\Http\Message\ServerRequestInterface as Request;

class AuthController
{
    private User $userModel;
    private JWTService $jwtService;
    
    public function __construct()
    {
        $this->userModel = new User();
        $this->jwtService = new JWTService();
    }
    
    public function register(Request $request, Response $response): Response
    {
        try {
            $data = json_decode($request->getBody()->getContents(), true);
            
            // Validate input
            if (empty($data['name']) || empty($data['email']) || empty($data['password'])) {
                return $this->errorResponse($response, 'All fields are required', 400);
            }
            
            // Check if user already exists
            if ($this->userModel->getByEmail($data['email'])) {
                return $this->errorResponse($response, 'User already exists', 409);
            }
            
            // Create user
            $user = $this->userModel->create($data);
            
            // Generate token
            $token = $this->jwtService->generateToken([
                'user_id' => $user['id'],
                'email' => $user['email']
            ]);
            
            $response->getBody()->write(json_encode([
                'success' => true,
                'data' => [
                    'user' => $user,
                    'token' => $token
                ],
                'message' => 'User registered successfully'
            ]));
            
            return $response->withHeader('Content-Type', 'application/json')->withStatus(201);
        } catch (\Exception $e) {
            return $this->errorResponse($response, 'Registration failed', 500);
        }
    }
    
    public function login(Request $request, Response $response): Response
    {
        try {
            $data = json_decode($request->getBody()->getContents(), true);
            
            // Validate input
            if (empty($data['email']) || empty($data['password'])) {
                return $this->errorResponse($response, 'Email and password are required', 400);
            }
            
            // Find user
            $user = $this->userModel->getByEmail($data['email']);
            if (!$user) {
                return $this->errorResponse($response, 'Invalid credentials', 401);
            }
            
            // Verify password
            if (!$this->userModel->verifyPassword($data['password'], $user['password'])) {
                return $this->errorResponse($response, 'Invalid credentials', 401);
            }
            
            // Remove password from response
            unset($user['password']);
            
            // Generate token
            $token = $this->jwtService->generateToken([
                'user_id' => $user['id'],
                'email' => $user['email']
            ]);
            
            $response->getBody()->write(json_encode([
                'success' => true,
                'data' => [
                    'user' => $user,
                    'token' => $token
                ],
                'message' => 'Login successful'
            ]));
            
            return $response->withHeader('Content-Type', 'application/json');
        } catch (\Exception $e) {
            return $this->errorResponse($response, 'Login failed', 500);
        }
    }
    
    private function errorResponse(Response $response, string $message, int $status): Response
    {
        $error = [
            'success' => false,
            'error' => $message
        ];
        
        $response->getBody()->write(json_encode($error));
        return $response->withHeader('Content-Type', 'application/json')->withStatus($status);
    }
}
```

**Expected Result:** Complete authentication system with user registration, login, and JWT token generation.

---

*This tutorial guide provides hands-on, practical examples for common development scenarios. Each tutorial builds upon previous knowledge and includes real-world applications.*