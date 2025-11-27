# Code Examples

A comprehensive collection of practical code examples, snippets, and implementation patterns for common development scenarios.

## 🚀 PHP Examples

### Authentication & Security

#### JWT Authentication Implementation
```php
<?php

namespace App\Auth;

use Firebase\JWT\JWT;
use Firebase\JWT\Key;

class JWTManager
{
    private string $secretKey;
    private string $algorithm = 'HS256';
    private int $expiration = 86400; // 24 hours
    
    public function __construct(string $secretKey)
    {
        $this->secretKey = $secretKey;
    }
    
    public function generateToken(array $payload): string
    {
        $now = time();
        $payload = array_merge($payload, [
            'iat' => $now,
            'exp' => $now + $this->expiration,
            'iss' => 'your-app.com'
        ]);
        
        return JWT::encode($payload, $this->secretKey, $this->algorithm);
    }
    
    public function validateToken(string $token): ?array
    {
        try {
            $decoded = JWT::decode($token, new Key($this->secretKey, $this->algorithm));
            return (array) $decoded;
        } catch (\Exception $e) {
            return null;
        }
    }
    
    public function refreshToken(string $token): ?string
    {
        $payload = $this->validateToken($token);
        if (!$payload) {
            return null;
        }
        
        // Remove timing claims
        unset($payload['iat'], $payload['exp']);
        
        return $this->generateToken($payload);
    }
}

// Usage Example
$jwtManager = new JWTManager($_ENV['JWT_SECRET']);

// Generate token
$token = $jwtManager->generateToken([
    'user_id' => 123,
    'email' => 'user@example.com',
    'role' => 'admin'
]);

// Validate token
$payload = $jwtManager->validateToken($token);
if ($payload) {
    echo "User ID: " . $payload['user_id'];
}
```

#### Password Hashing and Verification
```php
<?php

class PasswordManager
{
    private const DEFAULT_COST = 12;
    
    public static function hash(string $password, int $cost = self::DEFAULT_COST): string
    {
        $options = ['cost' => $cost];
        return password_hash($password, PASSWORD_ARGON2ID, $options);
    }
    
    public static function verify(string $password, string $hash): bool
    {
        return password_verify($password, $hash);
    }
    
    public static function needsRehash(string $hash, int $cost = self::DEFAULT_COST): bool
    {
        $options = ['cost' => $cost];
        return password_needs_rehash($hash, PASSWORD_ARGON2ID, $options);
    }
    
    public static function generateSecurePassword(int $length = 16): string
    {
        $chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*';
        $password = '';
        
        for ($i = 0; $i < $length; $i++) {
            $password .= $chars[random_int(0, strlen($chars) - 1)];
        }
        
        return $password;
    }
}

// Usage Examples
$password = 'user_password123';
$hash = PasswordManager::hash($password);

if (PasswordManager::verify($password, $hash)) {
    echo "Password is correct!";
}

if (PasswordManager::needsRehash($hash)) {
    $newHash = PasswordManager::hash($password);
    // Update hash in database
}

$securePassword = PasswordManager::generateSecurePassword(20);
```

### Database Operations

