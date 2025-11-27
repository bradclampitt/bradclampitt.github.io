# API Reference Guide

Comprehensive reference for API endpoints, authentication, and integration patterns used across projects.

## 🔐 Authentication

### Bearer Token Authentication
Most APIs use Bearer token authentication. Include the token in the Authorization header:

```bash
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
     https://api.example.com/endpoint
```

### API Key Authentication
Some services use API key authentication:

```bash
curl -H "X-API-Key: YOUR_API_KEY" \
     https://api.example.com/endpoint
```

### OAuth 2.0 Flow
For OAuth 2.0 authentication:

```bash
# Step 1: Get authorization code
https://oauth.example.com/authorize?client_id=YOUR_CLIENT_ID&response_type=code&redirect_uri=YOUR_REDIRECT_URI

# Step 2: Exchange code for access token
curl -X POST https://oauth.example.com/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=authorization_code&code=AUTH_CODE&client_id=YOUR_CLIENT_ID&client_secret=YOUR_CLIENT_SECRET"
```

## 🛒 E-commerce APIs

### Magento 2 REST API

#### Authentication
```bash
# Get admin token
curl -X POST "https://your-store.com/rest/V1/integration/admin/token" \
     -H "Content-Type: application/json" \
     -d '{"username":"admin","password":"password123"}'
```

#### Products
```bash
# Get all products
GET /rest/V1/products?searchCriteria[pageSize]=20

# Get product by SKU
GET /rest/V1/products/{sku}

# Create product
POST /rest/V1/products
Content-Type: application/json
Authorization: Bearer {token}

{
  "product": {
    "sku": "test-product",
    "name": "Test Product",
    "attribute_set_id": 4,
    "price": 29.99,
    "status": 1,
    "visibility": 4,
    "type_id": "simple",
    "weight": 1
  }
}

# Update product
PUT /rest/V1/products/{sku}

# Delete product
DELETE /rest/V1/products/{sku}
```

#### Orders
```bash
# Get all orders
GET /rest/V1/orders?searchCriteria[pageSize]=20

# Get order by ID
GET /rest/V1/orders/{id}

# Create order
POST /rest/V1/orders
{
  "entity": {
    "base_currency_code": "USD",
    "base_discount_amount": 0,
    "base_grand_total": 29.99,
    "base_subtotal": 29.99,
    "billing_address": {
      "address_type": "billing",
      "city": "Austin",
      "country_id": "US",
      "firstname": "John",
      "lastname": "Doe",
      "postcode": "78701",
      "region": "Texas",
      "street": ["123 Main St"],
      "telephone": "555-1234"
    }
  }
}
```

#### Customers
```bash
# Get all customers
GET /rest/V1/customers/search?searchCriteria[pageSize]=20

# Get customer by ID
GET /rest/V1/customers/{id}

# Create customer
POST /rest/V1/customers
{
  "customer": {
    "email": "john@example.com",
    "firstname": "John",
    "lastname": "Doe",
    "addresses": [{
      "defaultShipping": true,
      "defaultBilling": true,
      "firstname": "John",
      "lastname": "Doe",
      "region": {
        "regionCode": "TX",
        "region": "Texas",
        "regionId": 57
      },
      "postcode": "78701",
      "street": ["123 Main St"],
      "city": "Austin",
      "telephone": "555-1234",
      "countryId": "US"
    }]
  },
  "password": "password123"
}
```

### Shopify REST API

#### Authentication
```bash
# Using private app credentials
curl -H "X-Shopify-Access-Token: YOUR_ACCESS_TOKEN" \
     https://your-shop.myshopify.com/admin/api/2023-01/products.json
```

#### Products
```bash
# Get products
GET /admin/api/2023-01/products.json

# Create product
POST /admin/api/2023-01/products.json
{
  "product": {
    "title": "Test Product",
    "body_html": "<strong>Good product!</strong>",
    "vendor": "Test Vendor",
    "product_type": "Test Type",
    "variants": [{
      "price": "29.99",
      "sku": "test-123"
    }]
  }
}
```

## 💳 Payment APIs

### Stripe API

#### Authentication
```bash
curl -u sk_test_your_secret_key: \
     https://api.stripe.com/v1/charges
```

#### Common Endpoints
```bash
# Create payment intent
POST https://api.stripe.com/v1/payment_intents
{
  "amount": 2999,
  "currency": "usd",
  "payment_method_types": ["card"]
}

# Create customer
POST https://api.stripe.com/v1/customers
{
  "email": "customer@example.com",
  "name": "John Doe"
}

# Create subscription
POST https://api.stripe.com/v1/subscriptions
{
  "customer": "cus_customer_id",
  "items": [{
    "price": "price_id"
  }]
}
```

### PayPal API

#### Authentication
```bash
# Get access token
curl -X POST https://api.sandbox.paypal.com/v1/oauth2/token \
  -H "Accept: application/json" \
  -H "Accept-Language: en_US" \
  -u "client_id:client_secret" \
  -d "grant_type=client_credentials"
```

#### Create Payment
```bash
POST https://api.sandbox.paypal.com/v1/payments/payment
{
  "intent": "sale",
  "payer": {
    "payment_method": "paypal"
  },
  "transactions": [{
    "amount": {
      "total": "29.99",
      "currency": "USD"
    },
    "description": "Payment description"
  }],
  "redirect_urls": {
    "return_url": "https://example.com/return",
    "cancel_url": "https://example.com/cancel"
  }
}
```

## 📧 Communication APIs

### SendGrid API