#### Repository Pattern Implementation
```php
<?php

namespace App\Repositories;

use PDO;
use PDOStatement;

abstract class BaseRepository
{
    protected PDO $db;
    protected string $table;
    protected string $primaryKey = 'id';
    
    public function __construct(PDO $db)
    {
        $this->db = $db;
    }
    
    public function find(int $id): ?array
    {
        $stmt = $this->db->prepare("SELECT * FROM {$this->table} WHERE {$this->primaryKey} = ?");
        $stmt->execute([$id]);
        $result = $stmt->fetch(PDO::FETCH_ASSOC);
        
        return $result ?: null;
    }
    
    public function findAll(array $conditions = [], string $orderBy = '', int $limit = 0): array
    {
        $sql = "SELECT * FROM {$this->table}";
        $params = [];
        
        if (!empty($conditions)) {
            $sql .= " WHERE " . $this->buildWhereClause($conditions, $params);
        }
        
        if ($orderBy) {
            $sql .= " ORDER BY {$orderBy}";
        }
        
        if ($limit > 0) {
            $sql .= " LIMIT {$limit}";
        }
        
        $stmt = $this->db->prepare($sql);
        $stmt->execute($params);
        
        return $stmt->fetchAll(PDO::FETCH_ASSOC);
    }
    
    public function create(array $data): array
    {
        $columns = array_keys($data);
        $placeholders = array_fill(0, count($columns), '?');
        
        $sql = "INSERT INTO {$this->table} (" . implode(', ', $columns) . ") VALUES (" . implode(', ', $placeholders) . ")";
        
        $stmt = $this->db->prepare($sql);
        $stmt->execute(array_values($data));
        
        $id = $this->db->lastInsertId();
        return $this->find((int) $id);
    }
    
    public function update(int $id, array $data): ?array
    {
        if (empty($data)) {
            return $this->find($id);
        }
        
        $columns = array_keys($data);
        $setClause = implode(' = ?, ', $columns) . ' = ?';
        
        $sql = "UPDATE {$this->table} SET {$setClause} WHERE {$this->primaryKey} = ?";
        
        $params = array_values($data);
        $params[] = $id;
        
        $stmt = $this->db->prepare($sql);
        $stmt->execute($params);
        
        return $this->find($id);
    }
    
    public function delete(int $id): bool
    {
        $stmt = $this->db->prepare("DELETE FROM {$this->table} WHERE {$this->primaryKey} = ?");
        return $stmt->execute([$id]);
    }
    
    private function buildWhereClause(array $conditions, array &$params): string
    {
        $clauses = [];
        
        foreach ($conditions as $column => $value) {
            if (is_array($value)) {
                $placeholders = array_fill(0, count($value), '?');
                $clauses[] = "{$column} IN (" . implode(', ', $placeholders) . ")";
                $params = array_merge($params, $value);
            } else {
                $clauses[] = "{$column} = ?";
                $params[] = $value;
            }
        }
        
        return implode(' AND ', $clauses);
    }
}

// Concrete Repository
class UserRepository extends BaseRepository
{
    protected string $table = 'users';
    
    public function findByEmail(string $email): ?array
    {
        $stmt = $this->db->prepare("SELECT * FROM {$this->table} WHERE email = ?");
        $stmt->execute([$email]);
        $result = $stmt->fetch(PDO::FETCH_ASSOC);
        
        return $result ?: null;
    }
    
    public function findActiveUsers(): array
    {
        return $this->findAll(['status' => 'active'], 'created_at DESC');
    }
    
    public function searchByName(string $name): array
    {
        $stmt = $this->db->prepare("SELECT * FROM {$this->table} WHERE name LIKE ? ORDER BY name");
        $stmt->execute(["%{$name}%"]);
        
        return $stmt->fetchAll(PDO::FETCH_ASSOC);
    }
}

// Usage
$userRepo = new UserRepository($pdo);

// Find user by ID
$user = $userRepo->find(1);

// Create new user
$newUser = $userRepo->create([
    'name' => 'John Doe',
    'email' => 'john@example.com',
    'status' => 'active'
]);

// Update user
$updatedUser = $userRepo->update(1, ['status' => 'inactive']);

// Find by email
$user = $userRepo->findByEmail('john@example.com');
```

#### Database Transaction Manager
```php
<?php

class TransactionManager
{
    private PDO $db;
    private bool $inTransaction = false;
    
    public function __construct(PDO $db)
    {
        $this->db = $db;
    }
    
    public function transaction(callable $callback)
    {
        $this->begin();
        
        try {
            $result = $callback($this->db);
            $this->commit();
            return $result;
        } catch (\Exception $e) {
            $this->rollback();
            throw $e;
        }
    }
    
    public function begin(): void
    {
        if (!$this->inTransaction) {
            $this->db->beginTransaction();
            $this->inTransaction = true;
        }
    }
    
    public function commit(): void
    {
        if ($this->inTransaction) {
            $this->db->commit();
            $this->inTransaction = false;
        }
    }
    
    public function rollback(): void
    {
        if ($this->inTransaction) {
            $this->db->rollBack();
            $this->inTransaction = false;
        }
    }
    
    public function isInTransaction(): bool
    {
        return $this->inTransaction;
    }
}

// Usage Example
$transactionManager = new TransactionManager($pdo);

try {
    $result = $transactionManager->transaction(function($db) {
        // Multiple database operations
        $userRepo = new UserRepository($db);
        $orderRepo = new OrderRepository($db);
        
        $user = $userRepo->create(['name' => 'John', 'email' => 'john@example.com']);
        $order = $orderRepo->create(['user_id' => $user['id'], 'total' => 99.99]);
        
        return ['user' => $user, 'order' => $order];
    });
    
    echo "Transaction completed successfully!";
} catch (\Exception $e) {
    echo "Transaction failed: " . $e->getMessage();
}
```

### API Development

#### RESTful API Controller Pattern
```php
<?php

namespace App\Controllers\Api;

use App\Services\UserService;
use Psr\Http\Message\ResponseInterface as Response;
use Psr\Http\Message\ServerRequestInterface as Request;

class UserController extends BaseApiController
{
    private UserService $userService;
    
    public function __construct(UserService $userService)
    {
        $this->userService = $userService;
    }
    
    public function index(Request $request, Response $response): Response
    {
        try {
            $page = (int) ($request->getQueryParams()['page'] ?? 1);
            $limit = (int) ($request->getQueryParams()['limit'] ?? 20);
            $search = $request->getQueryParams()['search'] ?? '';
            
            $result = $this->userService->getUsers($page, $limit, $search);
            
            return $this->successResponse($response, $result, 'Users retrieved successfully');
        } catch (\Exception $e) {
            return $this->errorResponse($response, 'Failed to retrieve users', 500);
        }
    }
    
    public function show(Request $request, Response $response, array $args): Response
    {
        try {
            $id = (int) $args['id'];
            $user = $this->userService->getUserById($id);
            
            if (!$user) {
                return $this->errorResponse($response, 'User not found', 404);
            }
            
            return $this->successResponse($response, $user, 'User retrieved successfully');
        } catch (\Exception $e) {
            return $this->errorResponse($response, 'Failed to retrieve user', 500);
        }
    }
    
    public function store(Request $request, Response $response): Response
    {
        try {
            $data = $this->getJsonInput($request);
            
            // Validate input
            $validation = $this->validateUserInput($data);
            if (!$validation['valid']) {
                return $this->errorResponse($response, $validation['errors'], 422);
            }
            
            $user = $this->userService->createUser($data);
            
            return $this->successResponse($response, $user, 'User created successfully', 201);
        } catch (\Exception $e) {
            return $this->errorResponse($response, 'Failed to create user', 500);
        }
    }
    
    public function update(Request $request, Response $response, array $args): Response
    {
        try {
            $id = (int) $args['id'];
            $data = $this->getJsonInput($request);
            
            $user = $this->userService->updateUser($id, $data);
            
            if (!$user) {
                return $this->errorResponse($response, 'User not found', 404);
            }
            
            return $this->successResponse($response, $user, 'User updated successfully');
        } catch (\Exception $e) {
            return $this->errorResponse($response, 'Failed to update user', 500);
        }
    }
    
    public function destroy(Request $request, Response $response, array $args): Response
    {
        try {
            $id = (int) $args['id'];
            
            $deleted = $this->userService->deleteUser($id);
            
            if (!$deleted) {
                return $this->errorResponse($response, 'User not found', 404);
            }
            
            return $this->successResponse($response, null, 'User deleted successfully');
        } catch (\Exception $e) {
            return $this->errorResponse($response, 'Failed to delete user', 500);
        }
    }
    
    private function validateUserInput(array $data): array
    {
        $errors = [];
        
        if (empty($data['name'])) {
            $errors[] = 'Name is required';
        }
        
        if (empty($data['email'])) {
            $errors[] = 'Email is required';
        } elseif (!filter_var($data['email'], FILTER_VALIDATE_EMAIL)) {
            $errors[] = 'Email is invalid';
        }
        
        if (isset($data['password']) && strlen($data['password']) < 8) {
            $errors[] = 'Password must be at least 8 characters';
        }
        
        return [
            'valid' => empty($errors),
            'errors' => $errors
        ];
    }
}

// Base API Controller
abstract class BaseApiController
{
    protected function successResponse(Response $response, $data = null, string $message = '', int $status = 200): Response
    {
        $payload = [
            'success' => true,
            'message' => $message,
            'data' => $data
        ];
        
        $response->getBody()->write(json_encode($payload));
        return $response->withHeader('Content-Type', 'application/json')->withStatus($status);
    }
    
    protected function errorResponse(Response $response, $errors, int $status = 400): Response
    {
        $payload = [
            'success' => false,
            'errors' => is_array($errors) ? $errors : [$errors]
        ];
        
        $response->getBody()->write(json_encode($payload));
        return $response->withHeader('Content-Type', 'application/json')->withStatus($status);
    }
    
    protected function getJsonInput(Request $request): array
    {
        $input = json_decode($request->getBody()->getContents(), true);
        return $input ?? [];
    }
}
```