#### Send Email
```bash
POST https://api.sendgrid.com/v3/mail/send
Authorization: Bearer YOUR_API_KEY
Content-Type: application/json

{
  "personalizations": [{
    "to": [{"email": "recipient@example.com"}],
    "subject": "Hello from SendGrid"
  }],
  "from": {"email": "sender@example.com"},
  "content": [{
    "type": "text/html",
    "value": "<p>Hello, World!</p>"
  }]
}
```

### Twilio API

#### Send SMS
```bash
POST https://api.twilio.com/2010-04-01/Accounts/{AccountSid}/Messages.json
Authorization: Basic {base64(AccountSid:AuthToken)}

Body=Hello%20from%20Twilio&From=%2B1234567890&To=%2B0987654321
```

## ☁️ AWS APIs

### S3 API

#### Upload File
```bash
# Using AWS CLI
aws s3 cp file.txt s3://bucket-name/

# Using curl (with pre-signed URL)
curl -X PUT "https://bucket-name.s3.amazonaws.com/file.txt?X-Amz-Signature=..." \
     -H "Content-Type: text/plain" \
     --data-binary @file.txt
```

### Lambda API

#### Invoke Function
```bash
aws lambda invoke \
  --function-name my-function \
  --payload '{"key": "value"}' \
  response.json
```

## 📊 Analytics APIs

### Google Analytics 4

#### Authentication (Service Account)
```python
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import RunReportRequest

client = BetaAnalyticsDataClient.from_service_account_file("credentials.json")

request = RunReportRequest(
    property=f"properties/{property_id}",
    dimensions=[{"name": "city"}],
    metrics=[{"name": "sessions"}],
    date_ranges=[{"start_date": "2023-01-01", "end_date": "today"}]
)

response = client.run_report(request)
```

### Facebook Graph API

#### Get Page Insights
```bash
GET https://graph.facebook.com/v18.0/{page-id}/insights?metric=page_views_total&access_token={access-token}
```

## 🔍 Search APIs

### Elasticsearch

#### Search Documents
```bash
POST /index_name/_search
{
  "query": {
    "match": {
      "title": "search term"
    }
  },
  "size": 10,
  "from": 0
}
```

### Algolia

#### Search Index
```bash
POST https://APPLICATION_ID-dsn.algolia.net/1/indexes/INDEX_NAME/query
X-Algolia-API-Key: SEARCH_API_KEY
X-Algolia-Application-Id: APPLICATION_ID

{
  "query": "search term",
  "hitsPerPage": 20,
  "page": 0
}
```

## 📱 Social Media APIs

### Twitter API v2

#### Get Tweets
```bash
GET https://api.twitter.com/2/tweets/search/recent?query=from:username
Authorization: Bearer YOUR_BEARER_TOKEN
```

### Instagram Basic Display API

#### Get User Media
```bash
GET https://graph.instagram.com/me/media?fields=id,caption,media_type,media_url&access_token={access-token}
```

## 🛠️ Development Tools APIs

### GitHub API

#### Get Repository Information
```bash
GET https://api.github.com/repos/owner/repo
Authorization: token YOUR_PERSONAL_ACCESS_TOKEN
```

#### Create Issue
```bash
POST https://api.github.com/repos/owner/repo/issues
{
  "title": "Issue title",
  "body": "Issue description",
  "labels": ["bug", "priority-high"]
}
```

### Slack API

#### Send Message
```bash
POST https://slack.com/api/chat.postMessage
Authorization: Bearer xoxb-your-token
Content-Type: application/json

{
  "channel": "#general",
  "text": "Hello from API!"
}
```

## 📈 Error Handling Best Practices

### HTTP Status Codes
- `200 OK` - Request successful
- `201 Created` - Resource created successfully
- `400 Bad Request` - Invalid request parameters
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Access denied
- `404 Not Found` - Resource not found
- `429 Too Many Requests` - Rate limit exceeded
- `500 Internal Server Error` - Server error

### Error Response Format
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input parameters",
    "details": {
      "email": ["Email is required"],
      "password": ["Password must be at least 8 characters"]
    },
    "timestamp": "2024-01-15T10:30:00Z",
    "request_id": "req_123456789"
  }
}
```

### Rate Limiting
Most APIs implement rate limiting. Check response headers:
- `X-RateLimit-Limit` - Total requests allowed
- `X-RateLimit-Remaining` - Remaining requests
- `X-RateLimit-Reset` - Time when limit resets

## 🔧 Testing APIs

### Using curl
```bash
# GET request
curl -X GET "https://api.example.com/users" \
     -H "Authorization: Bearer token"

# POST request with JSON
curl -X POST "https://api.example.com/users" \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer token" \
     -d '{"name":"John","email":"john@example.com"}'

# Upload file
curl -X POST "https://api.example.com/upload" \
     -H "Authorization: Bearer token" \
     -F "file=@document.pdf"
```

### Using Postman
1. Create new request
2. Set HTTP method and URL
3. Add headers (Authorization, Content-Type)
4. Add request body (JSON, form-data, etc.)
5. Send request and review response

### Using JavaScript/Node.js
```javascript
// Using fetch
const response = await fetch('https://api.example.com/users', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + token
  },
  body: JSON.stringify({
    name: 'John',
    email: 'john@example.com'
  })
});

const data = await response.json();

// Using axios
const axios = require('axios');

const response = await axios.post('https://api.example.com/users', {
  name: 'John',
  email: 'john@example.com'
}, {
  headers: {
    'Authorization': 'Bearer ' + token
  }
});
```

---

*This API reference is continuously updated with new endpoints and best practices. Contribute improvements through our documentation process.* 