### Caching Strategies

#### Redis Cache Implementation
```php
<?php

namespace App\Cache;

use Redis;
use JsonException;

class RedisCache
{
    private Redis $redis;
    private string $prefix;
    private int $defaultTtl;
    
    public function __construct(Redis $redis, string $prefix = 'app:', int $defaultTtl = 3600)
    {
        $this->redis = $redis;
        $this->prefix = $prefix;
        $this->defaultTtl = $defaultTtl;
    }
    
    public function get(string $key, $default = null)
    {
        $value = $this->redis->get($this->prefix . $key);
        
        if ($value === false) {
            return $default;
        }
        
        try {
            return json_decode($value, true, 512, JSON_THROW_ON_ERROR);
        } catch (JsonException $e) {
            return $value;
        }
    }
    
    public function set(string $key, $value, int $ttl = null): bool
    {
        $ttl = $ttl ?? $this->defaultTtl;
        $serialized = is_string($value) ? $value : json_encode($value);
        
        return $this->redis->setex($this->prefix . $key, $ttl, $serialized);
    }
    
    public function delete(string $key): bool
    {
        return $this->redis->del($this->prefix . $key) > 0;
    }
    
    public function remember(string $key, callable $callback, int $ttl = null)
    {
        $value = $this->get($key);
        
        if ($value !== null) {
            return $value;
        }
        
        $value = $callback();
        $this->set($key, $value, $ttl);
        
        return $value;
    }
    
    public function flush(): bool
    {
        $keys = $this->redis->keys($this->prefix . '*');
        
        if (empty($keys)) {
            return true;
        }
        
        return $this->redis->del($keys) > 0;
    }
    
    public function increment(string $key, int $value = 1): int
    {
        return $this->redis->incrBy($this->prefix . $key, $value);
    }
    
    public function decrement(string $key, int $value = 1): int
    {
        return $this->redis->decrBy($this->prefix . $key, $value);
    }
    
    public function tags(array $tags): TaggedCache
    {
        return new TaggedCache($this, $tags);
    }
}

// Tagged Cache for cache invalidation
class TaggedCache
{
    private RedisCache $cache;
    private array $tags;
    
    public function __construct(RedisCache $cache, array $tags)
    {
        $this->cache = $cache;
        $this->tags = $tags;
    }
    
    public function get(string $key, $default = null)
    {
        return $this->cache->get($this->taggedKey($key), $default);
    }
    
    public function set(string $key, $value, int $ttl = null): bool
    {
        $this->storeTags($key);
        return $this->cache->set($this->taggedKey($key), $value, $ttl);
    }
    
    public function flush(): void
    {
        foreach ($this->tags as $tag) {
            $keys = $this->cache->get("tag:{$tag}:keys", []);
            
            foreach ($keys as $key) {
                $this->cache->delete($key);
            }
            
            $this->cache->delete("tag:{$tag}:keys");
        }
    }
    
    private function taggedKey(string $key): string
    {
        return 'tagged:' . md5(implode('|', $this->tags)) . ':' . $key;
    }
    
    private function storeTags(string $key): void
    {
        $taggedKey = $this->taggedKey($key);
        
        foreach ($this->tags as $tag) {
            $keys = $this->cache->get("tag:{$tag}:keys", []);
            $keys[] = $taggedKey;
            $this->cache->set("tag:{$tag}:keys", array_unique($keys));
        }
    }
}

// Usage Examples
$redis = new Redis();
$redis->connect('127.0.0.1', 6379);

$cache = new RedisCache($redis);

// Basic caching
$cache->set('user:123', ['name' => 'John', 'email' => 'john@example.com'], 3600);
$user = $cache->get('user:123');

// Remember pattern
$expensiveData = $cache->remember('expensive:calculation', function() {
    // Expensive operation
    sleep(2);
    return ['result' => 'computed value'];
}, 7200);

// Tagged caching
$cache->tags(['users', 'profiles'])->set('user:profile:123', $profileData);

// Flush all user-related cache
$cache->tags(['users'])->flush();
```

## 🌐 JavaScript/Alpine.js Examples

### Component Patterns

#### Reusable Modal Component
```javascript
// Modal Component
function modal() {
    return {
        isOpen: false,
        title: '',
        content: '',
        size: 'md', // sm, md, lg, xl
        
        open(title = '', content = '', size = 'md') {
            this.title = title;
            this.content = content;
            this.size = size;
            this.isOpen = true;
            document.body.style.overflow = 'hidden';
        },
        
        close() {
            this.isOpen = false;
            document.body.style.overflow = '';
        },
        
        get sizeClasses() {
            const sizes = {
                sm: 'max-w-sm',
                md: 'max-w-md',
                lg: 'max-w-lg',
                xl: 'max-w-xl'
            };
            return sizes[this.size] || sizes.md;
        }
    }
}

// Usage in HTML
/*
<div x-data="modal()" x-on:keydown.escape.window="close()">
    <!-- Trigger Button -->
    <button @click="open('Confirm Action', 'Are you sure you want to proceed?')" 
            class="bg-blue-500 text-white px-4 py-2 rounded">
        Open Modal
    </button>
    
    <!-- Modal -->
    <div x-show="isOpen" 
         x-transition:enter="transition ease-out duration-300"
         x-transition:enter-start="opacity-0"
         x-transition:enter-end="opacity-100"
         x-transition:leave="transition ease-in duration-200"
         x-transition:leave-start="opacity-100"
         x-transition:leave-end="opacity-0"
         class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50"
         @click.self="close()">
        
        <div :class="sizeClasses" 
             class="bg-white rounded-lg shadow-xl mx-4 w-full"
             x-transition:enter="transition ease-out duration-300"
             x-transition:enter-start="opacity-0 transform scale-95"
             x-transition:enter-end="opacity-100 transform scale-100"
             x-transition:leave="transition ease-in duration-200"
             x-transition:leave-start="opacity-100 transform scale-100"
             x-transition:leave-end="opacity-0 transform scale-95">
            
            <!-- Header -->
            <div class="flex items-center justify-between p-6 border-b">
                <h3 class="text-lg font-semibold" x-text="title"></h3>
                <button @click="close()" class="text-gray-400 hover:text-gray-600">
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                    </svg>
                </button>
            </div>
            
            <!-- Content -->
            <div class="p-6">
                <p x-text="content"></p>
            </div>
            
            <!-- Footer -->
            <div class="flex justify-end space-x-3 p-6 border-t">
                <button @click="close()" class="px-4 py-2 text-gray-600 border rounded hover:bg-gray-50">
                    Cancel
                </button>
                <button @click="close()" class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600">
                    Confirm
                </button>
            </div>
        </div>
    </div>
</div>
*/
```

#### Data Table with Sorting and Filtering
```javascript
function dataTable() {
    return {
        data: [],
        filteredData: [],
        searchTerm: '',
        sortColumn: '',
        sortDirection: 'asc',
        currentPage: 1,
        itemsPerPage: 10,
        loading: false,
        
        async init() {
            await this.loadData();
            this.filterData();
        },
        
        async loadData() {
            this.loading = true;
            try {
                const response = await fetch('/api/users');
                this.data = await response.json();
            } catch (error) {
                console.error('Failed to load data:', error);
            } finally {
                this.loading = false;
            }
        },
        
        filterData() {
            let filtered = this.data;
            
            // Apply search filter
            if (this.searchTerm) {
                filtered = filtered.filter(item => 
                    Object.values(item).some(value => 
                        String(value).toLowerCase().includes(this.searchTerm.toLowerCase())
                    )
                );
            }
            
            // Apply sorting
            if (this.sortColumn) {
                filtered.sort((a, b) => {
                    let aVal = a[this.sortColumn];
                    let bVal = b[this.sortColumn];
                    
                    // Handle different data types
                    if (typeof aVal === 'string') {
                        aVal = aVal.toLowerCase();
                        bVal = bVal.toLowerCase();
                    }
                    
                    if (aVal < bVal) return this.sortDirection === 'asc' ? -1 : 1;
                    if (aVal > bVal) return this.sortDirection === 'asc' ? 1 : -1;
                    return 0;
                });
            }
            
            this.filteredData = filtered;
            this.currentPage = 1; // Reset to first page
        },
        
        sort(column) {
            if (this.sortColumn === column) {
                this.sortDirection = this.sortDirection === 'asc' ? 'desc' : 'asc';
            } else {
                this.sortColumn = column;
                this.sortDirection = 'asc';
            }
            this.filterData();
        },
        
        get paginatedData() {
            const start = (this.currentPage - 1) * this.itemsPerPage;
            const end = start + this.itemsPerPage;
            return this.filteredData.slice(start, end);
        },
        
        get totalPages() {
            return Math.ceil(this.filteredData.length / this.itemsPerPage);
        },
        
        get pageNumbers() {
            const pages = [];
            const total = this.totalPages;
            const current = this.currentPage;
            
            // Always show first page
            pages.push(1);
            
            // Show pages around current page
            for (let i = Math.max(2, current - 1); i <= Math.min(total - 1, current + 1); i++) {
                if (!pages.includes(i)) {
                    pages.push(i);
                }
            }
            
            // Always show last page
            if (total > 1 && !pages.includes(total)) {
                pages.push(total);
            }
            
            return pages;
        },
        
        goToPage(page) {
            if (page >= 1 && page <= this.totalPages) {
                this.currentPage = page;
            }
        },
        
        getSortIcon(column) {
            if (this.sortColumn !== column) return '↕️';
            return this.sortDirection === 'asc' ? '↑' : '↓';
        }
    }
}

// Usage in HTML
/*
<div x-data="dataTable()" x-init="init()">
    <!-- Search -->
    <div class="mb-4">
        <input type="text" 
               x-model="searchTerm" 
               @input="filterData()"
               placeholder="Search..." 
               class="px-4 py-2 border rounded-lg w-full">
    </div>
    
    <!-- Loading State -->
    <div x-show="loading" class="text-center py-8">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto"></div>
        <p class="mt-2 text-gray-600">Loading...</p>
    </div>
    
    <!-- Table -->
    <div x-show="!loading" class="overflow-x-auto">
        <table class="min-w-full bg-white border border-gray-200">
            <thead class="bg-gray-50">
                <tr>
                    <th @click="sort('name')" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100">
                        Name <span x-text="getSortIcon('name')"></span>
                    </th>
                    <th @click="sort('email')" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100">
                        Email <span x-text="getSortIcon('email')"></span>
                    </th>
                    <th @click="sort('created_at')" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100">
                        Created <span x-text="getSortIcon('created_at')"></span>
                    </th>
                </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
                <template x-for="item in paginatedData" :key="item.id">
                    <tr class="hover:bg-gray-50">
                        <td class="px-6 py-4 whitespace-nowrap" x-text="item.name"></td>
                        <td class="px-6 py-4 whitespace-nowrap" x-text="item.email"></td>
                        <td class="px-6 py-4 whitespace-nowrap" x-text="new Date(item.created_at).toLocaleDateString()"></td>
                    </tr>
                </template>
            </tbody>
        </table>
    </div>
    
    <!-- Pagination -->
    <div x-show="totalPages > 1" class="flex items-center justify-between mt-4">
        <div class="text-sm text-gray-700">
            Showing <span x-text="(currentPage - 1) * itemsPerPage + 1"></span> to 
            <span x-text="Math.min(currentPage * itemsPerPage, filteredData.length)"></span> of 
            <span x-text="filteredData.length"></span> results
        </div>
        
        <div class="flex space-x-1">
            <button @click="goToPage(currentPage - 1)" 
                    :disabled="currentPage === 1"
                    :class="currentPage === 1 ? 'opacity-50 cursor-not-allowed' : 'hover:bg-gray-100'"
                    class="px-3 py-2 border rounded">
                Previous
            </button>
            
            <template x-for="page in pageNumbers" :key="page">
                <button @click="goToPage(page)" 
                        :class="page === currentPage ? 'bg-blue-500 text-white' : 'hover:bg-gray-100'"
                        class="px-3 py-2 border rounded"
                        x-text="page">
                </button>
            </template>
            
            <button @click="goToPage(currentPage + 1)" 
                    :disabled="currentPage === totalPages"
                    :class="currentPage === totalPages ? 'opacity-50 cursor-not-allowed' : 'hover:bg-gray-100'"
                    class="px-3 py-2 border rounded">
                Next
            </button>
        </div>
    </div>
</div>
*/
```

### Form Handling

#### Advanced Form with Validation
```javascript
function advancedForm() {
    return {
        form: {
            name: '',
            email: '',
            password: '',
            confirmPassword: '',
            terms: false
        },
        errors: {},
        touched: {},
        submitting: false,
        submitted: false,
        
        get isValid() {
            return Object.keys(this.getValidationErrors()).length === 0;
        },
        
        getValidationErrors() {
            const errors = {};
            
            // Name validation
            if (!this.form.name.trim()) {
                errors.name = 'Name is required';
            } else if (this.form.name.length < 2) {
                errors.name = 'Name must be at least 2 characters';
            }
            
            // Email validation
            if (!this.form.email.trim()) {
                errors.email = 'Email is required';
            } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(this.form.email)) {
                errors.email = 'Please enter a valid email address';
            }
            
            // Password validation
            if (!this.form.password) {
                errors.password = 'Password is required';
            } else if (this.form.password.length < 8) {
                errors.password = 'Password must be at least 8 characters';
            } else if (!/(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/.test(this.form.password)) {
                errors.password = 'Password must contain at least one uppercase letter, one lowercase letter, and one number';
            }
            
            // Confirm password validation
            if (!this.form.confirmPassword) {
                errors.confirmPassword = 'Please confirm your password';
            } else if (this.form.password !== this.form.confirmPassword) {
                errors.confirmPassword = 'Passwords do not match';
            }
            
            // Terms validation
            if (!this.form.terms) {
                errors.terms = 'You must accept the terms and conditions';
            }
            
            return errors;
        },
        
        validateField(field) {
            this.touched[field] = true;
            const allErrors = this.getValidationErrors();
            
            if (allErrors[field]) {
                this.errors[field] = allErrors[field];
            } else {
                delete this.errors[field];
            }
        },
        
        hasError(field) {
            return this.touched[field] && this.errors[field];
        },
        
        getFieldClass(field) {
            if (!this.touched[field]) return 'border-gray-300';
            return this.hasError(field) ? 'border-red-500' : 'border-green-500';
        },
        
        async submitForm() {
            // Mark all fields as touched
            Object.keys(this.form).forEach(field => {
                this.touched[field] = true;
            });
            
            // Validate all fields
            this.errors = this.getValidationErrors();
            
            if (!this.isValid) {
                return;
            }
            
            this.submitting = true;
            
            try {
                const response = await fetch('/api/register', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(this.form)
                });
                
                if (response.ok) {
                    this.submitted = true;
                    this.resetForm();
                } else {
                    const errorData = await response.json();
                    this.errors = errorData.errors || { general: 'Registration failed' };
                }
            } catch (error) {
                this.errors = { general: 'Network error. Please try again.' };
            } finally {
                this.submitting = false;
            }
        },
        
        resetForm() {
            this.form = {
                name: '',
                email: '',
                password: '',
                confirmPassword: '',
                terms: false
            };
            this.errors = {};
            this.touched = {};
            this.submitted = false;
        }
    }
}
```

## 🗄️ Database Examples

### Advanced SQL Queries

#### Complex Reporting Query
```sql
-- Sales Report with Rankings and Growth
WITH monthly_sales AS (
    SELECT 
        DATE_TRUNC('month', order_date) as month,
        user_id,
        SUM(total_amount) as monthly_total,
        COUNT(*) as order_count
    FROM orders 
    WHERE order_date >= CURRENT_DATE - INTERVAL '12 months'
        AND status = 'completed'
    GROUP BY DATE_TRUNC('month', order_date), user_id
),
user_growth AS (
    SELECT 
        user_id,
        month,
        monthly_total,
        order_count,
        LAG(monthly_total) OVER (PARTITION BY user_id ORDER BY month) as prev_month_total,
        ROW_NUMBER() OVER (PARTITION BY month ORDER BY monthly_total DESC) as monthly_rank
    FROM monthly_sales
),
top_customers AS (
    SELECT 
        u.id,
        u.name,
        u.email,
        ug.month,
        ug.monthly_total,
        ug.order_count,
        ug.prev_month_total,
        CASE 
            WHEN ug.prev_month_total IS NULL THEN NULL
            ELSE ROUND(((ug.monthly_total - ug.prev_month_total) / ug.prev_month_total * 100), 2)
        END as growth_percentage,
        ug.monthly_rank
    FROM user_growth ug
    JOIN users u ON u.id = ug.user_id
    WHERE ug.monthly_rank <= 10
)
SELECT 
    month,
    name as customer_name,
    email,
    monthly_total,
    order_count,
    growth_percentage,
    monthly_rank,
    CASE 
        WHEN growth_percentage > 20 THEN 'High Growth'
        WHEN growth_percentage > 0 THEN 'Positive Growth'
        WHEN growth_percentage < -20 THEN 'Declining'
        ELSE 'Stable'
    END as growth_category
FROM top_customers
ORDER BY month DESC, monthly_rank ASC;
```

#### Dynamic Search with Full-Text Search
```sql
-- PostgreSQL Full-Text Search Example
CREATE INDEX idx_products_search ON products 
USING GIN(to_tsvector('english', name || ' ' || description || ' ' || COALESCE(tags, '')));

-- Search function
CREATE OR REPLACE FUNCTION search_products(
    search_term TEXT,
    category_filter INTEGER[] DEFAULT NULL,
    price_min DECIMAL DEFAULT NULL,
    price_max DECIMAL DEFAULT NULL,
    sort_by TEXT DEFAULT 'relevance',
    limit_count INTEGER DEFAULT 20,
    offset_count INTEGER DEFAULT 0
)
RETURNS TABLE(
    id INTEGER,
    name VARCHAR,
    description TEXT,
    price DECIMAL,
    category_name VARCHAR,
    relevance_score REAL,
    total_count BIGINT
) AS $$
BEGIN
    RETURN QUERY
    WITH filtered_products AS (
        SELECT 
            p.id,
            p.name,
            p.description,
            p.price,
            c.name as category_name,
            CASE 
                WHEN search_term IS NOT NULL AND search_term != '' THEN
                    ts_rank(to_tsvector('english', p.name || ' ' || p.description || ' ' || COALESCE(p.tags, '')), 
                            plainto_tsquery('english', search_term))
                ELSE 0
            END as relevance_score
        FROM products p
        LEFT JOIN categories c ON c.id = p.category_id
        WHERE 
            (search_term IS NULL OR search_term = '' OR 
             to_tsvector('english', p.name || ' ' || p.description || ' ' || COALESCE(p.tags, '')) @@ plainto_tsquery('english', search_term))
            AND (category_filter IS NULL OR p.category_id = ANY(category_filter))
            AND (price_min IS NULL OR p.price >= price_min)
            AND (price_max IS NULL OR p.price <= price_max)
            AND p.active = true
    ),
    sorted_products AS (
        SELECT *,
               COUNT(*) OVER() as total_count
        FROM filtered_products
        ORDER BY 
            CASE WHEN sort_by = 'relevance' THEN relevance_score END DESC,
            CASE WHEN sort_by = 'price_asc' THEN price END ASC,
            CASE WHEN sort_by = 'price_desc' THEN price END DESC,
            CASE WHEN sort_by = 'name' THEN name END ASC,
            CASE WHEN sort_by = 'newest' THEN id END DESC
    )
    SELECT * FROM sorted_products
    LIMIT limit_count OFFSET offset_count;
END;
$$ LANGUAGE plpgsql;

-- Usage
SELECT * FROM search_products(
    'wireless headphones',
    ARRAY[1, 2, 3],  -- category IDs
    50.00,           -- min price
    500.00,          -- max price
    'relevance',     -- sort by
    20,              -- limit
    0                -- offset
);
```

### Database Optimization Examples

#### Index Strategy
```sql
-- Composite indexes for common query patterns
CREATE INDEX idx_orders_user_status_date ON orders (user_id, status, created_at);
CREATE INDEX idx_products_category_price ON products (category_id, price) WHERE active = true;

-- Partial indexes for specific conditions
CREATE INDEX idx_orders_pending ON orders (created_at) WHERE status = 'pending';
CREATE INDEX idx_users_active_email ON users (email) WHERE active = true;

-- Functional indexes
CREATE INDEX idx_users_lower_email ON users (LOWER(email));
CREATE INDEX idx_products_search_vector ON products USING GIN(to_tsvector('english', name || ' ' || description));

-- Query optimization with EXPLAIN ANALYZE
EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) 
SELECT u.name, COUNT(o.id) as order_count, SUM(o.total) as total_spent
FROM users u
LEFT JOIN orders o ON o.user_id = u.id AND o.status = 'completed'
WHERE u.created_at >= CURRENT_DATE - INTERVAL '1 year'
GROUP BY u.id, u.name
HAVING COUNT(o.id) > 5
ORDER BY total_spent DESC
LIMIT 100;
```

---

*This examples collection provides practical, production-ready code snippets that can be adapted and used in real-world projects. Each example includes best practices and common patterns used in modern web development.* 